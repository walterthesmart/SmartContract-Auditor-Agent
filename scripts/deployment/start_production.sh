#!/bin/bash

# HederaAuditAI Backend Production Startup Script
# For deployment next week

echo "🚀 Starting HederaAuditAI Backend (Production Mode)"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with required environment variables."
    exit 1
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test logo file
echo "🖼️ Testing logo file..."
python test_logo.py

# Kill any existing uvicorn processes
echo "🔄 Stopping any existing servers..."
pkill -f uvicorn || true

# Wait a moment for processes to stop
sleep 2

# Start the server on production port 8000
echo "🚀 Starting FastAPI server on port 8000..."
echo "Server will be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --log-level info
