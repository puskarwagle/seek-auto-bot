"""
Structured Logging Module
Handles all logging with JSON structure and multiple outputs
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger as loguru_logger

from utils.storage import JSONStorage


class StructuredLogger:
    def __init__(self):
        self.storage = None
        self.setup_complete = False
        
    def setup(self):
        """Setup structured logging"""
        if self.setup_complete:
            return
            
        # Remove default handler
        loguru_logger.remove()
        
        # Console handler with colors
        loguru_logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # File handler for detailed logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        loguru_logger.add(
            log_dir / "seek_bot.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
        
        # JSON file handler for structured logs
        loguru_logger.add(
            log_dir / "seek_bot.json",
            format=self._json_formatter,
            level="INFO",
            rotation="10 MB",
            retention="7 days"
        )
        
        # Initialize storage after setup
        try:
            self.storage = JSONStorage()
        except Exception as e:
            loguru_logger.error(f"Failed to initialize storage for logging: {e}")
        
        self.setup_complete = True
        loguru_logger.info("Structured logging initialized")
    
    def _json_formatter(self, record) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "process": record["process"].id,
            "thread": record["thread"].id
        }
        
        # Add extra data if present
        if record.get("extra"):
            log_data["extra"] = record["extra"]
        
        return json.dumps(log_data)
    
    def log(self, level: str, message: str, module: str = None, **kwargs):
        """Log message with structured data"""
        if not self.setup_complete:
            self.setup()
        
        # Add extra context
        extra_data = {
            "module": module or "seek_bot",
            **kwargs
        }
        
        # Log to file/console
        getattr(loguru_logger, level.lower())(message, extra=extra_data)
        
        # Save to JSON storage
        if self.storage:
            try:
                self.storage.save_log({
                    "level": level.upper(),
                    "message": message,
                    "module": module or "seek_bot",
                    "data": kwargs
                })
            except Exception as e:
                loguru_logger.error(f"Failed to save log to storage: {e}")
    
    def info(self, message: str, module: str = None, **kwargs):
        """Log info message"""
        self.log("INFO", message, module, **kwargs)
    
    def debug(self, message: str, module: str = None, **kwargs):
        """Log debug message"""
        self.log("DEBUG", message, module, **kwargs)
    
    def warning(self, message: str, module: str = None, **kwargs):
        """Log warning message"""
        self.log("WARNING", message, module, **kwargs)
    
    def error(self, message: str, module: str = None, **kwargs):
        """Log error message"""
        self.log("ERROR", message, module, **kwargs)
    
    def critical(self, message: str, module: str = None, **kwargs):
        """Log critical message"""
        self.log("CRITICAL", message, module, **kwargs)
    
    def auth(self, message: str, success: bool = True, **kwargs):
        """Log authentication events"""
        level = "INFO" if success else "ERROR"
        self.log(level, message, "auth", success=success, **kwargs)
    
    def scraper(self, message: str, jobs_count: int = 0, **kwargs):
        """Log scraper events"""
        self.log("INFO", message, "scraper", jobs_count=jobs_count, **kwargs)
    
    def applicator(self, message: str, applied_count: int = 0, **kwargs):
        """Log application events"""
        self.log("INFO", message, "applicator", applied_count=applied_count, **kwargs)
    
    def bot_status(self, status: str, task: str = None, **kwargs):
        """Log bot status changes"""
        self.log("INFO", f"Bot status: {status}", "bot", task=task, **kwargs)
    
    def performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.log("INFO", f"Performance: {operation} took {duration:.2f}s", "performance", 
                operation=operation, duration=duration, **kwargs)
    
    def api_call(self, endpoint: str, method: str, status_code: int = None, **kwargs):
        """Log API calls"""
        level = "INFO" if status_code and status_code < 400 else "ERROR"
        self.log(level, f"API call: {method} {endpoint}", "api", 
                method=method, endpoint=endpoint, status_code=status_code, **kwargs)
    
    def security(self, event: str, severity: str = "INFO", **kwargs):
        """Log security events"""
        self.log(severity, f"Security: {event}", "security", event=event, **kwargs)
    
    def get_recent_logs(self, limit: int = 100, level: str = None) -> list:
        """Get recent logs from storage with optional level filtering"""
        if not self.storage:
            return []

        try:
            logs = self.storage.load_logs()

            # Filter by level if specified
            if level:
                logs = [log for log in logs if log.get("level", "").upper() == level.upper()]

            # Sort by timestamp descending (most recent first)
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return logs[:limit]
        except Exception as e:
            loguru_logger.error(f"Failed to retrieve recent logs: {e}")
            return []
