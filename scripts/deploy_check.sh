#!/bin/bash
# Pre-deployment checklist script

echo "🔍 Pre-Deployment Checklist"
echo "============================"
echo ""

checks_passed=0
checks_failed=0

# Function to check something
check() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
        ((checks_passed++))
    else
        echo "❌ $1"
        ((checks_failed++))
    fi
}

# Check 1: Git repository is clean
echo "Checking git status..."
git diff-index --quiet HEAD --
check "Git working directory is clean"

# Check 2: Requirements file exists
echo "Checking requirements..."
[ -f "requirements.txt" ]
check "requirements.txt exists"

# Check 3: Main app file exists
echo "Checking app file..."
[ -f "multi_agent_app.py" ]
check "multi_agent_app.py exists"

# Check 4: Streamlit config exists
echo "Checking Streamlit config..."
[ -f ".streamlit/config.toml" ]
check "Streamlit config exists"

# Check 5: Database schema exists
echo "Checking database schema..."
[ -f "supabase/schema.sql" ]
check "Database schema exists"

# Check 6: Tests directory exists
echo "Checking tests..."
[ -d "tests" ] && [ -f "tests/conftest.py" ]
check "Test suite is present"

# Check 7: No sensitive files in git
echo "Checking for sensitive files..."
! git ls-files | grep -q "\.env$"
check "No .env file in git"

! git ls-files | grep -q "secrets\.toml$"
check "No secrets.toml in git"

# Check 8: Documentation exists
echo "Checking documentation..."
[ -f "DEPLOYMENT.md" ]
check "Deployment guide exists"

[ -f "README.md" ]
check "README exists"

# Check 9: Config modules exist
echo "Checking config modules..."
[ -f "config/database.py" ] && [ -f "config/environments.py" ] && [ -f "config/cost_control.py" ]
check "All config modules present"

# Check 10: Middleware exists
echo "Checking middleware..."
[ -f "middleware/security.py" ] && [ -f "middleware/content_filter.py" ] && [ -f "middleware/error_handler.py" ]
check "All middleware present"

# Summary
echo ""
echo "============================"
echo "📊 Results:"
echo "   ✅ Passed: $checks_passed"
echo "   ❌ Failed: $checks_failed"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo "🎉 All checks passed! Ready to deploy."
    echo ""
    echo "Next steps:"
    echo "1. Commit and push to GitHub"
    echo "2. Follow DEPLOYMENT.md for Streamlit Share setup"
    echo "3. Configure Supabase database"
    echo "4. Add secrets in Streamlit Share"
    exit 0
else
    echo "⚠️  Some checks failed. Please fix before deploying."
    exit 1
fi

