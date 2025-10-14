"""
Nutritionist Agent - Specialized agent for dietary analysis and macro-nutrient planning.
"""

from typing import Dict, Optional
from agents import Agent, Runner


class NutritionistAgent:
    """
    Specialized agent that analyzes dietary requirements and provides
    nutritional guidance based on user goals and history.
    """

    def __init__(self, prompt: str):
        """
        Initialize the Nutritionist Agent.

        Args:
            prompt: System prompt for the nutritionist agent
        """
        self.agent = Agent(
            name="Nutritionist Agent",
            instructions=f'"""{prompt}"""',
        )

    async def analyze_request(
        self, user_goal: str, user_profile: Optional[Dict] = None, profile_insights: Optional[str] = None
    ) -> str:
        """
        Analyze a nutrition request and provide dietary guidance.

        Args:
            user_goal: User's meal request
            user_profile: Optional user profile with history and preferences
            profile_insights: Optional insights from Profile Manager Agent

        Returns:
            Nutritional analysis and recommendations
        """
        # Build context-aware request
        analysis_request = self._build_analysis_request(user_goal, user_profile, profile_insights)

        # Run the agent
        result = await Runner.run(self.agent, analysis_request)
        return result.final_output

    def _build_analysis_request(
        self, user_goal: str, user_profile: Optional[Dict] = None, profile_insights: Optional[str] = None
    ) -> str:
        """
        Build a context-aware analysis request.

        Args:
            user_goal: User's meal request
            user_profile: Optional user profile
            profile_insights: Optional insights from Profile Manager

        Returns:
            Formatted request with context
        """
        request = f"## User Request\n{user_goal}\n\n"

        if profile_insights:
            request += f"## Profile Insights\n{profile_insights}\n\n"

        if user_profile:
            request += self._add_profile_context(user_profile)

        request += "\nProvide a detailed nutritional analysis for this request."
        return request

    def _add_profile_context(self, user_profile: Dict) -> str:
        """
        Add user profile context to the request.

        Args:
            user_profile: User profile dictionary

        Returns:
            Formatted context string
        """
        context = "## User Profile Context\n"

        prefs = user_profile.get("user_preferences", {})
        stats = user_profile.get("stats", {})

        if prefs.get("dietary_restrictions"):
            context += f"**Known Restrictions**: {', '.join(prefs['dietary_restrictions'])}\n"

        if prefs.get("disliked_items"):
            context += f"**Dislikes**: {', '.join(prefs['disliked_items'])}\n"

        if stats.get("total_meals_tracked", 0) > 0:
            context += f"**Total Meals Tracked**: {stats['total_meals_tracked']}\n"
            context += f"**Average Meal Calories**: {stats.get('avg_daily_calories', 'N/A')} cal\n"

            if stats.get("avg_meal_rating"):
                context += f"**Average Rating**: {stats['avg_meal_rating']}/5 ⭐\n"

        # Add today's meals context
        from memory.user_profile import get_todays_meals

        todays_meals = get_todays_meals(user_profile)
        if todays_meals:
            total_today = sum(m.get("calories", 0) for m in todays_meals)
            context += f"\n**⚠️ Today's Intake**: {len(todays_meals)} meal(s), {total_today} calories already logged\n"

        # Add recent meal patterns
        meal_history = user_profile.get("meal_history", [])
        if meal_history:
            recent = meal_history[-5:]
            highly_rated = [m for m in recent if m.get("rating", 0) >= 4]
            if highly_rated:
                context += f"\n**Recent Favorites** (4+ stars):\n"
                for meal in highly_rated:
                    context += f"- {meal.get('restaurant', 'Unknown')}, {meal.get('calories', 'N/A')} cal, {meal.get('rating', 0)}⭐\n"

        return context

