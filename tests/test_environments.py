"""
Tests for environment configuration.
"""

import pytest
from unittest.mock import patch
from config.environments import (
    Environment,
    EnvironmentConfig,
    get_environment,
    get_config,
    is_production,
)


class TestEnvironmentConfig:
    """Test environment configuration."""
    
    @patch.dict('os.environ', {'ENVIRONMENT': 'development'})
    def test_development_environment(self):
        """Test development environment detection."""
        config = EnvironmentConfig()
        assert config.env == Environment.DEVELOPMENT
        assert config.get("debug") is True
        assert config.get("log_level") == "DEBUG"
    
    @patch.dict('os.environ', {'ENVIRONMENT': 'production'})
    def test_production_environment(self):
        """Test production environment detection."""
        config = EnvironmentConfig()
        assert config.env == Environment.PRODUCTION
        assert config.get("debug") is False
        assert config.get("enable_content_filter") is True
    
    @patch.dict('os.environ', {'STREAMLIT_SHARING_MODE': 'True'})
    def test_streamlit_share_detection(self):
        """Test Streamlit Share environment detection."""
        config = EnvironmentConfig()
        assert config.env == Environment.PRODUCTION
    
    def test_get_model_config(self):
        """Test getting model configuration."""
        config = EnvironmentConfig()
        model_config = config.get_model_config()
        
        assert "model" in model_config
        assert "max_tokens" in model_config
        assert "temperature" in model_config
    
    def test_get_cost_limits(self):
        """Test getting cost limit configuration."""
        config = EnvironmentConfig()
        limits = config.get_cost_limits()
        
        assert "daily_limit" in limits
        assert "monthly_limit" in limits
        assert limits["daily_limit"] > 0
    
    def test_is_production(self):
        """Test production check."""
        config = EnvironmentConfig()
        result = config.is_production()
        assert isinstance(result, bool)
    
    def test_is_development(self):
        """Test development check."""
        config = EnvironmentConfig()
        result = config.is_development()
        assert isinstance(result, bool)


def test_get_environment():
    """Test getting current environment."""
    env = get_environment()
    assert isinstance(env, Environment)


def test_get_config():
    """Test getting configuration value."""
    value = get_config("app_name", "default")
    assert value is not None


def test_is_production_function():
    """Test is_production function."""
    result = is_production()
    assert isinstance(result, bool)

