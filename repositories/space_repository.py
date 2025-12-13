"""
Space Repository
Handles all database operations for space data (ISS, NEO, Solar Flares).
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class SpaceRepository:
    """Repository for space data operations."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create all space-related tables if they don't exist."""
        queries = [
            # ISS Positions table
            """
            CREATE TABLE IF NOT EXISTS iss_positions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                latitude DECIMAL(10, 6),
                longitude DECIMAL(10, 6),
                altitude DECIMAL(10, 2),
                velocity DECIMAL(10, 2),
                UNIQUE(timestamp)
            );
            CREATE INDEX IF NOT EXISTS idx_iss_timestamp ON iss_positions(timestamp);
            """,
            # Near-Earth Objects table
            """
            CREATE TABLE IF NOT EXISTS near_earth_objects (
                id SERIAL PRIMARY KEY,
                neo_id VARCHAR(50) NOT NULL,
                name VARCHAR(255),
                date DATE NOT NULL,
                estimated_diameter_min DECIMAL(10, 2),
                estimated_diameter_max DECIMAL(10, 2),
                relative_velocity DECIMAL(15, 2),
                miss_distance DECIMAL(20, 2),
                is_potentially_hazardous BOOLEAN,
                UNIQUE(neo_id, date)
            );
            CREATE INDEX IF NOT EXISTS idx_neo_date ON near_earth_objects(date);
            """,
            # Solar Flares table
            """
            CREATE TABLE IF NOT EXISTS solar_flares (
                id SERIAL PRIMARY KEY,
                flare_id VARCHAR(50) NOT NULL UNIQUE,
                begin_time TIMESTAMP,
                peak_time TIMESTAMP,
                end_time TIMESTAMP,
                class_type VARCHAR(10),
                source_location VARCHAR(50),
                active_region_num VARCHAR(20)
            );
            CREATE INDEX IF NOT EXISTS idx_flare_begin ON solar_flares(begin_time);
            """
        ]

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for query in queries:
                        cur.execute(query)
                conn.commit()
            logger.info("Space tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating space tables: {e}")
            raise DatabaseError(f"Failed to create space tables: {e}")

    def insert_iss_position(self, data: Dict[str, Any]) -> int:
        """Insert ISS position data."""
        query = """
        INSERT INTO iss_positions (timestamp, latitude, longitude, altitude, velocity)
        VALUES (%(timestamp)s, %(latitude)s, %(longitude)s, %(altitude)s, %(velocity)s)
        ON CONFLICT (timestamp) DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            altitude = EXCLUDED.altitude,
            velocity = EXCLUDED.velocity
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, data)
                conn.commit()
            logger.info("Inserted ISS position")
            return 1
        except Exception as e:
            logger.error(f"Error inserting ISS position: {e}")
            raise DatabaseError(f"Failed to insert ISS position: {e}")

    def insert_neo_data(self, neo_list: List[Dict[str, Any]]) -> int:
        """Insert NEO data with upsert."""
        if not neo_list:
            return 0

        query = """
        INSERT INTO near_earth_objects
            (neo_id, name, date, estimated_diameter_min, estimated_diameter_max,
             relative_velocity, miss_distance, is_potentially_hazardous)
        VALUES
            (%(neo_id)s, %(name)s, %(date)s, %(estimated_diameter_min)s, %(estimated_diameter_max)s,
             %(relative_velocity)s, %(miss_distance)s, %(is_potentially_hazardous)s)
        ON CONFLICT (neo_id, date) DO UPDATE SET
            name = EXCLUDED.name,
            estimated_diameter_min = EXCLUDED.estimated_diameter_min,
            estimated_diameter_max = EXCLUDED.estimated_diameter_max,
            relative_velocity = EXCLUDED.relative_velocity,
            miss_distance = EXCLUDED.miss_distance,
            is_potentially_hazardous = EXCLUDED.is_potentially_hazardous
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for neo in neo_list:
                        cur.execute(query, neo)
                conn.commit()
            logger.info(f"Inserted {len(neo_list)} NEO records")
            return len(neo_list)
        except Exception as e:
            logger.error(f"Error inserting NEO data: {e}")
            raise DatabaseError(f"Failed to insert NEO data: {e}")

    def insert_solar_flares(self, flares: List[Dict[str, Any]]) -> int:
        """Insert solar flare data with upsert."""
        if not flares:
            return 0

        query = """
        INSERT INTO solar_flares
            (flare_id, begin_time, peak_time, end_time, class_type, source_location, active_region_num)
        VALUES
            (%(flare_id)s, %(begin_time)s, %(peak_time)s, %(end_time)s,
             %(class_type)s, %(source_location)s, %(active_region_num)s)
        ON CONFLICT (flare_id) DO UPDATE SET
            begin_time = EXCLUDED.begin_time,
            peak_time = EXCLUDED.peak_time,
            end_time = EXCLUDED.end_time,
            class_type = EXCLUDED.class_type,
            source_location = EXCLUDED.source_location,
            active_region_num = EXCLUDED.active_region_num
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for flare in flares:
                        cur.execute(query, flare)
                conn.commit()
            logger.info(f"Inserted {len(flares)} solar flare records")
            return len(flares)
        except Exception as e:
            logger.error(f"Error inserting solar flares: {e}")
            raise DatabaseError(f"Failed to insert solar flares: {e}")

    def get_latest_iss_position(self) -> Dict[str, Any]:
        """Get the most recent ISS position."""
        query = "SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 1"
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()
                    return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Error getting ISS position: {e}")
            return {}

    def get_upcoming_neo(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get NEOs approaching in the next N days."""
        query = """
        SELECT * FROM near_earth_objects
        WHERE date >= CURRENT_DATE AND date <= CURRENT_DATE + %s
        ORDER BY date, miss_distance
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (days,))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting NEO data: {e}")
            return []

    def get_recent_solar_flares(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get solar flares from the last N days."""
        query = """
        SELECT * FROM solar_flares
        WHERE begin_time >= CURRENT_DATE - %s
        ORDER BY begin_time DESC
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (days,))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting solar flares: {e}")
            return []
