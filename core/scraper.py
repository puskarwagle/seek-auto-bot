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
            status = check_driver_status()
            logger.info(f"SUPREME STATUS: {status}")

            if not status.get("alive"):
                raise RuntimeError("No living driver. Overlord is sleeping.")

            driver = await get_the_driver()

            if len(driver.window_handles) < 2:
                raise RuntimeError("Seek tab is missing. Overlord setup incomplete.")

            # Switch to Seek tab
            driver.switch_to.window(driver.window_handles[1])
            logger.info(f"Switched to Seek tab: {driver.current_url}")

            # 🔍 Scraping logic starts here
            logger.info("🔍 Starting job scraping on seek.com.au...")
            
            # Ensure we're on seek.com.au
            if "seek.com.au" not in driver.current_url:
                logger.info("Navigating to seek.com.au...")
                driver.get("https://www.seek.com.au")
            
            # Wait for page to load
            import time
            time.sleep(3)
            
            # Look for job listings
            jobs = []
            try:
                # Find job cards/listings on the page
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                # Wait for job listings to load (adjust selector based on seek.com.au structure)
                wait = WebDriverWait(driver, 10)
                
                # Try to find job elements (common selectors for job sites)
                job_selectors = [
                    '[data-automation="normalJob"]',  # Seek specific
                    '.job-tile',
                    '.job-card',
                    '[data-testid="job-card"]',
                    'article[data-automation]'
                ]
                
                job_elements = []
                for selector in job_selectors:
                    try:
                        job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if job_elements:
                            logger.info(f"Found {len(job_elements)} job elements using selector: {selector}")
                            break
                    except:
                        continue
                
                # Extract job information
                for i, job_element in enumerate(job_elements[:10]):  # Limit to first 10 jobs
                    try:
                        # Extract job title
                        title_element = job_element.find_element(By.CSS_SELECTOR, 'a[data-automation="jobTitle"], h3 a, .job-title a, a[title]')
                        title = title_element.text.strip()
                        link = title_element.get_attribute('href')
                        
                        # Extract company name
                        try:
                            company_element = job_element.find_element(By.CSS_SELECTOR, '[data-automation="jobCompany"], .company-name, .employer-name')
                            company = company_element.text.strip()
                        except:
                            company = "Unknown Company"
                        
                        # Extract location
                        try:
                            location_element = job_element.find_element(By.CSS_SELECTOR, '[data-automation="jobLocation"], .location, .job-location')
                            location = location_element.text.strip()
                        except:
                            location = "Unknown Location"
                        
                        job_data = {
                            "id": f"seek_{i+1}",
                            "title": title,
                            "company": company,
                            "location": location,
                            "url": link,
                            "source": "seek.com.au",
                            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        jobs.append(job_data)
                        logger.info(f"Scraped job: {title} at {company}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract job {i+1}: {e}")
                        continue
                
                logger.info(f"🔍 Scraping completed! Found {len(jobs)} jobs")
                return jobs
                
            except Exception as e:
                logger.error(f"Failed to find job listings: {e}")
                logger.info("🔍 No jobs found, returning empty list")
                return []

        except Exception as e:
            logger.error(f"SCRAPE FAILURE: {e}")
            return []

    async def close(self):
        # You're not allowed to destroy the driver.
        pass
