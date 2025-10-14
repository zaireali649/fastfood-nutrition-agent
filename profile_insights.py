"""
Standalone script to get profile insights from the Profile Manager Agent.

Usage:
    python profile_insights.py <profile_name>
"""
# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from dotenv import load_dotenv
from agents import set_default_openai_key

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from multi_agents.profile_manager_agent import ProfileManagerAgent
from memory.user_profile import load_profile


async def get_profile_insights(profile_name: str):
    """Get personalized insights for a user profile."""
    
    # Load the profile
    profile = load_profile(profile_name)
    
    if not profile:
        print(f"Error: Profile '{profile_name}' not found.")
        print("\nAvailable profiles:")
        from memory.user_profile import list_profiles
        for p in list_profiles():
            print(f"  - {p}")
        return
    
    print(f"\n{'='*80}")
    print(f"  Profile Insights for: {profile_name}")
    print(f"{'='*80}\n")
    
    # Load prompt
    with open("prompts/profile_manager_prompt.txt", "r") as f:
        prompt = f.read()
    
    # Create agent and get insights
    profile_manager = ProfileManagerAgent(prompt)
    
    print("Analyzing your meal history and preferences...\n")
    
    insights = await profile_manager.analyze_profile(profile)
    
    print(insights)
    print(f"\n{'='*80}\n")


def main():
    """Main entry point."""
    # Load environment
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment.")
        return
    
    set_default_openai_key(api_key)
    
    # Get profile name from args
    if len(sys.argv) < 2:
        print("Usage: python profile_insights.py <profile_name>")
        print("\nAvailable profiles:")
        from memory.user_profile import list_profiles
        for p in list_profiles():
            print(f"  - {p}")
        return
    
    profile_name = sys.argv[1]
    
    # Run async
    asyncio.run(get_profile_insights(profile_name))


if __name__ == "__main__":
    main()

