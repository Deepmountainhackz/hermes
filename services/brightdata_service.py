"""
Bright Data Web Scraping Service
Handles web scraping for investor relations pages using Bright Data proxy network.
"""
import requests
import logging
import hashlib
import re
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from core.config import Config
from repositories.investor_relations_repository import InvestorRelationsRepository

logger = logging.getLogger(__name__)


class BrightDataService:
    """Service for scraping investor relations pages via Bright Data."""

    # Common IR document types to look for
    DOCUMENT_TYPES = {
        'earnings': ['earnings', 'quarterly', 'q1', 'q2', 'q3', 'q4', 'financial results'],
        'annual_report': ['annual report', '10-k', 'yearly', 'fiscal year'],
        'press_release': ['press release', 'news', 'announcement'],
        'sec_filing': ['10-q', '8-k', 'sec filing', 'form'],
        'presentation': ['presentation', 'investor day', 'conference', 'slides'],
        'guidance': ['guidance', 'outlook', 'forecast'],
        'dividend': ['dividend', 'distribution'],
        'proxy': ['proxy', 'def 14a', 'shareholder meeting'],
    }

    # Link patterns that typically point to IR documents
    DOC_LINK_PATTERNS = [
        r'\.pdf$',
        r'\.docx?$',
        r'\.xlsx?$',
        r'earnings',
        r'press[-_]?release',
        r'annual[-_]?report',
        r'investor',
        r'financial',
        r'sec[-_]?filing',
        r'presentation',
    ]

    def __init__(self, config: Config, repository: InvestorRelationsRepository):
        """
        Initialize the Bright Data service.

        Args:
            config: Application configuration
            repository: Investor relations repository instance
        """
        self.config = config
        self.repository = repository

        # Bright Data proxy configuration
        self.api_token = config.BRIGHT_DATA_API_TOKEN
        self.zone = config.BRIGHT_DATA_ZONE
        self.proxy_host = config.BRIGHT_DATA_PROXY_HOST
        self.proxy_port = config.BRIGHT_DATA_PROXY_PORT

        # Request settings
        self.timeout = config.API_TIMEOUT
        self.max_retries = config.API_MAX_RETRIES
        self.retry_delay = config.API_RETRY_DELAY
        self.rate_limit_delay = config.DEFAULT_RATE_LIMIT_DELAY

        # Build proxy URL if credentials are available
        self.proxy_url = None
        if self.api_token:
            # Format: http://brd-customer-<customer_id>-zone-<zone>:<password>@<host>:<port>
            self.proxy_url = f"http://brd-customer-{self.api_token}@{self.proxy_host}:{self.proxy_port}"

    def _get_session(self) -> requests.Session:
        """Create a requests session with Bright Data proxy."""
        session = requests.Session()

        if self.proxy_url:
            session.proxies = {
                'http': self.proxy_url,
                'https': self.proxy_url
            }
            session.verify = False  # Bright Data handles SSL

        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

        return session

    def _make_request(self, url: str, session: Optional[requests.Session] = None) -> Optional[str]:
        """
        Make an HTTP request with retry logic.

        Args:
            url: URL to fetch
            session: Optional session to reuse

        Returns:
            Response text or None on failure
        """
        if session is None:
            session = self._get_session()

        for attempt in range(self.max_retries):
            try:
                response = session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {url} - {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))

        return None

    def _classify_document_type(self, title: str, url: str) -> str:
        """
        Classify a document based on its title and URL.

        Args:
            title: Document title
            url: Document URL

        Returns:
            Document type classification
        """
        text = f"{title} {url}".lower()

        for doc_type, keywords in self.DOCUMENT_TYPES.items():
            for keyword in keywords:
                if keyword in text:
                    return doc_type

        return 'other'

    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """
        Try to extract a date from text.

        Args:
            text: Text that may contain a date

        Returns:
            Extracted datetime or None
        """
        # Common date patterns
        patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    from dateutil import parser
                    return parser.parse(match.group(1), fuzzy=True)
                except Exception:
                    pass

        return None

    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:64]

    def scrape_ir_page(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape a company's investor relations page.

        Args:
            company: Company dict with id, ticker, ir_url, etc.

        Returns:
            Dict with scrape results
        """
        ticker = company['ticker']
        ir_url = company['ir_url']
        company_id = company['id']

        logger.info(f"Scraping IR page for {ticker}: {ir_url}")

        result = {
            'ticker': ticker,
            'url': ir_url,
            'publications_found': 0,
            'publications_new': 0,
            'status': 'success',
            'error': None
        }

        session = self._get_session()
        html = self._make_request(ir_url, session)

        if not html:
            result['status'] = 'failed'
            result['error'] = 'Failed to fetch IR page'
            return result

        soup = BeautifulSoup(html, 'html.parser')
        publications = []

        # Find all links that might be IR documents
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            link_text = link.get_text(strip=True)

            # Skip empty or very short links
            if not href or len(link_text) < 3:
                continue

            # Check if this looks like an IR document
            full_url = urljoin(ir_url, href)
            is_document = any(
                re.search(pattern, full_url.lower() + ' ' + link_text.lower())
                for pattern in self.DOC_LINK_PATTERNS
            )

            if is_document:
                doc_type = self._classify_document_type(link_text, full_url)
                pub_date = self._extract_date_from_text(link_text)

                # Try to find surrounding text for context/summary
                parent = link.find_parent(['div', 'li', 'tr', 'article', 'section'])
                summary = None
                if parent:
                    summary_text = parent.get_text(strip=True)
                    if len(summary_text) > len(link_text):
                        summary = summary_text[:500]

                publications.append({
                    'company_id': company_id,
                    'ticker': ticker,
                    'title': link_text[:500],
                    'document_type': doc_type,
                    'url': full_url,
                    'publication_date': pub_date.date() if pub_date else None,
                    'content_hash': self._generate_content_hash(full_url),
                    'summary': summary
                })

        result['publications_found'] = len(publications)

        # Store publications in database
        if publications:
            inserted = self.repository.insert_bulk_publications(publications)
            result['publications_new'] = inserted

        # Update last scraped timestamp
        self.repository.update_last_scraped(company_id)

        logger.info(f"Scraped {ticker}: found {len(publications)} publications")
        return result

    def scrape_document_content(self, url: str, publication_id: int) -> Optional[Dict[str, Any]]:
        """
        Scrape the full content of a document/page.

        Args:
            url: URL to scrape
            publication_id: Publication ID to link content to

        Returns:
            Dict with content or None on failure
        """
        html = self._make_request(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Extract main text content
        text = soup.get_text(separator='\n', strip=True)

        # Extract metadata
        metadata = {
            'title': soup.title.string if soup.title else None,
            'meta_description': None,
            'word_count': len(text.split()),
            'scraped_at': datetime.now().isoformat()
        }

        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['meta_description'] = meta_desc.get('content')

        # Store in database
        content_id = self.repository.insert_content(
            publication_id=publication_id,
            raw_html=html[:100000],  # Limit size
            extracted_text=text[:50000],  # Limit size
            metadata=metadata
        )

        return {
            'content_id': content_id,
            'text_length': len(text),
            'word_count': metadata['word_count']
        }

    def collect_and_store_data(self, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main collection method - scrape all due companies.

        Args:
            tickers: Optional list of specific tickers to scrape

        Returns:
            Collection results summary
        """
        start_time = datetime.now()
        logger.info("Starting IR page collection")

        if tickers:
            # Get specific companies
            all_companies = self.repository.get_all_active_companies()
            companies = [c for c in all_companies if c['ticker'] in [t.upper() for t in tickers]]
        else:
            # Get companies due for scraping
            companies = self.repository.get_companies_to_scrape()

        if not companies:
            logger.info("No companies to scrape")
            return {
                'companies_scraped': 0,
                'publications_found': 0,
                'publications_new': 0,
                'failed': 0,
                'duration_seconds': 0,
                'timestamp': start_time
            }

        total_found = 0
        total_new = 0
        failed = 0

        for company in companies:
            try:
                result = self.scrape_ir_page(company)
                total_found += result['publications_found']
                total_new += result['publications_new']
                if result['status'] != 'success':
                    failed += 1

                # Rate limiting between companies
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Error scraping {company['ticker']}: {e}")
                failed += 1

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            'companies_scraped': len(companies),
            'publications_found': total_found,
            'publications_new': total_new,
            'failed': failed,
            'duration_seconds': round(duration, 2),
            'timestamp': end_time
        }

    def add_company_to_track(self, ticker: str, company_name: str, ir_url: str,
                              sector: Optional[str] = None) -> int:
        """
        Add a new company to track for IR scraping.

        Args:
            ticker: Stock ticker
            company_name: Company name
            ir_url: Investor relations page URL
            sector: Optional sector

        Returns:
            Company ID
        """
        return self.repository.add_company(
            ticker=ticker,
            company_name=company_name,
            ir_url=ir_url,
            sector=sector
        )

    def get_latest_publications(self, ticker: Optional[str] = None,
                                 document_type: Optional[str] = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest publications from database."""
        return self.repository.get_latest_publications(
            ticker=ticker,
            document_type=document_type,
            limit=limit
        )

    def search_publications(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search publications by keyword."""
        return self.repository.search_publications(search_term, limit)

    def get_tracked_companies(self) -> List[Dict[str, Any]]:
        """Get all companies being tracked."""
        return self.repository.get_all_active_companies()
