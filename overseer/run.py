#!/usr/bin/env python
"""
Run the Overseer FastAPI application.
"""

import argparse
import logging
import os
import sys
from typing import Optional

import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout  # Ensure logs go to stdout for Kubernetes
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run the Overseer FastAPI application.")
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("OVERSEER_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("OVERSEER_PORT", "8000")),
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=os.getenv("OVERSEER_RELOAD", "").lower() in ("true", "1", "yes"),
        help="Enable auto-reload (default: False)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("OVERSEER_WORKERS", "1")),
        help="Number of worker processes (default: 1)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("OVERSEER_LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level (default: info)",
    )
    return parser.parse_args()


def main() -> None:
    """Run the FastAPI application."""
    args = parse_args()
    
    logger.info(f"Starting Overseer API on {args.host}:{args.port}")
    logger.info(f"Workers: {args.workers}, Reload: {args.reload}, Log level: {args.log_level}")
    
    uvicorn.run(
        "overseer.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main() 