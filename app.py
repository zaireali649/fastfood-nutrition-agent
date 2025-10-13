"""
Fast Food Nutrition Agent Streamlit Application.

This module provides a web interface for the Fast Food Nutrition Agent,
allowing users to input their dietary preferences and receive personalized
meal recommendations from fast food restaurants.

The application uses Streamlit for the user interface and integrates with
the OpenAI agents library to generate nutrition-focused meal suggestions
based on user requirements including calorie limits, dietary restrictions,
and restaurant preferences.
"""

import asyncio
import os
from typing import Dict, List, Optional

import streamlit as st
from agents import set_default_openai_key
from dotenv import load_dotenv

from agent import get_task_generator, run_nutrition_agent
from memory.user_profile import (
    add_meal_to_history,
    create_default_profile,
    get_profile_summary,
    get_recent_meals,
    list_profiles,
    load_profile,
    save_profile,
)


def format_user_goal(
    restaurant: str,
    calories: int,
    dietary_restrictions: List[str],
    additional_notes: str,
) -> str:
    """
    Format user inputs into a natural language goal for the nutrition agent.

    Args:
        restaurant: The name of the restaurant where the user wants to eat.
        calories: The target calorie count for the meal.
        dietary_restrictions: List of dietary restrictions or preferences.
        additional_notes: Any additional preferences or notes from the user.

    Returns:
        A formatted string representing the user's meal request.

    Raises:
        ValueError: If restaurant name is empty or invalid.
    """
    # Validate restaurant input
    if not restaurant.strip():
        raise ValueError("Restaurant name cannot be empty")

    # Format dietary restrictions into natural language
    if dietary_restrictions:
        if len(dietary_restrictions) == 1:
            restrictions_text = (
                f"I have dietary restrictions: {dietary_restrictions[0]}"
            )
        else:
            restrictions_text = (
                f"I have dietary restrictions: {', '.join(dietary_restrictions)}"
            )
    else:
        restrictions_text = "I have no dietary restrictions"

    # Build the main user goal
    user_goal = f"I want a {calories} calorie meal from {restaurant.lower()}. {restrictions_text}."

    # Add additional notes if provided
    if additional_notes.strip():
        user_goal += f" Additional preferences: {additional_notes.strip()}."

    return user_goal


def display_previous_recommendations() -> None:
    """
    Display previously generated recommendations from session state.

    Shows recommendations that were generated in previous interactions
    and provides an option to clear them.
    """
    if (
        hasattr(st.session_state, "show_recommendations")
        and st.session_state.show_recommendations
    ):
        st.markdown("---")
        st.header("🍽️ Your Previous Meal Recommendations")
        st.markdown(st.session_state.recommendations)
        st.code(st.session_state.recommendations, language="text")
        st.caption("💡 You can select and copy the text above")

        if st.button("🗑️ Clear Previous Recommendations"):
            st.session_state.show_recommendations = False
            st.session_state.recommendations = ""
            st.rerun()


def generate_meal_recommendations(
    user_goal: str, restaurant: str, calories: int, user_profile: Optional[Dict] = None
) -> None:
    """
    Generate meal recommendations using the nutrition agent.

    Args:
        user_goal: The formatted user request for meal recommendations.
        restaurant: Restaurant name for logging
        calories: Calorie count for logging
        user_profile: Optional user profile for context

    Raises:
        FileNotFoundError: If the agent prompt file is not found.
        Exception: For any other errors during recommendation generation.
    """
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "❌ OpenAI API key not found. Please set your OPENAI_API_KEY environment variable."
        )
        st.stop()

    # Show loading spinner during processing
    with st.spinner("🤖 Analyzing your request and finding the best meal options..."):
        try:
            # Read the nutritionist prompt from file
            with open("prompts/agent_prompt.txt", "r") as file:
                prompt: str = file.read()

            # Create the nutrition agent
            task_generator = get_task_generator(prompt, user_profile)

            # Run the nutrition agent and get results (with context)
            recommendations: str = asyncio.run(
                run_nutrition_agent(task_generator, user_goal, user_profile)
            )

            # Store recommendations in session state for persistence
            st.session_state.recommendations = recommendations
            st.session_state.show_recommendations = True
            st.session_state.last_restaurant = restaurant
            st.session_state.last_calories = calories
            st.session_state.meal_logged = False

            # Display success message
            st.success("✅ Meal recommendations generated!")

            # Create a nice display for the recommendations
            st.markdown("---")
            st.header("🍽️ Your Personalized Meal Recommendations")

            # Display the recommendations in formatted markdown
            st.markdown(recommendations)

            # Add copy functionality
            st.markdown("---")

            if st.button(
                "📋 Copy to Clipboard",
                help="Copy the recommendations to your clipboard",
            ):
                st.code(recommendations, language="text")
                st.success(
                    "📋 Recommendations displayed above - you can now select and copy the text!"
                )

        except FileNotFoundError:
            st.error(
                "❌ Could not find the agent prompt file. Please ensure 'prompts/agent_prompt.txt' exists."
            )
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")


# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key explicitly for the agents library
set_default_openai_key(os.environ["OPENAI_API_KEY"])

# Configure Streamlit page settings
st.set_page_config(
    page_title="Fast Food Nutrition Agent", page_icon="🍔", layout="wide"
)

# Initialize session state for profile
if "current_profile" not in st.session_state:
    st.session_state.current_profile = None
if "profile_name" not in st.session_state:
    st.session_state.profile_name = None

# Title and description
st.title("🍔 Fast Food Nutrition Agent")
st.markdown("""
Get personalized meal recommendations from fast food restaurants based on your dietary needs and calorie requirements.
""")

# Create sidebar for user input controls
st.sidebar.header("👤 Profile Management")

# Profile selection and management
available_profiles = list_profiles()

profile_action = st.sidebar.radio(
    "Profile Options:",
    ["Use Existing Profile", "Create New Profile", "No Profile (Guest)"],
)

if profile_action == "Use Existing Profile":
    if available_profiles:
        selected_profile = st.sidebar.selectbox(
            "Select Profile:", [""] + available_profiles
        )

        if selected_profile:
            if (
                st.session_state.profile_name != selected_profile
                or st.session_state.current_profile is None
            ):
                st.session_state.current_profile = load_profile(selected_profile)
                st.session_state.profile_name = selected_profile

            if st.session_state.current_profile:
                st.sidebar.success(f"✓ Loaded: {selected_profile}")
                with st.sidebar.expander("📊 Profile Stats"):
                    st.markdown(get_profile_summary(st.session_state.current_profile))
    else:
        st.sidebar.info("No profiles found. Create one below!")
        profile_action = "Create New Profile"

elif profile_action == "Create New Profile":
    new_profile_name = st.sidebar.text_input(
        "Profile Name:", placeholder="e.g., John, Work Diet, Keto Plan"
    )

    if st.sidebar.button("Create Profile"):
        if new_profile_name:
            new_profile = create_default_profile()
            if save_profile(new_profile_name, new_profile):
                st.session_state.current_profile = new_profile
                st.session_state.profile_name = new_profile_name
                st.sidebar.success(f"✓ Created profile: {new_profile_name}")
                st.rerun()
            else:
                st.sidebar.error("Failed to create profile")
        else:
            st.sidebar.warning("Please enter a profile name")

elif profile_action == "No Profile (Guest)":
    st.session_state.current_profile = None
    st.session_state.profile_name = None
    st.sidebar.info("Using guest mode (no memory)")

st.sidebar.markdown("---")
st.sidebar.header("📋 Your Meal Preferences")

# Restaurant selection with two options: preset list or custom input
restaurant_option: str = st.sidebar.radio(
    "Restaurant:", ["Select from list", "Enter custom restaurant"]
)

# Get restaurant name based on user's selection method
restaurant: str
default_restaurants = [
    "Chick-fil-A",
    "McDonald's",
    "Subway",
    "Taco Bell",
    "Burger King",
    "KFC",
    "Pizza Hut",
    "Domino's",
]

# Add favorite restaurants to the list if profile exists
if st.session_state.current_profile:
    fav_restaurants = st.session_state.current_profile["user_preferences"].get(
        "favorite_restaurants", []
    )
    # Combine favorites with defaults (favorites first)
    all_restaurants = fav_restaurants + [
        r for r in default_restaurants if r not in fav_restaurants
    ]
else:
    all_restaurants = default_restaurants

