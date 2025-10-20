"""
Tests for content filtering.
"""

import pytest
from unittest.mock import Mock, patch
from middleware.content_filter import ContentFilter, check_content_safety


class TestContentFilter:
    """Test content filtering functionality."""
    
    @patch('middleware.content_filter.OpenAI')
    def test_content_filter_initialization(self, mock_openai):
        """Test content filter initialization."""
        filter = ContentFilter()
        # Should initialize without crashing
        assert filter is not None
    
    @patch('middleware.content_filter.OpenAI')
    def test_check_content_safe(self, mock_openai):
        """Test safe content passes filter."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.flagged = False
        mock_result.categories = Mock(model_dump=lambda: {})
        mock_response = Mock(results=[mock_result])
        mock_client.moderations.create.return_value = mock_response
        
        filter = ContentFilter()
        filter.client = mock_client
        filter.enabled = True
        
        is_safe, results = filter.check_content("I want a healthy burger")
        
        assert is_safe is True
        assert results["filtered"] is False
    
    @patch('middleware.content_filter.OpenAI')
    def test_check_content_unsafe(self, mock_openai):
        """Test unsafe content is flagged."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.flagged = True
        mock_result.categories = Mock(model_dump=lambda: {"violence": True})
        mock_response = Mock(results=[mock_result])
        mock_client.moderations.create.return_value = mock_response
        
        filter = ContentFilter()
        filter.client = mock_client
        filter.enabled = True
        
        is_safe, results = filter.check_content("inappropriate content")
        
        assert is_safe is False
        assert results["filtered"] is True
    
    def test_check_content_filter_disabled(self):
        """Test behavior when filter is disabled."""
        filter = ContentFilter()
        filter.enabled = False
        
        is_safe, results = filter.check_content("any content")
        
        assert is_safe is True
        assert results["filtered"] is False
    
    def test_filter_user_input_safe(self):
        """Test filtering safe user input."""
        filter = ContentFilter()
        filter.enabled = False  # Disable for testing
        
        is_safe, error = filter.filter_user_input("I want a salad")
        
        assert is_safe is True
        assert error == ""


def test_check_content_safety():
    """Test global content safety check."""
    is_safe, error = check_content_safety("I want a healthy meal")
    
    assert isinstance(is_safe, bool)
    assert isinstance(error, str)

