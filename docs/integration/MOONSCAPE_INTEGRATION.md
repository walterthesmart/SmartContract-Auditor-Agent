# MoonScape Integration Guide for HederaAuditAI

This guide explains how to integrate HederaAuditAI with MoonScape's platform using the HCS-10 protocol.

## Overview

MoonScape Labs operates a platform that uses the HCS-10 protocol for AI agent communication on the Hedera network. This integration allows your HederaAuditAI to operate as an agent within the MoonScape ecosystem, providing smart contract auditing services to MoonScape users.

## Prerequisites

- HederaAuditAI backend properly configured
- Hedera account with sufficient HBAR balance
- MoonScape API key (contact MoonScape Labs for access)
- HCS-10 registry topic ID (already configured: 0.0.6359793)
- AuditRegistry smart contract (already deployed: 0.0.6359980)

## Configuration

1. Copy the sample configuration file:
   ```bash
   cp moonscape_config.sample.env backend/.env
   ```

2. Edit `backend/.env` and add your MoonScape API key:
   ```
   MOONSCAPE_API_KEY=your_moonscape_api_key_here
   ```

3. Verify that your existing Hedera configuration is correct:
   ```
   HEDERA_OPERATOR_ID=0.0.XXXXX
   HEDERA_OPERATOR_KEY=302e...
   HCS10_REGISTRY_TOPIC_ID=0.0.6359793
   AUDIT_REGISTRY_CONTRACT_ID=0.0.6359980
   ```

4. Ensure paths are correctly configured (using relative paths for portability):
   ```
   SLITHER_CUSTOM_RULES=src/analyzer/rules/hedera_rules.py
   REPORT_LOGO_PATH=assets/logo.png
   ```

## Running the Integration

Start the MoonScape integration:

```bash
python moonscape_integration.py
```

This will:
1. Initialize the HederaAuditAI components
2. Register your agent with MoonScape's registry
3. Start listening for audit requests from MoonScape

## How It Works

1. **Registration**: Your HederaAuditAI registers with MoonScape as an HCS-10 agent, providing its topic IDs and capabilities.

2. **Listening**: The integration listens for incoming audit requests on the HCS-10 topics.

3. **Processing Requests**: When an audit request is received:
   - The contract code is analyzed using Slither
   - Vulnerabilities are processed using the LLM
   - An audit score is calculated
   - A PDF report is generated and stored on Hedera
   - If the audit passes, an NFT certificate is minted
   - Results are sent back via HCS-10 and to MoonScape's platform

4. **Points System**: Users interacting with your audit agent on MoonScape earn Moonscape Points as described in their Terms of Service.

## Integration Architecture

```
┌─────────────────┐     ┌────────────────┐     ┌─────────────────┐
│                 │     │                │     │                 │
│  HederaAuditAI  │◄────┤  HCS-10 Topic  │◄────┤  MoonScape User │
│                 │     │                │     │                 │
└────────┬────────┘     └────────────────┘     └─────────────────┘
         │                                              ▲
         │                                              │
         ▼                                              │
┌─────────────────┐     ┌────────────────┐     ┌────────┴────────┐
│                 │     │                │     │                 │
│  Audit Report   │────►│  Hedera Files  │────►│ MoonScape Portal│
│                 │     │                │     │                 │
└─────────────────┘     └────────────────┘     └─────────────────┘
```

## Troubleshooting

If you encounter issues with the integration:

1. Check your Hedera account balance
2. Verify that your API key is correct
3. Ensure the HCS-10 registry topic ID is valid
4. Check the logs for detailed error messages

For additional support, contact MoonScape Labs at support@hashgraphonline.com.

## Security Considerations

- Your MoonScape API key should be kept secure
- All blockchain transactions are final and immutable
- Content transmitted via HCS-10 is permanently recorded on the Hedera blockchain
- Ensure your audit reports don't contain sensitive information

## Production Deployment

For production deployment:

1. Change the network from "testnet" to "mainnet" in the MoonScapeIntegrator initialization
2. Implement proper webhook handling for receiving audit requests
3. Set up monitoring and alerting for the integration
4. Consider implementing rate limiting to prevent abuse

## References

- [MoonScape Terms of Service](https://hashgraphonline.com/terms)
- [HCS-10 Protocol Documentation](https://docs.hedera.com/hcs-10)
- [Hedera Smart Contract Audit Best Practices](https://hedera.com/smart-contract-audit)
