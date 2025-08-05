# MoonScape Deployment Guide for AuditRegistry Contract

This guide walks you through deploying your `AuditRegistry.sol` contract on MoonScape platform and integrating it with the HederaAuditAI system.

## Overview

MoonScape is a platform that facilitates smart contract deployment and management on the Hedera network. Your AuditRegistry contract will be deployed to Hedera testnet and integrated with MoonScape's ecosystem using the HCS-10 protocol.

## Prerequisites

### 1. Environment Setup
Ensure you have the following installed:
- Node.js (v16 or higher)
- npm or yarn
- Python 3.10+
- Hedera account with sufficient HBAR balance (minimum 50 HBAR recommended)

### 2. Required Credentials
- **Hedera Account**: Operator ID and private key
- **MoonScape API Key**: Contact MoonScape Labs for access
- **Groq API Key**: For LLM processing

## Step 1: Prepare Your Environment

### 1.1 Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Install Solidity compiler (if not already installed)
npm install -g solc

# Install Python dependencies
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables
Update your `config/.env` file:

```bash
# Hedera Network Configuration
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.your_account_id
HEDERA_OPERATOR_KEY=your_private_key_here

# MoonScape Integration
MOONSCAPE_API_KEY=your_moonscape_api_key_here
MOONSCAPE_API_BASE=https://api.hashgraphonline.com

# HCS-10 Configuration
HCS10_REGISTRY_TOPIC_ID=0.0.6359793
HCS10_AGENT_NAME=HederaAuditAI
HCS10_AGENT_DESCRIPTION=AI-powered auditing tool for Hedera smart contracts

# Other required configurations
GROQ_API_KEY=your_groq_api_key_here
SLITHER_CUSTOM_RULES=src/core/analyzer/hedera_rules.py
REPORT_LOGO_PATH=assets/images/logo.png
```

## Step 2: Deploy the AuditRegistry Contract

### 2.1 Using the Deployment Script
Run the automated deployment script:

```bash
# Navigate to project root
cd /path/to/Smart-Contract-Auditor-Agent

# Run the deployment script
node scripts/setup/deploy_audit_registry.js
```

This script will:
1. ✅ Compile the AuditRegistry.sol contract with OpenZeppelin dependencies
2. ✅ Store the bytecode on Hedera File Service
3. ✅ Deploy the contract to Hedera testnet
4. ✅ Set you as the contract owner
5. ✅ Update your `.env` file with the contract ID
6. ✅ Save the contract ABI for future interactions

### 2.2 Manual Deployment (Alternative)
If you prefer manual deployment:

```bash
# Compile the contract first
npx hardhat compile  # If using Hardhat
# OR
solc --bin --abi contracts/AuditRegistry.sol -o build/

# Then deploy using Hedera SDK
node scripts/setup/deploy_simple_contract.js
```

## Step 3: Verify Deployment

### 3.1 Check Contract on Hedera
Visit the Hedera testnet explorer:
- **HashScan**: https://hashscan.io/testnet
- Search for your contract ID to verify deployment

### 3.2 Test Contract Functions
```bash
# Test the deployment with a simple call
node -e "
const { Client, ContractCallQuery } = require('@hashgraph/sdk');
const client = Client.forTestnet();
client.setOperator('${HEDERA_OPERATOR_ID}', '${HEDERA_OPERATOR_KEY}');

// Test a view function
const query = new ContractCallQuery()
  .setContractId('${AUDIT_REGISTRY_CONTRACT_ID}')
  .setGas(100000)
  .setFunction('owner');

query.execute(client).then(result => {
  console.log('Contract owner:', result.getAddress(0));
}).catch(console.error);
"
```

## Step 4: MoonScape Integration

### 4.1 Register with MoonScape
```bash
# Run the MoonScape integration script
python src/integrations/moonscape/moonscape_integration.py
```

This will:
1. Register your HederaAuditAI as an agent on MoonScape
2. Set up HCS-10 communication channels
3. Link your deployed contract to the MoonScape ecosystem

### 4.2 Test the Integration
```bash
# Run the API demo with MoonScape integration
python scripts/demo/api_demo.py
```

When prompted, choose to test MoonScape integration (y/n): **y**

## Step 5: Production Deployment

### 5.1 Start the Backend Service
```bash
# Start the production server
bash scripts/deployment/start_production.sh
```

### 5.2 Verify All Services
Check that all components are running:

- ✅ **Backend API**: http://localhost:8000/health
- ✅ **Contract**: Deployed and accessible
- ✅ **MoonScape**: Registered and listening
- ✅ **HCS-10**: Topics configured and active

## Troubleshooting

### Common Issues

1. **Insufficient HBAR Balance**
   ```bash
   # Check your balance
   curl "https://testnet.mirrornode.hedera.com/api/v1/accounts/${HEDERA_OPERATOR_ID}"
   ```

2. **Contract Compilation Errors**
   ```bash
   # Ensure OpenZeppelin contracts are installed
   npm install @openzeppelin/contracts
   
   # Check Solidity version compatibility
   solc --version
   ```

3. **MoonScape API Issues**
   - Verify your API key is correct
   - Check MoonScape service status
   - Ensure network connectivity

4. **Environment Variable Issues**
   ```bash
   # Verify all required variables are set
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv('config/.env')
   
   required = ['HEDERA_OPERATOR_ID', 'HEDERA_OPERATOR_KEY', 'MOONSCAPE_API_KEY']
   for var in required:
       print(f'{var}: {\"✅\" if os.getenv(var) else \"❌\"}')"
   ```

## Next Steps

After successful deployment:

1. **Configure Auditors**: Add approved auditor addresses to your contract
2. **Set HCS-10 Topics**: Configure the communication channels
3. **Test Audit Flow**: Run a complete audit workflow
4. **Monitor Operations**: Set up logging and monitoring

## Support

For additional support:
- **Hedera**: https://docs.hedera.com
- **MoonScape**: support@hashgraphonline.com
- **Project Issues**: Create an issue in the project repository

## Security Considerations

- 🔒 Keep your private keys secure and never commit them to version control
- 🔒 Use environment variables for all sensitive configuration
- 🔒 Regularly backup your contract ABI and deployment information
- 🔒 Monitor contract interactions and audit logs
