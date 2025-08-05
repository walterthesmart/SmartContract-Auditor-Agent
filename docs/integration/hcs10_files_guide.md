# HCS-10 Integration Files Guide

This document provides an overview of the files related to the HCS-10 OpenConvAI integration in the HederaAuditAI project.

## Core Files

### Backend Implementation

- **`backend/src/hedera/hcs10_agent.py`**  
  The main HCS-10 agent implementation that handles agent initialization, topic creation, and message exchange.

- **`backend/src/hedera/integrator.py`**  
  Core Hedera services implementation including topic creation, message submission, and agent registration.

### Configuration

- **`backend/.env`**  
  Contains all necessary credentials and configuration for the HCS-10 integration:
  - `HEDERA_OPERATOR_ID` and `HEDERA_OPERATOR_KEY`: Hedera account credentials
  - `HCS10_REGISTRY_TOPIC_ID`: The topic ID for the HCS-10 registry (0.0.6359793)
  - `HCS10_AGENT_NAME` and `HCS10_AGENT_DESCRIPTION`: Agent metadata
  - `AUDIT_REGISTRY_CONTRACT_ID`: The deployed contract ID (0.0.6359980)

## Smart Contract

- **`contracts/AuditRegistry.sol`**  
  The smart contract that manages audit registrations, approvals, and NFT minting.

## Deployment and Testing

- **`deploy_simple_contract.js`**  
  Node.js script used to deploy the AuditRegistry contract to Hedera testnet.

- **`create_hcs_topic.py`**  
  Python script used to create the HCS-10 registry topic on Hedera testnet.

- **`debug_hcs10_integration.py`**  
  Debug script that verifies the HCS-10 integration components without triggering timeouts.

- **`hcs10_demo.py`**  
  Comprehensive demo script that demonstrates how to use the HCS-10 integration in a real application.

## Documentation

- **`backend/docs/credential_guide.md`**  
  Step-by-step guide for obtaining valid HCS-10 credentials and configuring the integration.

- **`backend/docs/hcs10_implementation_guide.md`**  
  Detailed implementation guide for using the HCS-10 agent in production applications.

- **`backend/docs/hashgraphHSC10.md`**  
  Overview of the HCS-10 OpenConvAI standard and its integration with HederaAuditAI.

## Usage in Applications

To use the HCS-10 integration in your applications:

1. Ensure all required environment variables are set in `.env`
2. Initialize the HederaService with your credentials
3. Initialize the HCS10Agent with the HederaService and registry topic ID
4. Use the agent to create connections, send audit requests, and process responses

For detailed implementation examples, refer to the `hcs10_demo.py` script and the `hcs10_implementation_guide.md` document.
