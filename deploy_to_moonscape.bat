@echo off
REM MoonScape Deployment Script for AuditRegistry Contract (Windows)
REM This script automates the entire deployment process

echo 🌙 MoonScape Deployment Script for AuditRegistry
echo ================================================

REM Check if we're in the right directory
if not exist "contracts\AuditRegistry.sol" (
    echo ❌ Error: AuditRegistry.sol not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "config\.env" (
    echo ❌ Error: config\.env file not found. Please create it first.
    echo 📋 You can copy from config\.env.example and fill in your values.
    pause
    exit /b 1
)

echo 🔍 Checking environment variables...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

echo ✅ Environment checked

REM Install Node.js dependencies if needed
echo 📦 Installing Node.js dependencies...
if not exist "node_modules" (
    npm install
) else (
    echo ✅ Node modules already installed
)

REM Install Solidity compiler dependency
echo 📦 Installing Solidity compiler...
npm install solc@^0.8.20

REM Check if Python dependencies are installed
echo 📦 Checking Python dependencies...
python -c "import slither" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
) else (
    echo ✅ Python dependencies already installed
)

REM Deploy the contract
echo 🚀 Deploying AuditRegistry contract to Hedera...
node scripts\setup\deploy_audit_registry.js

if errorlevel 1 (
    echo ❌ Contract deployment failed!
    pause
    exit /b 1
)

echo ✅ Contract deployment successful!

REM Read contract ID from .env file
for /f "tokens=2 delims==" %%a in ('findstr "AUDIT_REGISTRY_CONTRACT_ID=" config\.env') do set CONTRACT_ID=%%a

echo 📋 Contract ID: %CONTRACT_ID%
echo 🌐 Network: testnet
echo 👤 Owner: Check your config\.env file

REM Check if MoonScape API key is set
findstr "MOONSCAPE_API_KEY=" config\.env >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  MoonScape API key not found in config\.env
    echo 📋 To complete MoonScape integration:
    echo 1. Get your API key from MoonScape Labs
    echo 2. Add MOONSCAPE_API_KEY=your_key_here to config\.env
    echo 3. Run: python src\integrations\moonscape\moonscape_integration.py
    echo.
    echo 🎯 Contract deployment completed successfully!
    echo 📋 Contract ID: %CONTRACT_ID%
) else (
    echo.
    echo 🌙 Setting up MoonScape integration...
    echo 📡 Starting MoonScape integration...
    
    start /b python src\integrations\moonscape\moonscape_integration.py
    
    echo ✅ MoonScape integration started
    echo 📡 Listening for audit requests from MoonScape...
    
    echo.
    echo 🎯 Deployment completed successfully!
    echo 📋 Contract ID: %CONTRACT_ID%
    echo 🌙 MoonScape integration: Active
    echo 📡 HCS-10 topics: Configured
    echo.
    echo 🔗 Next steps:
    echo 1. Visit HashScan to verify your contract: https://hashscan.io/testnet/contract/%CONTRACT_ID%
    echo 2. Test the API: python scripts\demo\api_demo.py
    echo 3. Start the backend: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    echo.
)

echo Press any key to continue...
pause >nul