if restaurant_option == "Select from list":
    # Use predefined list of popular fast food chains
    restaurant = st.sidebar.selectbox("Choose a restaurant:", all_restaurants)
else:
    # Allow user to enter any restaurant name
    restaurant = st.sidebar.text_input(
        "Enter restaurant name:",
        placeholder="e.g., Five Guys, Chipotle, Panera Bread...",
    )

# Calorie target input with reasonable limits
# Use profile default if available
default_calories = 1200
if st.session_state.current_profile:
    default_calories = st.session_state.current_profile["user_preferences"].get(
        "default_calorie_target", 1200
    )

calories: int = st.sidebar.number_input(
    "Target calories:", min_value=300, max_value=2000, value=default_calories, step=50
)

# Dietary restrictions selection with two input methods
restrictions_option: str = st.sidebar.radio(
    "Dietary restrictions:", ["Select from list", "Enter custom restrictions"]
)

# Get dietary restrictions based on user's selection method
dietary_restrictions: List[str]

# Get defaults from profile if available
default_restrictions = []
if st.session_state.current_profile:
    default_restrictions = st.session_state.current_profile["user_preferences"].get(
        "dietary_restrictions", []
    )

if restrictions_option == "Select from list":
    # Use predefined list of common dietary restrictions
    restriction_options = [
        "No restrictions",
        "Gluten-free",
        "Dairy-free",
        "Vegetarian",
        "Vegan",
        "No pork",
        "No beef",
        "Low sodium",
        "Low carb",
        "Keto",
    ]
    
    # Filter defaults to only include values that exist in options (case-sensitive match)
    valid_defaults = [r for r in default_restrictions if r in restriction_options]
    
    dietary_restrictions = st.sidebar.multiselect(
        "Choose restrictions (if any):",
        restriction_options,
        default=valid_defaults,
    )
else:
    # Allow user to enter custom dietary restrictions
    default_custom = ", ".join(default_restrictions) if default_restrictions else ""
    custom_restrictions: str = st.sidebar.text_input(
        "Enter your dietary restrictions:",
        value=default_custom,
        placeholder="e.g., no nuts, halal, kosher, diabetic-friendly...",
    )
    dietary_restrictions = [custom_restrictions] if custom_restrictions else []

# Additional preferences and notes input
default_notes = ""
if st.session_state.current_profile:
    prefs = st.session_state.current_profile["user_preferences"]
    pref_methods = prefs.get("preferred_cooking_methods", [])
    dislikes = prefs.get("disliked_items", [])

    notes_parts = []
    if pref_methods:
        notes_parts.append(f"Prefer {', '.join(pref_methods)}")
    if dislikes:
        notes_parts.append(f"Dislike {', '.join(dislikes)}")
    default_notes = "; ".join(notes_parts)

additional_notes: str = st.sidebar.text_area(
    "Additional preferences or notes:",
    value=default_notes,
    placeholder="e.g., prefer grilled over fried, need extra protein, avoid spicy foods, want to maximize fiber, etc.",
    help="Be specific about your preferences. For example: 'I need extra protein for muscle building' or 'I prefer grilled options over fried'",
)

# Save preferences button
if st.session_state.current_profile and st.sidebar.button(
    "💾 Save Current Preferences to Profile"
):
    # Update profile with current preferences
    st.session_state.current_profile["user_preferences"][
        "default_calorie_target"
    ] = calories
    st.session_state.current_profile["user_preferences"][
        "dietary_restrictions"
    ] = dietary_restrictions

    # Add restaurant to favorites if not already there
    if (
        restaurant
        and restaurant
        not in st.session_state.current_profile["user_preferences"][
            "favorite_restaurants"
        ]
    ):
        st.session_state.current_profile["user_preferences"][
            "favorite_restaurants"
        ].append(restaurant)

    # Save to disk
    if save_profile(st.session_state.profile_name, st.session_state.current_profile):
        st.sidebar.success("✓ Preferences saved!")
    else:
        st.sidebar.error("Failed to save preferences")

