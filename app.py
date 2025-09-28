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
from typing import List

import streamlit as st
from agents import set_default_openai_key
from dotenv import load_dotenv

from agent import get_task_generator, run_nutrition_agent


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


def generate_meal_recommendations(user_goal: str) -> None:
    """
    Generate meal recommendations using the nutrition agent.

    Args:
        user_goal: The formatted user request for meal recommendations.

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
            task_generator = get_task_generator(prompt)

            # Run the nutrition agent and get results
            recommendations: str = asyncio.run(
                run_nutrition_agent(task_generator, user_goal)
            )

            # Store recommendations in session state for persistence
            st.session_state.recommendations = recommendations
            st.session_state.show_recommendations = True

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

# Title and description
st.title("🍔 Fast Food Nutrition Agent")
st.markdown("""
Get personalized meal recommendations from fast food restaurants based on your dietary needs and calorie requirements.
""")

# Create sidebar for user input controls
st.sidebar.header("📋 Your Meal Preferences")

# Restaurant selection with two options: preset list or custom input
restaurant_option: str = st.sidebar.radio(
    "Restaurant:", ["Select from list", "Enter custom restaurant"]
)

# Get restaurant name based on user's selection method
restaurant: str
if restaurant_option == "Select from list":
    # Use predefined list of popular fast food chains
    restaurant = st.sidebar.selectbox(
        "Choose a restaurant:",
        [
            "Chick-fil-A",
            "McDonald's",
            "Subway",
            "Taco Bell",
            "Burger King",
            "KFC",
            "Pizza Hut",
            "Domino's",
        ],
    )
else:
    # Allow user to enter any restaurant name
    restaurant = st.sidebar.text_input(
        "Enter restaurant name:",
        placeholder="e.g., Five Guys, Chipotle, Panera Bread...",
    )

# Calorie target input with reasonable limits
calories: int = st.sidebar.number_input(
    "Target calories:", min_value=300, max_value=2000, value=1200, step=50
)

# Dietary restrictions selection with two input methods
restrictions_option: str = st.sidebar.radio(
    "Dietary restrictions:", ["Select from list", "Enter custom restrictions"]
)

# Get dietary restrictions based on user's selection method
dietary_restrictions: List[str]
if restrictions_option == "Select from list":
    # Use predefined list of common dietary restrictions
    dietary_restrictions = st.sidebar.multiselect(
        "Choose restrictions (if any):",
        [
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
        ],
    )
else:
    # Allow user to enter custom dietary restrictions
    custom_restrictions: str = st.sidebar.text_input(
        "Enter your dietary restrictions:",
        placeholder="e.g., no nuts, halal, kosher, diabetic-friendly...",
    )
    dietary_restrictions = [custom_restrictions] if custom_restrictions else []

# Additional preferences and notes input
additional_notes: str = st.sidebar.text_area(
    "Additional preferences or notes:",
    placeholder="e.g., prefer grilled over fried, need extra protein, avoid spicy foods, want to maximize fiber, etc.",
    help="Be specific about your preferences. For example: 'I need extra protein for muscle building' or 'I prefer grilled options over fried'",
)

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

    # Display previous recommendations if they exist
    display_previous_recommendations()

    # Main action button to generate meal recommendations
    if st.button(
        "🍽️ Get Meal Recommendations", type="primary", use_container_width=True
    ):
        generate_meal_recommendations(user_goal)

with col2:
    # Information section explaining how the app works
    st.header("ℹ️ How it works")
    st.markdown("""
    1. **Select your preferences** in the sidebar
    2. **Click the button** to get recommendations
    3. **Review the suggestions** tailored to your needs
    
    The AI nutritionist will analyze your request and provide:
    - Specific menu items
    - Nutritional breakdown
    - Customization suggestions
    - Alternative options
    """)

    # Tips section for better user experience
    st.header("💡 Tips")
    st.markdown("""
    - Be specific about calorie goals
    - Mention any allergies or restrictions
    - Include preferences for cooking methods
    - Ask for alternatives if needed
    """)

# Application footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI")
