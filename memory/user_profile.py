"""
User Profile Management System.

This module handles loading, saving, and managing user profiles including
preferences, meal history, and statistics.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Directory to store user profiles
PROFILES_DIR = Path("data/profiles")


def ensure_profiles_directory() -> None:
    """Create the profiles directory if it doesn't exist."""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def create_default_profile() -> Dict:
    """
    Create a default user profile structure.

    Returns:
        Dictionary containing default profile data
    """
    return {
        "user_preferences": {
            "default_calorie_target": 1200,
            "dietary_restrictions": [],
            "favorite_restaurants": [],
            "disliked_items": [],
            "preferred_cooking_methods": [],
        },
        "meal_history": [],
        "stats": {
            "total_meals_tracked": 0,
            "avg_daily_calories": 0,
            "most_visited_restaurant": None,
            "profile_created": datetime.now().isoformat(),
        },
    }


def save_profile(profile_name: str, profile_data: Dict) -> bool:
    """
    Save a user profile to disk.

    Args:
        profile_name: Name of the profile to save
        profile_data: Profile data dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_profiles_directory()
        file_path = PROFILES_DIR / f"{profile_name}.json"

        with open(file_path, "w") as f:
            json.dump(profile_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False


def load_profile(profile_name: str) -> Optional[Dict]:
    """
    Load a user profile from disk.

    Args:
        profile_name: Name of the profile to load

    Returns:
        Profile data dictionary or None if not found
    """
    try:
        file_path = PROFILES_DIR / f"{profile_name}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None


def list_profiles() -> List[str]:
    """
    List all available user profiles.

    Returns:
        List of profile names
    """
    try:
        ensure_profiles_directory()
        profile_files = PROFILES_DIR.glob("*.json")
        return [f.stem for f in profile_files]
    except Exception as e:
        print(f"Error listing profiles: {e}")
        return []


def add_meal_to_history(profile_data: Dict, meal_data: Dict) -> Dict:
    """
    Add a meal to the user's meal history.

    Args:
        profile_data: User profile dictionary
        meal_data: Meal information to add

    Returns:
        Updated profile data
    """
    # Add timestamp if not present
    if "timestamp" not in meal_data:
        meal_data["timestamp"] = datetime.now().isoformat()

    # Add to history
    profile_data["meal_history"].append(meal_data)

    # Keep only last 30 meals
    if len(profile_data["meal_history"]) > 30:
        profile_data["meal_history"] = profile_data["meal_history"][-30:]

    # Update statistics
    profile_data = update_statistics(profile_data)

    return profile_data


def update_statistics(profile_data: Dict) -> Dict:
    """
    Update profile statistics based on meal history.

    Args:
        profile_data: User profile dictionary

    Returns:
        Updated profile data with recalculated stats
    """
    meals = profile_data["meal_history"]

    if not meals:
        return profile_data

    stats = profile_data["stats"]
    stats["total_meals_tracked"] = len(meals)

    # Calculate average calories
    total_calories = sum(meal.get("calories", 0) for meal in meals)
    stats["avg_daily_calories"] = round(total_calories / len(meals), 1)

    # Find most visited restaurant
    restaurants = [meal.get("restaurant") for meal in meals if meal.get("restaurant")]
    if restaurants:
        stats["most_visited_restaurant"] = max(
            set(restaurants), key=restaurants.count
        )

    # Calculate average rating
    ratings = [meal.get("rating") for meal in meals if meal.get("rating")]
    if ratings:
        stats["avg_meal_rating"] = round(sum(ratings) / len(ratings), 1)

    return profile_data


def get_todays_meals(profile_data: Dict) -> List[Dict]:
    """
    Get meals logged today.

    Args:
        profile_data: User profile dictionary

    Returns:
        List of today's meals
    """
    today = datetime.now().date()
    todays_meals = []

    for meal in profile_data["meal_history"]:
        meal_date_str = meal.get("timestamp", "")
        if meal_date_str:
            try:
                meal_date = datetime.fromisoformat(meal_date_str).date()
                if meal_date == today:
                    todays_meals.append(meal)
            except ValueError:
                continue

    return todays_meals


def get_recent_meals(profile_data: Dict, count: int = 10) -> List[Dict]:
    """
    Get the most recent meals.

    Args:
        profile_data: User profile dictionary
        count: Number of recent meals to return

    Returns:
        List of recent meals
    """
    meals = profile_data["meal_history"]
    return meals[-count:] if len(meals) > count else meals


def get_profile_summary(profile_data: Dict) -> str:
    """
    Generate a human-readable summary of the user profile.

    Args:
        profile_data: User profile dictionary

    Returns:
        Formatted summary string
    """
    prefs = profile_data["user_preferences"]
    stats = profile_data["stats"]

    summary = f"""
**Profile Summary:**
- Default calorie target: {prefs['default_calorie_target']} cal
- Dietary restrictions: {', '.join(prefs['dietary_restrictions']) if prefs['dietary_restrictions'] else 'None'}
- Favorite restaurants: {', '.join(prefs['favorite_restaurants'][:3]) if prefs['favorite_restaurants'] else 'None yet'}
- Total meals tracked: {stats['total_meals_tracked']}
- Average calories per meal: {stats['avg_daily_calories']} cal
- Average meal rating: {stats.get('avg_meal_rating', 'N/A')} ⭐
- Most visited: {stats.get('most_visited_restaurant', 'N/A')}
"""
    return summary.strip()


def export_meal_history_csv(profile_data: Dict, output_file: str) -> bool:
    """
    Export meal history to CSV format.

    Args:
        profile_data: User profile dictionary
        output_file: Output CSV file path

    Returns:
        True if successful, False otherwise
    """
    try:
        import csv

        meals = profile_data["meal_history"]

        if not meals:
            return False

        with open(output_file, "w", newline="") as f:
            fieldnames = [
                "timestamp",
                "restaurant",
                "calories",
                "protein",
                "sodium",
                "rating",
                "notes",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for meal in meals:
                writer.writerow(
                    {
                        "timestamp": meal.get("timestamp", ""),
                        "restaurant": meal.get("restaurant", ""),
                        "calories": meal.get("calories", ""),
                        "protein": meal.get("protein", ""),
                        "sodium": meal.get("sodium", ""),
                        "rating": meal.get("rating", ""),
                        "notes": meal.get("notes", ""),
                    }
                )

        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

