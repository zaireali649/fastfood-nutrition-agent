"""
Multi-Agent Fast Food Nutrition Application.

This Streamlit application uses a multi-agent system with specialized agents:
- Coordinator: Orchestrates the workflow
- Nutritionist: Analyzes dietary requirements
- Restaurant Expert: Provides menu recommendations
"""

import asyncio
import os
from typing import Dict, List, Optional

import streamlit as st
from agents import set_default_openai_key
from dotenv import load_dotenv

from multi_agents.coordinator import run_multi_agent_workflow
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
    """Format user inputs into a natural language goal."""
    if not restaurant.strip():
        raise ValueError("Restaurant name cannot be empty")

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

    user_goal = f"I want a {calories} calorie meal from {restaurant.lower()}. {restrictions_text}."

    if additional_notes.strip():
        user_goal += f" Additional preferences: {additional_notes.strip()}."

    return user_goal


def generate_multi_agent_recommendations(
    user_goal: str, restaurant: str, calories: int, user_profile: Optional[Dict] = None
) -> None:
    """Generate meal recommendations using the multi-agent system."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "❌ OpenAI API key not found. Please set your OPENAI_API_KEY environment variable."
        )
        st.stop()

    with st.spinner("🤖 Multi-agent system analyzing your request..."):
        try:
            # Run multi-agent workflow
            recommendations, session_context = asyncio.run(
                run_multi_agent_workflow(user_goal, user_profile)
            )

            # Store in session state
            st.session_state.recommendations = recommendations
            st.session_state.session_context = session_context
            st.session_state.show_recommendations = True
            st.session_state.last_restaurant = restaurant
            st.session_state.last_calories = calories
            st.session_state.meal_logged = False

            # Display success message
            st.success("✅ Multi-agent analysis complete!")

            # Show agent workflow info
            agents_used = session_context.get("agents_used", [])
            if agents_used:
                st.info(f"🤝 Agents collaborated: {' → '.join(agents_used)}")

            # Show warnings if fallback was triggered
            if session_context.get("fallback_triggered"):
                st.warning("⚠️ Fallback mode was used due to technical issues")

            # Display the recommendations
            st.markdown("---")
            st.header("🍽️ Your Multi-Agent Meal Recommendations")
            st.markdown(recommendations)

            # Add expandable section for technical details
            with st.expander("🔍 View Multi-Agent Workflow Details", expanded=False):
                st.json(session_context)

        except FileNotFoundError:
            st.error(
                "❌ Could not find agent prompt files. Please ensure all prompts exist in the 'prompts/' directory."
            )
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")


# Load environment variables
load_dotenv()
set_default_openai_key(os.environ.get("OPENAI_API_KEY", ""))

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Agent Nutrition System", page_icon="🤖", layout="wide"
)

# Initialize session state
if "current_profile" not in st.session_state:
    st.session_state.current_profile = None
if "profile_name" not in st.session_state:
    st.session_state.profile_name = None

# Title and description
st.title("🤖 Multi-Agent Fast Food Nutrition System")
st.markdown("""
**NEW:** Powered by specialized AI agents working together!
- 🧬 **Nutritionist Agent** analyzes your dietary needs
- 🍔 **Restaurant Expert** recommends specific menu items  
- 🎯 **Coordinator Agent** combines insights for optimal recommendations
""")

# Sidebar: Profile Management
st.sidebar.header("👤 Profile Management")

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

# Sidebar: Meal Preferences
st.sidebar.markdown("---")
st.sidebar.header("📋 Your Meal Preferences")

restaurant_option = st.sidebar.radio(
    "Restaurant:", ["Select from list", "Enter custom restaurant"]
)

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

if st.session_state.current_profile:
    fav_restaurants = st.session_state.current_profile["user_preferences"].get(
        "favorite_restaurants", []
    )
    all_restaurants = fav_restaurants + [
        r for r in default_restaurants if r not in fav_restaurants
    ]
else:
    all_restaurants = default_restaurants

if restaurant_option == "Select from list":
    restaurant = st.sidebar.selectbox("Choose a restaurant:", all_restaurants)
else:
    restaurant = st.sidebar.text_input(
        "Enter restaurant name:",
        placeholder="e.g., Five Guys, Chipotle, Panera Bread...",
    )

# Calorie target
default_calories = 1200
if st.session_state.current_profile:
    default_calories = st.session_state.current_profile["user_preferences"].get(
        "default_calorie_target", 1200
    )

calories = st.sidebar.number_input(
    "Target calories:", min_value=300, max_value=2000, value=default_calories, step=50
)

# Dietary restrictions
restrictions_option = st.sidebar.radio(
    "Dietary restrictions:", ["Select from list", "Enter custom restrictions"]
)

default_restrictions = []
if st.session_state.current_profile:
    default_restrictions = st.session_state.current_profile["user_preferences"].get(
        "dietary_restrictions", []
    )

if restrictions_option == "Select from list":
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

    valid_defaults = [r for r in default_restrictions if r in restriction_options]

    dietary_restrictions = st.sidebar.multiselect(
        "Choose restrictions (if any):",
        restriction_options,
        default=valid_defaults,
    )
else:
    default_custom = ", ".join(default_restrictions) if default_restrictions else ""
    custom_restrictions = st.sidebar.text_input(
        "Enter your dietary restrictions:",
        value=default_custom,
        placeholder="e.g., no nuts, halal, kosher...",
    )
    dietary_restrictions = [custom_restrictions] if custom_restrictions else []

# Additional notes
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

additional_notes = st.sidebar.text_area(
    "Additional preferences or notes:",
    value=default_notes,
    placeholder="e.g., prefer grilled over fried, need extra protein...",
)

# Save preferences button
if st.session_state.current_profile and st.sidebar.button(
    "💾 Save Current Preferences to Profile"
):
    st.session_state.current_profile["user_preferences"][
        "default_calorie_target"
    ] = calories
    st.session_state.current_profile["user_preferences"][
        "dietary_restrictions"
    ] = dietary_restrictions

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

    if save_profile(st.session_state.profile_name, st.session_state.current_profile):
        st.sidebar.success("✓ Preferences saved!")
    else:
        st.sidebar.error("Failed to save preferences")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Your Meal Request")

    try:
        user_goal = format_user_goal(
            restaurant, calories, dietary_restrictions, additional_notes
        )
        st.info(f"**Your request:** {user_goal}")

    except ValueError as e:
        st.warning(f"⚠️ {str(e)}")
        st.stop()

    # Display meal history
    if st.session_state.current_profile:
        recent_meals = get_recent_meals(st.session_state.current_profile, count=10)
        if recent_meals:
            with st.expander("📜 Recent Meal History (Last 10)", expanded=False):
                st.markdown("### Your Recent Orders")
                for i, meal in enumerate(reversed(recent_meals), 1):
                    rating_display = (
                        "⭐" * meal.get("rating", 0)
                        if meal.get("rating")
                        else "Not rated"
                    )
                    st.markdown(
                        f"**{i}.** {meal.get('restaurant', 'Unknown')} - "
                        f"{meal.get('calories', 'N/A')} cal - {rating_display}"
                    )

    # Main action button
    if st.button(
        "🤖 Get Multi-Agent Recommendations", type="primary", use_container_width=True
    ):
        st.session_state.meal_logged = False
        generate_multi_agent_recommendations(
            user_goal, restaurant, calories, st.session_state.current_profile
        )

    # Display previous recommendations
    if st.session_state.get("show_recommendations"):
        if st.button("🗑️ Clear Recommendations"):
            st.session_state.show_recommendations = False
            st.rerun()

    # Meal logging section
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
                key="meal_rating_slider",
            )

        with col_rate2:
            if st.button("💾 Log Meal to History", use_container_width=True):
                meal_entry = {
                    "restaurant": st.session_state.get("last_restaurant", restaurant),
                    "calories": st.session_state.get("last_calories", calories),
                    "rating": meal_rating,
                }

                updated_profile = add_meal_to_history(
                    st.session_state.current_profile, meal_entry
                )

                if save_profile(st.session_state.profile_name, updated_profile):
                    st.session_state.current_profile = load_profile(
                        st.session_state.profile_name
                    )
                    st.session_state.meal_logged = True
                    st.success("✓ Meal logged successfully!")
                    st.rerun()
                else:
                    st.error("Failed to log meal")

with col2:
    st.header("🤖 Multi-Agent System")
    st.markdown("""
    **How it works:**
    
    1. **Nutritionist Agent** 🧬
       - Analyzes your dietary needs
       - Calculates macro targets
       - Reviews your meal history
    
    2. **Restaurant Expert** 🍔
       - Recommends specific items
       - Suggests customizations
       - Optimizes for your goals
    
    3. **Profile Manager** 📊
       - Learns your preferences
       - Detects rating patterns
       - Provides personalized insights
    
    4. **Coordinator** 🎯
       - Combines all insights
       - Ensures consistency
       - Handles errors gracefully
    """)

    st.header("✨ Benefits")
    st.markdown("""
    - **More Accurate**: Specialized expertise
    - **Context-Aware**: Learns from history
    - **Reliable**: Automatic fallbacks
    - **Transparent**: See agent collaboration
    """)

    if st.session_state.current_profile:
        st.header("📊 Your Stats")
        stats = st.session_state.current_profile.get("stats", {})
        st.metric("Meals Tracked", stats.get("total_meals_tracked", 0))
        if stats.get("avg_daily_calories"):
            st.metric("Avg Calories/Meal", f"{stats['avg_daily_calories']:.0f}")
        if stats.get("avg_meal_rating"):
            st.metric("Avg Rating", f"{stats['avg_meal_rating']:.1f}/5 ⭐")
        
        # Profile insights button
        if stats.get("total_meals_tracked", 0) >= 3:
            if st.button("🔍 Get Profile Insights", use_container_width=True):
                with st.spinner("Analyzing your preferences..."):
                    from multi_agents.profile_manager_agent import ProfileManagerAgent
                    import asyncio
                    
                    with open("prompts/profile_manager_prompt.txt", "r") as f:
                        pm_prompt = f.read()
                    
                    pm_agent = ProfileManagerAgent(pm_prompt)
                    insights = asyncio.run(pm_agent.analyze_profile(st.session_state.current_profile))
                    
                    st.session_state.profile_insights = insights
                    st.rerun()
        
        # Display insights if available
        if st.session_state.get("profile_insights"):
            with st.expander("💡 Your Profile Insights", expanded=True):
                # Display in a scrollable text area for better formatting
                st.text_area(
                    "Analysis Results",
                    value=st.session_state.profile_insights,
                    height=400,
                    label_visibility="collapsed"
                )
                if st.button("Clear Insights"):
                    st.session_state.profile_insights = None
                    st.rerun()

st.markdown("---")
st.markdown("🤖 Powered by 4-Agent AI System (Nutritionist + Restaurant + Profile Manager + Coordinator) | Built with Streamlit and OpenAI")

