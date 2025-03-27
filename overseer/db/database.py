from databases import Database
from sqlalchemy import create_engine, MetaData
from alembic import command
from alembic.config import Config
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://overseer:overseer@postgres:5432/overseer"
)

# For SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# For async operations
database = Database(DATABASE_URL)

async def apply_migrations():
    """Apply database migrations on startup."""
    try:
        logger.info("Applying database migrations...")
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'alembic.ini'))
        alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL)
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to apply migrations: {e}")
        raise

async def get_database() -> Database:
    """Get database connection, ensuring migrations are applied first."""
    await apply_migrations()
    await database.connect()
    return database 