# main.py
"""
Seek Bot - Automated Job Application System
Entry point for CLI and bot orchestration
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

from utils.logging import setup_logging, logger
from utils.storage import JSONStorage
from utils.errors import SeekBotError, handle_critical_error
from core.auth import SeekAuth
# from core.scraper import SeekScraper
# from core.applicator import JobApplicator


class SeekBot:
    def __init__(self):
        self.storage = JSONStorage()
        self.auth = SeekAuth()
        # self.scraper = SeekScraper()
        # self.applicator = JobApplicator()
        self.running = False
        self.current_task = "idle"
        
    async def initialize(self):
        """Initialize bot with configuration validation"""
        try:
            logger.info("Initializing Seek Bot...")
            
            # Load and validate config
            config = self.storage.load_config()
            if not config:
                raise SeekBotError("No configuration found. Please set up via web interface.")
            
            # Validate required fields
            required_fields = ["user.email", "user.password", "user.agreement_accepted"]
            for field in required_fields:
                if not self._get_nested_value(config, field):
                    raise SeekBotError(f"Missing required field: {field}")
            
            if not config["user"]["agreement_accepted"]:
                raise SeekBotError("User agreement not accepted. Cannot proceed.")
            
            logger.info("Configuration validated successfully")
            return True
            
        except Exception as e:
            handle_critical_error(e, "Bot initialization failed")
            return False
    
    def _get_nested_value(self, obj: dict, path: str):
        """Get nested dictionary value using dot notation, raise if key missing"""
        keys = path.split('.')
        for key in keys:
            if not isinstance(obj, dict) or key not in obj:
                raise KeyError(f"Missing config key: '{key}' in path '{path}'")
            obj = obj[key]
        return obj
    
    async def start(self):
        """Main bot execution loop"""
        if not await self.initialize():
            return False
        
        self.running = True
        
        try:
            logger.info("Starting Seek Bot execution...")
            
            # Step 1: Authenticate
            self.current_task = "authenticating"
            if not await self.auth.login():
                raise SeekBotError("Authentication failed")
            
            # Step 2: Scrape jobs
            self.current_task = "scraping"
            jobs = await self.scraper.scrape_jobs()
            if not jobs:
                logger.warning("No jobs found matching criteria")
                return True
            
            logger.info(f"Found {len(jobs)} jobs matching criteria")
            
            # Step 3: Apply to jobs
            self.current_task = "applying"
            applied_count = await self.applicator.apply_to_jobs(jobs)
            
            logger.info(f"Applied to {applied_count} jobs successfully")
            self.current_task = "completed"
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            return True
        except Exception as e:
            handle_critical_error(e, "Bot execution failed")
            return False
        finally:
            self.running = False
            self.current_task = "idle"
            await self.cleanup()
    
    async def stop(self):
        """Stop bot execution gracefully"""
        logger.info("Stopping Seek Bot...")
        self.running = False
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            await self.auth.logout()
            await self.scraper.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def get_status(self) -> dict:
        """Get current bot status"""
        return {
            "running": self.running,
            "current_task": self.current_task,
            "timestamp": self.storage.get_timestamp()
        }


async def main():
    """CLI entry point"""
    setup_logging()
    
    # Handle graceful shutdown
    bot = SeekBot()
    
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal")
        asyncio.create_task(bot.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = await bot.start()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except Exception as e:
        handle_critical_error(e, "Fatal error in main")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())