# api/routes.py
"""
API Routes for Seek Bot Dashboard
All REST endpoints for bot control and data
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
import os
import uuid

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logging import logger
from utils.storage import JSONStorage
from utils.errors import SeekBotError
from core.bot import SeekBot


# Global bot instance
bot_instance: Optional[SeekBot] = None
router = APIRouter()


# Pydantic models
class ConfigModel(BaseModel):
    """User configuration model"""
    # User settings
    agreement_accepted: bool = Field(False, description="Terms agreement")
    
    # Job preferences
    keywords: list[str] = Field(default=[], description="Job search keywords")
    excluded_keywords: list[str] = Field(default=[], description="Keywords to exclude")
    locations: list[str] = Field(default=[], description="Preferred locations")
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    job_types: list[str] = Field(default=[], description="Job types")
    experience_levels: list[str] = Field(default=[], description="Experience levels")
    industries: list[str] = Field(default=[], description="Preferred industries")
    company_size: list[str] = Field(default=[], description="Company size preferences")
    remote_preference: str = Field("any", description="Remote work preference")
    visa_sponsorship: bool = Field(False, description="Requires visa sponsorship")
    minimum_rating: float = Field(3.5, description="Minimum company rating")
    
    # Application settings
    auto_apply: bool = Field(True, description="Auto-apply to jobs")
    max_applications_per_day: int = Field(1, description="Daily application limit")
    cover_letter_template: str = Field("", description="Cover letter template")
    cv_path: str = Field("", description="CV file path")
    apply_to_agencies: bool = Field(False, description="Apply to recruitment agencies")
    skip_assessment_required: bool = Field(True, description="Skip jobs requiring assessments")
    minimum_job_age_days: int = Field(1, description="Minimum job age in days")
    maximum_job_age_days: int = Field(7, description="Maximum job age in days")
    preferred_application_times: list[str] = Field(default=[], description="Preferred application times")
    
    # Filters
    excluded_companies: list[str] = Field(default=[], description="Companies to exclude")
    required_benefits: list[str] = Field(default=[], description="Required benefits")
    avoid_unpaid_trials: bool = Field(True, description="Avoid unpaid trial positions")
    minimum_description_length: int = Field(100, description="Minimum job description length")
    require_salary_disclosed: bool = Field(False, description="Require salary to be disclosed")
    
    # Smart matching
    skill_weight: float = Field(0.4, description="Weight for skill matching")
    location_weight: float = Field(0.2, description="Weight for location matching")
    salary_weight: float = Field(0.3, description="Weight for salary matching")
    company_weight: float = Field(0.1, description="Weight for company matching")
    auto_learn_preferences: bool = Field(True, description="Auto-learn from user preferences")
    
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
                "agreement_accepted": config.agreement_accepted,
                "agreement_timestamp": storage.get_timestamp() if config.agreement_accepted else None
            },
            "job_preferences": {
                "keywords": config.keywords,
                "excluded_keywords": config.excluded_keywords,
                "locations": config.locations,
                "salary_min": config.salary_min,
                "salary_max": config.salary_max,
                "job_types": config.job_types,
                "experience_levels": config.experience_levels,
                "industries": config.industries,
                "company_size": config.company_size,
                "remote_preference": config.remote_preference,
                "visa_sponsorship": config.visa_sponsorship,
                "minimum_rating": config.minimum_rating
            },
            "application_settings": {
                "auto_apply": config.auto_apply,
                "max_applications_per_day": config.max_applications_per_day,
                "cover_letter_template": config.cover_letter_template,
                "cv_path": config.cv_path,
                "apply_to_agencies": config.apply_to_agencies,
                "skip_assessment_required": config.skip_assessment_required,
                "minimum_job_age_days": config.minimum_job_age_days,
                "maximum_job_age_days": config.maximum_job_age_days,
                "preferred_application_times": config.preferred_application_times
            },
            "filters": {
                "excluded_companies": config.excluded_companies,
                "required_benefits": config.required_benefits,
                "avoid_unpaid_trials": config.avoid_unpaid_trials,
                "minimum_description_length": config.minimum_description_length,
                "require_salary_disclosed": config.require_salary_disclosed
            },
            "smart_matching": {
                "skill_weight": config.skill_weight,
                "location_weight": config.location_weight,
                "salary_weight": config.salary_weight,
                "company_weight": config.company_weight,
                "auto_learn_preferences": config.auto_learn_preferences
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


@router.post("/test-config")
async def test_config():
    """Test current configuration"""
    try:
        storage = JSONStorage()
        config = storage.load_config()
        
        # Basic validation
        if not config.get("user", {}).get("agreement_accepted"):
            return {"success": False, "message": "Terms not accepted"}
        
        if not config.get("job_preferences", {}).get("keywords"):
            return {"success": False, "message": "No keywords specified"}
        
        return {"success": True, "message": "Configuration is valid"}
        
    except Exception as e:
        logger.error(f"Config test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/reset")
async def reset_config():
    """Reset configuration to defaults"""
    try:
        storage = JSONStorage()
        # Delete existing config file to trigger default creation
        if storage.config_file.exists():
            storage.config_file.unlink()
        
        # Create new default config
        storage._create_default_config()
        
        logger.info("Configuration reset to defaults")
        return {"message": "Configuration reset successfully"}
        
    except Exception as e:
        logger.error(f"Config reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-resume")
async def upload_resume(resume: UploadFile = File(...)):
    """Upload resume file to data directory"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "application/msword", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if resume.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are allowed")
        
        # Validate file size (5MB max)
        if resume.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(resume.filename).suffix
        unique_filename = f"resume_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = data_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)
        
        logger.info(f"Resume uploaded successfully: {unique_filename}")
        
        return {
            "success": True,
            "filename": unique_filename,
            "filepath": str(file_path),
            "message": "Resume uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply")
async def apply_to_job(job_data: dict):
    """Apply to a specific job"""
    try:
        storage = JSONStorage()
        job_id = job_data.get("job_id")
        
        if not job_id:
            raise HTTPException(status_code=400, detail="Job ID required")
        
        # Check if already applied
        if storage.is_job_applied(job_id):
            return {"success": False, "message": "Already applied to this job"}
        
        # Find job in storage
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("id") == job_id), None)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Save application
        success = storage.save_applied_job(job)
        
        if success:
            logger.info(f"Applied to job: {job.get('title')}")
            return {"success": True, "message": "Application submitted successfully"}
        else:
            return {"success": False, "message": "Failed to save application"}
        
    except Exception as e:
        logger.error(f"Job application failed: {e}")
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