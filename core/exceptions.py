"""
Custom Exceptions
Application-specific exception classes.
"""


class HermesException(Exception):
    """Base exception for Hermes Intelligence Platform."""
    pass


class ConfigurationError(HermesException):
    """Raised when there's a configuration problem."""
    pass


class DatabaseError(HermesException):
    """Raised when database operations fail."""
    pass


class APIError(HermesException):
    """Raised when external API calls fail."""
    pass


class ValidationError(HermesException):
    """Raised when data validation fails."""
    pass


class DataCollectionError(HermesException):
    """Raised when data collection fails."""
    pass


class ServiceError(HermesException):
    """Raised when a service operation fails."""
    pass
