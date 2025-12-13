"""
Crypto Collector
Collects cryptocurrency price data using the Crypto Service.
"""
import logging
from typing import Optional

from core.config import Config
from core.database import DatabaseManager
from repositories.crypto_repository import CryptoRepository
from services.crypto_service import CryptoService

logger = logging.getLogger(__name__)


class CryptoCollector:
    """Collector for cryptocurrency data."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = CryptoRepository(self.db_manager)
        self.service = CryptoService(self.config, self.repository)

    def setup(self) -> None:
        """Set up database tables."""
        logger.info("Setting up crypto collector...")
        self.repository.create_tables()
        logger.info("Crypto collector setup completed")

    def collect(self) -> dict:
        """Collect cryptocurrency data."""
        logger.info("Starting crypto data collection")
        self.setup()
        return self.service.collect_and_store_data()


def main():
    """Main function for standalone execution."""
    logging.basicConfig(level=logging.INFO)
    collector = CryptoCollector()
    results = collector.collect()
    print(f"Collected {results['successful']} cryptocurrencies")
    return 0


if __name__ == "__main__":
    exit(main())
