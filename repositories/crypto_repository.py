"""
Crypto Repository
Handles all database operations for cryptocurrency data.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class CryptoRepository:
    """Repository for cryptocurrency data operations."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the crypto table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS crypto (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name VARCHAR(100),
            price DECIMAL(20, 8),
            change_24h DECIMAL(20, 8),
            change_percent_24h DECIMAL(10, 4),
            market_cap DECIMAL(30, 2),
            volume_24h DECIMAL(30, 2),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        );

        CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON crypto(symbol);
        CREATE INDEX IF NOT EXISTS idx_crypto_timestamp ON crypto(timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("Crypto table created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating crypto table: {e}")
            raise DatabaseError(f"Failed to create crypto table: {e}")

    def insert_bulk_crypto_data(self, crypto_data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple crypto records."""
        if not crypto_data_list:
            return 0

        insert_query = """
        INSERT INTO crypto (symbol, name, price, change_24h, change_percent_24h, market_cap, volume_24h, timestamp)
        VALUES (%(symbol)s, %(name)s, %(price)s, %(change_24h)s, %(change_percent_24h)s, %(market_cap)s, %(volume_24h)s, %(timestamp)s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            name = EXCLUDED.name,
            price = EXCLUDED.price,
            change_24h = EXCLUDED.change_24h,
            change_percent_24h = EXCLUDED.change_percent_24h,
            market_cap = EXCLUDED.market_cap,
            volume_24h = EXCLUDED.volume_24h
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in crypto_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            logger.info(f"Inserted {len(crypto_data_list)} crypto records")
            return len(crypto_data_list)
        except Exception as e:
            logger.error(f"Error inserting crypto data: {e}")
            raise DatabaseError(f"Failed to insert crypto data: {e}")

    def get_all_latest_crypto(self) -> List[Dict[str, Any]]:
        """Get the most recent data for all cryptocurrencies."""
        query = """
        WITH latest AS (
            SELECT symbol, MAX(timestamp) as max_ts
            FROM crypto
            GROUP BY symbol
        )
        SELECT c.symbol, c.name, c.price, c.change_24h, c.change_percent_24h,
               c.market_cap, c.volume_24h, c.timestamp
        FROM crypto c
        INNER JOIN latest l ON c.symbol = l.symbol AND c.timestamp = l.max_ts
        ORDER BY c.market_cap DESC NULLS LAST
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest crypto: {e}")
            return []

    def get_crypto_history(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical data for a cryptocurrency."""
        query = """
        SELECT symbol, name, price, change_percent_24h, timestamp
        FROM crypto
        WHERE symbol = %s AND timestamp >= %s
        ORDER BY timestamp ASC
        """
        start_date = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (symbol, start_date))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting crypto history: {e}")
            return []
