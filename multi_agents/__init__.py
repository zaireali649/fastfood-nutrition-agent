"""
Multi-Agent System for Fast Food Nutrition.

This package implements a sequential pipeline pattern with specialized agents:
- Coordinator: Orchestrates the workflow and handles errors
- Nutritionist: Analyzes dietary requirements and health impacts
- Restaurant: Recommends specific menu items and customizations
- Profile Manager: Learns user preferences and provides personalized insights
"""

from .coordinator import run_multi_agent_workflow
from .nutritionist_agent import NutritionistAgent
from .restaurant_agent import RestaurantAgent
from .profile_manager_agent import ProfileManagerAgent

__all__ = [
    "run_multi_agent_workflow",
    "NutritionistAgent",
    "RestaurantAgent",
    "ProfileManagerAgent",
]

