"""
Profile Manager Agent - Specialized agent for user preference learning and personalization.
"""

from typing import Dict, Optional
from agents import Agent, Runner


class ProfileManagerAgent:
    """
    Specialized agent that analyzes user behavior patterns and provides
    personalized insights to improve recommendations over time.
    """

    def __init__(self, prompt: str):
        """
        Initialize the Profile Manager Agent.

        Args:
            prompt: System prompt for the profile manager agent
        """
        self.agent = Agent(
            name="Profile Manager Agent",
            instructions=f'"""{prompt}"""',
        )

    async def analyze_profile(self, user_profile: Optional[Dict] = None) -> str:
        """
        Analyze user profile and provide personalized insights.

        Args:
            user_profile: User profile with history and preferences

        Returns:
            Profile insights and recommendations
        """
        if not user_profile:
            return "No profile data available. Create a profile to get personalized insights."

        # Build analysis request
        analysis_request = self._build_analysis_request(user_profile)

        # Run the agent
        result = await Runner.run(self.agent, analysis_request)
        return result.final_output

    def _build_analysis_request(self, user_profile: Dict) -> str:
        """
        Build a profile analysis request with user data.

        Args:
            user_profile: User profile dictionary

        Returns:
            Formatted analysis request
        """
        request = "## User Profile Data\n\n"

        # Add preferences
        prefs = user_profile.get("user_preferences", {})
        request += "### Current Preferences\n"
        request += f"- Default calorie target: {prefs.get('default_calorie_target', 'Not set')}\n"
        request += f"- Dietary restrictions: {', '.join(prefs.get('dietary_restrictions', [])) or 'None'}\n"
        request += f"- Favorite restaurants: {', '.join(prefs.get('favorite_restaurants', [])) or 'None yet'}\n"
        request += f"- Disliked items: {', '.join(prefs.get('disliked_items', [])) or 'None specified'}\n"
        request += f"- Preferred cooking: {', '.join(prefs.get('preferred_cooking_methods', [])) or 'Not specified'}\n\n"

        # Add statistics
        stats = user_profile.get("stats", {})
        request += "### Statistics\n"
        request += f"- Total meals tracked: {stats.get('total_meals_tracked', 0)}\n"
        request += f"- Average calories: {stats.get('avg_daily_calories', 'N/A')} cal\n"
        request += f"- Most visited: {stats.get('most_visited_restaurant', 'N/A')}\n"
        request += f"- Average rating: {stats.get('avg_meal_rating', 'N/A')}/5 stars\n\n"

        # Add detailed meal history
        meal_history = user_profile.get("meal_history", [])
        if meal_history:
            request += f"### Meal History ({len(meal_history)} meals)\n\n"

            # Group by rating
            by_rating = {5: [], 4: [], 3: [], 2: [], 1: []}
            for meal in meal_history:
                rating = meal.get("rating", 0)
                if rating in by_rating:
                    by_rating[rating].append(meal)

            # Show highly rated meals
            if by_rating[5] or by_rating[4]:
                request += "**High Ratings (4-5 stars):**\n"
                for meal in by_rating[5] + by_rating[4]:
                    request += f"- {meal.get('restaurant', 'Unknown')}, {meal.get('calories', 'N/A')} cal, {meal.get('rating', 0)}⭐\n"
                request += "\n"

            # Show poorly rated meals
            if by_rating[1] or by_rating[2]:
                request += "**Low Ratings (1-2 stars):**\n"
                for meal in by_rating[1] + by_rating[2]:
                    request += f"- {meal.get('restaurant', 'Unknown')}, {meal.get('calories', 'N/A')} cal, {meal.get('rating', 0)}⭐\n"
                request += "\n"

            # Show all meals chronologically for pattern detection
            request += "**Chronological History:**\n"
            for i, meal in enumerate(meal_history[-15:], 1):  # Last 15 meals
                request += f"{i}. {meal.get('restaurant', 'Unknown')}, {meal.get('calories', 'N/A')} cal, {meal.get('rating', 0)}⭐\n"
            request += "\n"

        else:
            request += "### Meal History\nNo meals logged yet.\n\n"

        request += """
## Task
Analyze this user's profile and meal history. Provide:
1. Detected preferences based on ratings and patterns
2. Assessment of recommendation accuracy
3. Specific suggestions for profile updates
4. Personalized tips for better meal choices

Be specific and reference actual data from their history.
"""

        return request

