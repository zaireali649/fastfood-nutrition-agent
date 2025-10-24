"""
Tests for user profile management.
"""

import pytest
import json
from pathlib import Path
from memory.user_profile import (
    create_default_profile,
    add_meal_to_history,
    update_statistics,
    get_recent_meals,
    get_profile_summary,
)


class TestProfileManagement:
    """Test profile management functions."""
    
    def test_create_default_profile(self):
        """Test creating a default profile."""
        profile = create_default_profile()
        
        assert "user_preferences" in profile
        assert "meal_history" in profile
        assert "stats" in profile
        assert profile["user_preferences"]["default_calorie_target"] == 1200
        assert isinstance(profile["meal_history"], list)
        assert len(profile["meal_history"]) == 0
    
    def test_add_meal_to_history(self, sample_profile, sample_meal):
        """Test adding a meal to history."""
        updated_profile = add_meal_to_history(sample_profile, sample_meal)
        
        assert len(updated_profile["meal_history"]) == 2
        assert updated_profile["meal_history"][-1]["restaurant"] == "McDonald's"
        assert updated_profile["stats"]["total_meals_tracked"] == 2
    
    def test_add_meal_history_limit(self, sample_profile):
        """Test meal history is limited to 30 entries."""
        # Add 35 meals
        for i in range(35):
            meal = {
                "restaurant": f"Restaurant {i}",
                "calories": 1000,
                "rating": 4,
            }
            sample_profile = add_meal_to_history(sample_profile, meal)
        
        # Should only keep last 30
        assert len(sample_profile["meal_history"]) == 30
    
    def test_update_statistics(self, sample_profile):
        """Test statistics update."""
        # Add another meal
        sample_profile["meal_history"].append({
            "restaurant": "Subway",
            "calories": 800,
            "rating": 5,
        })
        
        updated_profile = update_statistics(sample_profile)
        
        assert updated_profile["stats"]["total_meals_tracked"] == 2
        assert updated_profile["stats"]["avg_daily_calories"] == 1000.0  # (1200 + 800) / 2
        assert updated_profile["stats"]["most_visited_restaurant"] == "Subway"
    
    def test_get_recent_meals(self, sample_profile):
        """Test getting recent meals."""
        recent = get_recent_meals(sample_profile, count=5)
        
        assert len(recent) == 1
        assert recent[0]["restaurant"] == "Subway"
    
    def test_get_profile_summary(self, sample_profile):
        """Test profile summary generation."""
        summary = get_profile_summary(sample_profile)
        
        assert "Profile Summary" in summary
        assert "1200 cal" in summary
        assert "vegetarian" in summary
        assert "Subway" in summary
    
    def test_profile_with_no_meals(self):
        """Test profile operations with no meal history."""
        profile = create_default_profile()
        
        recent = get_recent_meals(profile, count=10)
        assert len(recent) == 0
        
        summary = get_profile_summary(profile)
        assert "0" in summary or "None" in summary

