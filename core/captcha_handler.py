# core/captcha_handler.py
"""
Manual Captcha Intervention System
Handles captcha detection and user intervention workflow

# Replace SeekAuth with SeekAuthWithCaptcha
from core.captcha_handler import SeekAuthWithCaptcha as SeekAuth

# In your bot status endpoint
def get_detailed_status():
    status = bot.get_status()
    if bot.auth.captcha_handler:
        status["captcha_intervention"] = bot.auth.captcha_handler.get_intervention_status()
    return status
"""

import asyncio
import time
import subprocess
import platform
from typing import Optional, Dict, Any
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils.logging import logger
from utils.errors import AuthError


class CaptchaHandler:
    def __init__(self, driver):
        self.driver = driver
        self.intervention_active = False
        self.intervention_start_time = None
        
        # Common captcha selectors
        self.captcha_selectors = [
            # reCAPTCHA
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            "#g-recaptcha-response",
            "[data-sitekey]",
            
            # hCaptcha
            "iframe[src*='hcaptcha']",
            ".h-captcha",
            "#h-captcha-response",
            
            # Generic captcha indicators
            "#captcha-container",
            ".captcha-wrapper",
            "[data-callback*='captcha']",
            ".challenge-container",
            
            # Seek-specific (if they have custom ones)
            "[data-automation*='captcha']",
            ".verification-challenge"
        ]
        
        # Error message selectors that might indicate captcha failure
        self.captcha_error_selectors = [
            ".captcha-error",
            "[data-automation='captchaError']",
            ".verification-error"
        ]

    async def detect_captcha(self) -> bool:
        """
        Detect if captcha is present on current page
        Returns True if captcha found, False otherwise
        """
        try:
            logger.debug("Scanning for captcha elements...")
            
            for selector in self.captcha_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            logger.info(f"Captcha detected: {selector}")
                            return True
                except Exception as e:
                    logger.debug(f"Error checking selector {selector}: {e}")
                    continue
            
            # Check for captcha-related text in page source
            page_source = self.driver.page_source.lower()
            captcha_keywords = [
                "recaptcha",
                "hcaptcha", 
                "i'm not a robot",
                "verify you are human",
                "prove you're not a robot"
            ]
            
            for keyword in captcha_keywords:
                if keyword in page_source:
                    logger.info(f"Captcha keyword detected: {keyword}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting captcha: {e}")
            return False

    async def wait_for_captcha_solution(self, timeout: int = 300) -> bool:
        """
        Wait for user to solve captcha manually
        Returns True if captcha solved, False if timeout
        """
        self.intervention_active = True
        self.intervention_start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("🤖 CAPTCHA INTERVENTION REQUIRED 🤖")
        logger.info("=" * 60)
        logger.info("Bot has been PAUSED - captcha detected")
        logger.info("Please solve the captcha manually in the browser window")
        logger.info(f"Timeout: {timeout} seconds")
        logger.info("=" * 60)
        
        # Send system notification
        self._send_notification("Seek Bot - Captcha Required", 
                              "Please solve captcha manually")
        
        # Wait for captcha to be solved
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if captcha is still present
                if not await self.detect_captcha():
                    logger.info("✅ Captcha solved! Resuming bot...")
                    self.intervention_active = False
                    return True
                
                # Check for captcha error messages
                if await self._check_captcha_errors():
                    logger.warning("❌ Captcha error detected - please try again")
                
                # Wait before next check
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error while waiting for captcha solution: {e}")
                await asyncio.sleep(2)
        
        # Timeout reached
        logger.error("⏰ Captcha intervention timeout reached")
        self.intervention_active = False
        return False

    async def _check_captcha_errors(self) -> bool:
        """Check for captcha error messages"""
        try:
            for selector in self.captcha_error_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            error_text = element.text.strip()
                            if error_text:
                                logger.warning(f"Captcha error: {error_text}")
                                return True
                except:
                    continue
            return False
        except Exception as e:
            logger.error(f"Error checking captcha errors: {e}")
            return False

    def _send_notification(self, title: str, message: str):
        """Send system notification to user"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
            elif system == "Linux":  # Linux
                subprocess.run([
                    "notify-send", title, message
                ])
            elif system == "Windows":  # Windows
                subprocess.run([
                    "powershell", "-Command",
                    f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");'
                    f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
                ])
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    def get_intervention_status(self) -> Dict[str, Any]:
        """Get current intervention status"""
        return {
            "active": self.intervention_active,
            "start_time": self.intervention_start_time,
            "duration": time.time() - self.intervention_start_time if self.intervention_start_time else 0
        }


# Integration with SeekAuth class
class SeekAuthWithCaptcha(SeekAuth):
    def __init__(self):
        super().__init__()
        self.captcha_handler = None

    async def login(self) -> bool:
        """Enhanced login with captcha handling"""
        try:
            logger.info("Starting Seek authentication...")
            
            # Load credentials
            config = self.storage.load_config()
            if not config or not config.get("user", {}).get("email"):
                raise AuthError("No credentials found in configuration")
            
            email = config["user"]["email"]
            password = config["user"]["password"]
            
            # Initialize browser with anti-detection
            self.driver = await self.browser_manager.create_driver()
            self.captcha_handler = CaptchaHandler(self.driver)
            await self.anti_detection.apply_stealth_mode(self.driver)
            
            # Navigate to login page
            logger.info("Navigating to login page...")
            await self._navigate_with_delay(self.login_url)
            
            # Check for captcha on login page
            if await self.captcha_handler.detect_captcha():
                logger.warning("Captcha detected on login page")
                if not await self.captcha_handler.wait_for_captcha_solution():
                    raise AuthError("Captcha intervention timeout")
            
            # Wait for page load and check for login form
            await self._wait_for_login_form()
            
            # Fill login form
            await self._fill_login_form(email, password)
            
            # Submit and verify login
            if await self._submit_and_verify_login():
                self.session_active = True
                logger.info("Authentication successful")
                return True
            else:
                raise AuthError("Login verification failed")
                
        except Exception as e:
            handle_auth_error(e, "Authentication failed")
            return False

    async def _submit_and_verify_login(self) -> bool:
        """Enhanced login submission with captcha handling"""
        try:
            # Find and click login button
            login_button = await self._find_login_button()
            if not login_button:
                raise AuthError("Login button not found")
            
            # Click login with human-like behavior
            await self.anti_detection.human_click(login_button)
            
            # Wait for page response
            await self.anti_detection.random_delay(3, 6)
            
            # Check for captcha after login attempt
            if await self.captcha_handler.detect_captcha():
                logger.warning("Captcha required after login attempt")
                if not await self.captcha_handler.wait_for_captcha_solution():
                    raise AuthError("Captcha intervention timeout")
                
                # Wait a bit more after captcha solution
                await self.anti_detection.random_delay(2, 4)
            
            # Verify login success
            return await self._verify_login_success()
            
        except Exception as e:
            raise AuthError(f"Login submission failed: {str(e)}")

    async def _find_login_button(self):
        """Find login button with multiple selectors"""
        login_button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "[data-automation='signInButton']",
            ".SignInForm_button",
            "button:contains('Sign in')",
            "[data-cy='sign-in-button']"
        ]
        
        for selector in login_button_selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed() and button.is_enabled():
                    return button
            except:
                continue
        
        return None