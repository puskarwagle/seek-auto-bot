"""
JSON Storage Module
Handles all JSON file operations for configuration and data
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from cryptography.fernet import Fernet

from utils.logging import logger
from utils.errors import StorageError

class JSONStorage:
    def __init__(self):
        self.base_dir = Path("data")
        self.config_file = Path("config/settings.json")
        self.jobs_file = self.base_dir / "jobs.json"
        self.applied_file = self.base_dir / "applied.json"
        self.logs_file = self.base_dir / "logs.json"
        
        # Create directories if they don't exist
        self.base_dir.mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        
        # Initialize encryption key
        self.encryption_key = self._get_or_create_encryption_key()
    
    def ensure_data_files(self) -> None:
        """Ensure all required data files exist with proper structure"""
        try:
            # Ensure config exists
            if not self.config_file.exists():
                self._create_default_config()
            
            # Ensure jobs file exists
            if not self.jobs_file.exists():
                self._create_empty_jobs_file()
            
            # Ensure applied jobs file exists
            if not self.applied_file.exists():
                self._create_empty_applied_file()
            
            # Ensure logs file exists
            if not self.logs_file.exists():
                self._create_empty_logs_file()
            
            logger.info("All data files ensured and ready")
            
        except Exception as e:
            logger.error(f"Failed to ensure data files: {e}")
            raise StorageError(f"Data file initialization failed: {str(e)}")
    
    def _create_empty_jobs_file(self) -> None:
        """Create empty jobs file with proper structure"""
        data = {
            "jobs": [],
            "total_count": 0,
            "last_updated": self.get_timestamp()
        }
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_empty_applied_file(self) -> None:
        """Create empty applied jobs file with proper structure"""
        data = {
            "applications": [],
            "total_count": 0,
            "last_updated": self.get_timestamp()
        }
        with open(self.applied_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_empty_logs_file(self) -> None:
        """Create empty logs file"""
        with open(self.logs_file, 'w') as f:
            json.dump([], f)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = self.base_dir / "encryption.key"
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Restrict permissions
            return key
    
    # def _encrypt_data(self, data: str) -> str:
    #     """Encrypt sensitive data"""
    #     try:
    #         f = Fernet(self.encryption_key)
    #         return f.encrypt(data.encode()).decode()
    #     except Exception as e:
    #         logger.error(f"Encryption failed: {e}")
    #         return data
    
    # def _decrypt_data(self, encrypted_data: str) -> str:
    #     """Decrypt sensitive data"""
    #     try:
    #         f = Fernet(self.encryption_key)
    #         return f.decrypt(encrypted_data.encode()).decode()
    #     except Exception as e:
    #         logger.error(f"Decryption failed: {e}")
    #         return encrypted_data
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if not self.config_file.exists():
                return self._create_default_config()
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise StorageError(f"Configuration load failed: {str(e)}")

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        try:
            # Create a copy to avoid modifying original
            config_copy = config.copy()
            # Add timestamp
            config_copy["last_updated"] = self.get_timestamp()
            
            with open(self.config_file, 'w') as f:
                json.dump(config_copy, f, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise StorageError(f"Configuration save failed: {str(e)}")

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            "user": {
                "agreement_accepted": False,
                "agreement_timestamp": None
            },
            "job_preferences": {
                "keywords": [],
                "excluded_keywords": [],
                "locations": [],
                "salary_min": 0,
                "salary_max": 0,
                "job_types": [],
                "experience_levels": [],
                "industries": [],
                "company_size": [],
                "remote_preference": "any",
                "visa_sponsorship": False,
                "minimum_rating": 3.5
            },
            "application_settings": {
                "auto_apply": False,
                "max_applications_per_day": 1,
                "cover_letter_template": "",
                "cv_path": "",
                "apply_to_agencies": False,
                "skip_assessment_required": True,
                "minimum_job_age_days": 1,
                "maximum_job_age_days": 7,
                "preferred_application_times": []
            },
            "filters": {
                "excluded_companies": [],
                "required_benefits": [],
                "avoid_unpaid_trials": True,
                "minimum_description_length": 100,
                "require_salary_disclosed": False
            },
            "smart_matching": {
                "skill_weight": 0.4,
                "location_weight": 0.2,
                "salary_weight": 0.3,
                "company_weight": 0.1,
                "auto_learn_preferences": True
            },
            "deepseek_api": {
                "api_key": "",
                "enabled": False
            },
            "created_at": self.get_timestamp(),
            "last_updated": self.get_timestamp()
        }
        
        self.save_config(default_config)
        return default_config
    
    def load_jobs(self) -> List[Dict[str, Any]]:
        """Load scraped jobs from JSON file"""
        try:
            if not self.jobs_file.exists():
                return []
            
            with open(self.jobs_file, 'r') as f:
                data = json.load(f)
            
            # Handle both old format (list) and new format (dict with jobs key)
            if isinstance(data, list):
                jobs = data
            else:
                jobs = data.get("jobs", [])
            
            logger.info(f"Loaded {len(jobs)} jobs from storage")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to load jobs: {e}")
            return []
    
    def save_jobs(self, jobs: List[Dict[str, Any]]) -> bool:
        """Save scraped jobs to JSON file"""
        try:
            # Add metadata
            data = {
                "jobs": jobs,
                "total_count": len(jobs),
                "last_updated": self.get_timestamp()
            }
            
            with open(self.jobs_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(jobs)} jobs to storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save jobs: {e}")
            raise StorageError(f"Jobs save failed: {str(e)}")
    
    def load_applied_jobs(self) -> List[Dict[str, Any]]:
        """Load applied jobs history"""
        try:
            if not self.applied_file.exists():
                return []
            
            with open(self.applied_file, 'r') as f:
                data = json.load(f)
            
            # Handle both old format (list) and new format (dict with applications key)
            if isinstance(data, list):
                applied = data
            else:
                applied = data.get("applications", [])
            
            return applied
            
        except Exception as e:
            logger.error(f"Failed to load applied jobs: {e}")
            return []
    
    def save_applied_job(self, job_data: Dict[str, Any]) -> bool:
        """Save single applied job to history"""
        try:
            applied_jobs = self.load_applied_jobs()
            
            # Add application metadata
            application = {
                "job_id": job_data.get("job_id"),
                "title": job_data.get("title"),
                "company": job_data.get("company"),
                "location": job_data.get("location"),
                "salary": job_data.get("salary"),
                "applied_at": self.get_timestamp(),
                "status": "applied",
                "job_url": job_data.get("url")
            }
            
            applied_jobs.append(application)
            
            # Save updated list
            data = {
                "applications": applied_jobs,
                "total_count": len(applied_jobs),
                "last_updated": self.get_timestamp()
            }
            
            with open(self.applied_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved applied job: {job_data.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save applied job: {e}")
            return False
    
    def is_job_applied(self, job_id: str) -> bool:
        """Check if job was already applied to"""
        try:
            applied_jobs = self.load_applied_jobs()
            return any(job.get("job_id") == job_id for job in applied_jobs)
        except Exception:
            return False
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics"""
        try:
            applied_jobs = self.load_applied_jobs()
            
            total_applications = len(applied_jobs)
            today = datetime.now().date()
            
            today_applications = sum(
                1 for job in applied_jobs 
                if datetime.fromisoformat(job.get("applied_at", "")).date() == today
            )
            
            companies = set(job.get("company") for job in applied_jobs)
            locations = set(job.get("location") for job in applied_jobs)
            
            return {
                "total_applications": total_applications,
                "today_applications": today_applications,
                "unique_companies": len(companies),
                "unique_locations": len(locations),
                "last_application": applied_jobs[-1].get("applied_at") if applied_jobs else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get application stats: {e}")
            return {
                "total_applications": 0,
                "today_applications": 0,
                "unique_companies": 0,
                "unique_locations": 0,
                "last_application": None
            }
    
    def save_log(self, log_data: Dict[str, Any]) -> bool:
        """Save log entry"""
        try:
            logs = self.load_logs()
            
            log_entry = {
                "timestamp": self.get_timestamp(),
                "level": log_data.get("level", "INFO"),
                "message": log_data.get("message"),
                "module": log_data.get("module"),
                "data": log_data.get("data", {})
            }
            
            logs.append(log_entry)
            
            # Keep only last 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(self.logs_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save log: {e}")
            return False
    
    def load_logs(self) -> List[Dict[str, Any]]:
        """Load application logs"""
        try:
            if not self.logs_file.exists():
                return []
            
            with open(self.logs_file, 'r') as f:
                logs = json.load(f)
            
            return logs if isinstance(logs, list) else []
            
        except Exception as e:
            logger.error(f"Failed to load logs: {e}")
            return []
    
    def clear_logs(self) -> bool:
        """Clear all logs"""
        try:
            with open(self.logs_file, 'w') as f:
                json.dump([], f)
            
            logger.info("Logs cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            return False
    
    def clear_jobs(self) -> bool:
        """Clear all scraped jobs"""
        try:
            self._create_empty_jobs_file()
            logger.info("Jobs cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear jobs: {e}")
            return False
    
    def clear_applied_jobs(self) -> bool:
        """Clear all applied jobs"""
        try:
            self._create_empty_applied_file()
            logger.info("Applied jobs cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear applied jobs: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """Clear all data files"""
        try:
            self.clear_jobs()
            self.clear_applied_jobs()
            self.clear_logs()
            logger.info("All data cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear all data: {e}")
            return False
    
    def backup_data(self) -> bool:
        """Create backup of all data"""
        try:
            backup_dir = self.base_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"
            
            backup_data = {
                "config": self.load_config(),
                "jobs": self.load_jobs(),
                "applied_jobs": self.load_applied_jobs(),
                "logs": self.load_logs(),
                "backup_timestamp": self.get_timestamp()
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Data backup created: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure"""
        required_sections = ["user", "job_preferences", "application_settings", "deepseek_api"]
        
        for section in required_sections:
            if section not in config:
                logger.error(f"Missing required config section: {section}")
                return False
        
        # Validate user section
        user_fields = ["agreement_accepted"]
        for field in user_fields:
            if field not in config["user"]:
                logger.error(f"Missing user field: {field}")
                return False
        
        return True
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information and statistics"""
        try:
            return {
                "config_exists": self.config_file.exists(),
                "jobs_count": len(self.load_jobs()),
                "applied_count": len(self.load_applied_jobs()),
                "logs_count": len(self.load_logs()),
                "config_size": self.config_file.stat().st_size if self.config_file.exists() else 0,
                "jobs_size": self.jobs_file.stat().st_size if self.jobs_file.exists() else 0,
                "applied_size": self.applied_file.stat().st_size if self.applied_file.exists() else 0,
                "logs_size": self.logs_file.stat().st_size if self.logs_file.exists() else 0
            }
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {}