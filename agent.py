"""
Fast Food Nutrition Agent

A simple agent that recommends high protein, low sodium meals from fast food restaurants
based on user dietary restrictions and calorie requirements.
"""

import os
import asyncio
from typing import List
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key


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


async def run_nutrition_agent(task_generator: Agent, user_goal: str) -> str:
    """
    Process a single nutrition request and return the results.

    Args:
        task_generator: The configured nutrition agent
        user_goal: User's specific meal request

    Returns:
        The agent's meal recommendation response
    """
    # Get meal recommendations from the agent
    tasks = await generate_tasks(task_generator, user_goal)
    return tasks


def get_task_generator(prompt: str) -> Agent:
    """
    Create and configure the nutrition agent with the given prompt.

    Args:
        prompt: The system prompt containing nutritionist instructions

    Returns:
        Configured Agent instance for nutrition recommendations
    """
    return Agent(
        name="Task Generator",
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
