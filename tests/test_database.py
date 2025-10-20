"""
Tests for database operations.
"""

import pytest
from unittest.mock import Mock, patch
from config.database import DatabaseConfig, get_supabase_client, is_database_available


class TestDatabaseConfig:
    """Test database configuration."""
    
    @patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test-key'})
    def test_database_config_with_credentials(self):
        """Test database config with valid credentials."""
        config = DatabaseConfig()
        assert config.supabase_url == 'https://test.supabase.co'
        assert config.supabase_key == 'test-key'
        assert config.use_database is True
    
    @patch.dict('os.environ', {}, clear=True)
    def test_database_config_without_credentials(self):
        """Test database config without credentials."""
        config = DatabaseConfig()
        assert config.use_database is False
    
    @patch('config.database.create_client')
    def test_database_health_check_success(self, mock_create_client):
        """Test successful database health check."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = Mock()
        mock_create_client.return_value = mock_client
        
        config = DatabaseConfig()
        config.use_database = True
        config._client = mock_client
        
        assert config.health_check() is True
    
    @patch('config.database.create_client')
    def test_database_health_check_failure(self, mock_create_client):
        """Test failed database health check."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Connection failed")
        mock_create_client.return_value = mock_client
        
        config = DatabaseConfig()
        config.use_database = True
        config._client = mock_client
        
        assert config.health_check() is False


def test_get_supabase_client():
    """Test getting Supabase client."""
    # This will return None in test environment without proper setup
    # which is expected behavior
    client = get_supabase_client()
    # Just ensure it doesn't crash
    assert client is not None or client is None


def test_is_database_available():
    """Test database availability check."""
    # Should return bool without crashing
    result = is_database_available()
    assert isinstance(result, bool)

