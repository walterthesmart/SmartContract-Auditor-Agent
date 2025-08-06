@echo off
echo 🚀 Setting up HederaAuditAI Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Navigate to frontend directory
if not exist "frontend" (
    echo ❌ Frontend directory not found!
    pause
    exit /b 1
)

cd frontend

REM Install dependencies
echo 📦 Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Create environment file if it doesn't exist
if not exist ".env.local" (
    echo 🔧 Creating environment configuration...
    copy .env.local.example .env.local
    echo ✅ Created .env.local from example
    echo 📝 Please edit .env.local with your configuration
) else (
    echo ✅ Environment file already exists
)

REM Run type checking
echo 🔍 Running type check...
npm run type-check

REM Run linting
echo 🧹 Running linter...
npm run lint

REM Build the application
echo 🏗️  Building application...
npm run build

if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo.
echo 🎉 Frontend setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit frontend/.env.local with your API configuration
echo 2. Start the development server: cd frontend ^&^& npm run dev
echo 3. Open http://localhost:3000 in your browser
echo.
echo 🔧 Available commands:
echo   npm run dev          - Start development server
echo   npm run build        - Build for production
echo   npm run start        - Start production server
echo   npm run lint         - Run ESLint
echo   npm run type-check   - Run TypeScript checks
echo   npm run format       - Format code with Prettier
echo.
echo 📚 Documentation: See frontend/README.md for detailed information

pause
