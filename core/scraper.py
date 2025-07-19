# scraper.py - LEAN MACHINE

from utils.browser import get_the_driver, check_driver_status
from utils.logging import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SeekScraper:
    # Config-driven selectors
    SELECTORS = {
        'keywords': [
            '#keywords-input',
            'input[name="keywords"]',
            'input[placeholder="Enter keywords"]'
        ],
        'location': [
            '#SearchBar*_Where',
            'input[name="where"]',  
            'input[data-automation="SearchBar__Where"]'
        ]
    }
    
    def __init__(self, config=None):
        self.driver = None
        self.wait = None
        self.config = config or {}

    def set_driver(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def _find_element(self, field_type):
        """Find element using multiple selectors"""
        for selector in self.SELECTORS[field_type]:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, selector)
            except:
                continue
        raise Exception(f"Element not found: {field_type}")

    def _fill_field(self, field_type, value):
        """Fill input field with value"""
        element = self._find_element(field_type)
        element.clear()
        element.send_keys(value)
        return element

    async def _setup_driver(self):
        """Get driver and navigate to seek"""
        driver = await get_the_driver()
        
        # Switch to seek tab if multiple tabs
        if len(driver.window_handles) >= 2:
            driver.switch_to.window(driver.window_handles[0])
        
        # Navigate to seek if not already there
        if "seek.com.au" not in driver.current_url:
            driver.get("https://www.seek.com.au")
            time.sleep(2)  # Page load
        
        return driver

    def _build_search_config(self):
        """Build search config from stored config"""
        if not self.config or 'job_preferences' not in self.config:
            logger.warning("No job preferences found in config, using defaults")
            return {
                'keywords': 'python',
                'location': 'Sydney'
            }
        
        job_prefs = self.config['job_preferences']
        
        # Build keywords string from preferences
        keywords = ' '.join(job_prefs.get('keywords', ['python']))
        
        # Get location (use first one in the list)
        location = job_prefs.get('locations', ['Sydney'])[0]
        
        # Build search config
        search_config = {
            'keywords': keywords,
            'location': location,
            'job_types': job_prefs.get('job_types', []),
            'salary_min': job_prefs.get('salary_min'),
            'salary_max': job_prefs.get('salary_max'),
            'excluded_keywords': job_prefs.get('excluded_keywords', []),
            'experience_levels': job_prefs.get('experience_levels', []),
            'remote_preference': job_prefs.get('remote_preference')
        }
        
        logger.info(f"Built search config: keywords='{keywords}', location='{location}'")
        return search_config
    
    async def scrape_jobs(self, search_config=None):
        # Use provided search_config or extract from stored config
        if not search_config:
            search_config = self._build_search_config()
            
        try:
            # Setup
            driver = await self._setup_driver()
            self.set_driver(driver)
            
            # Fill search form
            keywords_input = self._fill_field('keywords', search_config['keywords'])
            self._fill_field('location', search_config['location'])
            
            # Submit search
            keywords_input.send_keys(Keys.RETURN)
            time.sleep(3)  # Results load
            
            logger.info(f"✅ Search completed: {driver.current_url}")
            
            # Return search results with additional metadata from config
            return [{
                "search_term": search_config['keywords'], 
                "location": search_config['location'],
                "filters": {
                    "job_types": search_config.get('job_types', []),
                    "salary_range": f"{search_config.get('salary_min', 'any')}-{search_config.get('salary_max', 'any')}",
                    "excluded_keywords": search_config.get('excluded_keywords', []),
                    "experience_levels": search_config.get('experience_levels', []),
                    "remote_preference": search_config.get('remote_preference', 'any')
                },
                "status": "success",
                "timestamp": time.time()
            }]
            
        except Exception as e:
            logger.error(f"❌ Scrape failed: {e}")
            return []

    async def close(self):
        pass