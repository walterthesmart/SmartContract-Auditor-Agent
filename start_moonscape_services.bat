@echo off
REM Start MoonScape Services Script
REM This script starts the auditor services using the existing deployed contract

echo 🌙 Starting MoonScape Services
echo ================================

REM Check if we're in the right directory
if not exist "config\.env" (
    echo ❌ Error: config\.env file not found. Please run this script from the project root.
    pause
    exit /b 1
)

echo 📋 Using existing deployed contract: 0.0.6359980
echo 🌐 Network: testnet
echo 📡 HCS-10 Topic: 0.0.6359793

REM Start the API server in background
echo 🚀 Starting API server...
start /b python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

REM Wait a moment for the server to start
timeout /t 5 /nobreak >nul

REM Check if API is running
echo 🔍 Checking API health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  API server may still be starting...
) else (
    echo ✅ API server is running
)

echo.
echo 🎯 Services Started Successfully!
echo.
echo 📋 Available Services:
echo - API Server: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo.
echo 🔗 Next Steps:
echo 1. Test the API: python scripts\demo\api_demo.py
echo 2. View documentation: http://localhost:8000/docs
echo 3. Submit contracts for analysis
echo.
echo 🌙 MoonScape Integration:
echo - Agent Name: HederaAuditAI
echo - Registry Topic: 0.0.6359793
echo - Contract ID: 0.0.6359980
echo.
echo Press any key to open API documentation in browser...
pause >nul

REM Open API documentation in default browser
start http://localhost:8000/docs

echo.
echo 🎉 MoonScape services are now running!
echo Press Ctrl+C to stop the services when done.
echo.
pause
