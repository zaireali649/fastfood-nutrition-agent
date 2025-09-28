# 🍔 Fast Food Nutrition Agent

A Streamlit web application that provides personalized meal recommendations from fast food restaurants based on your dietary preferences, calorie requirements, and nutritional goals. Powered by OpenAI's GPT models, this AI nutritionist helps you make informed dining decisions while staying within your dietary constraints.

## ✨ Features

- **🎯 Personalized Recommendations**: Get meal suggestions tailored to your specific dietary needs
- **🏪 Multiple Restaurants**: Support for popular fast food chains and custom restaurant input
- **📊 Calorie Management**: Set and maintain your calorie targets (300-2000 calories)
- **🚫 Dietary Restrictions**: Handle various dietary needs including:
  - Gluten-free, Dairy-free, Vegetarian, Vegan
  - Religious restrictions (Halal, Kosher)
  - Health conditions (Diabetic-friendly, Low sodium)
  - Custom dietary preferences
- **💡 Smart Customization**: AI considers restaurant-specific customization options
- **📱 User-Friendly Interface**: Clean, intuitive Streamlit web interface
- **💾 Session Persistence**: Recommendations persist during your session
- **📋 Easy Copy**: Copy recommendations for easy sharing or saving

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fastfood-nutrition-agent.git
   cd fastfood-nutrition-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501` to access the application

## 🏗️ Project Structure

```
fastfood-nutrition-agent/
├── app.py                    # Main Streamlit application
├── agent.py                  # OpenAI agent configuration and logic
├── requirements.txt          # Python dependencies
├── test-requirements.txt     # Testing dependencies
├── NEXT_STEPS.md            # Development roadmap and improvements
├── README.md                # This file
└── prompts/
    └── agent_prompt.txt     # AI nutritionist system prompt
```

## 🎮 How to Use

1. **Select Your Restaurant**
   - Choose from popular chains (Chick-fil-A, McDonald's, Subway, etc.)
   - Or enter a custom restaurant name

2. **Set Your Calorie Target**
   - Input your desired calorie range (300-2000 calories)

3. **Specify Dietary Restrictions**
   - Select from common restrictions or enter custom ones
   - Include any allergies or dietary preferences

4. **Add Additional Notes**
   - Specify preferences like "extra protein" or "prefer grilled over fried"

5. **Get Recommendations**
   - Click "Get Meal Recommendations" to receive personalized suggestions
   - View formatted recommendations with nutritional guidance
   - Copy recommendations for future reference

## 🧠 How It Works

The application uses a sophisticated AI agent built on OpenAI's GPT models:

1. **User Input Processing**: Your preferences are formatted into a natural language request
2. **AI Analysis**: The nutritionist agent analyzes your requirements against restaurant menus
3. **Recommendation Generation**: The AI provides specific meal suggestions with customization options
4. **Nutritional Focus**: Recommendations prioritize high protein and low sodium options
5. **Constraint Adherence**: All suggestions respect your calorie limits and dietary restrictions

## 🛠️ Technical Details

### Dependencies

- **Streamlit**: Web application framework
- **OpenAI Agents**: AI agent functionality
- **Python-dotenv**: Environment variable management

### Key Components

- **`app.py`**: Streamlit interface with user input handling and result display
- **`agent.py`**: OpenAI agent configuration and recommendation generation
- **`prompts/agent_prompt.txt`**: System prompt defining the AI nutritionist's behavior

### Architecture

```
User Input → Streamlit UI → Agent Processing → OpenAI API → Formatted Recommendations
```

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run linting
ruff check .
pydocstyle .

# Run the application in development mode
streamlit run app.py
```

### Code Quality

The project follows Python best practices:
- **Type hints** for better code clarity
- **Pydocstyle** compliant docstrings
- **Ruff** for code formatting and linting
- **Modular design** with separated concerns

## 📋 Current Limitations

- Requires OpenAI API key and associated costs
- Recommendations based on general nutritional knowledge
- No real-time menu data integration
- Limited to fast food restaurants

## 🚧 Roadmap

See [NEXT_STEPS.md](NEXT_STEPS.md) for detailed development roadmap including:

- **Testing Framework**: Comprehensive unit and integration tests
- **Enhanced UI**: Better user experience and accessibility
- **Data Persistence**: User preferences and meal history
- **Advanced Features**: Nutritional analysis, price comparison, meal planning
- **Deployment**: Docker support, CI/CD pipeline, production deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models and agents framework
- Streamlit for the excellent web application framework
- The nutrition and health community for dietary guidance principles

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/fastfood-nutrition-agent/issues) page
2. Create a new issue with detailed information
3. Include your environment details and error messages

---

**Made with ❤️ for healthier fast food choices**