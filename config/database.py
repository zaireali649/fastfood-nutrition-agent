"""
Database configuration and connection management for Supabase.

This module handles:
- Supabase connection pooling
- Environment-based configuration
- Automatic fallback to JSON storage
- Connection health checks
"""

import os
from typing import Optional
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration manager."""
    
    def __init__(self):
        """Initialize database configuration from environment variables."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.use_database = self._should_use_database()
        self._client: Optional[Client] = None
        
    def _should_use_database(self) -> bool:
        """Determine if database should be used based on config."""
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found. Falling back to JSON storage.")
            return False
        return True
    
    @property
    def client(self) -> Optional[Client]:
        """Get or create Supabase client."""
        if not self.use_database:
            return None
            
        if self._client is None:
            try:
                self._client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.use_database = False
                return None
                
        return self._client
    
    def health_check(self) -> bool:
        """Check database connection health."""
        if not self.use_database:
            return False
            
        try:
            # Try a simple query to check connection
            self.client.table('user_profiles').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database config instance
db_config = DatabaseConfig()


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client instance."""
    return db_config.client


def is_database_available() -> bool:
    """Check if database is available and configured."""
    return db_config.use_database and db_config.client is not None

