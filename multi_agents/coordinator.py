"""
Coordinator Agent - Orchestrates multi-agent workflow and handles errors.

Implements a sequential pipeline pattern where:
1. User request is analyzed by the Nutritionist Agent
2. Restaurant recommendations are generated based on nutritional guidance
3. Results are combined into a unified response
"""

import asyncio
from typing import Dict, Optional, Tuple
from agents import Agent, Runner

from .nutritionist_agent import NutritionistAgent
from .restaurant_agent import RestaurantAgent
from .profile_manager_agent import ProfileManagerAgent


class CoordinatorAgent:
    """
    Coordinator that orchestrates the multi-agent workflow.
    Implements error handling and fallback strategies.
    """

    def __init__(
        self,
        coordinator_prompt: str,
        nutritionist_prompt: str,
        restaurant_prompt: str,
        profile_manager_prompt: str,
    ):
        """
        Initialize the Coordinator with all agent prompts.

        Args:
            coordinator_prompt: Prompt for the coordinator
            nutritionist_prompt: Prompt for the nutritionist agent
            restaurant_prompt: Prompt for the restaurant agent
            profile_manager_prompt: Prompt for the profile manager agent
        """
        self.coordinator = Agent(
            name="Coordinator Agent",
            instructions=f'"""{coordinator_prompt}"""',
        )
        self.nutritionist = NutritionistAgent(nutritionist_prompt)
        self.restaurant = RestaurantAgent(restaurant_prompt)
        self.profile_manager = ProfileManagerAgent(profile_manager_prompt)

    async def process_request(
        self, user_goal: str, user_profile: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """
        Process a user request through the multi-agent pipeline.

        Args:
            user_goal: User's meal request
            user_profile: Optional user profile for context

        Returns:
            Tuple of (final_response, session_context)
        """
        session_context = {
            "user_goal": user_goal,
            "agents_used": [],
            "errors": [],
            "fallback_triggered": False,
        }

        try:
            # Step 1: Get profile insights (if user has sufficient history)
            profile_insights = None
            if user_profile and user_profile.get("stats", {}).get("total_meals_tracked", 0) >= 3:
                profile_insights = await self._get_profile_insights(
                    user_profile, session_context
                )

            # Step 2: Get nutritional analysis
            nutritional_analysis = await self._get_nutritional_analysis(
                user_goal, user_profile, profile_insights, session_context
            )

            # Step 3: Get restaurant recommendations
            restaurant_recommendations = await self._get_restaurant_recommendations(
                user_goal, nutritional_analysis, user_profile, profile_insights, session_context
            )

            # Step 4: Combine results through coordinator
            final_response = await self._coordinate_response(
                user_goal,
                nutritional_analysis,
                restaurant_recommendations,
                profile_insights,
                user_profile,
                session_context,
            )

            return final_response, session_context

        except Exception as e:
            # Fallback strategy: use single agent approach
            session_context["errors"].append(str(e))
            session_context["fallback_triggered"] = True

            fallback_response = await self._fallback_single_agent(
                user_goal, user_profile
            )
            return fallback_response, session_context

    async def _get_profile_insights(
        self, user_profile: Dict, session_context: Dict
    ) -> str:
        """
        Get profile insights from the Profile Manager Agent.

        Args:
            user_profile: User profile
            session_context: Session context for tracking

        Returns:
            Profile insights summary
        """
        try:
            insights = await asyncio.wait_for(
                self.profile_manager.analyze_profile(user_profile), timeout=45.0
            )
            session_context["agents_used"].append("Profile Manager Agent")
            return insights
        except asyncio.TimeoutError:
            session_context["errors"].append("Profile Manager Agent timeout")
            return "Profile insights unavailable due to timeout."
        except Exception as e:
            session_context["errors"].append(f"Profile Manager Agent error: {str(e)}")
            return f"Profile insights unavailable: {str(e)}"

    async def _get_nutritional_analysis(
        self, user_goal: str, user_profile: Optional[Dict], profile_insights: Optional[str], session_context: Dict
    ) -> str:
        """
        Get nutritional analysis from the Nutritionist Agent.

        Args:
            user_goal: User's meal request
            user_profile: Optional user profile
            session_context: Session context for tracking

        Returns:
            Nutritional analysis
        """
        try:
            # Pass profile insights to nutritionist if available
            analysis = await asyncio.wait_for(
                self.nutritionist.analyze_request(user_goal, user_profile, profile_insights), timeout=45.0
            )
            session_context["agents_used"].append("Nutritionist Agent")
            return analysis
        except asyncio.TimeoutError:
            session_context["errors"].append("Nutritionist Agent timeout")
            return "Nutritional analysis unavailable due to timeout."
        except Exception as e:
            session_context["errors"].append(f"Nutritionist Agent error: {str(e)}")
            return f"Nutritional analysis unavailable: {str(e)}"

    async def _get_restaurant_recommendations(
        self,
        user_goal: str,
        nutritional_analysis: str,
        user_profile: Optional[Dict],
        profile_insights: Optional[str],
        session_context: Dict,
    ) -> str:
        """
        Get restaurant recommendations from the Restaurant Agent.

        Args:
            user_goal: User's meal request
            nutritional_analysis: Analysis from nutritionist
            user_profile: Optional user profile
            session_context: Session context for tracking

        Returns:
            Restaurant recommendations
        """
        try:
            # Pass profile insights to restaurant agent if available
            recommendations = await asyncio.wait_for(
                self.restaurant.get_recommendations(
                    user_goal, nutritional_analysis, user_profile, profile_insights
                ),
                timeout=45.0,
            )
            session_context["agents_used"].append("Restaurant Agent")
            return recommendations
        except asyncio.TimeoutError:
            session_context["errors"].append("Restaurant Agent timeout")
            return "Restaurant recommendations unavailable due to timeout."
        except Exception as e:
            session_context["errors"].append(f"Restaurant Agent error: {str(e)}")
            return f"Restaurant recommendations unavailable: {str(e)}"

    async def _coordinate_response(
        self,
        user_goal: str,
        nutritional_analysis: str,
        restaurant_recommendations: str,
        profile_insights: Optional[str],
        user_profile: Optional[Dict],
        session_context: Dict,
    ) -> str:
        """
        Coordinate and combine agent outputs into a unified response.

        Args:
            user_goal: User's meal request
            nutritional_analysis: Analysis from nutritionist
            restaurant_recommendations: Recommendations from restaurant agent
            user_profile: Optional user profile
            session_context: Session context for tracking

        Returns:
            Final coordinated response
        """
        try:
            # Build coordination request
            coordination_request = f"""
## Original User Request
{user_goal}
"""
            
            if profile_insights:
                coordination_request += f"""
## Profile Insights (from Profile Manager Agent)
{profile_insights}
"""

            coordination_request += f"""
## Nutritional Analysis (from Nutritionist Agent)
{nutritional_analysis}

## Restaurant Recommendations (from Restaurant Agent)
{restaurant_recommendations}
"""

            if user_profile:
                coordination_request += f"\n## User Context Available\n"
                prefs = user_profile.get("user_preferences", {})
                stats = user_profile.get("stats", {})
                if stats.get("total_meals_tracked", 0) > 0:
                    coordination_request += f"- User has tracked {stats['total_meals_tracked']} meals\n"
                    coordination_request += f"- Average rating: {stats.get('avg_meal_rating', 'N/A')}/5\n"

            coordination_request += """

Please combine these analyses into a cohesive, user-friendly response. Include:
1. A brief acknowledgment of their request and context (reference profile insights if available)
2. The nutritional guidance
3. The specific restaurant recommendations
4. Any final tips or encouragement based on their preferences
"""

            result = await asyncio.wait_for(
                Runner.run(self.coordinator, coordination_request), timeout=45.0
            )

            session_context["agents_used"].append("Coordinator Agent")
            return result.final_output

        except Exception as e:
            # If coordination fails, return combined output directly
            session_context["errors"].append(f"Coordinator error: {str(e)}")
            combined = f"{nutritional_analysis}\n\n---\n\n{restaurant_recommendations}"
            if profile_insights:
                combined = f"## Your Preferences\n{profile_insights}\n\n---\n\n{combined}"
            return combined

    async def _fallback_single_agent(
        self, user_goal: str, user_profile: Optional[Dict]
    ) -> str:
        """
        Fallback to single-agent mode if multi-agent workflow fails.

        Args:
            user_goal: User's meal request
            user_profile: Optional user profile

        Returns:
            Response from fallback agent
        """
        try:
            # Use the original single-agent approach
            from agent import run_nutrition_agent, get_task_generator

            with open("prompts/agent_prompt.txt", "r") as f:
                prompt = f.read()

            task_generator = get_task_generator(prompt)
            response = await run_nutrition_agent(task_generator, user_goal, user_profile)

            return f"""
⚠️ *Using simplified single-agent mode due to technical issues*

{response}
"""
        except Exception as e:
            return f"""
❌ An error occurred while processing your request.

**Error Details**: {str(e)}

Please try again or contact support if the issue persists.
"""


async def run_multi_agent_workflow(
    user_goal: str, user_profile: Optional[Dict] = None
) -> Tuple[str, Dict]:
    """
    Main entry point for the multi-agent workflow.

    Args:
        user_goal: User's meal request
        user_profile: Optional user profile for context

    Returns:
        Tuple of (final_response, session_context)
    """
    # Load prompts
    with open("prompts/coordinator_prompt.txt", "r") as f:
        coordinator_prompt = f.read()

    with open("prompts/nutritionist_agent_prompt.txt", "r") as f:
        nutritionist_prompt = f.read()

    with open("prompts/restaurant_agent_prompt.txt", "r") as f:
        restaurant_prompt = f.read()

    with open("prompts/profile_manager_prompt.txt", "r") as f:
        profile_manager_prompt = f.read()

    # Create coordinator and process request
    coordinator = CoordinatorAgent(
        coordinator_prompt, nutritionist_prompt, restaurant_prompt, profile_manager_prompt
    )

    return await coordinator.process_request(user_goal, user_profile)

