"""
Production Entry Point - Fast Food Nutrition Agent

This is the main production entry point with startup checks and health monitoring.
Streamlit Share should run: `multi_agent_app.py` directly.
This file provides CLI utilities and startup validation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging before any imports
from monitoring.logger import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)


def startup_checks() -> bool:
    """
    Run startup checks before launching app.
    
    Returns:
        True if all checks pass, False otherwise
    """
    logger.info("=" * 60)
    logger.info("🚀 Fast Food Nutrition Agent - Startup Checks")
    logger.info("=" * 60)
    
    checks_passed = True
    
    # Check 1: Environment variables
    logger.info("Checking environment configuration...")
    required_vars = ["OPENAI_API_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"❌ Missing required environment variable: {var}")
            checks_passed = False
        else:
            logger.info(f"✅ {var} configured")
    
    # Check 2: Database connectivity (optional)
    logger.info("Checking database connectivity...")
    try:
        from config.database import is_database_available, db_config
        if is_database_available():
            if db_config.health_check():
                logger.info("✅ Database connection healthy")
            else:
                logger.warning("⚠️ Database connection degraded (fallback to JSON)")
        else:
            logger.info("ℹ️  Database not configured (using JSON storage)")
    except Exception as e:
        logger.warning(f"⚠️ Database check failed: {e} (fallback to JSON)")
    
    # Check 3: Required directories
    logger.info("Checking required directories...")
    required_dirs = ["data/profiles", "logs"]
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            logger.info(f"Creating directory: {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ {dir_path} exists")
    
    # Check 4: Import critical modules
    logger.info("Checking critical modules...")
    try:
        import streamlit
        import openai
        from multi_agents.coordinator import run_multi_agent_workflow
        logger.info("✅ All critical modules importable")
    except ImportError as e:
        logger.error(f"❌ Failed to import critical module: {e}")
        checks_passed = False
    
    # Check 5: Cost controls
    logger.info("Checking cost controls...")
    try:
        from config.cost_control import cost_controller
        limits = cost_controller.get_usage_summary()
        logger.info(f"✅ Daily limit: ${limits['daily_limit']:.2f}")
        logger.info(f"✅ Monthly limit: ${limits['monthly_limit']:.2f}")
    except Exception as e:
        logger.error(f"❌ Cost controls check failed: {e}")
        checks_passed = False
    
    logger.info("=" * 60)
    if checks_passed:
        logger.info("✅ All startup checks passed")
    else:
        logger.error("❌ Some startup checks failed")
    logger.info("=" * 60)
    
    return checks_passed


def main():
    """Main entry point for production app."""
    # Run startup checks
    if not startup_checks():
        logger.error("Startup checks failed. Please fix the issues above.")
        sys.exit(1)
    
    # Import and run Streamlit app
    logger.info("Starting Streamlit application...")
    logger.info("For manual start: streamlit run multi_agent_app.py")
    
    # Note: When deployed to Streamlit Share, this file should not be used.
    # Streamlit Share should run multi_agent_app.py directly.
    print("\n" + "=" * 60)
    print("✅ Startup checks complete!")
    print("=" * 60)
    print("\nTo run the application:")
    print("  streamlit run multi_agent_app.py")
    print("\nFor Streamlit Share deployment:")
    print("  Main file: multi_agent_app.py")
    print("=" * 60)


if __name__ == "__main__":
    main
