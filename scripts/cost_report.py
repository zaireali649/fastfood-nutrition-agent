#!/usr/bin/env python3
"""
Generate cost usage report.

Shows OpenAI API usage and costs.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.cost_control import get_usage_stats
from config.environments import get_config


def main():
    """Generate and display cost report."""
    print("💰 OpenAI API Cost Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get usage stats
    stats = get_usage_stats()
    
    # Daily usage
    print("📊 Daily Usage:")
    print("-" * 60)
    print(f"   Usage:     ${stats['daily_usage']:.4f}")
    print(f"   Limit:     ${stats['daily_limit']:.2f}")
    print(f"   Remaining: ${stats['daily_remaining']:.4f}")
    print(f"   Used:      {stats['daily_percent']:.1f}%")
    
    # Progress bar
    bar_length = 40
    filled = int(bar_length * stats['daily_percent'] / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {stats['daily_percent']:.1f}%")
    print()
    
    # Monthly usage
    print("📅 Monthly Usage:")
    print("-" * 60)
    print(f"   Usage:     ${stats['monthly_usage']:.4f}")
    print(f"   Limit:     ${stats['monthly_limit']:.2f}")
    print(f"   Remaining: ${stats['monthly_remaining']:.4f}")
    print(f"   Used:      {stats['monthly_percent']:.1f}%")
    
    # Progress bar
    filled = int(bar_length * stats['monthly_percent'] / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {stats['monthly_percent']:.1f}%")
    print()
    
    # Projections
    days_in_month = 30
    current_day = datetime.now().day
    daily_rate = stats['daily_usage']
    projected_monthly = daily_rate * days_in_month
    
    print("📈 Projections:")
    print("-" * 60)
    print(f"   Daily Rate:        ${daily_rate:.4f}")
    print(f"   Projected Monthly: ${projected_monthly:.2f}")
    print(f"   Budget Remaining:  ${max(0, stats['monthly_limit'] - projected_monthly):.2f}")
    print()
    
    # Warnings
    if stats['daily_percent'] > 90:
        print("⚠️  WARNING: Approaching daily limit!")
    elif stats['monthly_percent'] > 90:
        print("⚠️  WARNING: Approaching monthly limit!")
    elif projected_monthly > stats['monthly_limit']:
        print("⚠️  WARNING: Projected to exceed monthly budget!")
    else:
        print("✅ Usage within normal limits")
    
    print()
    print("=" * 60)
    
    # Recommendations
    if stats['monthly_percent'] > 80:
        print()
        print("💡 Recommendations:")
        print("   • Reduce max_tokens in config/environments.py")
        print("   • Enable response caching")
        print("   • Increase rate limiting")
        print("   • Review API usage in Supabase")


if __name__ == "__main__":
    main()

