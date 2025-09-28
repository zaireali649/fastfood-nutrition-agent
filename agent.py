import os
from agents import Agent, Runner
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env into the environment

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

with open('agent_prompt.txt', 'r') as file:
    prompt = file.read()
    
task_generator = Agent(
    name="Task Generator",
    instructions=f'"""{prompt}"""',
)

async def generate_tasks(goal):
    result = await Runner.run(task_generator, goal)
    return result.final_output

async def main():
    user_goal = "I want a 1200 calorie meal from chick-fil-a. I have no dietary restrictions."
    user_goal = "I want a 1200 calorie meal from chick-fil-a. I cannot have gluten."
    user_goal = "I want a 1200 calorie meal from Mcdonald's. I cannot have pork."
    tasks = await generate_tasks(user_goal)
    print(tasks)

if __name__ == "__main__":
    asyncio.run(main())