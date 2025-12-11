"""
Markets Data Collector
Collects stock market data using the Markets Service.
"""
import logging
from datetime import datetime
from typing import Optional

from core.config import Config
from core.database import DatabaseManager
from core.exceptions import APIError, DatabaseError
from repositories.markets_repository import MarketsRepository
from services.markets_service import MarketsService

logger = logging.getLogger(__name__)


class MarketsCollector:
    """Collector for market data."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the collector.
        
        Args:
            config: Configuration instance (creates default if None)
        """
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = MarketsRepository(self.db_manager)
        self.service = MarketsService(self.config, self.repository)
    
    def setup(self) -> None:
        """Set up database tables and indexes."""
        logger.info("Setting up markets collector...")
        try:
            self.repository.create_tables()
            logger.info("Markets collector setup completed")
        except DatabaseError as e:
            logger.error(f"Failed to setup markets collector: {e}")
            raise
    
    def collect(self, symbols: Optional[list] = None) -> dict:
        """
        Collect market data.
        
        Args:
            symbols: List of stock symbols to collect (uses defaults if None)
            
        Returns:
            Dictionary with collection results
        """
        logger.info("=" * 60)
        logger.info("MARKETS DATA COLLECTION STARTED")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        try:
            # Ensure tables exist
            self.setup()
            
            # Collect and store data
            results = self.service.collect_and_store_data(symbols)
            
            logger.info("=" * 60)
            logger.info("MARKETS DATA COLLECTION COMPLETED")
            logger.info(f"Total Symbols: {results['total_symbols']}")
            logger.info(f"Successful: {results['successful']}")
            logger.info(f"Failed: {results['failed']}")
            logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
            logger.info("=" * 60)
            
            return results
            
        except APIError as e:
            logger.error(f"API error during market data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR'
            }
        except DatabaseError as e:
            logger.error(f"Database error during market data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'DATABASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error during market data collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNKNOWN_ERROR'
            }
    
    def get_latest_data(self) -> list:
        """
        Get the latest market data from database.
        
        Returns:
            List of stock data dictionaries
        """
        try:
            return self.service.get_latest_prices()
        except Exception as e:
            logger.error(f"Error getting latest market data: {e}")
            return []
    
    def get_stock_with_sparkline(self, symbol: str, days: int = 7) -> dict:
        """
        Get stock data with sparkline price history.
        
        Args:
            symbol: Stock symbol
            days: Number of days for sparkline
            
        Returns:
            Dictionary with stock data and sparkline prices
        """
        try:
            latest = self.repository.get_latest_stock_price(symbol)
            if not latest:
                return {}
            
            sparkline_prices = self.service.get_sparkline_data(symbol, days)
            
            return {
                **latest,
                'sparkline': sparkline_prices
            }
        except Exception as e:
            logger.error(f"Error getting stock with sparkline for {symbol}: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 365) -> int:
        """
        Remove old market data.
        
        Args:
            days: Keep data newer than this many days
            
        Returns:
            Number of records deleted
        """
        try:
            deleted = self.repository.delete_old_records(days)
            logger.info(f"Cleaned up {deleted} old market records")
            return deleted
        except DatabaseError as e:
            logger.error(f"Error cleaning up old market data: {e}")
            return 0


def main():
    """Main function for running the collector standalone."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        collector = MarketsCollector()
        results = collector.collect()
        
        if results.get('successful', 0) > 0:
            print(f"\n✓ Successfully collected data for {results['successful']} stocks")
        
        if results.get('failed', 0) > 0:
            print(f"\n✗ Failed to collect data for {results['failed']} stocks")
            
    except Exception as e:
        logger.error(f"Fatal error in markets collector: {e}")
        print(f"\n✗ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
