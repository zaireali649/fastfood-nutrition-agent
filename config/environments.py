"""
Environment configuration for dev/staging/prod environments.

Handles:
- Environment detection
- Model selection based on environment
- Cost limits per environment
- Feature flags
"""

import os
from enum import Enum
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentConfig:
    """Environment-specific configuration."""
    
    def __init__(self):
        """Initialize environment configuration."""
        self.env = self._detect_environment()
        self.config = self._load_config()
        logger.info(f"Running in {self.env.value} environment")
    
    def _detect_environment(self) -> Environment:
        """Detect current environment from environment variables."""
        env_name = os.getenv("ENVIRONMENT", "development").lower()
        
        # Streamlit Share specific detection
        if os.getenv("STREAMLIT_SHARING_MODE") == "True":
            return Environment.PRODUCTION
            
        try:
            return Environment(env_name)
        except ValueError:
            logger.warning(f"Unknown environment '{env_name}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration based on environment."""
        base_config = {
            "app_name": "Fast Food Nutrition Agent",
            "version": "3.0.0",
            "debug": False,
            "log_level": "INFO",
        }
        
        if self.env == Environment.DEVELOPMENT:
            return {
                **base_config,
                "debug": True,
                "log_level": "DEBUG",
                "model": "gpt-3.5-turbo",
                "model_fallback": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7,
                "daily_cost_limit": 1.00,  # $1/day in dev
                "request_limit_per_hour": 100,
                "enable_content_filter": False,
                "enable_monitoring": False,
            }
        
        elif self.env == Environment.STAGING:
            return {
                **base_config,
                "debug": True,
                "log_level": "INFO",
                "model": "gpt-3.5-turbo",
                "model_fallback": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7,
                "daily_cost_limit": 0.50,  # $0.50/day in staging
                "request_limit_per_hour": 50,
                "enable_content_filter": True,
                "enable_monitoring": True,
            }
        
        else:  # PRODUCTION
            return {
                **base_config,
                "debug": False,
                "log_level": "WARNING",
                "model": "gpt-3.5-turbo",  # Most cost-effective
                "model_fallback": "gpt-3.5-turbo",
                "max_tokens": 800,  # Reduced for cost savings
                "temperature": 0.7,
                "daily_cost_limit": 0.17,  # ~$5/month = $0.17/day
                "request_limit_per_hour": 20,  # Prevent abuse
                "enable_content_filter": True,
                "enable_monitoring": True,
                "enable_caching": True,
            }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.env == Environment.DEVELOPMENT
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "model": self.get("model"),
            "model_fallback": self.get("model_fallback"),
            "max_tokens": self.get("max_tokens"),
            "temperature": self.get("temperature"),
        }
    
    def get_cost_limits(self) -> Dict[str, float]:
        """Get cost limit configuration."""
        return {
            "daily_limit": self.get("daily_cost_limit"),
            "monthly_limit": self.get("daily_cost_limit") * 30,
            "request_limit_per_hour": self.get("request_limit_per_hour"),
        }


# Global environment config instance
env_config = EnvironmentConfig()


def get_environment() -> Environment:
    """Get current environment."""
    return env_config.env


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return env_config.get(key, default)


def is_production() -> bool:
    """Check if running in production."""
    return env_config.is_production()

