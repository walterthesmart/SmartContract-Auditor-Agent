# Smart Contract Auditor Agent

An AI-powered auditing tool for Hedera smart contracts with HCS-10 OpenConvAI support and MoonScape platform integration.

## 🌟 Features

### Backend (Python/FastAPI)
- **Smart Contract Analysis**: Static analysis using Slither with custom Hedera rules
- **AI-Powered Explanations**: LLM-based vulnerability explanations and fix suggestions
- **Report Generation**: Professional PDF audit reports
- **Hedera Integration**: File storage and NFT certificate minting
- **HCS-10 OpenConvAI**: Decentralized AI agent communication protocol
- **MoonScape Platform**: Integration with MoonScape ecosystem

### Frontend (Next.js/TypeScript)
- **Modern Web Interface**: Responsive Next.js 14 application with TypeScript
- **Code Editor**: Monaco Editor with Solidity/Vyper syntax highlighting
- **Real-time Updates**: Live audit results and progress tracking
- **File Upload**: Drag & drop contract file upload
- **Interactive Dashboard**: Comprehensive vulnerability analysis display
- **Report Management**: PDF generation, preview, and download
- **NFT Certificates**: Display and manage audit NFT certificates
- **Mobile Responsive**: Optimized for all device sizes

## 🌙 **Deploy to MoonScape - Quick Start**

### **Prerequisites**
- Python 3.10+
- Node.js 16+
- Hedera account with HBAR balance (minimum 50 HBAR)
- Groq API key for LLM processing

### **1. Setup Environment**

```bash
# Clone and navigate to project
git clone <repository_url>
cd Smart-Contract-Auditor-Agent

# Install dependencies
npm install
pip install -r requirements.txt

# Copy environment template
cp config/.env.example config/.env
```

### **2. Configure Environment Variables**

Edit `config/.env` with your credentials:

```bash
# Hedera Network Configuration
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.your_account_id
HEDERA_OPERATOR_KEY=your_private_key_here

# LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-70b-8192

# MoonScape Integration (Optional - get from MoonScape Labs)
MOONSCAPE_API_KEY=your_moonscape_api_key_here
MOONSCAPE_API_BASE=https://api.hashgraphonline.com

# HCS-10 Configuration (Pre-configured)
HCS10_REGISTRY_TOPIC_ID=0.0.6359793
HCS10_AGENT_NAME=HederaAuditAI
HCS10_AGENT_DESCRIPTION=AI-powered auditing tool for Hedera smart contracts
```

### **3. Deploy to MoonScape**

**Option A: Automated Deployment (Recommended)**
```bash
# Windows
deploy_to_moonscape.bat

# Linux/Mac
./deploy_to_moonscape.sh
```

**Option B: Manual Deployment**
```bash
# 1. Check readiness
python scripts/setup/check_deployment_readiness.py

# 2. Deploy contract
node scripts/setup/deploy_audit_registry.js

# 3. Start MoonScape integration
python src/integrations/moonscape/moonscape_integration.py

# 4. Start API server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 5. Set up and start frontend (in a new terminal)
./setup-frontend.sh  # or setup-frontend.bat on Windows
cd frontend && npm run dev
```

### **4. Verify Deployment**

- **Frontend**: Visit http://localhost:3000 for the web interface
- **API**: Check http://localhost:8000/health for backend status
- **API Documentation**: Visit http://localhost:8000/docs for interactive API docs
- **Contract**: Visit https://hashscan.io/testnet and search for your contract ID

## 📊 What Gets Deployed

✅ **AuditRegistry Smart Contract** - Manages audit registrations and NFT certificates
✅ **HCS-10 Agent Registration** - Your AI auditor becomes discoverable on MoonScape
✅ **Topic Communication** - Real-time audit request handling via HCS topics
✅ **API Backend** - RESTful API for contract analysis and reporting
✅ **File Storage** - Audit reports stored on Hedera File Service

## 🚀 Usage After Deployment

### **Frontend Application**
The modern web interface is available at `http://localhost:3000` (development) and provides:

- **Smart Contract Editor**: Upload or paste contract code with syntax highlighting
- **Security Analysis**: Run comprehensive security audits with real-time results
- **Vulnerability Dashboard**: Interactive display of security findings and recommendations
- **Report Generation**: Create and download professional PDF audit reports
- **NFT Certificates**: View and manage blockchain-verified audit certificates
- **Tutorial & Resources**: Built-in guidance and learning materials

### **API Endpoints**
- `POST /analyze` - Analyze smart contract code
- `POST /generate-report` - Generate PDF audit report
- `GET /health` - Health check endpoint
- `POST /upload-contract` - Upload contract file for analysis

### **Example Usage**
```python
import requests

# Analyze a smart contract
response = requests.post("http://localhost:8000/analyze", json={
    "contract_code": "pragma solidity ^0.8.0; contract Example { ... }",
    "contract_metadata": {
        "name": "ExampleContract",
        "language": "solidity"
    }
})

audit_results = response.json()
```

### **MoonScape Integration Features**
- 🔗 **Agent Discovery**: Your auditor appears in MoonScape's agent registry
- 📡 **Request Handling**: Automatically processes audit requests from MoonScape users
- 🤖 **AI Analysis**: Provides intelligent vulnerability detection and explanations
- 📊 **Report Generation**: Creates professional PDF audit reports
- 🎯 **NFT Certificates**: Mints NFTs for successfully audited contracts

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test MoonScape integration specifically
python scripts/demo/api_demo.py

# Check deployment readiness
python scripts/setup/check_deployment_readiness.py
```

## 📚 Documentation

- **[MoonScape Integration Guide](docs/integration/MOONSCAPE_INTEGRATION.md)** - Complete integration details
- **[MoonScape Deployment Guide](docs/deployment/MOONSCAPE_DEPLOYMENT.md)** - Step-by-step deployment

## 🆘 Support

- **Hedera**: https://docs.hedera.com
- **MoonScape**: support@hashgraphonline.com
- **Issues**: Create an issue in this repository

## 🔮 Current Status

### ✅ **Pre-Deployed Components**
- **HCS-10 Registry Topic**: `0.0.6359793` (Active on testnet)
- **Sample Contract**: `0.0.6359980` (Reference implementation)

### 🎯 **Ready for Production**
Your deployment will create a new AuditRegistry contract and register it with MoonScape for immediate use!