# Create main content area with two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Your Meal Request")

    try:
        # Format user inputs into a natural language goal
        user_goal: str = format_user_goal(
            restaurant, calories, dietary_restrictions, additional_notes
        )

        # Display the formatted request to the user
        st.info(f"**Your request:** {user_goal}")

    except ValueError as e:
        # Handle validation errors (e.g., empty restaurant name)
        st.warning(f"⚠️ {str(e)}")
        st.stop()

    # Display meal history if profile exists
    if st.session_state.current_profile:
        recent_meals = get_recent_meals(st.session_state.current_profile, count=10)
        if recent_meals:
            with st.expander("📜 Recent Meal History (Last 10)", expanded=False):
                st.markdown("### Your Recent Orders")
                for i, meal in enumerate(reversed(recent_meals), 1):
                    rating_display = (
                        "⭐" * meal.get("rating", 0) if meal.get("rating") else "Not rated"
                    )
                    st.markdown(
                        f"**{i}.** {meal.get('restaurant', 'Unknown')} - "
                        f"{meal.get('calories', 'N/A')} cal - {rating_display}"
                    )
                    if meal.get("timestamp"):
                        from datetime import datetime
                        try:
                            dt = datetime.fromisoformat(meal["timestamp"])
                            st.caption(f"Date: {dt.strftime('%Y-%m-%d %H:%M')}")
                        except ValueError:
                            pass

    # Main action button to generate meal recommendations
    if st.button(
        "🍽️ Get Meal Recommendations", type="primary", use_container_width=True
    ):
        # Reset meal_logged flag when getting new recommendations
        st.session_state.meal_logged = False
        generate_meal_recommendations(
            user_goal, restaurant, calories, st.session_state.current_profile
        )

    # Display previous recommendations if they exist
    display_previous_recommendations()

    # Add meal logging section if recommendations exist and user has a profile
    if (
        st.session_state.get("show_recommendations")
        and st.session_state.current_profile
        and not st.session_state.get("meal_logged", False)
    ):
        st.markdown("---")
        st.subheader("📊 Log This Meal")
        st.markdown("Help improve future recommendations by rating this meal!")

        col_rate1, col_rate2 = st.columns(2)

        with col_rate1:
            meal_rating = st.select_slider(
                "How satisfied were you?",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="1 = Not satisfied, 5 = Very satisfied",
                key="meal_rating_slider"
            )

        with col_rate2:
            if st.button("💾 Log Meal to History", use_container_width=True):
                # Create meal entry
                meal_entry = {
                    "restaurant": st.session_state.get("last_restaurant", restaurant),
                    "calories": st.session_state.get("last_calories", calories),
                    "rating": meal_rating,
                }

                # Add to profile and update statistics
                updated_profile = add_meal_to_history(
                    st.session_state.current_profile, meal_entry
                )
                
                # Save to disk
                if save_profile(st.session_state.profile_name, updated_profile):
                    # Reload from disk to ensure sync
                    st.session_state.current_profile = load_profile(st.session_state.profile_name)
                    st.session_state.meal_logged = True
                    st.success("✓ Meal logged successfully!")
                    st.rerun()
                else:
                    st.error("Failed to log meal")

with col2:
    # Information section explaining how the app works
    st.header("ℹ️ How it works")
    st.markdown("""
    1. **Create or load a profile** in the sidebar
    2. **Select your preferences** (auto-filled from profile)
    3. **Click the button** to get recommendations
    4. **Rate your meal** to improve future suggestions
    
    The AI nutritionist will analyze your request and provide:
    - Specific menu items
    - Nutritional breakdown
    - Customization suggestions
    - Context-aware recommendations
    """)

    # Tips section for better user experience
    st.header("💡 New Features")
    st.markdown("""
    - **📊 User Profiles**: Save preferences & track history
    - **🧠 Context-Aware**: Agent learns your preferences
    - **📈 Meal History**: View past orders & ratings
    - **⭐ Rating System**: Improve recommendations over time
    - **💾 Auto-Fill**: Preferences load automatically
    """)

    if st.session_state.current_profile:
        st.header("📊 Your Stats")
        stats = st.session_state.current_profile.get("stats", {})
        st.metric("Meals Tracked", stats.get("total_meals_tracked", 0))
        if stats.get("avg_daily_calories"):
            st.metric("Avg Calories/Meal", f"{stats['avg_daily_calories']:.0f}")
        if stats.get("avg_meal_rating"):
            st.metric("Avg Rating", f"{stats['avg_meal_rating']:.1f}/5 ⭐")

# Application footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI")
