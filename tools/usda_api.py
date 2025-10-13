"""
USDA FoodData Central API Integration.

This module provides functions to search and retrieve nutritional information
from the USDA FoodData Central database for verification and comparison.
"""

import requests
from typing import Dict, List, Optional


# USDA FoodData Central API endpoint
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"


def search_usda_food(query: str, page_size: int = 5) -> List[Dict]:
    """
    Search USDA FoodData Central database for food items.

    Args:
        query: Food name or description to search for
        page_size: Number of results to return (default: 5)

    Returns:
        List of food items with nutritional information
    """
    try:
        # Note: Using the public endpoint without API key has rate limits
        # For production, get a free API key from https://fdc.nal.usda.gov/api-key-signup.html
        url = f"{USDA_API_URL}/foods/search"
        params = {
            "query": query,
            "pageSize": page_size,
            "dataType": ["Survey (FNDDS)", "Branded"],  # Focus on common foods
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            foods = data.get("foods", [])

            # Simplify the response structure
            simplified_foods = []
            for food in foods:
                food_item = {
                    "description": food.get("description", "Unknown"),
                    "brand": food.get("brandOwner", "Generic"),
                    "calories": None,
                    "protein": None,
                    "sodium": None,
                    "carbs": None,
                    "fat": None,
                }

                # Extract key nutrients
                nutrients = food.get("foodNutrients", [])
                for nutrient in nutrients:
                    nutrient_name = nutrient.get("nutrientName", "")
                    nutrient_value = nutrient.get("value", 0)

                    if "Energy" in nutrient_name and "kcal" in nutrient_name:
                        food_item["calories"] = round(nutrient_value, 1)
                    elif "Protein" in nutrient_name:
                        food_item["protein"] = round(nutrient_value, 1)
                    elif "Sodium" in nutrient_name:
                        food_item["sodium"] = round(nutrient_value, 1)
                    elif "Carbohydrate" in nutrient_name:
                        food_item["carbs"] = round(nutrient_value, 1)
                    elif "Total lipid (fat)" in nutrient_name or "Fat" in nutrient_name:
                        food_item["fat"] = round(nutrient_value, 1)

                simplified_foods.append(food_item)

            return simplified_foods
        else:
            return []

    except Exception as e:
        print(f"Error searching USDA database: {e}")
        return []


def get_nutritional_comparison(item1: str, item2: str) -> str:
    """
    Compare nutritional profiles of two food items.

    Args:
        item1: First food item name
        item2: Second food item name

    Returns:
        Formatted comparison string
    """
    # Search for both items
    results1 = search_usda_food(item1, page_size=1)
    results2 = search_usda_food(item2, page_size=1)

    if not results1 or not results2:
        return "Could not retrieve nutritional data for comparison."

    food1 = results1[0]
    food2 = results2[0]

    comparison = f"""
### Nutritional Comparison

**{food1['description']}** vs **{food2['description']}**

| Nutrient | {food1['description'][:20]} | {food2['description'][:20]} | Difference |
|----------|---------|---------|------------|
| Calories | {food1['calories'] or 'N/A'} | {food2['calories'] or 'N/A'} | {_calc_diff(food1['calories'], food2['calories'])} |
| Protein (g) | {food1['protein'] or 'N/A'} | {food2['protein'] or 'N/A'} | {_calc_diff(food1['protein'], food2['protein'])} |
| Sodium (mg) | {food1['sodium'] or 'N/A'} | {food2['sodium'] or 'N/A'} | {_calc_diff(food1['sodium'], food2['sodium'])} |
| Carbs (g) | {food1['carbs'] or 'N/A'} | {food2['carbs'] or 'N/A'} | {_calc_diff(food1['carbs'], food2['carbs'])} |
| Fat (g) | {food1['fat'] or 'N/A'} | {food2['fat'] or 'N/A'} | {_calc_diff(food1['fat'], food2['fat'])} |

*Source: USDA FoodData Central*
"""
    return comparison


def _calc_diff(val1: Optional[float], val2: Optional[float]) -> str:
    """Calculate and format the difference between two values."""
    if val1 is None or val2 is None:
        return "N/A"

    diff = val1 - val2
    if diff > 0:
        return f"+{diff:.1f}"
    else:
        return f"{diff:.1f}"


def verify_nutrition_claim(food_name: str, claimed_calories: int) -> str:
    """
    Verify nutritional claims against USDA database.

    Args:
        food_name: Name of the food item
        claimed_calories: Claimed calorie count

    Returns:
        Verification message
    """
    results = search_usda_food(food_name, page_size=3)

    if not results:
        return f"Could not verify nutrition data for '{food_name}' in USDA database."

    # Show top results
    verification = f"### USDA Verification for '{food_name}'\n\n"
    verification += f"**Claimed calories:** {claimed_calories}\n\n"
    verification += "**USDA Database Results:**\n\n"

    for i, food in enumerate(results, 1):
        calories = food.get("calories")
        if calories:
            diff = abs(calories - claimed_calories)
            match_status = "✓ Close match" if diff < 50 else "⚠ Different"
            verification += (
                f"{i}. {food['description']}: {calories} cal - {match_status}\n"
            )
        else:
            verification += f"{i}. {food['description']}: No calorie data\n"

    return verification

