# api/main.py
"""
FastAPI Server for Seek Bot Dashboard
Main application entry point
"""

import asyncio
import sys
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
from api.routes import router


# Global bot instance
bot_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Seek Bot Dashboard...")
    
    # Initialize storage and create default files
    storage = JSONStorage()
    storage.ensure_data_files()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Seek Bot Dashboard...")
    global bot_instance
    if bot_instance and bot_instance.running:
        await bot_instance.stop()


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
    
    # Development configuration
    config = {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
        "log_level": "info"
    }
    
    logger.info(f"Starting server at http://{config['host']}:{config['port']}")
    uvicorn.run("api.main:app", **config)


if __name__ == "__main__":
    main()