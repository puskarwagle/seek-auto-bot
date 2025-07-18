# core/bot.py - SERVANT TO THE BROWSER OVERLORD
"""
Seek Bot Core - Now serves THE supreme browser overlord
"""

import asyncio
from utils.logging import logger
from utils.storage import JSONStorage
from utils.errors import SeekBotError, handle_critical_error
from utils.browser import SUPREME_BROWSER_OVERLORD, get_the_driver
from core.auth import SeekAuth
from core.scraper import SeekScraper


class SeekBot:
    """Seek Bot - Humble servant to THE browser overlord"""
    
    def __init__(self):
        self.storage = JSONStorage()
        # No longer create our own browser manager - we serve THE overlord
        self.auth = SeekAuth()  # Remove browser_manager parameter
        self.scraper = SeekScraper()  # Remove browser_manager parameter
        self.running = False
        self.current_task = "idle"
        self.driver = None  # Will be provided by THE overlord
    
    async def initialize(self) -> bool:
        """Initialize bot and validate configuration"""
        try:
            logger.info("Initializing Seek Bot...")
            # No config needed - user handles login manually on seek.com.au
            logger.info("Bot ready - user handles login manually on seek.com.au")
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization failed: {str(e)}")
            return False
    
    def _get_nested_value(self, obj: dict, path: str):
        """Get nested dictionary value by dot notation"""
        keys = path.split(".")
        for key in keys:
            if not isinstance(obj, dict) or key not in obj:
                raise KeyError(f"Missing config key '{key}' in path '{path}'")
            obj = obj[key]
        return obj
    
    async def start(self) -> bool:
        """Start bot execution - now serves THE overlord"""
        if not await self.initialize():
            return False
        
        self.running = True
        try:
            logger.info("Starting Seek Bot execution...")
            
            # Request THE driver from THE overlord
            logger.info("Requesting THE driver from THE supreme overlord...")
            self.driver = await get_the_driver()
            
            # Check overlord status
            status = SUPREME_BROWSER_OVERLORD.get_supreme_status()
            if status["alive"]:
                logger.info(f"OVERLORD STATUS: {status['message']}")
                logger.info(f"Current URL: {status.get('current_url', 'unknown')}")
                logger.info(f"Session ID: {status.get('session_id', 'unknown')}")
            else:
                logger.error(f"OVERLORD STATUS: {status['message']}")
                return False
            
            # Pass THE driver to our servants
            self.auth.set_driver(self.driver)
            self.scraper.set_driver(self.driver)
            
            # Step 1: Skip auth
            logger.info("Skipping authentication — user handles login manually.")
            
            # Step 2: Scrape jobs
            self.current_task = "scraping"
            jobs = await self.scraper.scrape_jobs()
            if not jobs:
                logger.warning("No jobs found matching criteria")
                self.current_task = "idle"
                return True
            
            logger.info(f"Found {len(jobs)} jobs matching criteria")
            
            # Save jobs to storage for dashboard display
            self.storage.save_jobs(jobs)
            logger.info(f"Saved {len(jobs)} jobs to storage")
            
            # Step 3: Apply to jobs (commented out for now)
            # self.current_task = "applying"
            # applied_count = await self.applicator.apply_to_jobs(jobs)
            # logger.info(f"Applied to {applied_count} jobs successfully")
            
            self.current_task = "completed"
            logger.info("Bot execution completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bot execution failed: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            handle_critical_error(e, "Bot execution failed")
            return False
        finally:
            self.running = False
            self.current_task = "idle"
            # DON'T destroy THE driver - THE overlord manages it
            logger.info("Bot execution finished - THE driver remains with THE overlord")
    
    async def stop(self):
        """Stop bot execution"""
        logger.info("Stopping Seek Bot...")
        self.running = False
        # DON'T destroy THE driver - THE overlord manages it
        logger.info("Bot stopped - THE driver remains with THE overlord")
    
    def get_status(self) -> dict:
        """Get bot status"""
        overlord_status = SUPREME_BROWSER_OVERLORD.get_supreme_status()
        return {
            "running": self.running,
            "current_task": self.current_task,
            "timestamp": self.storage.get_timestamp(),
            "overlord_status": overlord_status["status"],
            "driver_alive": overlord_status["alive"]
        }