import os
from agents import Agent, Runner, set_default_openai_key
import asyncio
from dotenv import load_dotenv


async def generate_tasks(task_generator, goal):
    result = await Runner.run(task_generator, goal)
    return result.final_output


async def run_nutrition_agent(task_generator, user_goal):
    tasks = await generate_tasks(task_generator, user_goal)
    print(tasks)


def get_task_generator(prompt):
    return Agent(
        name="Task Generator",
        instructions=f'"""{prompt}"""',
    )


async def main():
    load_dotenv()  # Load variables from .env into the environment

    set_default_openai_key(os.environ["OPENAI_API_KEY"])

    with open("prompts/agent_prompt.txt", "r") as file:
        prompt = file.read()

    task_generator = get_task_generator(prompt)

    user_goals = [
        "I want a 1200 calorie meal from chick-fil-a. I have no dietary restrictions.",
        "I want a 1200 calorie meal from chick-fil-a. I cannot have gluten.",
        "I want a 1200 calorie meal from Mcdonald's. I cannot have pork.",
    ]
    for user_goal in user_goals:
        await run_nutrition_agent(task_generator, user_goal)


if __name__ == "__main__":
    asyncio.run(main())
