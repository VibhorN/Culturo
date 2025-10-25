#!/bin/bash

# WorldWise Startup Script
# This script helps you get WorldWise up and running quickly

echo "🌍 Welcome to WorldWise - Cultural Immersion Companion!"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 16+ and try again."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Check if we're in the right directory
if [ ! -f "backend/app.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "Expected structure:"
    echo "  backend/app.py"
    echo "  frontend/package.json"
    exit 1
fi

echo "✅ Project structure looks good"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit backend/.env with your API keys"
    echo "   Required keys: DEEPGRAM_API_KEY, VAPI_API_KEY, ANTHROPIC_API_KEY"
    echo "   Optional keys: SPOTIFY_CLIENT_ID, NEWS_API_KEY, REDDIT_CLIENT_ID"
fi

cd ..

# Setup frontend
echo ""
echo "🔧 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --legacy-peer-deps

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start WorldWise:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: ./start.sh"
echo ""
echo "Or start manually:"
echo "  Backend:  cd backend && source venv/bin/activate && python app.py"
echo "  Frontend: cd frontend && npm start"
echo ""
echo "🌍 Happy cultural exploring!"
