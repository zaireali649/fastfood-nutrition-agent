#!/bin/bash
# Test runner script with coverage

set -e

echo "🧪 Running Fast Food Nutrition Agent Tests"
echo "==========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate || source venv/Scripts/activate
    echo "✅ Virtual environment activated"
fi

# Run tests with coverage
echo ""
echo "📊 Running tests with coverage..."
pytest tests/ \
    --verbose \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=70

# Check test results
if [ $? -eq 0 ]; then
    echo ""
    echo "==========================================="
    echo "✅ All tests passed!"
    echo "📊 Coverage report: htmlcov/index.html"
    echo "==========================================="
else
    echo ""
    echo "==========================================="
    echo "❌ Some tests failed"
    echo "==========================================="
    exit 1
fi

