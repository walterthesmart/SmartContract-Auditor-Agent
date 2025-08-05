#!/bin/bash

# MoonScape Deployment Script for AuditRegistry Contract
# This script automates the entire deployment process

echo "🌙 MoonScape Deployment Script for AuditRegistry"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "contracts/AuditRegistry.sol" ]; then
    echo "❌ Error: AuditRegistry.sol not found. Please run this script from the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f "config/.env" ]; then
    echo "❌ Error: config/.env file not found. Please create it first."
    echo "📋 You can copy from config/.env.example and fill in your values."
    exit 1
fi

# Load environment variables
source config/.env

# Check required environment variables
echo "🔍 Checking environment variables..."

if [ -z "$HEDERA_OPERATOR_ID" ]; then
    echo "❌ HEDERA_OPERATOR_ID not set in config/.env"
    exit 1
fi

if [ -z "$HEDERA_OPERATOR_KEY" ]; then
    echo "❌ HEDERA_OPERATOR_KEY not set in config/.env"
    exit 1
fi

echo "✅ Environment variables checked"

# Install Node.js dependencies if needed
echo "📦 Installing Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "✅ Node modules already installed"
fi

# Install Solidity compiler dependency
echo "📦 Installing Solidity compiler..."
npm install solc@^0.8.20

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python -c "import slither" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "✅ Python dependencies already installed"
fi

# Deploy the contract
echo "🚀 Deploying AuditRegistry contract to Hedera..."
node scripts/setup/deploy_audit_registry.js

if [ $? -eq 0 ]; then
    echo "✅ Contract deployment successful!"
    
    # Get the contract ID from .env
    CONTRACT_ID=$(grep "AUDIT_REGISTRY_CONTRACT_ID=" config/.env | cut -d'=' -f2)
    
    echo "📋 Contract ID: $CONTRACT_ID"
    echo "🌐 Network: ${HEDERA_NETWORK:-testnet}"
    echo "👤 Owner: $HEDERA_OPERATOR_ID"
    
    # Check if MoonScape API key is set
    if [ -n "$MOONSCAPE_API_KEY" ]; then
        echo ""
        echo "🌙 Setting up MoonScape integration..."
        
        # Start the MoonScape integration
        python src/integrations/moonscape/moonscape_integration.py &
        MOONSCAPE_PID=$!
        
        echo "✅ MoonScape integration started (PID: $MOONSCAPE_PID)"
        echo "📡 Listening for audit requests from MoonScape..."
        
        # Wait a moment for initialization
        sleep 5
        
        echo ""
        echo "🎯 Deployment completed successfully!"
        echo "📋 Contract ID: $CONTRACT_ID"
        echo "🌙 MoonScape integration: Active"
        echo "📡 HCS-10 topics: Configured"
        echo ""
        echo "🔗 Next steps:"
        echo "1. Visit HashScan to verify your contract: https://hashscan.io/testnet/contract/$CONTRACT_ID"
        echo "2. Test the API: python scripts/demo/api_demo.py"
        echo "3. Start the backend: bash scripts/deployment/start_production.sh"
        echo ""
        echo "Press Ctrl+C to stop the MoonScape integration listener."
        
        # Keep the script running to maintain MoonScape integration
        wait $MOONSCAPE_PID
        
    else
        echo ""
        echo "⚠️  MoonScape API key not found in config/.env"
        echo "📋 To complete MoonScape integration:"
        echo "1. Get your API key from MoonScape Labs"
        echo "2. Add MOONSCAPE_API_KEY=your_key_here to config/.env"
        echo "3. Run: python src/integrations/moonscape/moonscape_integration.py"
        echo ""
        echo "🎯 Contract deployment completed successfully!"
        echo "📋 Contract ID: $CONTRACT_ID"
    fi
    
else
    echo "❌ Contract deployment failed!"
    exit 1
fi
