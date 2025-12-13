"""
World Bank Collector
Collects global development indicators from World Bank API.
"""
import logging
from typing import Optional

from core.config import Config
from core.database import DatabaseManager
from repositories.worldbank_repository import WorldBankRepository
from services.worldbank_service import WorldBankService

logger = logging.getLogger(__name__)


class WorldBankCollector:
    """Collector for World Bank development indicators."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = WorldBankRepository(self.db_manager)
        self.service = WorldBankService(self.config, self.repository)

    def setup(self) -> None:
        """Set up database tables."""
        logger.info("Setting up World Bank collector...")
        self.repository.create_tables()
        logger.info("World Bank collector setup completed")

    def collect(self) -> dict:
        """Collect World Bank data."""
        logger.info("Starting World Bank data collection")
        self.setup()
        return self.service.collect_and_store_data()


def main():
    """Main function for standalone execution."""
    logging.basicConfig(level=logging.INFO)
    collector = WorldBankCollector()
    results = collector.collect()
    print(f"Collected {results['successful']} World Bank indicators")
    return 0


if __name__ == "__main__":
    exit(main())
