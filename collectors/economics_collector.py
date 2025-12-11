"""
Economics Data Collector
Collects economic indicators data.
"""
import logging
from datetime import datetime
from typing import Optional

from core.config import Config
from core.database import DatabaseManager
from core.exceptions import APIError, DatabaseError
from repositories.economics_repository import EconomicsRepository
from services.economics_service import EconomicsService

logger = logging.getLogger(__name__)


class EconomicsCollector:
    """Collector for economic indicators data."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = EconomicsRepository(self.db_manager)
        self.service = EconomicsService(self.config, self.repository)
    
    def setup(self) -> None:
        """Set up database tables."""
        try:
            self.repository.create_tables()
        except DatabaseError as e:
            logger.error(f"Setup failed: {e}")
            raise
    
    def collect(self, indicators: Optional[dict] = None) -> dict:
        """Collect economic data."""
        logger.info("ECONOMICS DATA COLLECTION STARTED")
        
        try:
            self.setup()
            results = self.service.collect_and_store_data(indicators)
            logger.info(f"COMPLETED: {results['successful']} successful, {results['failed']} failed")
            return results
        except Exception as e:
            logger.error(f"Collection error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_latest_data(self) -> list:
        """Get latest economic data."""
        try:
            return self.service.get_latest_indicators()
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            return []


def main():
    logging.basicConfig(level=logging.INFO)
    collector = EconomicsCollector()
    results = collector.collect()
    if results.get('successful', 0) > 0:
        print(f"\n✓ Collected {results['successful']} indicators")
    return 0


if __name__ == "__main__":
    exit(main())
