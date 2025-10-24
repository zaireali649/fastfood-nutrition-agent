"""
Health Check Endpoint for Streamlit.

Provides health status that can be displayed in the UI or queried externally.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any
import logging
from monitoring.health import get_health
from core.circuit_breaker import get_all_circuit_breaker_status
from config.cost_control import get_usage_stats

logger = logging.getLogger(__name__)


def render_health_dashboard():
    """Render health check dashboard in Streamlit sidebar."""
    with st.sidebar.expander("🏥 System Health", expanded=False):
        health = get_health()
        
        # Overall status
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓"
        }
        
        overall_status = health["status"]
        st.markdown(f"### {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        st.caption(f"Last checked: {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Component status
        st.markdown("**Components:**")
        for component, details in health["components"].items():
            comp_status = details["status"]
            comp_emoji = status_emoji.get(comp_status, "❓")
            comp_name = component.replace('_', ' ').title()
            st.markdown(f"{comp_emoji} **{comp_name}**")
            
            if comp_status != "healthy":
                st.caption(f"↳ {details['message']}")
            st.write("")  # Add spacing
        
        # Budget status
        if "budget" in health["components"]:
            budget = health["components"]["budget"]
            if "daily_usage" in budget:
                st.markdown("---")
                st.markdown("**Budget:**")
                st.markdown(f"• Daily: `{budget['daily_usage']}`/`{budget['daily_limit']}`")
                st.markdown(f"• Monthly: `{budget['monthly_usage']}`/`{budget['monthly_limit']}`")
        
        # Circuit breakers
        circuit_status = get_all_circuit_breaker_status()
        if circuit_status:
            st.markdown("---")
            st.markdown("**Circuit Breakers:**")
            for name, status in circuit_status.items():
                state = status["state"]
                state_emoji = {
                    "closed": "✅",
                    "open": "❌",
                    "half_open": "⚠️"
                }.get(state, "❓")
                st.markdown(f"{state_emoji} {name}: `{state}`")


def render_cost_dashboard():
    """Render cost monitoring dashboard in Streamlit sidebar."""
    with st.sidebar.expander("💰 Cost Monitor", expanded=False):
        try:
            stats = get_usage_stats()
            
            # Daily Usage
            st.markdown("**Daily Usage:**")
            daily_percent = min(100, stats['daily_percent'])
            st.progress(daily_percent / 100)
            st.markdown(f"`${stats['daily_usage']:.4f}` / `${stats['daily_limit']:.2f}`")
            st.caption(f"{daily_percent:.1f}% used")
            
            st.write("")  # Spacing
            
            # Monthly Usage
            st.markdown("**Monthly Usage:**")
            monthly_percent = min(100, stats['monthly_percent'])
            st.progress(monthly_percent / 100)
            st.markdown(f"`${stats['monthly_usage']:.4f}` / `${stats['monthly_limit']:.2f}`")
            st.caption(f"{monthly_percent:.1f}% used")
            
            st.markdown("---")
            
            # Status
            if daily_percent > 90:
                st.error("⚠️ Approaching daily limit!")
            elif monthly_percent > 90:
                st.warning("⚠️ Approaching monthly limit!")
            elif stats['monthly_usage'] > 0:
                st.success("✅ Within budget")
            else:
                st.info("ℹ️ No usage yet today")
                
        except Exception as e:
            st.error(f"💸 Cost data unavailable: {e}")


def get_health_json() -> Dict[str, Any]:
    """
    Get health status as JSON (for API/monitoring).
    
    Returns:
        Health status dictionary
    """
    try:
        health = get_health()
        
        # Add circuit breaker status
        health["circuit_breakers"] = get_all_circuit_breaker_status()
        
        # Add cost status
        try:
            health["cost_status"] = get_usage_stats()
        except Exception as e:
            logger.error(f"Failed to get cost stats: {e}")
            health["cost_status"] = {"error": str(e)}
        
        return health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def display_detailed_health():
    """Display detailed health information in main content area."""
    st.header("🏥 System Health Dashboard")
    
    health = get_health_json()
    
    # Overall status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = health.get("status", "unknown")
        status_color = {
            "healthy": "🟢",
            "degraded": "🟡",
            "unhealthy": "🔴",
            "unknown": "⚪"
        }.get(status, "⚪")
        st.metric("Status", f"{status_color} {status.upper()}")
    
    with col2:
        st.metric("Version", health.get("version", "unknown"))
    
    with col3:
        timestamp = health.get("timestamp", "")
        if timestamp:
            st.metric("Last Check", timestamp.split("T")[1][:8])
    
    # Components
    st.subheader("Component Status")
    for component, details in health.get("components", {}).items():
        with st.expander(f"{component.replace('_', ' ').title()} - {details['status']}", expanded=details['status'] != 'healthy'):
            st.json(details)
    
    # Circuit Breakers
    if health.get("circuit_breakers"):
        st.subheader("Circuit Breakers")
        for name, status in health["circuit_breakers"].items():
            col1, col2, col3 = st.columns(3)
            col1.write(f"**{name}**")
            col2.write(status["state"])
            col3.write(f"Failures: {status['failure_count']}")
    
    # Cost Status
    if health.get("cost_status"):
        st.subheader("Cost Status")
        cost = health["cost_status"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Daily Usage",
                f"${cost.get('daily_usage', 0):.4f}",
                f"{cost.get('daily_percent', 0):.1f}%"
            )
        
        with col2:
            st.metric(
                "Monthly Usage",
                f"${cost.get('monthly_usage', 0):.4f}",
                f"{cost.get('monthly_percent', 0):.1f}%"
            )
    
    # Raw JSON
    with st.expander("Raw JSON", expanded=False):
        st.json(health)

