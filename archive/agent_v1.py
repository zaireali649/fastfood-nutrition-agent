"""
Fast Food Nutrition Agent

A context-aware agent that recommends high protein, low sodium meals from fast food
restaurants based on user dietary restrictions, calorie requirements, and historical
preferences.
"""

import os
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key

from memory.user_profile import get_todays_meals, get_recent_meals


async def generate_tasks(task_generator: Agent, goal: str) -> str:
    """
    Generate meal recommendations using the nutrition agent.

    Args:
        task_generator: The configured nutrition agent
        goal: User's meal request with restaurant, calories, and dietary restrictions

    Returns:
        The agent's meal recommendation response
    """
    result = await Runner.run(task_generator, goal)
    return result.final_output


async def run_nutrition_agent(
    task_generator: Agent, user_goal: str, user_profile: Optional[Dict] = None
) -> str:
    """
    Process a single nutrition request and return the results.

    Args:
        task_generator: The configured nutrition agent
        user_goal: User's specific meal request
        user_profile: Optional user profile for context

    Returns:
        The agent's meal recommendation response
    """
    # Build context-aware goal if profile exists
    if user_profile:
        # Read the base prompt
        with open("prompts/agent_prompt.txt", "r") as file:
            base_prompt = file.read()

        # Enhance with context
        contextual_prompt = build_context_prompt(base_prompt, user_profile, user_goal)

        # Create new agent with context
        contextual_agent = Agent(
            name="Nutrition Agent", instructions=f'"""{contextual_prompt}"""'
        )

        # Get meal recommendations with context
        tasks = await generate_tasks(contextual_agent, user_goal)
    else:
        # Get meal recommendations without context
        tasks = await generate_tasks(task_generator, user_goal)

    return tasks


def build_context_prompt(
    base_prompt: str, user_profile: Optional[Dict] = None, user_goal: str = ""
) -> str:
    """
    Build a context-aware prompt incorporating user profile and history.

    Args:
        base_prompt: The base nutritionist prompt
        user_profile: User profile dictionary with preferences and history
        user_goal: Current user request

    Returns:
        Enhanced prompt with context
    """
    if not user_profile:
        return base_prompt

    prefs = user_profile.get("user_preferences", {})
    stats = user_profile.get("stats", {})

    # Build context section
    context = "\n\n## USER CONTEXT\n"

    # Add preferences
    if prefs.get("dietary_restrictions"):
        context += (
            f"- Known dietary restrictions: {', '.join(prefs['dietary_restrictions'])}\n"
        )

    if prefs.get("disliked_items"):
        context += f"- Dislikes: {', '.join(prefs['disliked_items'])}\n"

    if prefs.get("preferred_cooking_methods"):
        context += f"- Preferred cooking methods: {', '.join(prefs['preferred_cooking_methods'])}\n"

    if prefs.get("favorite_restaurants"):
        context += f"- Favorite restaurants: {', '.join(prefs['favorite_restaurants'][:3])}\n"

    # Add statistics
    if stats.get("total_meals_tracked", 0) > 0:
        context += f"\n- Total meals tracked: {stats['total_meals_tracked']}\n"
        context += f"- Average meal calories: {stats.get('avg_daily_calories', 'N/A')} cal\n"

        if stats.get("most_visited_restaurant"):
            context += f"- Most visited restaurant: {stats['most_visited_restaurant']}\n"

        if stats.get("avg_meal_rating"):
            context += f"- Average meal satisfaction: {stats['avg_meal_rating']}/5 stars\n"

    # Add recent meal history
    recent_meals = get_recent_meals(user_profile, count=5)
    if recent_meals:
        context += "\n### Recent Meals (Last 5):\n"
        for i, meal in enumerate(reversed(recent_meals), 1):
            rating_stars = "⭐" * meal.get("rating", 0) if meal.get("rating") else "Not rated"
            context += f"{i}. {meal.get('restaurant', 'Unknown')} - {meal.get('calories', 'N/A')} cal - {rating_stars}\n"

    # Add today's meals
    todays_meals = get_todays_meals(user_profile)
    if todays_meals:
        total_today = sum(m.get("calories", 0) for m in todays_meals)
        context += f"\n⚠️ User has already logged {len(todays_meals)} meal(s) today ({total_today} cal)\n"

    # Combine base prompt with context
    enhanced_prompt = f"{base_prompt}\n{context}\n\n## CURRENT REQUEST\n{user_goal}"

    return enhanced_prompt


def get_task_generator(prompt: str, user_profile: Optional[Dict] = None) -> Agent:
    """
    Create and configure the nutrition agent with the given prompt.

    Args:
        prompt: The system prompt containing nutritionist instructions
        user_profile: Optional user profile for context-aware recommendations

    Returns:
        Configured Agent instance for nutrition recommendations
    """
    return Agent(
        name="Nutrition Agent",
        instructions=f'"""{prompt}"""',
    )


async def run_nutrition_workflow() -> None:
    """
    Main workflow function that processes multiple nutrition requests.

    Sets up the environment, creates the agent, and processes a list of meal requests
    from different fast food restaurants with various dietary restrictions.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Set OpenAI API key explicitly for the agents library
    set_default_openai_key(os.environ["OPENAI_API_KEY"])

    # Read the nutritionist prompt from file
    with open("prompts/agent_prompt.txt", "r") as file:
        prompt = file.read()

    # Create the nutrition agent
    task_generator = get_task_generator(prompt)

    # Define test meal requests with different restaurants and dietary restrictions
    user_goals: List[str] = [
        "I want a 1200 calorie meal from chick-fil-a. I have no dietary restrictions.",
        "I want a 1200 calorie meal from chick-fil-a. I cannot have gluten.",
        "I want a 1200 calorie meal from Mcdonald's. I cannot have pork.",
    ]

    # Process each meal request sequentially
    for user_goal in user_goals:
        await run_nutrition_agent(task_generator, user_goal)


if __name__ == "__main__":
    # Run the nutrition workflow
    asyncio.run(run_nutrition_workflow())
