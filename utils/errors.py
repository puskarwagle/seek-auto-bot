"""
Seek Bot Error Handling Module
Comprehensive error handling with structured logging and recovery strategies
"""

import traceback
import sys
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pathlib import Path

from utils.logging import logger


class SeekBotError(Exception):
    """Base exception for all Seek Bot errors"""
    
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API responses"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class AuthError(SeekBotError):
    """Authentication and authorization errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_ERROR", details)


class ScrapingError(SeekBotError):
    """Job scraping and data extraction errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SCRAPING_ERROR", details)


class ApplicationError(SeekBotError):
    """Job application submission errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "APPLICATION_ERROR", details)


class ConfigurationError(SeekBotError):
    """Configuration and setup errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class BrowserError(SeekBotError):
    """Browser automation and WebDriver errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BROWSER_ERROR", details)


class RateLimitError(SeekBotError):
    """Rate limiting and anti-detection errors"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class ValidationError(SeekBotError):
    """Data validation and format errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class StorageError(SeekBotError):
    """File system and data storage errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "STORAGE_ERROR", details)


class NetworkError(SeekBotError):
    """Network connectivity and HTTP errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, "NETWORK_ERROR", details)


# Error Handler Functions
def handle_critical_error(error: Exception, context: str = "Unknown context"):
    """Handle critical errors that should stop execution"""
    error_data = {
        "context": context,
        "error_type": type(error).__name__,
        "message": str(error),
        "traceback": traceback.format_exc(),
        "timestamp": datetime.now().isoformat()
    }
    
    logger.critical("Critical error occurred", extra=error_data)
    
    # Store error for dashboard
    try:
        from utils.storage import JSONStorage
        storage = JSONStorage()
        storage.save_log(error_data)
    except Exception as storage_error:
        logger.error(f"Failed to store error log: {storage_error}")


def handle_auth_error(error: Exception, context: str = "Authentication"):
    """Handle authentication errors with specific logging"""
    if isinstance(error, AuthError):
        logger.error(f"Auth error in {context}: {error.message}", extra=error.to_dict())
    else:
        auth_error = AuthError(f"Authentication failed: {str(error)}", details={"original_error": str(error)})
        logger.error(f"Auth error in {context}: {auth_error.message}", extra=auth_error.to_dict())


def handle_scraping_error(error: Exception, context: str = "Scraping", recoverable: bool = True):
    """Handle scraping errors with recovery strategies"""
    if isinstance(error, ScrapingError):
        scraping_error = error
    else:
        scraping_error = ScrapingError(f"Scraping failed: {str(error)}", details={"original_error": str(error)})
    
    log_level = "warning" if recoverable else "error"
    getattr(logger, log_level)(f"Scraping error in {context}: {scraping_error.message}", extra=scraping_error.to_dict())
    
    return scraping_error


def handle_application_error(error: Exception, job_id: Optional[str] = None):
    """Handle job application errors"""
    details = {"job_id": job_id} if job_id else {}
    
    if isinstance(error, ApplicationError):
        app_error = error
    else:
        app_error = ApplicationError(f"Application failed: {str(error)}", details=details)
    
    logger.error(f"Application error for job {job_id}: {app_error.message}", extra=app_error.to_dict())
    return app_error


def handle_browser_error(error: Exception, action: str = "Browser action"):
    """Handle browser automation errors"""
    if isinstance(error, BrowserError):
        browser_error = error
    else:
        browser_error = BrowserError(f"Browser error during {action}: {str(error)}", details={"action": action})
    
    logger.error(f"Browser error: {browser_error.message}", extra=browser_error.to_dict())
    return browser_error


def handle_rate_limit_error(error: Exception, retry_after: Optional[int] = None):
    """Handle rate limiting errors"""
    if isinstance(error, RateLimitError):
        rate_error = error
    else:
        rate_error = RateLimitError(f"Rate limit exceeded: {str(error)}", retry_after=retry_after)
    
    logger.warning(f"Rate limit error: {rate_error.message}", extra=rate_error.to_dict())
    return rate_error


def handle_validation_error(error: Exception, field: Optional[str] = None):
    """Handle data validation errors"""
    if isinstance(error, ValidationError):
        validation_error = error
    else:
        validation_error = ValidationError(f"Validation failed: {str(error)}", field=field)
    
    logger.error(f"Validation error: {validation_error.message}", extra=validation_error.to_dict())
    return validation_error


def handle_storage_error(error: Exception, operation: str = "Storage operation"):
    """Handle file system and storage errors"""
    if isinstance(error, StorageError):
        storage_error = error
    else:
        storage_error = StorageError(f"Storage error during {operation}: {str(error)}", details={"operation": operation})
    
    logger.error(f"Storage error: {storage_error.message}", extra=storage_error.to_dict())
    return storage_error


def handle_network_error(error: Exception, url: Optional[str] = None, status_code: Optional[int] = None):
    """Handle network and HTTP errors"""
    details = {}
    if url:
        details["url"] = url
    if status_code:
        details["status_code"] = status_code
    
    if isinstance(error, NetworkError):
        network_error = error
    else:
        network_error = NetworkError(f"Network error: {str(error)}", status_code=status_code, details=details)
    
    logger.error(f"Network error: {network_error.message}", extra=network_error.to_dict())
    return network_error


# Retry Decorator
def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0, 
                   exceptions: tuple = (Exception,)):
    """Decorator to retry functions on specific exceptions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} in {wait_time}s: {str(e)}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                        raise last_exception
            raise last_exception
        
        def sync_wrapper(*args, **kwargs):
            import time
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} in {wait_time}s: {str(e)}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                        raise last_exception
            raise last_exception
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Error Context Manager
class ErrorContext:
    """Context manager for structured error handling"""
    
    def __init__(self, context: str, critical: bool = False):
        self.context = context
        self.critical = critical
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"Starting operation: {self.context}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.debug(f"Operation completed successfully: {self.context} ({duration:.2f}s)")
        else:
            error_data = {
                "context": self.context,
                "duration": duration,
                "error_type": exc_type.__name__,
                "message": str(exc_val)
            }
            
            if self.critical:
                handle_critical_error(exc_val, self.context)
            else:
                logger.error(f"Operation failed: {self.context} ({duration:.2f}s)", extra=error_data)
        
        return False  # Don't suppress exceptions


# Validation Helpers
def validate_required_fields(data: Dict[str, Any], required_fields: list, context: str = "Validation"):
    """Validate that required fields are present and non-empty"""
    missing_fields = []
    
    for field in required_fields:
        if '.' in field:
            # Handle nested fields
            value = data
            for key in field.split('.'):
                value = value.get(key, {}) if isinstance(value, dict) else {}
            if not value:
                missing_fields.append(field)
        else:
            if field not in data or not data[field]:
                missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields in {context}: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None