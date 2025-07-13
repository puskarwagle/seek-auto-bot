"""
API Routes for Seek Bot Dashboard
All REST endpoints for bot control and data
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logging import logger
from utils.storage import JSONStorage
from utils.errors import SeekBotError
from main import SeekBot


# Global bot instance
bot_instance: Optional[SeekBot] = None
router = APIRouter()


# Pydantic models
class ConfigModel(BaseModel):
    """User configuration model"""
    email: str = Field(..., description="Seek account email")
    password: str = Field(..., description="Seek account password")
    agreement_accepted: bool = Field(False, description="Terms agreement")
    
    # Job preferences
    keywords: list[str] = Field(default=[], description="Job search keywords")
    locations: list[str] = Field(default=[], description="Preferred locations")
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    job_types: list[str] = Field(default=[], description="Job types")
    experience_levels: list[str] = Field(default=[], description="Experience levels")
    
    # Application settings
    auto_apply: bool = Field(True, description="Auto-apply to jobs")
    max_applications_per_day: int = Field(20, description="Daily application limit")
    cover_letter_template: str = Field("", description="Cover letter template")
    cv_path: str = Field("", description="CV file path")
    
    # DeepSeek API
    deepseek_api_key: str = Field("", description="DeepSeek API key")
    deepseek_enabled: bool = Field(False, description="Enable DeepSeek features")


class StatusResponse(BaseModel):
    """Bot status response"""
    running: bool
    current_task: str
    timestamp: str
    jobs_found: int = 0
    applications_sent: int = 0
    errors: int = 0


class LogEntry(BaseModel):
    """Log entry model"""
    timestamp: str
    level: str
    message: str
    module: str


# Routes
@router.get("/status")
async def get_bot_status() -> StatusResponse:
    """Get current bot status"""
    try:
        global bot_instance
        storage = JSONStorage()
        
        if bot_instance:
            status = bot_instance.get_status()
        else:
            status = {
                "running": False,
                "current_task": "idle",
                "timestamp": storage.get_timestamp()
            }
        
        # Get job stats
        jobs_data = storage.load_jobs()
        applied_data = storage.load_applied_jobs()
        
        return StatusResponse(
            running=status["running"],
            current_task=status["current_task"],
            timestamp=status["timestamp"],
            jobs_found=len(jobs_data),
            applications_sent=len(applied_data),
            errors=0  # TODO: Track errors
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_bot(background_tasks: BackgroundTasks):
    """Start the bot"""
    try:
        global bot_instance
        
        if bot_instance and bot_instance.running:
            raise HTTPException(status_code=400, detail="Bot is already running")
        
        # Create new bot instance
        bot_instance = SeekBot()
        
        # Start bot in background
        background_tasks.add_task(run_bot_async)
        
        logger.info("Bot started successfully")
        return {"message": "Bot started successfully", "status": "running"}
        
    except Exception as e:
        logger.error(f"Bot start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_bot():
    """Stop the bot"""
    try:
        global bot_instance
        
        if not bot_instance or not bot_instance.running:
            raise HTTPException(status_code=400, detail="Bot is not running")
        
        await bot_instance.stop()
        logger.info("Bot stopped successfully")
        
        return {"message": "Bot stopped successfully", "status": "stopped"}
        
    except Exception as e:
        logger.error(f"Bot stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    try:
        storage = JSONStorage()
        config = storage.load_config()
        
        if not config:
            # Return default config
            return {
                "user": {
                    "email": "",
                    "password": "",
                    "agreement_accepted": False
                },
                "job_preferences": {
                    "keywords": [],
                    "locations": [],
                    "salary_min": None,
                    "salary_max": None,
                    "job_types": [],
                    "experience_levels": []
                },
                "application_settings": {
                    "auto_apply": True,
                    "max_applications_per_day": 20,
                    "cover_letter_template": "",
                    "cv_path": ""
                },
                "deepseek_api": {
                    "api_key": "",
                    "enabled": False
                }
            }
        
        # Hide sensitive data
        if config.get("user", {}).get("password"):
            config["user"]["password"] = "***"
        if config.get("deepseek_api", {}).get("api_key"):
            config["deepseek_api"]["api_key"] = "***"
        
        return config
        
    except Exception as e:
        logger.error(f"Config retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_config(config: ConfigModel):
    """Update configuration"""
    try:
        storage = JSONStorage()
        
        # Build config structure
        config_data = {
            "user": {
                "email": config.email,
                "password": config.password,
                "agreement_accepted": config.agreement_accepted,
                "agreement_timestamp": storage.get_timestamp()
            },
            "job_preferences": {
                "keywords": config.keywords,
                "locations": config.locations,
                "salary_min": config.salary_min,
                "salary_max": config.salary_max,
                "job_types": config.job_types,
                "experience_levels": config.experience_levels
            },
            "application_settings": {
                "auto_apply": config.auto_apply,
                "max_applications_per_day": config.max_applications_per_day,
                "cover_letter_template": config.cover_letter_template,
                "cv_path": config.cv_path
            },
            "deepseek_api": {
                "api_key": config.deepseek_api_key,
                "enabled": config.deepseek_enabled
            }
        }
        
        # Save configuration
        storage.save_config(config_data)
        
        logger.info("Configuration updated successfully")
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Config update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_jobs():
    """Get scraped jobs"""
    try:
        storage = JSONStorage()
        jobs = storage.load_jobs()
        return {"jobs": jobs, "count": len(jobs)}
        
    except Exception as e:
        logger.error(f"Jobs retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applied")
async def get_applied_jobs():
    """Get applied jobs history"""
    try:
        storage = JSONStorage()
        applied = storage.load_applied_jobs()
        return {"applied": applied, "count": len(applied)}
        
    except Exception as e:
        logger.error(f"Applied jobs retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_logs(limit: int = 100):
    """Get application logs"""
    try:
        storage = JSONStorage()
        logs = storage.load_logs()
        
        # Return last N logs
        return {"logs": logs[-limit:], "count": len(logs)}
        
    except Exception as e:
        logger.error(f"Logs retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data")
async def clear_data(data_type: str):
    """Clear specific data type"""
    try:
        storage = JSONStorage()
        
        if data_type == "jobs":
            storage.clear_jobs()
        elif data_type == "applied":
            storage.clear_applied_jobs()
        elif data_type == "logs":
            storage.clear_logs()
        elif data_type == "all":
            storage.clear_all_data()
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        logger.info(f"Cleared {data_type} data")
        return {"message": f"Cleared {data_type} data successfully"}
        
    except Exception as e:
        logger.error(f"Data clearing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_bot_async():
    """Run bot in background task"""
    try:
        global bot_instance
        if bot_instance:
            await bot_instance.start()
    except Exception as e:
        logger.error(f"Background bot execution failed: {e}")
        if bot_instance:
            bot_instance.running = False
            bot_instance.current_task = "error"