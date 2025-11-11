class HermesException(Exception):
    """Base exception for all Hermes-specific errors"""
    pass

class DataCollectionError(HermesException):
    """Raised when data collection fails"""
    pass

class DataValidationError(HermesException):
    """Raised when data validation fails"""
    pass

class DatabaseError(HermesException):
    """Raised when database operations fail"""
    pass

class APIError(HermesException):
    """Raised when external API calls fail"""
    pass

class ConfigurationError(HermesException):
    """Raised when configuration is invalid"""
    pass
