from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "Hermes Intelligence Platform"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int = 5432
    
    ALPHA_VANTAGE_API_KEY: str
    OPENWEATHER_API_KEY: str
    NASA_API_KEY: str = "DEMO_KEY"
    NEWS_API_KEY: str
    USDA_NASS_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    COLLECTION_INTERVAL_HOURS: int = 2
    HISTORICAL_DATA_RETENTION_DAYS: int = 90
    CACHE_TTL_SECONDS: int = 300
    API_RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

settings = Settings()