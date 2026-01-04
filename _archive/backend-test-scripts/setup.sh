#!/bin/bash
# Setup script for Stack8s Backend

echo "🚀 Stack8s Backend Setup"
echo "========================"
echo ""

# Check Python version
echo "Checking Python version..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check for .env.local
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local not found"
    echo "Please create .env.local from .env.local.example:"
    echo "  cp .env.local.example .env.local"
    echo "  # Then edit .env.local with your credentials"
    echo ""
else
    echo "✅ .env.local found"
fi

echo ""
echo "========================"
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Ensure .env.local is configured with your credentials"
echo "2. Apply database migration:"
echo "   psql \$SUPABASE_DB_URL -f migrations/001_create_chat_schema.sql"
echo "3. Start the server:"
echo "   python -m app.main"
echo "4. Run tests:"
echo "   python scripts/test_api.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
echo ""

