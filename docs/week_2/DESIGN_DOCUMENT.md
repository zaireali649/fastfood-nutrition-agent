# Context-Aware Fast Food Nutrition Assistant - Design

## Purpose: Research Domain
**Personalized Nutrition Intelligence for Fast-Food Consumers**

An AI assistant that recommends high-protein, low-sodium meals from fast-food restaurants based on user dietary needs, preferences, and historical eating patterns.

## Tools: External Data Integration
**USDA FoodData Central API** (`tools/usda_api.py`)
- Verifies nutritional claims from restaurants
- Compares fast-food items with whole-food alternatives  
- Provides authoritative macro/micronutrient data

## Memory: Multi-Layer Enhancement System

**Layer 1 - Session State**: Current conversation context  
**Layer 2 - User Profile**: Dietary restrictions, preferences, favorite restaurants (JSON storage)  
**Layer 3 - Meal History**: Last 30 meals with ratings, automatic statistics calculation

**Performance Enhancement**:
- Without memory: Generic recommendations
- With memory: "You gave Chick-fil-A 5 stars twice. Here are similar grilled options at McDonald's..."

The agent receives enriched prompts with user context (restrictions, past meals, ratings) enabling personalized recommendations that improve over time based on user feedback.
