"""
Anti-Detection Module
Implements stealth techniques to avoid bot detection
"""

import asyncio
import random
import time
from typing import List, Tuple, Optional
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

from utils.logging import logger


class AntiDetection:
    def __init__(self):
        self.human_typing_speed = (80, 120)  # WPM range
        self.mouse_move_duration = (0.5, 1.5)  # seconds
        self.scroll_patterns = [
            "linear", "smooth", "jerky", "pause_and_scroll"
        ]
        
    async def apply_stealth_mode(self, driver: WebDriver):
        """Apply comprehensive stealth techniques"""
        try:
            logger.info("Applying stealth mode...")
            
            # Execute stealth scripts
            await self._execute_stealth_scripts(driver)
            
            # Set realistic viewport
            await self._set_realistic_viewport(driver)
            
            # Simulate human behavior patterns
            await self._simulate_initial_behavior(driver)
            
            logger.info("Stealth mode applied successfully")
            
        except Exception as e:
            logger.error(f"Stealth mode error: {e}")
    
    async def _execute_stealth_scripts(self, driver: WebDriver):
        """Execute JavaScript stealth scripts"""
        stealth_scripts = [
            # Override webdriver property
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """,
            
            # Override plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """,
            
            # Override languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            """,
            
            # Override canvas fingerprinting
            """
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type) {
                if (type === '2d') {
                    const context = getContext.call(this, type);
                    const originalFillText = context.fillText;
                    context.fillText = function(text, x, y, maxWidth) {
                        const noise = Math.random() * 0.1;
                        return originalFillText.call(this, text, x + noise, y + noise, maxWidth);
                    };
                    return context;
                }
                return getContext.call(this, type);
            };
            """,
            
            # Override WebGL fingerprinting
            """
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter.call(this, parameter);
            };
            """
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                logger.warning(f"Stealth script execution failed: {e}")
    
    async def _set_realistic_viewport(self, driver: WebDriver):
        """Set realistic viewport dimensions"""
        viewports = [
            (1920, 1080),
            (1366, 768),
            (1440, 900),
            (1536, 864),
            (1280, 720)
        ]
        
        width, height = random.choice(viewports)
        driver.set_window_size(width, height)
        
        # Random position
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        driver.set_window_position(x, y)
    
    async def _simulate_initial_behavior(self, driver: WebDriver):
        """Simulate initial human behavior on page load"""
        # Random scroll to simulate reading
        await self.random_scroll(driver, 2, 4)
        
        # Random mouse movement
        await self.random_mouse_movement(driver)
        
        # Random delay
        await self.random_delay(1, 3)
    
    async def random_delay(self, min_seconds: float, max_seconds: float):
        """Generate random delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def human_type(self, element: WebElement, text: str):
        """Type text with human-like speed and patterns"""
        try:
            # Clear existing text
            element.clear()
            await self.random_delay(0.1, 0.3)
            
            # Calculate typing speed
            wpm = random.randint(*self.human_typing_speed)
            chars_per_second = (wpm * 5) / 60  # Average 5 chars per word
            
            for char in text:
                element.send_keys(char)
                
                # Random typing delays
                if char == ' ':
                    # Longer pause at spaces
                    await self.random_delay(0.1, 0.3)
                elif char in '.,!?':
                    # Pause at punctuation
                    await self.random_delay(0.2, 0.4)
                else:
                    # Normal character delay
                    base_delay = 1 / chars_per_second
                    variation = base_delay * random.uniform(0.5, 1.5)
                    await asyncio.sleep(variation)
                
                # Random typos and corrections (5% chance)
                if random.random() < 0.05 and char.isalpha():
                    # Type wrong character
                    wrong_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
                    element.send_keys(wrong_char)
                    await self.random_delay(0.1, 0.3)
                    
                    # Backspace and correct
                    element.send_keys(Keys.BACKSPACE)
                    await self.random_delay(0.1, 0.2)
                    element.send_keys(char)
        
        except Exception as e:
            logger.error(f"Human typing error: {e}")
            # Fallback to regular typing
            element.send_keys(text)
    
    async def human_click(self, element: WebElement):
        """Click element with human-like behavior"""
        try:
            driver = element._parent
            actions = ActionChains(driver)
            
            # Move to element with random offset
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            
            # Random pause before click
            await self.random_delay(0.1, 0.5)
            
            # Click with random duration
            actions.click_and_hold()
            await self.random_delay(0.05, 0.15)
            actions.release()
            
            actions.perform()
            
        except Exception as e:
            logger.error(f"Human click error: {e}")
            # Fallback to regular click
            element.click()
    
    async def random_scroll(self, driver: WebDriver, min_scrolls: int, max_scrolls: int):
        """Perform random scrolling patterns"""
        try:
            scroll_count = random.randint(min_scrolls, max_scrolls)
            pattern = random.choice(self.scroll_patterns)
            
            for _ in range(scroll_count):
                if pattern == "linear":
                    scroll_amount = random.randint(200, 600)
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                
                elif pattern == "smooth":
                    scroll_amount = random.randint(100, 300)
                    driver.execute_script(f"""
                        window.scrollBy({{
                            top: {scroll_amount},
                            behavior: 'smooth'
                        }});
                    """)
                
                elif pattern == "jerky":
                    for _ in range(random.randint(2, 5)):
                        small_scroll = random.randint(50, 150)
                        driver.execute_script(f"window.scrollBy(0, {small_scroll});")
                        await self.random_delay(0.1, 0.3)
                
                elif pattern == "pause_and_scroll":
                    scroll_amount = random.randint(300, 800)
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    await self.random_delay(1, 3)  # Longer pause
                
                await self.random_delay(0.5, 2)
            
            # Random scroll back up sometimes
            if random.random() < 0.3:
                scroll_back = random.randint(100, 400)
                driver.execute_script(f"window.scrollBy(0, -{scroll_back});")
        
        except Exception as e:
            logger.error(f"Random scroll error: {e}")
    
    async def random_mouse_movement(self, driver: WebDriver):
        """Simulate random mouse movements"""
        try:
            actions = ActionChains(driver)
            
            # Get viewport dimensions
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(0, viewport_width)
                y = random.randint(0, viewport_height)
                
                actions.move_by_offset(x, y)
                await self.random_delay(0.5, 1.5)
            
            actions.perform()
        
        except Exception as e:
            logger.error(f"Mouse movement error: {e}")
    
    async def simulate_reading_behavior(self, driver: WebDriver, element: WebElement):
        """Simulate reading behavior on specific element"""
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            await self.random_delay(0.5, 1)
            
            # Get element text length to estimate reading time
            text_length = len(element.text)
            
            # Average reading speed: 200-300 words per minute
            words_estimate = text_length / 5  # Rough estimate
            reading_time = (words_estimate / 250) * 60  # seconds
            
            # Add randomness (50% to 150% of estimated time)
            actual_time = reading_time * random.uniform(0.5, 1.5)
            
            # Simulate reading with micro-scrolls
            if actual_time > 2:
                micro_scrolls = int(actual_time / 2)
                for _ in range(micro_scrolls):
                    micro_scroll = random.randint(10, 50)
                    driver.execute_script(f"arguments[0].scrollTop += {micro_scroll};", element)
                    await self.random_delay(1, 3)
            else:
                await self.random_delay(actual_time, actual_time * 1.5)
        
        except Exception as e:
            logger.error(f"Reading behavior simulation error: {e}")
    
    async def avoid_bot_traps(self, driver: WebDriver):
        """Avoid common bot detection traps"""
        try:
            # Check for invisible elements (honeypots)
            honeypot_selectors = [
                "input[style*='display: none']",
                "input[style*='visibility: hidden']",
                ".honeypot",
                "#honeypot"
            ]
            
            for selector in honeypot_selectors:
                elements = driver.find_elements("css selector", selector)
                for element in elements:
                    if element.is_displayed():
                        logger.warning(f"Potential honeypot detected: {selector}")
                        # Don't interact with honeypot elements
            
            # Check for timing-based detection
            await self.random_delay(1, 3)
            
            # Simulate human-like page interaction
            await self.random_mouse_movement(driver)
            
        except Exception as e:
            logger.error(f"Bot trap avoidance error: {e}")
    
    def generate_realistic_user_agent(self) -> str:
        """Generate realistic user agent string"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]
        
        return random.choice(user_agents)