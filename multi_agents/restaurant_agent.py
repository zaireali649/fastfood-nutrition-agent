"""
Restaurant Agent - Specialized agent for menu recommendations and customizations.
"""

from typing import Dict, Optional
from agents import Agent, Runner


class RestaurantAgent:
    """
    Specialized agent with deep knowledge of fast food menus and nutrition.
    Provides specific menu recommendations with customizations.
    """

    def __init__(self, prompt: str):
        """
        Initialize the Restaurant Agent.

        Args:
            prompt: System prompt for the restaurant agent
        """
        self.agent = Agent(
            name="Restaurant Expert Agent",
            instructions=f'"""{prompt}"""',
        )

    async def get_recommendations(
        self,
        user_goal: str,
        nutritional_analysis: str,
        user_profile: Optional[Dict] = None,
        profile_insights: Optional[str] = None,
    ) -> str:
        """
        Get specific restaurant recommendations based on nutritional guidance.

        Args:
            user_goal: User's meal request
            nutritional_analysis: Analysis from the nutritionist agent
            user_profile: Optional user profile with preferences
            profile_insights: Optional insights from Profile Manager Agent

        Returns:
            Restaurant-specific meal recommendations
        """
        # Build recommendation request
        rec_request = self._build_recommendation_request(
            user_goal, nutritional_analysis, user_profile, profile_insights
        )

        # Run the agent
        result = await Runner.run(self.agent, rec_request)
        return result.final_output

    def _build_recommendation_request(
        self,
        user_goal: str,
        nutritional_analysis: str,
        user_profile: Optional[Dict] = None,
        profile_insights: Optional[str] = None,
    ) -> str:
        """
        Build a context-aware recommendation request.

        Args:
            user_goal: User's meal request
            nutritional_analysis: Nutritional guidance
            user_profile: Optional user profile
            profile_insights: Optional insights from Profile Manager

        Returns:
            Formatted request with context
        """
        request = f"## User Request\n{user_goal}\n\n"
        
        if profile_insights:
            request += f"## Profile Insights (from Profile Manager)\n{profile_insights}\n\n"
        
        request += f"## Nutritional Guidance\n{nutritional_analysis}\n\n"

        if user_profile:
            request += self._add_preference_context(user_profile)

        request += "\nProvide 2-3 specific menu recommendations with exact items and nutritional breakdowns."
        return request

    def _add_preference_context(self, user_profile: Dict) -> str:
        """
        Add user preferences and favorites to the request.

        Args:
            user_profile: User profile dictionary

        Returns:
            Formatted context string
        """
        context = "## User Preferences\n"

        prefs = user_profile.get("user_preferences", {})

        if prefs.get("favorite_restaurants"):
            context += f"**Favorite Restaurants**: {', '.join(prefs['favorite_restaurants'][:5])}\n"

        if prefs.get("preferred_cooking_methods"):
            context += f"**Preferred Cooking**: {', '.join(prefs['preferred_cooking_methods'])}\n"

        if prefs.get("disliked_items"):
            context += f"**⚠️ AVOID THESE**: {', '.join(prefs['disliked_items'])}\n"

        # Add meal history for pattern recognition
        meal_history = user_profile.get("meal_history", [])
        if meal_history:
            recent = meal_history[-10:]

            # Find highly rated items
            highly_rated = [m for m in recent if m.get("rating", 0) >= 4]
            if highly_rated:
                context += f"\n**User's Highly Rated Meals** (reference these for similar suggestions):\n"
                for meal in highly_rated[-3:]:  # Last 3 highly rated
                    context += f"- {meal.get('restaurant', 'Unknown')}: {meal.get('rating', 0)}⭐ ({meal.get('calories', 'N/A')} cal)\n"

            # Find poorly rated items to avoid
            poorly_rated = [m for m in recent if m.get("rating", 0) <= 2]
            if poorly_rated:
                context += f"\n**⚠️ User Did Not Enjoy** (avoid similar items):\n"
                for meal in poorly_rated[-2:]:
                    context += f"- {meal.get('restaurant', 'Unknown')}: {meal.get('rating', 0)}⭐\n"

        return context

