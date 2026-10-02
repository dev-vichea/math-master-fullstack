"""
Configuration - Application settings and environment configuration.

Settings loaded from:
- Environment variables
- .env file
- Default values
"""

from app.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
