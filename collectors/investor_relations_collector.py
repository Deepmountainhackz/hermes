"""
Investor Relations Collector
Orchestrates scraping of company IR pages using Bright Data.
"""
import logging
from typing import Optional, List, Dict, Any

from core.config import Config
from core.database import DatabaseManager
from repositories.investor_relations_repository import InvestorRelationsRepository
from services.brightdata_service import BrightDataService

logger = logging.getLogger(__name__)


class InvestorRelationsCollector:
    """Collector for investor relations page scraping."""

    # Default companies to track (can be expanded via add_company)
    DEFAULT_COMPANIES = [
        {'ticker': 'AAPL', 'name': 'Apple Inc.', 'url': 'https://investor.apple.com/investor-relations/default.aspx', 'sector': 'Technology'},
        {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'url': 'https://www.microsoft.com/en-us/Investor', 'sector': 'Technology'},
        {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'url': 'https://abc.xyz/investor/', 'sector': 'Technology'},
        {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'url': 'https://ir.aboutamazon.com/', 'sector': 'Consumer Cyclical'},
        {'ticker': 'META', 'name': 'Meta Platforms Inc.', 'url': 'https://investor.fb.com/home/default.aspx', 'sector': 'Technology'},
        {'ticker': 'NVDA', 'name': 'NVIDIA Corporation', 'url': 'https://investor.nvidia.com/', 'sector': 'Technology'},
        {'ticker': 'TSLA', 'name': 'Tesla Inc.', 'url': 'https://ir.tesla.com/', 'sector': 'Consumer Cyclical'},
        {'ticker': 'JPM', 'name': 'JPMorgan Chase & Co.', 'url': 'https://www.jpmorganchase.com/ir', 'sector': 'Financial Services'},
        {'ticker': 'V', 'name': 'Visa Inc.', 'url': 'https://investor.visa.com/', 'sector': 'Financial Services'},
        {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'url': 'https://investor.jnj.com/', 'sector': 'Healthcare'},
    ]

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the collector.

        Args:
            config: Optional configuration (uses default if not provided)
        """
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = InvestorRelationsRepository(self.db_manager)
        self.service = BrightDataService(self.config, self.repository)

    def setup(self) -> None:
        """Set up database tables and seed default companies."""
        self.repository.create_tables()

        # Add default companies if not already present
        existing = self.repository.get_all_active_companies()
        existing_tickers = {c['ticker'] for c in existing}

        for company in self.DEFAULT_COMPANIES:
            if company['ticker'] not in existing_tickers:
                self.repository.add_company(
                    ticker=company['ticker'],
                    company_name=company['name'],
                    ir_url=company['url'],
                    sector=company['sector']
                )
                logger.info(f"Added default company: {company['ticker']}")

    def collect(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the collection process.

        Args:
            tickers: Optional list of specific tickers to scrape

        Returns:
            Collection results summary
        """
        self.setup()
        return self.service.collect_and_store_data(tickers)

    def add_company(self, ticker: str, company_name: str, ir_url: str,
                    sector: Optional[str] = None) -> int:
        """
        Add a company to track.

        Args:
            ticker: Stock ticker symbol
            company_name: Full company name
            ir_url: Investor relations page URL
            sector: Optional sector classification

        Returns:
            Company ID
        """
        self.setup()
        return self.service.add_company_to_track(ticker, company_name, ir_url, sector)

    def remove_company(self, ticker: str) -> bool:
        """
        Remove a company from tracking (deactivate).

        Args:
            ticker: Stock ticker to deactivate

        Returns:
            True if successful
        """
        return self.repository.deactivate_company(ticker)

    def get_tracked_companies(self) -> List[Dict[str, Any]]:
        """Get all tracked companies."""
        return self.service.get_tracked_companies()

    def get_latest_publications(self, ticker: Optional[str] = None,
                                 document_type: Optional[str] = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest scraped publications.

        Args:
            ticker: Optional filter by ticker
            document_type: Optional filter by document type
            limit: Maximum results

        Returns:
            List of publications
        """
        return self.service.get_latest_publications(ticker, document_type, limit)

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search publications by keyword.

        Args:
            query: Search term
            limit: Maximum results

        Returns:
            List of matching publications
        """
        return self.service.search_publications(query, limit)

    def cleanup_old_data(self, days: int = 90) -> int:
        """
        Clean up old raw content (keeps publication metadata).

        Args:
            days: Number of days to retain content

        Returns:
            Number of records deleted
        """
        return self.repository.delete_old_content(days)
