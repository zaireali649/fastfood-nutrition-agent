"""
Content filtering using OpenAI Moderation API.

Features:
- Automatic content moderation
- Harmful content detection
- Logging of flagged content
"""

import logging
from typing import Dict, Any, Optional
from openai import OpenAI
import os

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filters user content for inappropriate material."""
    
    def __init__(self):
        """Initialize content filter."""
        self.client = None
        self.enabled = os.getenv("ENABLE_CONTENT_FILTER", "true").lower() == "true"
        
        if self.enabled:
            try:
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client for content filtering: {e}")
                self.enabled = False
    
    def check_content(self, text: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if content passes moderation.
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (is_safe, moderation_results)
        """
        if not self.enabled:
            return True, {"filtered": False, "reason": "filtering_disabled"}
        
        if not self.client:
            logger.warning("Content filter not initialized, allowing content")
            return True, {"filtered": False, "reason": "filter_unavailable"}
        
        try:
            # Call OpenAI moderation API
            response = self.client.moderations.create(input=text)
            result = response.results[0]
            
            # Check if content is flagged
            if result.flagged:
                logger.warning(f"Content flagged by moderation API: {result.categories}")
                
                # Get specific categories that were flagged
                flagged_categories = [
                    category for category, flagged in result.categories.model_dump().items()
                    if flagged
                ]
                
                return False, {
                    "filtered": True,
                    "reason": "inappropriate_content",
                    "categories": flagged_categories,
                }
            
            return True, {"filtered": False, "reason": "content_safe"}
            
        except Exception as e:
            logger.error(f"Content moderation API error: {e}")
            # Fail open - allow content if API is down
            return True, {"filtered": False, "reason": "moderation_error"}
    
    def filter_user_input(self, user_goal: str) -> tuple[bool, str]:
        """
        Filter user input for inappropriate content.
        
        Args:
            user_goal: User's meal request
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        is_safe, results = self.check_content(user_goal)
        
        if not is_safe:
            categories = results.get("categories", [])
            logger.warning(f"User input blocked: {categories}")
            
            return False, (
                "Your request contains content that doesn't meet our guidelines. "
                "Please rephrase your request focusing on dietary preferences and meal requirements."
            )
        
        return True, ""


# Global content filter instance
content_filter = ContentFilter()


def check_content_safety(text: str) -> tuple[bool, str]:
    """
    Check if text is safe to process.
    
    Args:
        text: Text to check
        
    Returns:
        Tuple of (is_safe, error_message)
    """
    return content_filter.filter_user_input(text)

