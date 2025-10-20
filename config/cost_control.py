"""
OpenAI API cost control and monitoring.

Features:
- Real-time cost tracking
- Daily/monthly spending limits
- Rate limiting
- Usage alerts
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
from config.database import get_supabase_client, is_database_available
from config.environments import get_config

logger = logging.getLogger(__name__)


# OpenAI pricing (as of 2024)
MODEL_COSTS = {
    "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
    "gpt-4-turbo": {"input": 0.01 / 1000, "output": 0.03 / 1000},
    "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
}


class CostController:
    """Manages OpenAI API cost tracking and limits."""
    
    def __init__(self):
        """Initialize cost controller."""
        self.daily_limit = get_config("daily_cost_limit", 0.17)
        self.monthly_limit = self.daily_limit * 30
        self.hourly_request_limit = get_config("request_limit_per_hour", 20)
        self._in_memory_usage: Dict[str, list] = {"requests": [], "costs": []}
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for an API call.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        if model not in MODEL_COSTS:
            # Default to gpt-3.5-turbo pricing
            model = "gpt-3.5-turbo"
        
        pricing = MODEL_COSTS[model]
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        
        return input_cost + output_cost
    
    def can_make_request(self, estimated_cost: float = 0.01) -> Tuple[bool, str]:
        """
        Check if request can be made within budget limits.
        
        Args:
            estimated_cost: Estimated cost of the request
            
        Returns:
            Tuple of (can_make_request, reason_if_not)
        """
        # Check hourly rate limit
        if not self._check_rate_limit():
            return False, f"Hourly rate limit exceeded ({self.hourly_request_limit} requests/hour)"
        
        # Check daily budget
        daily_usage = self.get_daily_usage()
        if daily_usage + estimated_cost > self.daily_limit:
            return False, f"Daily budget limit reached (${self.daily_limit:.2f})"
        
        # Check monthly budget
        monthly_usage = self.get_monthly_usage()
        if monthly_usage + estimated_cost > self.monthly_limit:
            return False, f"Monthly budget limit reached (${self.monthly_limit:.2f})"
        
        return True, ""
    
    def _check_rate_limit(self) -> bool:
        """Check if within hourly rate limit."""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Clean old requests from in-memory cache
        self._in_memory_usage["requests"] = [
            ts for ts in self._in_memory_usage["requests"] 
            if ts > one_hour_ago
        ]
        
        # Check database if available
        if is_database_available():
            try:
                client = get_supabase_client()
                result = client.table("api_usage") \
                    .select("id") \
                    .gte("timestamp", one_hour_ago.isoformat()) \
                    .execute()
                
                return len(result.data) < self.hourly_request_limit
            except Exception as e:
                logger.error(f"Error checking rate limit: {e}")
        
        # Fallback to in-memory tracking
        return len(self._in_memory_usage["requests"]) < self.hourly_request_limit
    
    def get_daily_usage(self) -> float:
        """Get total cost for today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if is_database_available():
            try:
                client = get_supabase_client()
                result = client.table("api_usage") \
                    .select("estimated_cost") \
                    .gte("timestamp", today.isoformat()) \
                    .execute()
                
                return sum(row["estimated_cost"] for row in result.data)
            except Exception as e:
                logger.error(f"Error getting daily usage: {e}")
        
        # Fallback to in-memory tracking
        return sum(
            cost for ts, cost in self._in_memory_usage["costs"]
            if ts > today
        )
    
    def get_monthly_usage(self) -> float:
        """Get total cost for this month."""
        first_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if is_database_available():
            try:
                client = get_supabase_client()
                result = client.table("api_usage") \
                    .select("estimated_cost") \
                    .gte("timestamp", first_of_month.isoformat()) \
                    .execute()
                
                return sum(row["estimated_cost"] for row in result.data)
            except Exception as e:
                logger.error(f"Error getting monthly usage: {e}")
        
        # Fallback to in-memory tracking
        return sum(
            cost for ts, cost in self._in_memory_usage["costs"]
            if ts > first_of_month
        )
    
    def log_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_type: str = "recommendation",
        profile_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log API usage for tracking.
        
        Args:
            model: Model used
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            request_type: Type of request
            profile_id: User profile ID (if applicable)
            success: Whether request succeeded
            error_message: Error message if failed
        """
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens
        now = datetime.now()
        
        # Store in memory
        self._in_memory_usage["requests"].append(now)
        self._in_memory_usage["costs"].append((now, cost))
        
        # Log to database if available
        if is_database_available():
            try:
                client = get_supabase_client()
                client.table("api_usage").insert({
                    "model": model,
                    "tokens_used": total_tokens,
                    "estimated_cost": cost,
                    "request_type": request_type,
                    "profile_id": profile_id,
                    "success": success,
                    "error_message": error_message,
                }).execute()
            except Exception as e:
                logger.error(f"Error logging usage to database: {e}")
        
        # Log warning if approaching limits
        daily_usage = self.get_daily_usage()
        if daily_usage > self.daily_limit * 0.8:
            logger.warning(f"Approaching daily limit: ${daily_usage:.4f} / ${self.daily_limit:.2f}")
    
    def get_usage_summary(self) -> Dict[str, any]:
        """Get usage summary statistics."""
        daily_usage = self.get_daily_usage()
        monthly_usage = self.get_monthly_usage()
        
        return {
            "daily_usage": daily_usage,
            "daily_limit": self.daily_limit,
            "daily_remaining": max(0, self.daily_limit - daily_usage),
            "daily_percent": (daily_usage / self.daily_limit * 100) if self.daily_limit > 0 else 0,
            "monthly_usage": monthly_usage,
            "monthly_limit": self.monthly_limit,
            "monthly_remaining": max(0, self.monthly_limit - monthly_usage),
            "monthly_percent": (monthly_usage / self.monthly_limit * 100) if self.monthly_limit > 0 else 0,
        }


# Global cost controller instance
cost_controller = CostController()


def can_make_api_request(estimated_cost: float = 0.01) -> Tuple[bool, str]:
    """Check if API request can be made."""
    return cost_controller.can_make_request(estimated_cost)


def log_api_usage(
    model: str,
    input_tokens: int,
    output_tokens: int,
    **kwargs
) -> None:
    """Log API usage."""
    cost_controller.log_usage(model, input_tokens, output_tokens, **kwargs)


def get_usage_stats() -> Dict[str, any]:
    """Get usage statistics."""
    return cost_controller.get_usage_summary()

