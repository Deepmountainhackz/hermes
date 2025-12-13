"""
World Bank Repository
Handles all database operations for World Bank development indicators.
"""
from typing import List, Dict, Any
from datetime import datetime
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class WorldBankRepository:
    """Repository for World Bank indicator data operations."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the worldbank_indicators table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS worldbank_indicators (
            id SERIAL PRIMARY KEY,
            indicator_code VARCHAR(50) NOT NULL,
            indicator_name VARCHAR(200),
            category VARCHAR(50),
            country_code VARCHAR(10) NOT NULL,
            country_name VARCHAR(100),
            year INTEGER NOT NULL,
            value DECIMAL(30, 6),
            unit VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(indicator_code, country_code, year)
        );

        CREATE INDEX IF NOT EXISTS idx_wb_indicator_code ON worldbank_indicators(indicator_code);
        CREATE INDEX IF NOT EXISTS idx_wb_country_code ON worldbank_indicators(country_code);
        CREATE INDEX IF NOT EXISTS idx_wb_year ON worldbank_indicators(year);
        CREATE INDEX IF NOT EXISTS idx_wb_category ON worldbank_indicators(category);
        CREATE INDEX IF NOT EXISTS idx_wb_timestamp ON worldbank_indicators(timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("World Bank indicators table created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating worldbank_indicators table: {e}")
            raise DatabaseError(f"Failed to create worldbank_indicators table: {e}")

    def insert_bulk_indicator_data(self, indicator_data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple indicator records."""
        if not indicator_data_list:
            return 0

        insert_query = """
        INSERT INTO worldbank_indicators
            (indicator_code, indicator_name, category, country_code, country_name, year, value, unit, timestamp)
        VALUES
            (%(indicator_code)s, %(indicator_name)s, %(category)s, %(country_code)s,
             %(country_name)s, %(year)s, %(value)s, %(unit)s, %(timestamp)s)
        ON CONFLICT (indicator_code, country_code, year) DO UPDATE SET
            indicator_name = EXCLUDED.indicator_name,
            category = EXCLUDED.category,
            country_name = EXCLUDED.country_name,
            value = EXCLUDED.value,
            unit = EXCLUDED.unit,
            timestamp = EXCLUDED.timestamp
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in indicator_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            logger.info(f"Inserted {len(indicator_data_list)} World Bank indicator records")
            return len(indicator_data_list)
        except Exception as e:
            logger.error(f"Error inserting World Bank data: {e}")
            raise DatabaseError(f"Failed to insert World Bank data: {e}")

    def get_all_latest_indicators(self) -> List[Dict[str, Any]]:
        """Get the most recent data for all indicators (latest year for each)."""
        query = """
        WITH latest AS (
            SELECT indicator_code, country_code, MAX(year) as max_year
            FROM worldbank_indicators
            GROUP BY indicator_code, country_code
        )
        SELECT w.indicator_code, w.indicator_name, w.category,
               w.country_code, w.country_name, w.year, w.value, w.unit, w.timestamp
        FROM worldbank_indicators w
        INNER JOIN latest l
            ON w.indicator_code = l.indicator_code
            AND w.country_code = l.country_code
            AND w.year = l.max_year
        ORDER BY w.category, w.indicator_name, w.country_name
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest World Bank indicators: {e}")
            return []

    def get_indicators_by_country(self, country_code: str) -> List[Dict[str, Any]]:
        """Get all latest indicators for a specific country."""
        query = """
        WITH latest AS (
            SELECT indicator_code, MAX(year) as max_year
            FROM worldbank_indicators
            WHERE country_code = %s
            GROUP BY indicator_code
        )
        SELECT w.indicator_code, w.indicator_name, w.category,
               w.country_code, w.country_name, w.year, w.value, w.unit
        FROM worldbank_indicators w
        INNER JOIN latest l
            ON w.indicator_code = l.indicator_code
            AND w.year = l.max_year
        WHERE w.country_code = %s
        ORDER BY w.category, w.indicator_name
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (country_code, country_code))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting indicators for country {country_code}: {e}")
            return []

    def get_indicators_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all latest indicators for a specific category."""
        query = """
        WITH latest AS (
            SELECT indicator_code, country_code, MAX(year) as max_year
            FROM worldbank_indicators
            WHERE category = %s
            GROUP BY indicator_code, country_code
        )
        SELECT w.indicator_code, w.indicator_name, w.category,
               w.country_code, w.country_name, w.year, w.value, w.unit
        FROM worldbank_indicators w
        INNER JOIN latest l
            ON w.indicator_code = l.indicator_code
            AND w.country_code = l.country_code
            AND w.year = l.max_year
        WHERE w.category = %s
        ORDER BY w.indicator_name, w.country_name
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (category, category))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting indicators for category {category}: {e}")
            return []

    def get_indicator_history(self, indicator_code: str, country_code: str,
                               years: int = 10) -> List[Dict[str, Any]]:
        """Get historical data for an indicator and country."""
        query = """
        SELECT indicator_code, indicator_name, category,
               country_code, country_name, year, value, unit
        FROM worldbank_indicators
        WHERE indicator_code = %s AND country_code = %s
        ORDER BY year DESC
        LIMIT %s
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (indicator_code, country_code, years))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting indicator history: {e}")
            return []

    def get_indicator_comparison(self, indicator_code: str) -> List[Dict[str, Any]]:
        """Get latest values of an indicator across all countries for comparison."""
        query = """
        WITH latest AS (
            SELECT country_code, MAX(year) as max_year
            FROM worldbank_indicators
            WHERE indicator_code = %s
            GROUP BY country_code
        )
        SELECT w.indicator_code, w.indicator_name, w.category,
               w.country_code, w.country_name, w.year, w.value, w.unit
        FROM worldbank_indicators w
        INNER JOIN latest l
            ON w.country_code = l.country_code
            AND w.year = l.max_year
        WHERE w.indicator_code = %s
        ORDER BY w.value DESC NULLS LAST
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (indicator_code, indicator_code))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting indicator comparison: {e}")
            return []

    def get_available_countries(self) -> List[Dict[str, str]]:
        """Get list of all countries with data."""
        query = """
        SELECT DISTINCT country_code, country_name
        FROM worldbank_indicators
        WHERE country_name IS NOT NULL
        ORDER BY country_name
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting available countries: {e}")
            return []

    def get_available_indicators(self) -> List[Dict[str, str]]:
        """Get list of all available indicators."""
        query = """
        SELECT DISTINCT indicator_code, indicator_name, category
        FROM worldbank_indicators
        ORDER BY category, indicator_name
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting available indicators: {e}")
            return []
