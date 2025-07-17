#utils/browser.py
"""
Browser Management Module
Handles Selenium WebDriver setup with anti-detection
"""

import asyncio
import random
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
    def __init__(self):
        self.driver_path = None
        self.user_data_dir = Path.home() / ".seek_bot" / "chrome_profile"
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_driver(self) -> webdriver.Chrome:
        """Create Chrome driver with anti-detection setup"""
        try:
            logger.info("Creating Chrome driver with stealth mode...")
            
            # Chrome options for stealth
            options = self._get_chrome_options()
            
            # Use undetected-chromedriver
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect
                driver_executable_path=self.driver_path
            )
            
            # Set timeouts
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            
            # Apply additional stealth
            await self._apply_driver_stealth(driver)
            
            logger.info("Chrome driver created successfully")
            return driver
            
        except Exception as e:
            raise BrowserError(f"Failed to create Chrome driver: {str(e)}")
    
    def _get_chrome_options(self) -> Options:
        """Configure Chrome options for stealth"""
        options = Options()
        
        # Basic stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        
        # Performance options
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Privacy options
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        
        # User agent and language
        user_agent = self._get_random_user_agent()
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--lang=en-US,en')
        
        # Window size randomization
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        # Persistent profile
        options.add_argument(f'--user-data-dir={self.user_data_dir}')
        options.add_argument('--profile-directory=Default')
        
        # Memory and performance
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # Disable logging
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        return options
    
    def _get_random_user_agent(self) -> str:
        """Get random realistic user agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        return random.choice(user_agents)
    
    async def _apply_driver_stealth(self, driver: webdriver.Chrome):
        """Apply additional stealth techniques to driver"""
        try:
            # Execute stealth scripts
            stealth_scripts = [
                # Remove webdriver property
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                
                # Override chrome property
                "Object.defineProperty(navigator, 'chrome', {get: () => ({runtime: {}})})",
                
                # Override permissions
                """
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: (parameters) => (
                            parameters.name === 'notifications' ?
                            Promise.resolve({state: Notification.permission}) :
                            Promise.resolve({state: 'granted'})
                        )
                    })
                });
                """,
                
                # Override plugins
                """
                Object.defineProperty(navigator, 'plugins', {
                    get: () => ([
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", filename: "internal-pdf-viewer"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ])
                });
                """,
                
                # Override language
                "Object.defineProperty(navigator, 'language', {get: () => 'en-US'})",
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
            ]
            
            for script in stealth_scripts:
                try:
                    driver.execute_script(script)
                except Exception as e:
                    logger.warning(f"Stealth script failed: {e}")
            
            # Set realistic screen properties
            screen_script = f"""
            Object.defineProperty(screen, 'width', {{get: () => {random.randint(1200, 1920)}}});
            Object.defineProperty(screen, 'height', {{get: () => {random.randint(800, 1080)}}});
            Object.defineProperty(screen, 'availWidth', {{get: () => screen.width}});
            Object.defineProperty(screen, 'availHeight', {{get: () => screen.height - 40}});
            """
            driver.execute_script(screen_script)
            
        except Exception as e:
            logger.warning(f"Driver stealth application failed: {e}")
    
    async def close_driver(self, driver: webdriver.Chrome):
        """Safely close the driver"""
        try:
            if driver:
                logger.info("Closing Chrome driver...")
                driver.quit()
                logger.info("Chrome driver closed successfully")
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
    
    async def get_driver_status(self, driver: webdriver.Chrome) -> dict:
        """Get driver status information"""
        try:
            return {
                "session_id": driver.session_id,
                "current_url": driver.current_url,
                "title": driver.title,
                "window_handles": len(driver.window_handles),
                "page_source_length": len(driver.page_source)
            }
        except Exception as e:
            logger.error(f"Error getting driver status: {e}")
            return {"error": str(e)}
    
    async def refresh_driver(self, driver: webdriver.Chrome):
        """Refresh driver to avoid detection"""
        try:
            # Clear cookies and cache
            driver.delete_all_cookies()
            
            # Execute cache clearing script
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            
            # Random delay
            await asyncio.sleep(random.uniform(1, 3))
            
            logger.info("Driver refreshed successfully")
            
        except Exception as e:
            logger.error(f"Driver refresh failed: {e}")
            raise BrowserError(f"Failed to refresh driver: {str(e)}")
    
    def set_driver_path(self, path: str):
        """Set custom ChromeDriver path"""
        self.driver_path = path
        logger.info(f"ChromeDriver path set to: {path}")
    
    def get_user_data_dir(self) -> Path:
        """Get Chrome user data directory"""
        return self.user_data_dir