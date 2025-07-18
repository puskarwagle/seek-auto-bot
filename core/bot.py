# core/bot.py (FIXED)
import asyncio
from utils.logging import logger
from utils.storage import JSONStorage
from utils.errors import SeekBotError, handle_critical_error
from utils.browser import BrowserManager
from core.auth import SeekAuth
from core.scraper import SeekScraper

class SeekBot:
    def __init__(self):
        self.storage = JSONStorage()
        self.browser_manager = BrowserManager()  # Singleton
        self.auth = SeekAuth(self.browser_manager)
        self.scraper = SeekScraper(self.browser_manager)
        self.running = False
        self.current_task = "idle"

    async def initialize(self) -> bool:
        try:
            logger.info("Initializing Seek Bot...")
            config = self.storage.load_config()
            if not config:
                raise SeekBotError("No configuration found. Please configure via the dashboard.")

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
        keys = path.split(".")
        for key in keys:
            if not isinstance(obj, dict) or key not in obj:
                raise KeyError(f"Missing config key '{key}' in path '{path}'")
            obj = obj[key]
        return obj

    async def start(self) -> bool:
        if not await self.initialize():
            return False

        self.running = True
        try:
            logger.info("Starting Seek Bot execution...")

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

            # Step 3: Apply to jobs (commented out for now)
            # self.current_task = "applying"
            # applied_count = await self.applicator.apply_to_jobs(jobs)
            # logger.info(f"Applied to {applied_count} jobs successfully")
            
            self.current_task = "completed"
            return True

        except Exception as e:
            handle_critical_error(e, "Bot execution failed")
            return False

        finally:
            self.running = False
            self.current_task = "idle"
            await self.cleanup()

    async def stop(self):
        logger.info("Stopping Seek Bot...")
        self.running = False
        await self.cleanup()

    async def cleanup(self):
        try:
            await self.auth.logout()
            await self.scraper.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def get_status(self) -> dict:
        return {
            "running": self.running,
            "current_task": self.current_task,
            "timestamp": self.storage.get_timestamp()
        }