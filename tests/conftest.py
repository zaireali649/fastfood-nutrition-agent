"""
Pytest configuration and fixtures.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    
    # Mock chat completion response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test meal recommendation"))]
    mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    
    client.chat.completions.create.return_value = mock_response
    
    # Mock moderation response
    mock_moderation = Mock()
    mock_moderation.results = [Mock(
        flagged=False,
        categories=Mock(model_dump=lambda: {})
    )]
    client.moderations.create.return_value = mock_moderation
    
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = Mock()
    
    # Mock table operations
    mock_table = Mock()
    mock_result = Mock(data=[])
    mock_table.select.return_value.execute.return_value = mock_result
    mock_table.insert.return_value.execute.return_value = mock_result
    mock_table.update.return_value.eq.return_value.execute.return_value = mock_result
    mock_table.delete.return_value.eq.return_value.execute.return_value = mock_result
    
    client.table.return_value = mock_table
    
    return client


@pytest.fixture
def sample_profile():
    """Sample user profile for testing."""
    return {
        "user_preferences": {
            "default_calorie_target": 1200,
            "dietary_restrictions": ["vegetarian"],
            "favorite_restaurants": ["Subway"],
            "disliked_items": ["pickles"],
            "preferred_cooking_methods": ["grilled"],
        },
        "meal_history": [
            {
                "restaurant": "Subway",
                "calories": 1200,
                "rating": 4,
                "timestamp": datetime.now().isoformat(),
            }
        ],
        "stats": {
            "total_meals_tracked": 1,
            "avg_daily_calories": 1200,
            "avg_meal_rating": 4.0,
            "profile_created": datetime.now().isoformat(),
        },
    }


@pytest.fixture
def sample_meal():
    """Sample meal data for testing."""
    return {
        "restaurant": "McDonald's",
        "calories": 800,
        "rating": 5,
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("ENABLE_CONTENT_FILTER", "false")
    monkeypatch.setenv("ENABLE_MONITORING", "false")

