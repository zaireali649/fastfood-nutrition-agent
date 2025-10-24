"""
Tests for cost control and rate limiting.
"""

import pytest
from datetime import datetime, timedelta
from config.cost_control import CostController, can_make_api_request, get_usage_stats


class TestCostController:
    """Test cost control functionality."""
    
    def test_estimate_cost_gpt35(self):
        """Test cost estimation for GPT-3.5."""
        controller = CostController()
        cost = controller.estimate_cost("gpt-3.5-turbo", 1000, 500)
        
        # Expected: (1000 * 0.0005/1000) + (500 * 0.0015/1000)
        expected = 0.0005 + 0.00075
        assert abs(cost - expected) < 0.0001
    
    def test_estimate_cost_gpt4(self):
        """Test cost estimation for GPT-4."""
        controller = CostController()
        cost = controller.estimate_cost("gpt-4", 1000, 500)
        
        # Expected: (1000 * 0.03/1000) + (500 * 0.06/1000)
        expected = 0.03 + 0.03
        assert abs(cost - expected) < 0.0001
    
    def test_can_make_request_within_budget(self):
        """Test request allowed within budget."""
        controller = CostController()
        can_request, reason = controller.can_make_request(0.001)
        
        # Should be allowed for small cost
        assert can_request is True
        assert reason == ""
    
    def test_can_make_request_exceeds_budget(self):
        """Test request blocked when exceeding budget."""
        controller = CostController()
        controller.daily_limit = 0.01
        
        # Try to make a request that exceeds daily limit
        can_request, reason = controller.can_make_request(1.0)
        
        assert can_request is False
        assert "budget" in reason.lower()
    
    def test_log_usage(self):
        """Test usage logging."""
        controller = CostController()
        
        # Should not crash
        controller.log_usage(
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            request_type="test",
            success=True
        )
        
        # Verify in-memory storage
        assert len(controller._in_memory_usage["requests"]) > 0
    
    def test_get_usage_summary(self):
        """Test usage summary generation."""
        controller = CostController()
        
        # Log some usage
        controller.log_usage("gpt-3.5-turbo", 100, 50, success=True)
        
        summary = controller.get_usage_summary()
        
        assert "daily_usage" in summary
        assert "daily_limit" in summary
        assert "monthly_usage" in summary
        assert summary["daily_usage"] >= 0


def test_can_make_api_request():
    """Test global API request check."""
    can_request, reason = can_make_api_request(0.001)
    assert isinstance(can_request, bool)
    assert isinstance(reason, str)


def test_get_usage_stats():
    """Test getting usage statistics."""
    stats = get_usage_stats()
    
    assert "daily_usage" in stats
    assert "daily_limit" in stats
    assert "monthly_usage" in stats
    assert "daily_percent" in stats

