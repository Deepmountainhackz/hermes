"""Disasters Collector."""
import logging
from typing import Optional
from core.config import Config
from core.database import DatabaseManager
from repositories.disasters_repository import DisastersRepository
from services.disasters_service import DisastersService

logger = logging.getLogger(__name__)

class DisastersCollector:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = DisastersRepository(self.db_manager)
        self.service = DisastersService(self.config, self.repository)
    
    def setup(self):
        self.repository.create_tables()
    
    def collect(self):
        self.setup()
        return self.service.collect_and_store_data()
