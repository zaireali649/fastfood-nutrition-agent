import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from agent import get_task_generator, run_nutrition_agent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Fast Food Nutrition Agent", page_icon="🍔", layout="wide"
)

# Title and description
st.title("🍔 Fast Food Nutrition Agent")
st.markdown("""
Get personalized meal recommendations from fast food restaurants based on your dietary needs and calorie requirements.
""")

# Sidebar for user inputs
st.sidebar.header("📋 Your Meal Preferences")

# Restaurant selection
restaurant_option = st.sidebar.radio(
    "Restaurant:", ["Select from list", "Enter custom restaurant"]
)

if restaurant_option == "Select from list":
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
    restaurant = st.sidebar.text_input(
        "Enter restaurant name:",
        placeholder="e.g., Five Guys, Chipotle, Panera Bread...",
    )

# Calorie input
calories = st.sidebar.number_input(
    "Target calories:", min_value=300, max_value=2000, value=1200, step=50
)

# Dietary restrictions
restrictions_option = st.sidebar.radio(
    "Dietary restrictions:", ["Select from list", "Enter custom restrictions"]
)

if restrictions_option == "Select from list":
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
    custom_restrictions = st.sidebar.text_input(
        "Enter your dietary restrictions:",
        placeholder="e.g., no nuts, halal, kosher, diabetic-friendly...",
    )
    dietary_restrictions = [custom_restrictions] if custom_restrictions else []

# Additional notes
additional_notes = st.sidebar.text_area(
    "Additional preferences or notes:",
    placeholder="e.g., prefer grilled over fried, need extra protein, avoid spicy foods, want to maximize fiber, etc.",
    help="Be specific about your preferences. For example: 'I need extra protein for muscle building' or 'I prefer grilled options over fried'",
)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Your Meal Request")

    # Handle empty restaurant input
    if not restaurant.strip():
        st.warning("⚠️ Please enter a restaurant name.")
        st.stop()

    # Format dietary restrictions more naturally
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

    # Build the user goal with better phrasing
    user_goal = f"I want a {calories} calorie meal from {restaurant.lower()}. {restrictions_text}."

    # Add additional notes with proper context
    if additional_notes.strip():
        user_goal += f" Additional preferences: {additional_notes.strip()}."

    st.info(f"**Your request:** {user_goal}")

    # Show previous recommendations if they exist
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

    # Generate recommendations button
    if st.button(
        "🍽️ Get Meal Recommendations", type="primary", use_container_width=True
    ):
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            st.error(
                "❌ OpenAI API key not found. Please set your OPENAI_API_KEY environment variable."
            )
            st.stop()

        # Show loading spinner
        with st.spinner(
            "🤖 Analyzing your request and finding the best meal options..."
        ):
            try:
                # Read the nutritionist prompt
                with open("prompts/agent_prompt.txt", "r") as file:
                    prompt = file.read()

                # Create the nutrition agent
                task_generator = get_task_generator(prompt)

                # Run the nutrition agent and get results
                recommendations = asyncio.run(
                    run_nutrition_agent(task_generator, user_goal)
                )

                # Store recommendations in session state
                st.session_state.recommendations = recommendations
                st.session_state.show_recommendations = True

                # Display the recommendations
                st.success("✅ Meal recommendations generated!")

                # Create a nice display for the recommendations
                st.markdown("---")
                st.header("🍽️ Your Personalized Meal Recommendations")

                # Display the recommendations in a formatted way
                st.markdown(recommendations)

                # Add a copy button for the recommendations
                st.markdown("---")
                st.code(recommendations, language="text")
                st.caption(
                    "💡 You can select and copy the text above, or use the copy button below"
                )

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

with col2:
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

    st.header("💡 Tips")
    st.markdown("""
    - Be specific about calorie goals
    - Mention any allergies or restrictions
    - Include preferences for cooking methods
    - Ask for alternatives if needed
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI")
