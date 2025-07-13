# core/auth.py
"""
Seek Authentication Module
Handles login, session management, and auth persistence
"""

import asyncio
import json
from typing import Optional, Dict, Any
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from utils.browser import BrowserManager
from utils.storage import JSONStorage
from utils.logging import logger
from utils.errors import AuthError, handle_auth_error
from core.anti_detection import AntiDetection


class SeekAuth:
    def __init__(self):
        self.storage = JSONStorage()
        self.browser_manager = BrowserManager()
        self.anti_detection = AntiDetection()
        self.driver = None
        self.session_active = False
        
        # Seek URLs
        self.base_url = "https://www.seek.com.au"
        self.login_url = f"{self.base_url}/sign-in"
        self.profile_url = f"{self.base_url}/profile"
        
    async def login(self) -> bool:
        """Authenticate with Seek using stored credentials"""
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
            await self.anti_detection.apply_stealth_mode(self.driver)
            
            # Navigate to login page
            logger.info("Navigating to login page...")
            await self._navigate_with_delay(self.login_url)
            
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
    
    async def _navigate_with_delay(self, url: str):
        """Navigate to URL with human-like delay"""
        await self.anti_detection.random_delay(2, 4)
        self.driver.get(url)
        await self.anti_detection.random_delay(3, 6)
    
    async def _wait_for_login_form(self):
        """Wait for login form to be present"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Common selectors for Seek login form
            selectors = [
                "input[name='emailAddress']",
                "input[type='email']",
                "#emailAddress",
                "[data-automation='emailAddress']"
            ]
            
            form_found = False
            for selector in selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    form_found = True
                    break
                except TimeoutException:
                    continue
            
            if not form_found:
                raise AuthError("Login form not found on page")
                
        except TimeoutException:
            raise AuthError("Login page failed to load")
    
    async def _fill_login_form(self, email: str, password: str):
        """Fill login form with human-like typing"""
        try:
            logger.info("Filling login credentials...")
            
            # Find email field
            email_selectors = [
                "input[name='emailAddress']",
                "input[type='email']", 
                "#emailAddress",
                "[data-automation='emailAddress']"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not email_field:
                raise AuthError("Email field not found")
            
            # Type email with human-like speed
            await self.anti_detection.human_type(email_field, email)
            await self.anti_detection.random_delay(1, 2)
            
            # Find password field
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "#password",
                "[data-automation='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not password_field:
                raise AuthError("Password field not found")
            
            # Type password
            await self.anti_detection.human_type(password_field, password)
            await self.anti_detection.random_delay(1, 3)
            
        except Exception as e:
            raise AuthError(f"Failed to fill login form: {str(e)}")
    
    async def _submit_and_verify_login(self) -> bool:
        """Submit login form and verify successful authentication"""
        try:
            # Find and click login button
            login_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "[data-automation='signInButton']",
                ".SignInForm_button",
                "button:contains('Sign in')"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not login_button:
                raise AuthError("Login button not found")
            
            # Click login with human-like behavior
            await self.anti_detection.human_click(login_button)
            
            # Wait for login to process
            await self.anti_detection.random_delay(3, 6)
            
            # Verify login success
            return await self._verify_login_success()
            
        except Exception as e:
            raise AuthError(f"Login submission failed: {str(e)}")
    
    async def _verify_login_success(self) -> bool:
        """Verify that login was successful"""
        try:
            # Check current URL
            current_url = self.driver.current_url
            
            # Success indicators
            success_indicators = [
                "dashboard" in current_url,
                "profile" in current_url,
                current_url != self.login_url
            ]
            
            # Check for error messages
            error_selectors = [
                ".error-message",
                ".alert-error",
                "[data-automation='errorMessage']",
                ".SignInForm_error"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if error_element.is_displayed():
                        error_text = error_element.text
                        raise AuthError(f"Login failed: {error_text}")
                except:
                    continue
            
            # Check for successful login elements
            success_selectors = [
                "[data-automation='userMenu']",
                ".user-menu",
                ".profile-menu",
                "nav[aria-label='User menu']"
            ]
            
            wait = WebDriverWait(self.driver, 10)
            for selector in success_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info("Login verification successful")
                    return True
                except TimeoutException:
                    continue
            
            # If no success indicators found, check URL change
            if any(success_indicators):
                logger.info("Login appears successful based on URL change")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Login verification error: {e}")
            return False
    
    async def logout(self):
        """Logout and clean up session"""
        try:
            if self.session_active and self.driver:
                logger.info("Logging out...")
                
                # Try to find logout button
                logout_selectors = [
                    "[data-automation='signOutButton']",
                    "a[href*='sign-out']",
                    ".logout-link"
                ]
                
                for selector in logout_selectors:
                    try:
                        logout_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        await self.anti_detection.human_click(logout_button)
                        break
                    except:
                        continue
                
                self.session_active = False
                
        except Exception as e:
            logger.error(f"Logout error: {e}")
        finally:
            if self.driver:
                await self.browser_manager.close_driver(self.driver)
                self.driver = None
    
    def is_authenticated(self) -> bool:
        """Check if current session is authenticated"""
        return self.session_active and self.driver is not None
    
    async def refresh_session(self) -> bool:
        """Refresh authentication session if needed"""
        if not self.is_authenticated():
            logger.info("Session expired, re-authenticating...")
            return await self.login()
        return True