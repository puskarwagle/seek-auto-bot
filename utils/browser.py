# utils/browser.py - FIXED OVERLORD
"""
Browser Management Module - THE ONE TRUE DRIVER AUTHORITY
Fixed driver detection and unified locking
"""

import asyncio
import random
import threading
from typing import Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc

from utils.logging import logger
from utils.errors import BrowserError


class BrowserManager:
    """THE SUPREME DRIVER OVERLORD - All drivers bow to this singleton"""
    
    _instance = None
    _driver = None
    _lock = threading.RLock()  # Changed to RLock for reentrant access
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.driver_path = None
            self._driver_locked_in = False
            self.user_data_dir = Path.home() / ".seek_bot" / "chrome_profile"
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            self._initialized = True
            logger.info("BROWSER OVERLORD INITIALIZED - Ready to rule all drivers")
    
    # ====== UNIFIED DRIVER GETTER ======
    async def get_driver(self) -> webdriver.Chrome:
        """THE SUPREME METHOD - Get THE driver (async)"""
        return self._get_driver_internal()
    
    def get_driver_sync(self) -> webdriver.Chrome:
        """THE SUPREME METHOD - Get THE driver (sync)"""
        return self._get_driver_internal()
    
    def _get_driver_internal(self) -> Optional[webdriver.Chrome]:
        """Internal unified driver getter with single-creation policy"""
        with self._lock:
            if self._driver_locked_in:
                if self._is_driver_alive():
                    logger.info("OVERLORD: Returning locked-in supreme driver")
                    return self._driver
                else:
                    logger.warning("OVERLORD: Locked-in driver is dead. No more driver creation allowed.")
                    return None  # Or raise an error if you want

            if self._is_driver_alive():
                logger.info("OVERLORD: Returning existing living driver (pre-lock-in)")
                self._driver_locked_in = True
                return self._driver

            logger.info("OVERLORD: No living driver found. Creating supreme driver (ONE TIME ONLY).")
            self._driver = self._create_supreme_driver_sync()
            self._driver_locked_in = True  # 🔐 Lock it in!
            return self._driver

    
    # ====== IMPROVED DRIVER HEALTH ORACLE ======
    def _is_driver_alive(self) -> bool:
        """Check if THE driver is alive and serving"""
        if self._driver is None:
            logger.debug("OVERLORD: No driver instance exists")
            return False

        try:
            # Try basic health check
            session_id = self._driver.session_id
            current_url = self._driver.current_url
            handles = self._driver.window_handles

            if not session_id:
                logger.debug("OVERLORD: No session ID found")
                return False
            if not handles:
                logger.debug("OVERLORD: No window handles found")
                return False

            logger.debug(f"OVERLORD: Driver is alive. URL: {current_url}, Handles: {len(handles)}")
            return True

        except Exception as e:
            logger.warning(f"OVERLORD: Driver health check failed: {e}")
            # Health check failure doesn't mean driver is dead - could be temporary/threading issue
            # Don't reset lock-in status - preserve "ONE TIME ONLY" policy
            return False

    def has_driver(self) -> bool:
        """Public method to check driver status"""
        with self._lock:
            return self._is_driver_alive()
    
    # ====== SIMPLIFIED DRIVER CREATION ======
    def _create_supreme_driver_sync(self) -> webdriver.Chrome:
        """Create THE supreme driver with all anti-detection powers"""
        try:
            logger.info("OVERLORD: Forging new supreme driver with ultimate stealth...")
            
            # Get supreme options
            options = self._get_supreme_options()
            
            # Create supreme driver using undetected-chromedriver
            driver = uc.Chrome(
                options=options,
                version_main=None,
                driver_executable_path=self.driver_path
            )
            
            # Set supreme timeouts
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            
            # Apply basic stealth synchronously
            self._apply_basic_stealth_sync(driver)
            
            logger.info("OVERLORD: Supreme driver forged successfully")
            return driver
            
        except Exception as e:
            logger.error(f"OVERLORD: Failed to create supreme driver: {e}")
            raise BrowserError(f"Supreme driver creation failed: {str(e)}")
    
    # ====== SUPREME OPTIONS CONFIGURATION ======
    def _get_supreme_options(self) -> Options:
        """Configure supreme Chrome options for ultimate stealth"""
        options = Options()
        
        # Supreme stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Performance supremacy
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Privacy supremacy
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        
        # Supreme user agent
        user_agent = self._get_supreme_user_agent()
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--lang=en-US,en')
        
        # Supreme window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        # Supreme persistent profile
        options.add_argument(f'--user-data-dir={self.user_data_dir}')
        options.add_argument('--profile-directory=Default')
        
        # Supreme performance
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # Supreme silence
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        return options
    
    def _get_supreme_user_agent(self) -> str:
        """Get supreme realistic user agent"""
        supreme_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        return random.choice(supreme_agents)
    
    # ====== BASIC STEALTH POWERS ======
    def _apply_basic_stealth_sync(self, driver: webdriver.Chrome):
        """Apply basic stealth synchronously"""
        try:
            basic_scripts = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                "Object.defineProperty(navigator, 'chrome', {get: () => ({runtime: {}})})",
                "Object.defineProperty(navigator, 'language', {get: () => 'en-US'})",
            ]
            
            for script in basic_scripts:
                try:
                    driver.execute_script(script)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.warning(f"OVERLORD: Basic stealth failed: {e}")
    
    # ====== SUPREME DESTRUCTION POWERS ======
    async def destroy_driver(self):
        """Destroy THE driver when overlord commands it"""
        self._destroy_driver_internal()
    
    def destroy_driver_sync(self):
        """Synchronous version of driver destruction"""
        self._destroy_driver_internal()
    
    def _destroy_driver_internal(self):
        """Internal unified driver destruction"""
        with self._lock:
            if self._driver:
                try:
                    logger.info("OVERLORD: Destroying supreme driver...")
                    self._driver.quit()
                    self._driver = None
                    logger.info("OVERLORD: Supreme driver destroyed successfully")
                except Exception as e:
                    logger.error(f"OVERLORD: Error destroying driver: {e}")
                    self._driver = None
    
    # ====== SUPREME STATUS REPORTING ======
    def get_supreme_status(self) -> dict:
        """Get status of THE supreme driver"""
        with self._lock:
            try:
                if not self._is_driver_alive():
                    return {
                        "status": "NO_DRIVER",
                        "alive": False,
                        "message": "No living driver under overlord control"
                    }
                    
                return {
                    "status": "SUPREME_DRIVER_ACTIVE",
                    "alive": True,
                    "session_id": self._driver.session_id,
                    "current_url": self._driver.current_url,
                    "title": self._driver.title,
                    "window_handles": len(self._driver.window_handles),
                    "message": "Supreme driver serving faithfully"
                }
            except Exception as e:
                return {
                    "status": "ERROR",
                    "alive": False,
                    "error": str(e),
                    "message": "Error checking supreme driver status"
                }
    
    # ====== SUPREME RECOVERY POWERS ======
    async def recover_driver(self):
        """Force recovery of THE driver"""
        logger.info("OVERLORD: Initiating supreme driver recovery...")
        await self.destroy_driver()
        new_driver = await self.get_driver()
        logger.info("OVERLORD: Supreme driver recovery completed")
        return new_driver
    
    # ====== SUPREME CONFIGURATION ======
    def set_driver_path(self, path: str):
        """Set path for supreme driver executable"""
        self.driver_path = path
        logger.info(f"OVERLORD: Supreme driver path set to: {path}")
    
    def get_user_data_dir(self) -> Path:
        """Get supreme Chrome user data directory"""
        return self.user_data_dir


# ====== THE SUPREME SINGLETON INSTANCE ======
SUPREME_BROWSER_OVERLORD = BrowserManager()


# ====== CONVENIENCE FUNCTIONS FOR SERVANTS ======
async def get_the_driver() -> webdriver.Chrome:
    """Get THE driver from THE overlord"""
    return await SUPREME_BROWSER_OVERLORD.get_driver()

def get_the_driver_sync() -> webdriver.Chrome:
    """Get THE driver from THE overlord (synchronous)"""
    return SUPREME_BROWSER_OVERLORD.get_driver_sync()

async def destroy_the_driver():
    """Destroy THE driver through THE overlord"""
    await SUPREME_BROWSER_OVERLORD.destroy_driver()

def check_driver_status() -> dict:
    """Check THE driver status through THE overlord"""
    return SUPREME_BROWSER_OVERLORD.get_supreme_status()