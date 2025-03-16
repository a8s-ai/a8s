"""
Main FastAPI application for the Overseer service.
"""

import logging
import os
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from overseer import __version__
from overseer.api.deployments import router as deployments_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Overseer API",
    description="Kubernetes deployment service for a8s project",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(deployments_router)


@app.get("/", tags=["health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint.

    Returns:
        A dictionary with the service status.
    """
    return {"status": "ok", "version": __version__}


@app.get("/version", tags=["health"])
async def version() -> Dict[str, str]:
    """Version endpoint.

    Returns:
        A dictionary with the service version.
    """
    return {"version": __version__}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler.

    Args:
        request: The request that caused the exception.
        exc: The exception that was raised.

    Returns:
        A JSON response with the error details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    ) 