"""
Configuration Management
Loads and validates configuration from environment variables.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Hermes Intelligence Platform."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        
        # Database Configuration
        self.DATABASE_HOST: str = os.getenv('DATABASE_HOST', 'localhost')
        self.DATABASE_PORT: int = int(os.getenv('DATABASE_PORT', '5432'))
        self.DATABASE_NAME: str = os.getenv('DATABASE_NAME', 'hermes_db')
        self.DATABASE_USER: str = os.getenv('DATABASE_USER', '')
        self.DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD', '')
        
        # Database URL (constructed from above)
        self.DATABASE_URL: str = os.getenv(
            'DATABASE_URL',
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
        
        # API Keys
        self.ALPHA_VANTAGE_API_KEY: str = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.NEWSAPI_KEY: str = os.getenv('NEWSAPI_KEY', '')
        self.OPENWEATHER_API_KEY: str = os.getenv('OPENWEATHER_API_KEY', '')
        self.NASA_API_KEY: str = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE: str = os.getenv('LOG_FILE', 'logs/hermes.log')
        
        # Ensure log directory exists
        log_path = Path(self.LOG_FILE).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Application Settings
        self.ENV: str = os.getenv('ENV', 'development')
        self.DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def validate(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            ('DATABASE_NAME', self.DATABASE_NAME),
            ('DATABASE_USER', self.DATABASE_USER),
            ('DATABASE_PASSWORD', self.DATABASE_PASSWORD),
        ]
        
        missing = [field for field, value in required_fields if not value]
        
        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            return False
        
        return True
    
    def __repr__(self) -> str:
        """String representation of config (without sensitive data)."""
        return (
            f"Config(database={self.DATABASE_NAME}, "
            f"host={self.DATABASE_HOST}, "
            f"env={self.ENV})"
        )


# Global config instance
config = Config()
