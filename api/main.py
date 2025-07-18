# api/main.py - SERVANT TO THE BROWSER OVERLORD
"""
FastAPI Server for Seek Bot Dashboard
Now serves THE supreme browser overlord
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
from utils.browser import SUPREME_BROWSER_OVERLORD, get_the_driver_sync
from api.routes import router


# Global instances
bot_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Seek Bot Dashboard...")

    # Ensure data files exist
    storage = JSONStorage()
    storage.ensure_data_files()
    logger.info("All data files ensured and ready")
    
    # Open stealth Chrome browser automatically with dashboard and seek.com.au
    asyncio.create_task(open_stealth_browser_delayed())

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Seek Bot Dashboard...")
    global bot_instance
    
    if bot_instance and bot_instance.running:
        await bot_instance.stop()
    
    # Destroy THE driver through THE overlord
    await SUPREME_BROWSER_OVERLORD.destroy_driver()
    logger.info("OVERLORD: Supreme driver destroyed on shutdown")


async def open_stealth_browser_delayed():
    """Open stealth Chrome browser with seek.com.au and dashboard after server is ready"""
    await asyncio.sleep(5)  # Wait longer for server to be fully ready
    try:
        logger.info("Opening stealth Chrome browser with seek.com.au and dashboard...")
        # Get THE driver from THE overlord
        driver = get_the_driver_sync()
        
        # First open seek.com.au (more reliable)
        logger.info("Opening seek.com.au...")
        driver.get("https://www.seek.com.au")
        logger.info("Seek.com.au opened successfully")
        
        # Wait a moment then open dashboard in new tab
        await asyncio.sleep(2)
        logger.info("Opening dashboard in new tab...")
        driver.execute_script("window.open('http://127.0.0.1:3877', '_blank');")
        
        # Switch to dashboard tab
        driver.switch_to.window(driver.window_handles[1])
        logger.info("Dashboard opened in new tab")
        
        logger.info("Stealth Chrome browser setup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to open stealth Chrome browser: {e}")
        logger.info("Chrome driver is still available for manual navigation")



def create_app(host: str = "127.0.0.1", port: int = 3877) -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Seek Bot Dashboard",
        description="Automated Job Application System - Powered by THE Browser Overlord",
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
    
    @app.get("/api/browser-status")
    async def browser_status():
        """Get THE overlord's driver status"""
        return SUPREME_BROWSER_OVERLORD.get_supreme_status()
    
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


# Create app instance at module level
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
    logger.info("THE BROWSER OVERLORD is ready to serve")
    
    # No background thread - browser will open on first dashboard access
    
    # Start FastAPI server
    uvicorn.run("api.main:app", **config)


if __name__ == "__main__":
    main()