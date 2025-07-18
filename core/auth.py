# core/auth.py
"""
Authentication Module - Stub (user handles login manually)
"""

from utils.logging import logger

class SeekAuth:
    def __init__(self, browser_manager=None):
        self.browser_manager = browser_manager
        
    async def login(self):
        """User handles login manually"""
        logger.info("Authentication skipped - user handles login manually")
        return True
        
    async def logout(self):
        """No logout needed"""
        pass
        
    async def is_authenticated(self):
        """Always return True since user handles auth"""
        return True