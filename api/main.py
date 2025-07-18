# api/main.py
"""
FastAPI Server for Seek Bot Dashboard
Main application entry point
"""

import asyncio
import sys
import threading
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logging import setup_logging, logger
from utils.storage import JSONStorage
from utils.errors import SeekBotError
from utils.browser import BrowserManager
from api.routes import router


# Global instances
bot_instance = None
browser_manager = BrowserManager()  # Singleton instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Seek Bot Dashboard...")

    # Ensure data files exist
    storage = JSONStorage()
    storage.ensure_data_files()
    logger.info("All data files ensured and ready")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Seek Bot Dashboard...")
    global bot_instance
    
    if bot_instance and bot_instance.running:
        await bot_instance.stop()
    
    # Close browser using singleton manager
    await browser_manager.close_driver()


def wait_for_server_and_open_browser(host: str, port: int):
    """Wait for server to be ready then open browser"""
    import socket
    import time
    
    def is_server_ready():
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except:
            return False
    
    # Wait for server to be ready (max 30 seconds)
    for _ in range(30):
        if is_server_ready():
            logger.info("Server is ready, opening browser...")
            try:
                # Create browser using singleton manager
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get driver through singleton
                driver = loop.run_until_complete(browser_manager.get_driver())
                driver.get(f"http://{host}:{port}")
                
                # Open seek.com.au in a new tab using Selenium's native method
                driver.execute_script("window.open('about:blank', '_blank');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get("https://www.seek.com.au")
                driver.switch_to.window(driver.window_handles[0])  # Switch back to dashboard   
                
                logger.info("Dashboard opened in browser successfully")
                return
                
            except Exception as e:
                logger.error(f"Failed to open browser: {e}")
                return
        
        time.sleep(1)
    
    logger.error("Server failed to start within timeout")

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Seek Bot Dashboard",
        description="Automated Job Application System",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static files
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    
    # Templates
    templates = Jinja2Templates(directory="web/templates")
    
    # Routes
    app.include_router(router, prefix="/api")
    
    @app.get("/")
    async def dashboard(request: Request):
        """Serve dashboard page"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.exception_handler(SeekBotError)
    async def seekbot_exception_handler(request: Request, exc: SeekBotError):
        """Handle custom SeekBot errors"""
        logger.error(f"SeekBot error: {exc}")
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "type": "SeekBotError"}
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "type": "InternalError"}
        )
    
    return app


# Create app instance
app = create_app()


def main():
    """Run the FastAPI server"""
    setup_logging()
    
    # Server configuration
    host = "127.0.0.1"
    port = 3877
    
    config = {
        "host": host,
        "port": port,
        "reload": True,
        "log_level": "info"
    }
    
    logger.info(f"Starting server at http://{host}:{port}")
    
    # Start browser opener in background thread
    browser_thread = threading.Thread(
        target=wait_for_server_and_open_browser,
        args=(host, port),
        daemon=True
    )
    browser_thread.start()
    
    # Start FastAPI server
    uvicorn.run("api.main:app", **config)


if __name__ == "__main__":
    main()