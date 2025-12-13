"""
GDELT Collector
Orchestrates collection of global events and social unrest data.
"""
import logging
from typing import Dict, Any

from core.config import Config
from core.database import DatabaseManager
from services.gdelt_service import GdeltService
from repositories.gdelt_repository import GdeltRepository

logger = logging.getLogger(__name__)


class GdeltCollector:
    """Collector for GDELT global events data."""

    def __init__(self, config: Config):
        """Initialize the collector."""
        self.config = config
        self.db_manager = DatabaseManager(config)
        self.repository = GdeltRepository(self.db_manager)
        self.service = GdeltService(config, self.repository)

    def setup(self) -> None:
        """Set up database tables."""
        logger.info("Setting up GDELT collector")
        self.repository.create_tables()

    def collect(self) -> Dict[str, Any]:
        """Run the GDELT data collection."""
        logger.info("Starting GDELT data collection")
        return self.service.collect_and_store_data()

    def cleanup(self, days: int = 30) -> int:
        """Clean up old GDELT records."""
        return self.repository.delete_old_records(days)
