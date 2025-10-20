#!/usr/bin/env python3
"""
Health check script for monitoring.

Run this to check if all systems are operational.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring.health import get_health
import json


def main():
    """Run health check and display results."""
    print("🏥 Running Health Check...")
    print("=" * 50)
    print()
    
    health = get_health()
    
    # Display overall status
    status = health["status"]
    status_emoji = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌",
        "unknown": "❓"
    }
    
    print(f"Overall Status: {status_emoji.get(status, '❓')} {status.upper()}")
    print(f"Timestamp: {health['timestamp']}")
    print(f"Version: {health['version']}")
    print()
    
    # Display component status
    print("Component Status:")
    print("-" * 50)
    
    components = health["components"]
    
    for component, details in components.items():
        comp_status = details["status"]
        comp_emoji = status_emoji.get(comp_status, "❓")
        print(f"{comp_emoji} {component.replace('_', ' ').title()}: {comp_status}")
        print(f"   {details['message']}")
        
        # Show additional details if present
        for key, value in details.items():
            if key not in ["status", "message"]:
                print(f"   {key}: {value}")
        print()
    
    # Print JSON for machine parsing
    print()
    print("JSON Output:")
    print("-" * 50)
    print(json.dumps(health, indent=2))
    
    # Exit code based on status
    if status == "healthy":
        sys.exit(0)
    elif status == "degraded":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

