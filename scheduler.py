"""
Hermes Data Collection Scheduler
Automated data collection using APScheduler with metadata tracking.
"""

import logging
import signal
import sys
import time
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from core.config import Config
from core.database import DatabaseManager

# Import all collectors
from collectors.markets_collector import MarketsCollector
from collectors.crypto_collector import CryptoCollector
from collectors.forex_collector import ForexCollector
from collectors.commodities_collector import CommoditiesCollector
from collectors.weather_collector import WeatherCollector
from collectors.news_collector import NewsCollector
from collectors.economics_collector import EconomicsCollector
from collectors.space_collector import SpaceCollector
from collectors.disasters_collector import DisastersCollector
from collectors.gdelt_collector import GdeltCollector
from collectors.worldbank_collector import WorldBankCollector
from collectors.investor_relations_collector import InvestorRelationsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HermesScheduler')


class CollectorRunner:
    """Runs collectors and tracks metadata."""

    def __init__(self, config: Config, db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self._ensure_metadata_table()

    def _ensure_metadata_table(self):
        """Create collection_metadata table if not exists."""
        try:
            self.db_manager.execute_command("""
                CREATE TABLE IF NOT EXISTS collection_metadata (
                    id SERIAL PRIMARY KEY,
                    collector_name VARCHAR(50) UNIQUE NOT NULL,
                    last_run TIMESTAMP,
                    last_success TIMESTAMP,
                    last_duration_seconds DECIMAL(10, 3),
                    records_collected INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'idle',
                    error_message TEXT,
                    run_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception as e:
            logger.warning(f"Could not create metadata table: {e}")

    def _update_metadata(self, collector_name: str, status: str,
                         duration: float = None, records: int = None,
                         error: str = None):
        """Update collection metadata for a collector."""
        try:
            # Upsert metadata
            self.db_manager.execute_command("""
                INSERT INTO collection_metadata
                    (collector_name, last_run, status, last_duration_seconds,
                     records_collected, error_message, run_count)
                VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, 1)
                ON CONFLICT (collector_name) DO UPDATE SET
                    last_run = CURRENT_TIMESTAMP,
                    status = EXCLUDED.status,
                    last_duration_seconds = COALESCE(EXCLUDED.last_duration_seconds, collection_metadata.last_duration_seconds),
                    records_collected = COALESCE(EXCLUDED.records_collected, collection_metadata.records_collected),
                    error_message = EXCLUDED.error_message,
                    run_count = collection_metadata.run_count + 1,
                    last_success = CASE WHEN EXCLUDED.status = 'success'
                                       THEN CURRENT_TIMESTAMP
                                       ELSE collection_metadata.last_success END
            """, (collector_name, status, duration, records, error))
        except Exception as e:
            logger.error(f"Failed to update metadata for {collector_name}: {e}")

    def run_collector(self, collector_class, collector_name: str) -> bool:
        """Run a collector and track its execution."""
        logger.info(f"Starting {collector_name} collection...")
        self._update_metadata(collector_name, 'running')

        start_time = time.time()
        try:
            collector = collector_class(self.config)
            collector.setup()
            result = collector.collect()

            duration = time.time() - start_time
            records = result.success_count if hasattr(result, 'success_count') else 0

            self._update_metadata(
                collector_name, 'success',
                duration=duration,
                records=records
            )
            logger.info(f"✓ {collector_name}: {records} records in {duration:.1f}s")
            return True

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)[:500]  # Truncate long errors
            self._update_metadata(
                collector_name, 'failed',
                duration=duration,
                error=error_msg
            )
            logger.error(f"✗ {collector_name} failed: {e}")
            return False


class HermesScheduler:
    """Main scheduler for Hermes data collection."""

    # Collector configurations: (class, name, interval_minutes, enabled)
    COLLECTORS = {
        'markets': (MarketsCollector, 'markets', 15, True),
        'crypto': (CryptoCollector, 'crypto', 10, True),
        'forex': (ForexCollector, 'forex', 15, True),
        'commodities': (CommoditiesCollector, 'commodities', 30, True),
        'weather': (WeatherCollector, 'weather', 30, True),
        'news': (NewsCollector, 'news', 60, True),
        'economics': (EconomicsCollector, 'economics', 1440, True),  # Daily
        'space': (SpaceCollector, 'space', 1440, True),  # Daily
        'disasters': (DisastersCollector, 'disasters', 60, True),
        'gdelt': (GdeltCollector, 'gdelt', 60, True),
        'worldbank': (WorldBankCollector, 'worldbank', 1440, True),  # Daily
        'investor_relations': (InvestorRelationsCollector, 'investor_relations', 1440, True),  # Daily
    }

    def __init__(self):
        self.config = Config()
        self.db_manager = DatabaseManager(self.config)
        self.runner = CollectorRunner(self.config, self.db_manager)
        self.scheduler = BackgroundScheduler()
        self._shutdown = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Shutdown signal received...")
        self._shutdown = True
        self.stop()

    def _create_job(self, collector_key: str):
        """Create a scheduled job for a collector."""
        collector_class, name, interval, enabled = self.COLLECTORS[collector_key]

        if not enabled:
            logger.info(f"Skipping {name} (disabled)")
            return

        # Create the job function
        def job_func():
            self.runner.run_collector(collector_class, name)

        # Schedule based on interval
        if interval >= 1440:  # Daily or longer - use cron
            self.scheduler.add_job(
                job_func,
                CronTrigger(hour=6, minute=0),  # Run at 6 AM
                id=f"collect_{name}",
                name=f"Collect {name}",
                replace_existing=True
            )
            logger.info(f"Scheduled {name}: daily at 6:00 AM")
        else:
            self.scheduler.add_job(
                job_func,
                IntervalTrigger(minutes=interval),
                id=f"collect_{name}",
                name=f"Collect {name}",
                replace_existing=True
            )
            logger.info(f"Scheduled {name}: every {interval} minutes")

    def start(self, run_initial: bool = True):
        """Start the scheduler."""
        logger.info("=" * 50)
        logger.info("Starting Hermes Scheduler")
        logger.info("=" * 50)

        # Schedule all collectors
        for collector_key in self.COLLECTORS:
            self._create_job(collector_key)

        # Run initial collection if requested
        if run_initial:
            logger.info("\nRunning initial data collection...")
            self.run_all_now()

        # Start the scheduler
        self.scheduler.start()
        logger.info("\nScheduler started. Press Ctrl+C to stop.\n")

        # Keep running until shutdown
        try:
            while not self._shutdown:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        self.stop()

    def run_all_now(self):
        """Run all collectors immediately."""
        logger.info("Running all collectors...")
        for collector_key, (collector_class, name, _, enabled) in self.COLLECTORS.items():
            if enabled:
                self.runner.run_collector(collector_class, name)

    def run_one(self, collector_name: str) -> bool:
        """Run a single collector by name."""
        if collector_name not in self.COLLECTORS:
            logger.error(f"Unknown collector: {collector_name}")
            return False

        collector_class, name, _, _ = self.COLLECTORS[collector_name]
        return self.runner.run_collector(collector_class, name)

    def stop(self):
        """Stop the scheduler gracefully."""
        logger.info("Stopping scheduler...")
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped.")

    def get_status(self) -> list:
        """Get status of all collectors from metadata."""
        try:
            result = self.db_manager.execute_query("""
                SELECT collector_name, last_run, last_success,
                       last_duration_seconds, records_collected,
                       status, error_message, run_count
                FROM collection_metadata
                ORDER BY collector_name
            """)
            return result
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return []

    def get_next_runs(self) -> dict:
        """Get next scheduled run times for all jobs."""
        next_runs = {}
        for job in self.scheduler.get_jobs():
            next_runs[job.id] = job.next_run_time
        return next_runs


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Hermes Data Collection Scheduler')
    parser.add_argument('--run-once', action='store_true',
                        help='Run all collectors once and exit')
    parser.add_argument('--collector', type=str,
                        help='Run specific collector and exit')
    parser.add_argument('--no-initial', action='store_true',
                        help='Skip initial collection when starting scheduler')
    parser.add_argument('--status', action='store_true',
                        help='Show collector status and exit')

    args = parser.parse_args()

    scheduler = HermesScheduler()

    if args.status:
        print("\n=== Collector Status ===\n")
        status = scheduler.get_status()
        if status:
            for s in status:
                print(f"{s['collector_name']:15} | {s['status']:10} | "
                      f"Last: {s['last_run'] or 'Never':20} | "
                      f"Records: {s['records_collected'] or 0}")
        else:
            print("No collection data yet.")
        return

    if args.collector:
        success = scheduler.run_one(args.collector)
        sys.exit(0 if success else 1)

    if args.run_once:
        scheduler.run_all_now()
        return

    # Start continuous scheduling
    scheduler.start(run_initial=not args.no_initial)


if __name__ == "__main__":
    main()
