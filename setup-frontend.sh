#!/bin/bash

# HederaAuditAI Frontend Setup Script
echo "🚀 Setting up HederaAuditAI Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Navigate to frontend directory
cd frontend || {
    echo "❌ Frontend directory not found!"
    exit 1
}

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "🔧 Creating environment configuration..."
    cp .env.local.example .env.local
    echo "✅ Created .env.local from example"
    echo "📝 Please edit .env.local with your configuration"
else
    echo "✅ Environment file already exists"
fi

# Run type checking
echo "🔍 Running type check..."
npm run type-check

if [ $? -ne 0 ]; then
    echo "⚠️  Type check failed, but continuing..."
fi

# Run linting
echo "🧹 Running linter..."
npm run lint

if [ $? -ne 0 ]; then
    echo "⚠️  Linting issues found, but continuing..."
fi

# Build the application
echo "🏗️  Building application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "🎉 Frontend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit frontend/.env.local with your API configuration"
echo "2. Start the development server: cd frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🔧 Available commands:"
echo "  npm run dev          - Start development server"
echo "  npm run build        - Build for production"
echo "  npm run start        - Start production server"
echo "  npm run lint         - Run ESLint"
echo "  npm run type-check   - Run TypeScript checks"
echo "  npm run format       - Format code with Prettier"
echo ""
echo "📚 Documentation: See frontend/README.md for detailed information"
