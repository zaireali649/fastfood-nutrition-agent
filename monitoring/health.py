"""
Application health check endpoint.

Features:
- Database connectivity check
- API connectivity check
- System resource check
"""

import logging
from datetime import datetime
from typing import Dict, Any
from config.database import get_supabase_client, is_database_available
from config.cost_control import get_usage_stats
import os

logger = logging.getLogger(__name__)


class HealthChecker:
    """Performs health checks on application components."""
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            if not is_database_available():
                return {
                    "status": "degraded",
                    "message": "Database not configured, using JSON fallback",
                }
            
            client = get_supabase_client()
            # Try a simple query
            client.table("user_profiles").select("id").limit(1).execute()
            
            return {
                "status": "healthy",
                "message": "Database connection OK",
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}",
            }
    
    def check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API configuration."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            return {
                "status": "unhealthy",
                "message": "OpenAI API key not configured",
            }
        
        if not api_key.startswith("sk-"):
            return {
                "status": "unhealthy",
                "message": "Invalid OpenAI API key format",
            }
        
        return {
            "status": "healthy",
            "message": "OpenAI API configured",
        }
    
    def check_budget_status(self) -> Dict[str, Any]:
        """Check API budget status."""
        try:
            usage = get_usage_stats()
            
            # Check if approaching limits
            if usage["daily_percent"] > 90:
                status = "warning"
                message = "Approaching daily budget limit"
            elif usage["monthly_percent"] > 90:
                status = "warning"
                message = "Approaching monthly budget limit"
            else:
                status = "healthy"
                message = "Budget OK"
            
            return {
                "status": status,
                "message": message,
                "daily_usage": f"${usage['daily_usage']:.4f}",
                "daily_limit": f"${usage['daily_limit']:.2f}",
                "monthly_usage": f"${usage['monthly_usage']:.4f}",
                "monthly_limit": f"${usage['monthly_limit']:.2f}",
            }
        except Exception as e:
            logger.error(f"Budget status check failed: {e}")
            return {
                "status": "unknown",
                "message": f"Error checking budget: {str(e)}",
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        db_health = self.check_database()
        api_health = self.check_openai_api()
        budget_health = self.check_budget_status()
        
        # Determine overall status
        statuses = [db_health["status"], api_health["status"], budget_health["status"]]
        
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "warning" in statuses or "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": db_health,
                "openai_api": api_health,
                "budget": budget_health,
            },
            "version": "3.0.0",
        }


# Global health checker
health_checker = HealthChecker()


def get_health() -> Dict[str, Any]:
    """Get application health status."""
    return health_checker.get_health_status()

