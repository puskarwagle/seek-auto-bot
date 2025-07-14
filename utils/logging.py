"""
Structured Logging Module
Handles all logging with JSON structure and multiple outputs
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger as loguru_logger


class StructuredLogger:
    def __init__(self):
        self.setup_complete = False
        self.data_dir = Path("data")
        self.logs_file = self.data_dir / "logs.json"

    def setup(self):
        """Setup structured logging"""
        if self.setup_complete:
            return

        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)

        # Remove default Loguru handler
        loguru_logger.remove()

        # Console handler with colors and proper format keys
        loguru_logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True,
        )

        # File handler for detailed logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        loguru_logger.add(
            log_dir / "seek_bot.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
        )

        # JSON file handler - use sink function instead of format string
        loguru_logger.add(
            self._json_sink,
            level="INFO",
        )

        self.setup_complete = True
        loguru_logger.info("Structured logging initialized")

    def _json_sink(self, message):
        """JSON sink function that writes to file"""
        try:
            # Extract record from message
            record = message.record
            
            log_data = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "module": record["name"],
                "function": record["function"],
                "line": record["line"],
                "message": str(record["message"]),
                "process": record["process"].id,
                "thread": record["thread"].id,
            }

            # Add extra data if present
            if record.get("extra"):
                log_data["extra"] = record["extra"]

            # Write to JSON log file
            log_dir = Path("logs")
            json_file = log_dir / "seek_bot.json"
            
            with open(json_file, "a") as f:
                f.write(json.dumps(log_data) + "\n")
                
        except Exception as e:
            # Fallback to stderr if JSON logging fails
            print(f"JSON logging failed: {e}", file=sys.stderr)

    def _save_log_to_storage(self, log_data: Dict[str, Any]):
        """Save log to JSON storage independently"""
        try:
            if "timestamp" not in log_data:
                log_data["timestamp"] = datetime.now().isoformat()

            logs = self._load_logs_from_storage()

            logs.append(log_data)

            # Keep only last 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]

            with open(self.logs_file, "w") as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            loguru_logger.error(f"Failed to save log to storage: {e}")

    def _load_logs_from_storage(self) -> List[Dict[str, Any]]:
        """Load logs from JSON storage independently"""
        try:
            if self.logs_file.exists():
                with open(self.logs_file, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            loguru_logger.error(f"Failed to load logs from storage: {e}")
            return []

    def log(self, level: str, message: str, module: str = None, **kwargs):
        """Log message with structured data"""
        if not self.setup_complete:
            self.setup()

        extra_data = {
            "extra": {
                "module": module or "seek_bot",
                **kwargs,
            }
        }

        # Log to file/console
        getattr(loguru_logger, level.lower())(message, **extra_data)

        # Save to JSON storage independently
        self._save_log_to_storage(
            {
                "timestamp": datetime.now().isoformat(),
                "level": level.upper(),
                "message": message,
                "module": module or "seek_bot",
                "data": kwargs,
            }
        )

    def info(self, message: str, module: str = None, **kwargs):
        self.log("INFO", message, module, **kwargs)

    def debug(self, message: str, module: str = None, **kwargs):
        self.log("DEBUG", message, module, **kwargs)

    def warning(self, message: str, module: str = None, **kwargs):
        self.log("WARNING", message, module, **kwargs)

    def error(self, message: str, module: str = None, **kwargs):
        self.log("ERROR", message, module, **kwargs)

    def critical(self, message: str, module: str = None, **kwargs):
        self.log("CRITICAL", message, module, **kwargs)

    # Your custom log methods stay the same below
    def auth(self, message: str, success: bool = True, **kwargs):
        level = "INFO" if success else "ERROR"
        self.log(level, message, "auth", success=success, **kwargs)

    def scraper(self, message: str, jobs_count: int = 0, **kwargs):
        self.log("INFO", message, "scraper", jobs_count=jobs_count, **kwargs)

    def applicator(self, message: str, applied_count: int = 0, **kwargs):
        self.log("INFO", message, "applicator", applied_count=applied_count, **kwargs)

    def bot_status(self, status: str, task: str = None, **kwargs):
        self.log("INFO", f"Bot status: {status}", "bot", task=task, **kwargs)

    def performance(self, operation: str, duration: float, **kwargs):
        self.log(
            "INFO",
            f"Performance: {operation} took {duration:.2f}s",
            "performance",
            operation=operation,
            duration=duration,
            **kwargs,
        )

    def api_call(self, endpoint: str, method: str, status_code: int = None, **kwargs):
        level = "INFO" if status_code and status_code < 400 else "ERROR"
        self.log(
            level,
            f"API call: {method} {endpoint}",
            "api",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            **kwargs,
        )

    def security(self, event: str, severity: str = "INFO", **kwargs):
        self.log(severity, f"Security: {event}", "security", event=event, **kwargs)

    def get_recent_logs(self, limit: int = 100, level: str = None) -> List[Dict[str, Any]]:
        try:
            logs = self._load_logs_from_storage()
            if level:
                logs = [log for log in logs if log.get("level", "").upper() == level.upper()]
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return logs[:limit]
        except Exception as e:
            loguru_logger.error(f"Failed to retrieve recent logs: {e}")
            return []


# Global logger instance
_logger = StructuredLogger()


def setup_logging():
    """Setup structured logging - call once at app startup"""
    _logger.setup()


logger = _logger