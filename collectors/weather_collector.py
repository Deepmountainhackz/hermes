"""Weather Collector."""
import logging
from typing import Optional
from core.config import Config
from core.database import DatabaseManager
from repositories.weather_repository import WeatherRepository
from services.weather_service import WeatherService

logger = logging.getLogger(__name__)

class WeatherCollector:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        self.repository = WeatherRepository(self.db_manager)
        self.service = WeatherService(self.config, self.repository)
    
    def setup(self):
        self.repository.create_tables()
    
    def collect(self, cities=None):
        self.setup()
        return self.service.collect_and_store_data(cities)
    
    def get_latest_data(self):
        return self.service.get_latest_weather()
