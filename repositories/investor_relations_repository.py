"""
Investor Relations Repository
Handles all database operations for company IR pages, publications, and scraped content.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class InvestorRelationsRepository:
    """Repository for investor relations data operations."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.

        Args:
            db_manager: Database manager instance for connection handling
        """
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the investor relations tables if they don't exist."""
        create_query = """
        -- Company IR pages tracking
        CREATE TABLE IF NOT EXISTS ir_companies (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(20) NOT NULL,
            company_name VARCHAR(255),
            ir_url TEXT NOT NULL,
            sector VARCHAR(100),
            last_scraped TIMESTAMP,
            scrape_frequency_hours INT DEFAULT 24,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker)
        );

        -- Scraped publications/documents
        CREATE TABLE IF NOT EXISTS ir_publications (
            id SERIAL PRIMARY KEY,
            company_id INT REFERENCES ir_companies(id) ON DELETE CASCADE,
            ticker VARCHAR(20) NOT NULL,
            title VARCHAR(500),
            document_type VARCHAR(100),
            url TEXT NOT NULL,
            publication_date DATE,
            content_hash VARCHAR(64),
            summary TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(url)
        );

        -- Raw scraped content for full-text search
        CREATE TABLE IF NOT EXISTS ir_content (
            id SERIAL PRIMARY KEY,
            publication_id INT REFERENCES ir_publications(id) ON DELETE CASCADE,
            raw_html TEXT,
            extracted_text TEXT,
            metadata JSONB,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_ir_companies_ticker ON ir_companies(ticker);
        CREATE INDEX IF NOT EXISTS idx_ir_companies_active ON ir_companies(active);
        CREATE INDEX IF NOT EXISTS idx_ir_publications_ticker ON ir_publications(ticker);
        CREATE INDEX IF NOT EXISTS idx_ir_publications_date ON ir_publications(publication_date DESC);
        CREATE INDEX IF NOT EXISTS idx_ir_publications_type ON ir_publications(document_type);
        CREATE INDEX IF NOT EXISTS idx_ir_content_scraped ON ir_content(scraped_at);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("Investor relations tables and indexes created/verified")
        except Exception as e:
            logger.error(f"Error creating IR tables: {e}")
            raise DatabaseError(f"Failed to create IR tables: {e}")

    def add_company(self, ticker: str, company_name: str, ir_url: str,
                    sector: Optional[str] = None, scrape_frequency_hours: int = 24) -> int:
        """
        Add a company to track for IR scraping.

        Args:
            ticker: Stock ticker symbol
            company_name: Full company name
            ir_url: URL to investor relations page
            sector: Optional sector classification
            scrape_frequency_hours: How often to scrape (default 24 hours)

        Returns:
            Company ID
        """
        query = """
        INSERT INTO ir_companies (ticker, company_name, ir_url, sector, scrape_frequency_hours)
        VALUES (%(ticker)s, %(company_name)s, %(ir_url)s, %(sector)s, %(scrape_frequency_hours)s)
        ON CONFLICT (ticker) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            ir_url = EXCLUDED.ir_url,
            sector = EXCLUDED.sector,
            scrape_frequency_hours = EXCLUDED.scrape_frequency_hours
        RETURNING id
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, {
                        'ticker': ticker.upper(),
                        'company_name': company_name,
                        'ir_url': ir_url,
                        'sector': sector,
                        'scrape_frequency_hours': scrape_frequency_hours
                    })
                    result = cur.fetchone()
                conn.commit()
            logger.info(f"Added/updated company {ticker} for IR tracking")
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error adding company {ticker}: {e}")
            raise DatabaseError(f"Failed to add company: {e}")

    def get_companies_to_scrape(self) -> List[Dict[str, Any]]:
        """
        Get companies that need to be scraped based on their schedule.

        Returns:
            List of companies ready for scraping
        """
        query = """
        SELECT id, ticker, company_name, ir_url, sector, last_scraped, scrape_frequency_hours
        FROM ir_companies
        WHERE active = TRUE
        AND (
            last_scraped IS NULL
            OR last_scraped < NOW() - (scrape_frequency_hours || ' hours')::INTERVAL
        )
        ORDER BY last_scraped NULLS FIRST
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [{
                        'id': row[0],
                        'ticker': row[1],
                        'company_name': row[2],
                        'ir_url': row[3],
                        'sector': row[4],
                        'last_scraped': row[5],
                        'scrape_frequency_hours': row[6]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting companies to scrape: {e}")
            raise DatabaseError(f"Failed to get companies: {e}")

    def get_all_active_companies(self) -> List[Dict[str, Any]]:
        """Get all active companies being tracked."""
        query = """
        SELECT id, ticker, company_name, ir_url, sector, last_scraped, scrape_frequency_hours
        FROM ir_companies
        WHERE active = TRUE
        ORDER BY ticker
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [{
                        'id': row[0],
                        'ticker': row[1],
                        'company_name': row[2],
                        'ir_url': row[3],
                        'sector': row[4],
                        'last_scraped': row[5],
                        'scrape_frequency_hours': row[6]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting active companies: {e}")
            raise DatabaseError(f"Failed to get companies: {e}")

    def update_last_scraped(self, company_id: int) -> None:
        """Update the last_scraped timestamp for a company."""
        query = "UPDATE ir_companies SET last_scraped = NOW() WHERE id = %s"

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (company_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating last_scraped for company {company_id}: {e}")
            raise DatabaseError(f"Failed to update last_scraped: {e}")

    def insert_publication(self, publication_data: Dict[str, Any]) -> int:
        """
        Insert a scraped publication.

        Args:
            publication_data: Dictionary with publication details

        Returns:
            Publication ID
        """
        query = """
        INSERT INTO ir_publications
            (company_id, ticker, title, document_type, url, publication_date, content_hash, summary)
        VALUES
            (%(company_id)s, %(ticker)s, %(title)s, %(document_type)s, %(url)s,
             %(publication_date)s, %(content_hash)s, %(summary)s)
        ON CONFLICT (url) DO UPDATE SET
            title = EXCLUDED.title,
            document_type = EXCLUDED.document_type,
            publication_date = EXCLUDED.publication_date,
            summary = EXCLUDED.summary,
            scraped_at = NOW()
        RETURNING id
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, publication_data)
                    result = cur.fetchone()
                conn.commit()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error inserting publication: {e}")
            raise DatabaseError(f"Failed to insert publication: {e}")

    def insert_bulk_publications(self, publications: List[Dict[str, Any]]) -> int:
        """
        Insert multiple publications in a single transaction.

        Args:
            publications: List of publication data dictionaries

        Returns:
            Number of records inserted/updated
        """
        if not publications:
            return 0

        query = """
        INSERT INTO ir_publications
            (company_id, ticker, title, document_type, url, publication_date, content_hash, summary)
        VALUES
            (%(company_id)s, %(ticker)s, %(title)s, %(document_type)s, %(url)s,
             %(publication_date)s, %(content_hash)s, %(summary)s)
        ON CONFLICT (url) DO UPDATE SET
            title = EXCLUDED.title,
            document_type = EXCLUDED.document_type,
            publication_date = EXCLUDED.publication_date,
            summary = EXCLUDED.summary,
            scraped_at = NOW()
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for pub in publications:
                        cur.execute(query, pub)
                conn.commit()
            logger.info(f"Inserted/updated {len(publications)} publications")
            return len(publications)
        except Exception as e:
            logger.error(f"Error inserting bulk publications: {e}")
            raise DatabaseError(f"Failed to insert publications: {e}")

    def insert_content(self, publication_id: int, raw_html: str,
                       extracted_text: str, metadata: Optional[Dict] = None) -> int:
        """
        Store raw scraped content for a publication.

        Args:
            publication_id: ID of the parent publication
            raw_html: Raw HTML content
            extracted_text: Extracted text content
            metadata: Optional metadata dict

        Returns:
            Content ID
        """
        query = """
        INSERT INTO ir_content (publication_id, raw_html, extracted_text, metadata)
        VALUES (%(publication_id)s, %(raw_html)s, %(extracted_text)s, %(metadata)s)
        RETURNING id
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    import json
                    cur.execute(query, {
                        'publication_id': publication_id,
                        'raw_html': raw_html,
                        'extracted_text': extracted_text,
                        'metadata': json.dumps(metadata) if metadata else None
                    })
                    result = cur.fetchone()
                conn.commit()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error inserting content: {e}")
            raise DatabaseError(f"Failed to insert content: {e}")

    def get_latest_publications(self, ticker: Optional[str] = None,
                                 document_type: Optional[str] = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get the most recent publications.

        Args:
            ticker: Optional filter by company ticker
            document_type: Optional filter by document type
            limit: Maximum records to return

        Returns:
            List of publication dictionaries
        """
        conditions = []
        params = []

        if ticker:
            conditions.append("p.ticker = %s")
            params.append(ticker.upper())
        if document_type:
            conditions.append("p.document_type = %s")
            params.append(document_type)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        query = f"""
        SELECT p.id, p.ticker, c.company_name, p.title, p.document_type,
               p.url, p.publication_date, p.summary, p.scraped_at
        FROM ir_publications p
        LEFT JOIN ir_companies c ON p.company_id = c.id
        {where_clause}
        ORDER BY p.publication_date DESC NULLS LAST, p.scraped_at DESC
        LIMIT %s
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    rows = cur.fetchall()
                    return [{
                        'id': row[0],
                        'ticker': row[1],
                        'company_name': row[2],
                        'title': row[3],
                        'document_type': row[4],
                        'url': row[5],
                        'publication_date': row[6],
                        'summary': row[7],
                        'scraped_at': row[8]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest publications: {e}")
            raise DatabaseError(f"Failed to get publications: {e}")

    def get_publication_content(self, publication_id: int) -> Optional[Dict[str, Any]]:
        """Get the full content for a publication."""
        query = """
        SELECT id, raw_html, extracted_text, metadata, scraped_at
        FROM ir_content
        WHERE publication_id = %s
        ORDER BY scraped_at DESC
        LIMIT 1
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (publication_id,))
                    row = cur.fetchone()
                    if row:
                        return {
                            'id': row[0],
                            'raw_html': row[1],
                            'extracted_text': row[2],
                            'metadata': row[3],
                            'scraped_at': row[4]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting publication content: {e}")
            raise DatabaseError(f"Failed to get content: {e}")

    def search_publications(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search publications by title or summary.

        Args:
            search_term: Text to search for
            limit: Maximum results

        Returns:
            List of matching publications
        """
        query = """
        SELECT p.id, p.ticker, c.company_name, p.title, p.document_type,
               p.url, p.publication_date, p.summary, p.scraped_at
        FROM ir_publications p
        LEFT JOIN ir_companies c ON p.company_id = c.id
        WHERE p.title ILIKE %s OR p.summary ILIKE %s
        ORDER BY p.publication_date DESC NULLS LAST
        LIMIT %s
        """
        search_pattern = f"%{search_term}%"

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (search_pattern, search_pattern, limit))
                    rows = cur.fetchall()
                    return [{
                        'id': row[0],
                        'ticker': row[1],
                        'company_name': row[2],
                        'title': row[3],
                        'document_type': row[4],
                        'url': row[5],
                        'publication_date': row[6],
                        'summary': row[7],
                        'scraped_at': row[8]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error searching publications: {e}")
            raise DatabaseError(f"Failed to search: {e}")

    def delete_old_content(self, days: int = 90) -> int:
        """
        Delete raw content older than specified days (keep publications).

        Args:
            days: Number of days to retain content

        Returns:
            Number of records deleted
        """
        query = "DELETE FROM ir_content WHERE scraped_at < %s"
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old content records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old content: {e}")
            raise DatabaseError(f"Failed to delete old content: {e}")

    def deactivate_company(self, ticker: str) -> bool:
        """Deactivate a company from scraping."""
        query = "UPDATE ir_companies SET active = FALSE WHERE ticker = %s"

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ticker.upper(),))
                    affected = cur.rowcount
                conn.commit()
            return affected > 0
        except Exception as e:
            logger.error(f"Error deactivating company {ticker}: {e}")
            raise DatabaseError(f"Failed to deactivate company: {e}")
