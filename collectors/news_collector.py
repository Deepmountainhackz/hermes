"""News Collector."""
import logging
from typing import Optional
from core.config import Config
from core.database import DatabaseManager
from repositories.news_repository import NewsRepository
from services.news_service import NewsService

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = NewsRepository(self.db_manager)
        self.service = NewsService(self.config, self.repository)
    
    def setup(self):
        self.repository.create_tables()
    
    def collect(self):
        self.setup()
        return self.service.collect_and_store_data()
