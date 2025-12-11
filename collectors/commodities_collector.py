"""
Commodities Data Collector
Collects commodities price data using the Commodities Service.
"""
import logging
from datetime import datetime
from typing import Optional

from core.config import Config
from core.database import DatabaseManager
from core.exceptions import APIError, DatabaseError
from repositories.commodities_repository import CommoditiesRepository
from services.commodities_service import CommoditiesService

logger = logging.getLogger(__name__)


class CommoditiesCollector:
    """Collector for commodities data."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the collector.
        
        Args:
            config: Configuration instance (creates default if None)
        """
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = CommoditiesRepository(self.db_manager)
        self.service = CommoditiesService(self.config, self.repository)
    
    def setup(self) -> None:
        """Set up database tables and indexes."""
        logger.info("Setting up commodities collector...")
        try:
            self.repository.create_tables()
            logger.info("Commodities collector setup completed")
        except DatabaseError as e:
            logger.error(f"Failed to setup commodities collector: {e}")
            raise
    
    def collect(self, commodities: Optional[list] = None) -> dict:
        """
        Collect commodities data.
        
        Args:
            commodities: List of commodity symbols to collect (uses defaults if None)
            
        Returns:
            Dictionary with collection results
        """
        logger.info("=" * 60)
        logger.info("COMMODITIES DATA COLLECTION STARTED")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        try:
            # Ensure tables exist
            self.setup()
            
            # Collect and store data
            results = self.service.collect_and_store_data(commodities)
            
            logger.info("=" * 60)
            logger.info("COMMODITIES DATA COLLECTION COMPLETED")
            logger.info(f"Total Commodities: {results['total_commodities']}")
            logger.info(f"Successful: {results['successful']}")
            logger.info(f"Failed: {results['failed']}")
            logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
            logger.info("=" * 60)
            
            return results
            
        except APIError as e:
            logger.error(f"API error during commodities data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR'
            }
        except DatabaseError as e:
            logger.error(f"Database error during commodities data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DATABASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error during commodities data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNKNOWN_ERROR'
            }
    
    def get_latest_data(self) -> list:
        """
        Get the latest commodities data from database.
        
        Returns:
            List of commodity data dictionaries
        """
        try:
            return self.service.get_latest_prices()
        except Exception as e:
            logger.error(f"Error getting latest commodities data: {e}")
            return []
    
    def get_commodity_with_sparkline(self, commodity: str, days: int = 7) -> dict:
        """
        Get commodity data with sparkline price history.
        
        Args:
            commodity: Commodity symbol
            days: Number of days for sparkline
            
        Returns:
            Dictionary with commodity data and sparkline prices
        """
        try:
            latest = self.repository.get_latest_commodity_price(commodity)
            if not latest:
                return {}
            
            sparkline_prices = self.service.get_sparkline_data(commodity, days)
            
            return {
                **latest,
                'sparkline': sparkline_prices
            }
        except Exception as e:
            logger.error(f"Error getting commodity with sparkline for {commodity}: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 365) -> int:
        """
        Remove old commodities data.
        
        Args:
            days: Keep data newer than this many days
            
        Returns:
            Number of records deleted
        """
        try:
            deleted = self.repository.delete_old_records(days)
            logger.info(f"Cleaned up {deleted} old commodity records")
            return deleted
        except DatabaseError as e:
            logger.error(f"Error cleaning up old commodities data: {e}")
            return 0


def main():
    """Main function for running the collector standalone."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        collector = CommoditiesCollector()
        results = collector.collect()
        
        if results.get('successful', 0) > 0:
            print(f"\n✓ Successfully collected data for {results['successful']} commodities")
        
        if results.get('failed', 0) > 0:
            print(f"\n✗ Failed to collect data for {results['failed']} commodities")
            
    except Exception as e:
        logger.error(f"Fatal error in commodities collector: {e}")
        print(f"\n✗ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
