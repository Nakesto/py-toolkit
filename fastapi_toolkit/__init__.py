"""FastAPI Toolkit - A comprehensive toolkit for FastAPI applications.

This package provides:
- Dependency injection utilities
- Middleware for timeout, logging, error handling, and CORS
- Database connections (MySQL, PostgreSQL)
- Response helpers
- Cache connections (Redis, Memcache)
"""

from .dependency_injection import DIContainer, inject, get_container
from .middleware import (
    TimeoutMiddleware,
    LoggingMiddleware,
    ErrorHandlerMiddleware,
    CORSMiddleware
)
from .database import DatabaseManager, MySQLConnection, PostgreSQLConnection
from .response import BaseResponse, SuccessResponse, ErrorResponse
from .cache import CacheManager, RedisConnection, MemcacheConnection

__version__ = "1.0.0"
__author__ = "FastAPI Toolkit"

__all__ = [
    "DIContainer",
    "inject",
    "get_container",
    "TimeoutMiddleware",
    "LoggingMiddleware",
    "ErrorHandlerMiddleware",
    "CORSMiddleware",
    "DatabaseManager",
    "MySQLConnection",
    "PostgreSQLConnection",
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "CacheManager",
    "RedisConnection",
    "MemcacheConnection",
]