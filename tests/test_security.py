"""
Tests for security middleware.
"""

import pytest
from middleware.security import SecurityValidator, sanitize_user_inputs


class TestSecurityValidator:
    """Test security validation functions."""
    
    def test_validate_text_input_success(self):
        """Test valid text input."""
        is_valid, sanitized, error = SecurityValidator.validate_text_input(
            "I want a healthy meal",
            "request"
        )
        assert is_valid is True
        assert sanitized == "I want a healthy meal"
        assert error == ""
    
    def test_validate_text_input_empty(self):
        """Test empty text input."""
        is_valid, sanitized, error = SecurityValidator.validate_text_input(
            "",
            "request",
            allow_empty=False
        )
        assert is_valid is False
        assert error != ""
    
    def test_validate_text_input_too_long(self):
        """Test text exceeding max length."""
        long_text = "a" * 1001
        is_valid, sanitized, error = SecurityValidator.validate_text_input(
            long_text,
            "request"
        )
        assert is_valid is False
        assert "exceeds maximum length" in error
    
    def test_validate_text_input_sql_injection(self):
        """Test SQL injection detection."""
        malicious_input = "test'; DROP TABLE users; --"
        is_valid, sanitized, error = SecurityValidator.validate_text_input(
            malicious_input,
            "request"
        )
        assert is_valid is False
        assert "Invalid characters" in error
    
    def test_validate_text_input_xss_attempt(self):
        """Test XSS attempt detection."""
        xss_input = '<script>alert("xss")</script>'
        is_valid, sanitized, error = SecurityValidator.validate_text_input(
            xss_input,
            "request"
        )
        assert is_valid is False
        assert "Invalid characters" in error
    
    def test_validate_restaurant_name_success(self):
        """Test valid restaurant name."""
        is_valid, sanitized, error = SecurityValidator.validate_restaurant_name(
            "McDonald's"
        )
        assert is_valid is True
        assert sanitized == "McDonald's"
    
    def test_validate_restaurant_name_invalid_chars(self):
        """Test restaurant name with invalid characters."""
        is_valid, sanitized, error = SecurityValidator.validate_restaurant_name(
            "Test@#$%Restaurant"
        )
        assert is_valid is False
    
    def test_validate_profile_name_success(self):
        """Test valid profile name."""
        is_valid, sanitized, error = SecurityValidator.validate_profile_name(
            "John_Doe-123"
        )
        assert is_valid is True
    
    def test_validate_profile_name_invalid(self):
        """Test invalid profile name."""
        is_valid, sanitized, error = SecurityValidator.validate_profile_name(
            "John@Doe"
        )
        assert is_valid is False
    
    def test_validate_calorie_target_success(self):
        """Test valid calorie target."""
        is_valid, value, error = SecurityValidator.validate_calorie_target(1200)
        assert is_valid is True
        assert value == 1200
    
    def test_validate_calorie_target_too_low(self):
        """Test calorie target below minimum."""
        is_valid, value, error = SecurityValidator.validate_calorie_target(200)
        assert is_valid is False
    
    def test_validate_calorie_target_too_high(self):
        """Test calorie target above maximum."""
        is_valid, value, error = SecurityValidator.validate_calorie_target(6000)
        assert is_valid is False
    
    def test_validate_dietary_restrictions_success(self):
        """Test valid dietary restrictions."""
        restrictions = ["vegetarian", "gluten-free"]
        is_valid, sanitized, error = SecurityValidator.validate_dietary_restrictions(
            restrictions
        )
        assert is_valid is True
        assert len(sanitized) == 2
    
    def test_validate_dietary_restrictions_too_many(self):
        """Test too many dietary restrictions."""
        restrictions = [f"restriction_{i}" for i in range(15)]
        is_valid, sanitized, error = SecurityValidator.validate_dietary_restrictions(
            restrictions
        )
        assert is_valid is False
    
    def test_validate_rating_success(self):
        """Test valid rating."""
        is_valid, value, error = SecurityValidator.validate_rating(4)
        assert is_valid is True
        assert value == 4
    
    def test_validate_rating_out_of_range(self):
        """Test rating out of valid range."""
        is_valid, value, error = SecurityValidator.validate_rating(6)
        assert is_valid is False


def test_sanitize_user_inputs_success():
    """Test successful input sanitization."""
    result = sanitize_user_inputs(
        "I want a healthy meal",
        "McDonald's"
    )
    assert result["valid"] is True
    assert result["user_goal"] == "I want a healthy meal"
    assert result["restaurant"] == "McDonald's"
    assert len(result["errors"]) == 0


def test_sanitize_user_inputs_invalid():
    """Test input sanitization with invalid data."""
    result = sanitize_user_inputs(
        "test'; DROP TABLE --",
        "Test<script>Restaurant"
    )
    assert result["valid"] is False
    assert len(result["errors"]) > 0

