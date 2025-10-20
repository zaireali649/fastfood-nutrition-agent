"""
Application metrics tracking.

Features:
- Performance metrics
- Business metrics
- System health metrics
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from config.database import get_supabase_client, is_database_available
import time

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._in_memory_metrics: Dict[str, list] = {}
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "count",
        tags: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags for filtering
        """
        timestamp = datetime.now()
        
        # Store in memory
        if metric_name not in self._in_memory_metrics:
            self._in_memory_metrics[metric_name] = []
        
        self._in_memory_metrics[metric_name].append({
            "timestamp": timestamp,
            "value": value,
            "unit": unit,
            "tags": tags or {}
        })
        
        # Store in database if available
        if is_database_available():
            try:
                client = get_supabase_client()
                client.table("system_metrics").insert({
                    "metric_name": metric_name,
                    "metric_value": value,
                    "metric_unit": unit,
                    "tags": tags or {},
                }).execute()
            except Exception as e:
                logger.error(f"Failed to record metric to database: {e}")
    
    def record_request_duration(self, duration_seconds: float, request_type: str = "general"):
        """Record request duration metric."""
        self.record_metric(
            "request_duration",
            duration_seconds,
            unit="seconds",
            tags={"request_type": request_type}
        )
    
    def record_agent_execution(self, agent_name: str, duration: float, success: bool):
        """Record agent execution metrics."""
        self.record_metric(
            "agent_execution_time",
            duration,
            unit="seconds",
            tags={"agent": agent_name, "success": success}
        )
        
        self.record_metric(
            "agent_execution_count",
            1,
            unit="count",
            tags={"agent": agent_name, "success": success}
        )
    
    def record_database_query(self, table: str, operation: str, duration: float):
        """Record database query metrics."""
        self.record_metric(
            "database_query_time",
            duration,
            unit="seconds",
            tags={"table": table, "operation": operation}
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics."""
        summary = {}
        
        for metric_name, values in self._in_memory_metrics.items():
            recent_values = [v["value"] for v in values[-100:]]  # Last 100 values
            
            if recent_values:
                summary[metric_name] = {
                    "count": len(recent_values),
                    "avg": sum(recent_values) / len(recent_values),
                    "min": min(recent_values),
                    "max": max(recent_values),
                    "unit": values[-1]["unit"],
                }
        
        return summary


# Global metrics collector
metrics_collector = MetricsCollector()


def record_metric(metric_name: str, value: float, **kwargs):
    """Record a metric."""
    metrics_collector.record_metric(metric_name, value, **kwargs)


def time_operation(operation_name: str):
    """
    Context manager to time an operation.
    
    Usage:
        with time_operation("database_query"):
            # Do work
            pass
    """
    class TimerContext:
        def __init__(self, name):
            self.name = name
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            metrics_collector.record_request_duration(duration, self.name)
            return False
    
    return TimerContext(operation_name)

