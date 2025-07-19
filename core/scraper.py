# scraper.py - NO MORE FREE WILL

from utils.browser import get_the_driver, check_driver_status
from utils.logging import logger

class SeekScraper:
    def __init__(self):
        self.driver = None  # must exist

    def set_driver(self, driver):
        self.driver = driver

    async def scrape_jobs(self):
        try:
            # Get the driver directly
            driver = await get_the_driver()
            logger.info(f"Got driver, current URL: {driver.current_url}")
            logger.info(f"Available tabs: {len(driver.window_handles)}")

            # Switch to seek.com.au tab (should be tab 0, index 0)
            if len(driver.window_handles) >= 2:
                logger.info("Switching to seek.com.au tab...")
                driver.switch_to.window(driver.window_handles[0])
                logger.info(f"✅ Switched to tab: {driver.current_url}")
            else:
                logger.warning("Only one tab available, staying on current tab")

            # Ensure we're on seek.com.au
            if "seek.com.au" not in driver.current_url:
                logger.info("Navigating to seek.com.au...")
                driver.get("https://www.seek.com.au")
                logger.info("✅ Navigated to seek.com.au")

            # Wait for page to load
            import time
            time.sleep(3)
            logger.info("✅ Page loaded, looking for search inputs...")

            # Find the keywords input field
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            try:
                # Wait for the keywords input to be present
                wait = WebDriverWait(driver, 10)
                
                # Try to find the keywords input field
                keywords_input = None
                input_selectors = [
                    '#keywords-input',  # ID selector
                    'input[name="keywords"]',  # Name selector
                    'input[placeholder="Enter keywords"]',  # Placeholder selector
                    'input[id="keywords-input"]'  # Full ID selector
                ]
                
                for selector in input_selectors:
                    try:
                        keywords_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        logger.info(f"✅ Found keywords input using selector: {selector}")
                        break
                    except:
                        logger.info(f"❌ Selector failed: {selector}")
                        continue

                if keywords_input:
                    # Clear any existing text and type "python developer"
                    keywords_input.clear()
                    search_term = "python developer"
                    keywords_input.send_keys(search_term)
                    logger.info(f"✅ Typed '{search_term}' into keywords input")
                    
                    # Wait a moment
                    time.sleep(1)

                    # Find and fill the location input
                    location_selectors = [
                        '#SearchBar*_Where',
                        'input[name="where"]',
                        'input[placeholder*="suburb"]',
                        'input[data-automation="SearchBar__Where"]'
                    ]

                    location_input = None
                    for selector in location_selectors:
                        try:
                            location_input = driver.find_element(By.CSS_SELECTOR, selector)
                            logger.info(f"✅ Found location input: {selector}")
                            break
                        except:
                            continue

                    if location_input:
                        location_input.clear()
                        location_input.send_keys("Sydney")
                        logger.info("✅ Typed 'Sydney' into location input")
                        time.sleep(1)
                    else:
                        logger.error("❌ Location input not found")
                    
                    # Try to press Enter or find search button
                    from selenium.webdriver.common.keys import Keys
                    keywords_input.send_keys(Keys.RETURN)
                    logger.info("✅ Pressed Enter to search")
                    
                    # Wait for search results
                    time.sleep(5)
                    logger.info(f"✅ Search completed, current URL: {driver.current_url}")
                    
                    return [{"message": "Search completed successfully", "search_term": search_term, "location": "Sydney"}]
                else:
                    logger.error("❌ Could not find keywords input field")
                    return []

            except Exception as e:
                logger.error(f"❌ Error finding/using search inputs: {e}")
                return []

        except Exception as e:
            logger.error(f"❌ SCRAPE FAILURE: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def close(self):
        # You're not allowed to destroy the driver.
        pass