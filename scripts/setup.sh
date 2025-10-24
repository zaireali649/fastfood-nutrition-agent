#!/bin/bash
# Setup script for Fast Food Nutrition Agent
# Run this locally before deployment

set -e  # Exit on error

echo "🚀 Fast Food Nutrition Agent - Setup Script"
echo "============================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Install dev dependencies
echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt
echo "✅ Dev dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/profiles
mkdir -p logs
mkdir -p .streamlit
echo "✅ Directories created"
echo ""

# Check for .env file
echo "🔐 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "📝 Creating .env template..."
    cat > .env << EOL
# Environment Configuration
ENVIRONMENT=development

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-key-here

# Supabase Configuration (optional for local dev)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-key-here

# Optional Settings
ENABLE_CONTENT_FILTER=false
ENABLE_MONITORING=false
EOL
    echo "✅ .env template created - PLEASE EDIT WITH YOUR KEYS"
else
    echo "✅ .env file exists"
fi
echo ""

# Check for secrets.toml
echo "🔒 Checking Streamlit secrets..."
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Warning: .streamlit/secrets.toml not found"
    echo "📝 Creating secrets template..."
    cat > .streamlit/secrets.toml << EOL
# Streamlit Secrets (for local testing)
OPENAI_API_KEY = "sk-your-key-here"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-key-here"
ENVIRONMENT = "development"
EOL
    echo "✅ Secrets template created - PLEASE EDIT WITH YOUR KEYS"
else
    echo "✅ secrets.toml exists"
fi
echo ""

# Run tests
echo "🧪 Running tests..."
if pytest tests/ --quiet --tb=short; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed (this is OK for first setup)"
fi
echo ""

# Display next steps
echo "============================================"
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. Edit .env with your OpenAI API key"
echo "   2. (Optional) Add Supabase credentials for database"
echo "   3. Run app locally: streamlit run multi_agent_app.py"
echo "   4. Follow DEPLOYMENT.md for production deployment"
echo ""
echo "🔗 Quick Links:"
echo "   • Get OpenAI key: https://platform.openai.com/api-keys"
echo "   • Get Supabase: https://supabase.com/dashboard"
echo "   • Deployment guide: ./DEPLOYMENT.md"
echo ""
echo "🚀 Ready to start! Run: streamlit run multi_agent_app.py"
echo "============================================"

