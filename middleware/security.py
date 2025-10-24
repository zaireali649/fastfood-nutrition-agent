"""
Security middleware for input validation and sanitization.

Features:
- Input validation
- SQL injection prevention
- XSS protection
- Length limits
- Character filtering
"""

import re
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validates and sanitizes user inputs."""
    
    # Maximum input lengths
    MAX_TEXT_LENGTH = 1000
    MAX_RESTAURANT_LENGTH = 100
    MAX_PROFILE_NAME_LENGTH = 50
    MAX_RESTRICTION_LENGTH = 100
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--)",
        r"(;.*--)",
        r"(\bEXEC\b|\bEXECUTE\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    @classmethod
    def validate_text_input(
        cls,
        text: str,
        field_name: str = "text",
        max_length: Optional[int] = None,
        allow_empty: bool = False
    ) -> tuple[bool, str, str]:
        """
        Validate and sanitize text input.
        
        Args:
            text: Input text to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed
            
        Returns:
            Tuple of (is_valid, sanitized_text, error_message)
        """
        if not text and not allow_empty:
            return False, "", f"{field_name} cannot be empty"
        
        if not text:
            return True, "", ""
        
        # Check length
        max_len = max_length or cls.MAX_TEXT_LENGTH
        if len(text) > max_len:
            return False, "", f"{field_name} exceeds maximum length of {max_len} characters"
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected in {field_name}: {text[:50]}")
                return False, "", f"Invalid characters detected in {field_name}"
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"XSS attempt detected in {field_name}: {text[:50]}")
                return False, "", f"Invalid characters detected in {field_name}"
        
        # Sanitize: remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return True, sanitized, ""
    
    @classmethod
    def validate_restaurant_name(cls, name: str) -> tuple[bool, str, str]:
        """Validate restaurant name."""
        is_valid, sanitized, error = cls.validate_text_input(
            name,
            "Restaurant name",
            cls.MAX_RESTAURANT_LENGTH,
            allow_empty=False
        )
        
        if not is_valid:
            return is_valid, sanitized, error
        
        # Additional validation: only allow letters, numbers, spaces, hyphens, apostrophes
        if not re.match(r"^[a-zA-Z0-9\s\-'&.]+$", sanitized):
            return False, "", "Restaurant name contains invalid characters"
        
        return True, sanitized, ""
    
    @classmethod
    def validate_profile_name(cls, name: str) -> tuple[bool, str, str]:
        """Validate profile name."""
        is_valid, sanitized, error = cls.validate_text_input(
            name,
            "Profile name",
            cls.MAX_PROFILE_NAME_LENGTH,
            allow_empty=False
        )
        
        if not is_valid:
            return is_valid, sanitized, error
        
        # Additional validation: alphanumeric, spaces, underscores, hyphens only
        if not re.match(r"^[a-zA-Z0-9\s_-]+$", sanitized):
            return False, "", "Profile name can only contain letters, numbers, spaces, hyphens, and underscores"
        
        return True, sanitized, ""
    
    @classmethod
    def validate_calorie_target(cls, calories: int) -> tuple[bool, int, str]:
        """Validate calorie target."""
        if not isinstance(calories, int):
            try:
                calories = int(calories)
            except (ValueError, TypeError):
                return False, 0, "Calories must be a number"
        
        if calories < 300:
            return False, 0, "Calorie target must be at least 300"
        
        if calories > 5000:
            return False, 0, "Calorie target must be at most 5000"
        
        return True, calories, ""
    
    @classmethod
    def validate_dietary_restrictions(cls, restrictions: List[str]) -> tuple[bool, List[str], str]:
        """Validate dietary restrictions list."""
        if not isinstance(restrictions, list):
            return False, [], "Dietary restrictions must be a list"
        
        sanitized = []
        for restriction in restrictions:
            is_valid, sanitized_text, error = cls.validate_text_input(
                restriction,
                "Dietary restriction",
                cls.MAX_RESTRICTION_LENGTH,
                allow_empty=True
            )
            
            if not is_valid:
                return False, [], error
            
            if sanitized_text:  # Only add non-empty restrictions
                sanitized.append(sanitized_text)
        
        # Limit number of restrictions
        if len(sanitized) > 10:
            return False, [], "Maximum 10 dietary restrictions allowed"
        
        return True, sanitized, ""
    
    @classmethod
    def validate_rating(cls, rating: int) -> tuple[bool, int, str]:
        """Validate meal rating."""
        if not isinstance(rating, int):
            try:
                rating = int(rating)
            except (ValueError, TypeError):
                return False, 0, "Rating must be a number"
        
        if rating < 1 or rating > 5:
            return False, 0, "Rating must be between 1 and 5"
        
        return True, rating, ""


def sanitize_user_inputs(user_goal: str, restaurant: str) -> Dict[str, Any]:
    """
    Sanitize all user inputs before processing.
    
    Args:
        user_goal: User's meal request
        restaurant: Restaurant name
        
    Returns:
        Dictionary with validation results and sanitized inputs
    """
    validator = SecurityValidator()
    
    # Validate restaurant
    restaurant_valid, restaurant_clean, restaurant_error = validator.validate_restaurant_name(restaurant)
    
    # Validate user goal
    goal_valid, goal_clean, goal_error = validator.validate_text_input(
        user_goal,
        "User request",
        allow_empty=False
    )
    
    return {
        "valid": restaurant_valid and goal_valid,
        "restaurant": restaurant_clean,
        "user_goal": goal_clean,
        "errors": [e for e in [restaurant_error, goal_error] if e],
    }

