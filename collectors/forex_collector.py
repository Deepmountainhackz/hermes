"""
Forex Data Collector
Collects currency exchange rate data using the Forex Service.
"""
import logging
from datetime import datetime
from typing import Optional

from core.config import Config
from core.database import DatabaseManager
from core.exceptions import APIError, DatabaseError
from repositories.forex_repository import ForexRepository
from services.forex_service import ForexService

logger = logging.getLogger(__name__)


class ForexCollector:
    """Collector for forex data."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the collector.
        
        Args:
            config: Configuration instance (creates default if None)
        """
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = ForexRepository(self.db_manager)
        self.service = ForexService(self.config, self.repository)
    
    def setup(self) -> None:
        """Set up database tables and indexes."""
        logger.info("Setting up forex collector...")
        try:
            self.repository.create_tables()
            logger.info("Forex collector setup completed")
        except DatabaseError as e:
            logger.error(f"Failed to setup forex collector: {e}")
            raise
    
    def collect(self, currency_pairs: Optional[list] = None) -> dict:
        """
        Collect forex data.
        
        Args:
            currency_pairs: List of currency pair dicts (uses defaults if None)
            
        Returns:
            Dictionary with collection results
        """
        logger.info("=" * 60)
        logger.info("FOREX DATA COLLECTION STARTED")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        try:
            # Ensure tables exist
            self.setup()
            
            # Collect and store data
            results = self.service.collect_and_store_data(currency_pairs)
            
            logger.info("=" * 60)
            logger.info("FOREX DATA COLLECTION COMPLETED")
            logger.info(f"Total Pairs: {results['total_pairs']}")
            logger.info(f"Successful: {results['successful']}")
            logger.info(f"Failed: {results['failed']}")
            logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
            logger.info("=" * 60)
            
            return results
            
        except APIError as e:
            logger.error(f"API error during forex data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR'
            }
        except DatabaseError as e:
            logger.error(f"Database error during forex data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DATABASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error during forex data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNKNOWN_ERROR'
            }
    
    def get_latest_data(self) -> list:
        """
        Get the latest forex data from database.
        
        Returns:
            List of forex data dictionaries
        """
        try:
            return self.service.get_latest_rates()
        except Exception as e:
            logger.error(f"Error getting latest forex data: {e}")
            return []
    
    def get_forex_with_sparkline(self, pair: str, days: int = 7) -> dict:
        """
        Get forex data with sparkline rate history.
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            days: Number of days for sparkline
            
        Returns:
            Dictionary with forex data and sparkline rates
        """
        try:
            latest = self.repository.get_latest_forex_rate(pair)
            if not latest:
                return {}
            
            sparkline_rates = self.service.get_sparkline_data(pair, days)
            
            return {
                **latest,
                'sparkline': sparkline_rates
            }
        except Exception as e:
            logger.error(f"Error getting forex with sparkline for {pair}: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 365) -> int:
        """
        Remove old forex data.
        
        Args:
            days: Keep data newer than this many days
            
        Returns:
            Number of records deleted
        """
        try:
            deleted = self.repository.delete_old_records(days)
            logger.info(f"Cleaned up {deleted} old forex records")
            return deleted
        except DatabaseError as e:
            logger.error(f"Error cleaning up old forex data: {e}")
            return 0


def main():
    """Main function for running the collector standalone."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        collector = ForexCollector()
        results = collector.collect()
        
        if results.get('successful', 0) > 0:
            print(f"\n✓ Successfully collected data for {results['successful']} currency pairs")
        
        if results.get('failed', 0) > 0:
            print(f"\n✗ Failed to collect data for {results['failed']} currency pairs")
            
    except Exception as e:
        logger.error(f"Fatal error in forex collector: {e}")
        print(f"\n✗ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
