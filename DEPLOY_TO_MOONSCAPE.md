# 🌙 Deploy to MoonScape - Complete Guide

This guide will help you deploy your Smart Contract Auditor Agent to the MoonScape platform.

## ✅ Prerequisites Verified

Your system is ready for deployment! All checks passed:
- ✅ Node.js v20.14.0
- ✅ Python 3.12.4  
- ✅ All dependencies installed
- ✅ Environment configured
- ✅ Contract files ready

## 🚀 Deployment Options

### Option 1: Automated Deployment (Recommended)

```bash
# Windows
.\deploy_to_moonscape.bat

# Linux/Mac  
./deploy_to_moonscape.sh
```

### Option 2: Manual Step-by-Step

#### Step 1: Deploy the Contract
```bash
node scripts/setup/deploy_audit_registry.js
```

#### Step 2: Start MoonScape Integration
```bash
python src/integrations/moonscape/moonscape_integration.py
```

#### Step 3: Start the API Server
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Troubleshooting

### Network Connectivity Issues

If you encounter network errors like "2 UNKNOWN", try:

1. **Check Hedera Network Status**
   - Visit: https://status.hedera.com
   - Ensure testnet is operational

2. **Verify Network Connection**
   ```bash
   # Test connectivity to Hedera
   ping testnet.mirrornode.hedera.com
   ```

3. **Check Firewall/Proxy Settings**
   - Ensure ports 50211, 50212 are open for Hedera gRPC
   - Disable VPN if using one
   - Check corporate firewall settings

4. **Retry Deployment**
   ```bash
   # Wait a few minutes and retry
   node scripts/setup/deploy_audit_registry.js
   ```

### Alternative: Use Existing Contract

If deployment fails, you can use the pre-deployed contract:

1. **Update your .env file:**
   ```bash
   AUDIT_REGISTRY_CONTRACT_ID=0.0.6359980
   ```

2. **Start the services:**
   ```bash
   # Start MoonScape integration
   python src/integrations/moonscape/moonscape_integration.py &

   # Start API server
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

## 📊 What Gets Deployed

When successful, your deployment creates:

✅ **New AuditRegistry Contract** - Your own instance on Hedera testnet  
✅ **HCS-10 Agent Registration** - Discoverable on MoonScape  
✅ **Topic Communication** - Real-time audit request handling  
✅ **API Backend** - RESTful API at http://localhost:8000  
✅ **File Storage** - Reports stored on Hedera File Service  

## 🎯 Verification Steps

After deployment:

1. **Check Contract on HashScan**
   - Visit: https://hashscan.io/testnet
   - Search for your contract ID

2. **Test API Health**
   ```bash
   curl http://localhost:8000/health
   ```

3. **View API Documentation**
   - Visit: http://localhost:8000/docs

4. **Test Contract Analysis**
   ```bash
   python scripts/demo/api_demo.py
   ```

## 🌙 MoonScape Integration Features

Once deployed, your auditor provides:

- 🔗 **Agent Discovery**: Appears in MoonScape's agent registry
- 📡 **Request Handling**: Processes audit requests automatically  
- 🤖 **AI Analysis**: Intelligent vulnerability detection
- 📊 **Report Generation**: Professional PDF audit reports
- 🎯 **NFT Certificates**: Mints NFTs for audited contracts

## 📋 Next Steps

1. **Get MoonScape API Key** (Optional)
   - Contact: support@hashgraphonline.com
   - Add to config/.env: `MOONSCAPE_API_KEY=your_key_here`

2. **Configure Auditors**
   - Add approved auditor addresses to your contract

3. **Test Full Workflow**
   - Submit a contract for analysis
   - Generate audit report
   - Mint NFT certificate

4. **Monitor Operations**
   - Check logs for audit requests
   - Monitor contract interactions

## 🆘 Support

- **Hedera Issues**: https://docs.hedera.com
- **MoonScape Support**: support@hashgraphonline.com
- **Project Issues**: Create an issue in this repository

## 🔄 Current Status

Your environment is **READY** for deployment. If you encounter network issues, they are likely temporary. Try again in a few minutes or use the alternative approach with the pre-deployed contract.

---

**Ready to deploy?** Run `.\deploy_to_moonscape.bat` when the network is available!
