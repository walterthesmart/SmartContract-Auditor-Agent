# HCS-10 Implementation Guide for HederaAuditAI

## Overview

This guide provides detailed instructions for implementing the HCS-10 OpenConvAI standard in production applications using the HederaAuditAI backend. The HCS-10 integration enables decentralized AI agent communication for smart contract auditing.

## Prerequisites

- Hedera testnet account with sufficient HBAR
- Deployed AuditRegistry contract (ID: `0.0.6359980`)
- Created HCS-10 registry topic (ID: `0.0.6359793`)
- Properly configured `.env` file with all required variables

## Implementation Steps

### 1. Initialize the HederaService

```python
from src.hedera.integrator import HederaService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Hedera service
hedera_service = HederaService(
    operator_id=os.getenv("HEDERA_OPERATOR_ID"),
    operator_key=os.getenv("HEDERA_OPERATOR_KEY"),
    network="testnet"  # Use "mainnet" for production
)
```

### 2. Initialize the HCS-10 Agent

```python
from src.hedera.hcs10_agent import HCS10Agent
import asyncio

async def initialize_agent():
    """Initialize the HCS-10 agent asynchronously to avoid blocking."""
    try:
        agent = HCS10Agent(
            hedera_service=hedera_service,
            registry_topic_id=os.getenv("HCS10_REGISTRY_TOPIC_ID"),
            agent_name=os.getenv("HCS10_AGENT_NAME"),
            agent_description=os.getenv("HCS10_AGENT_DESCRIPTION")
        )
        return agent
    except Exception as e:
        print(f"Error initializing HCS-10 agent: {e}")
        return None

# Initialize the agent asynchronously
agent_task = asyncio.create_task(initialize_agent())

# Later, when you need the agent:
agent = await agent_task
```

### 3. Create a Connection with Another Agent

```python
# Create a connection with another agent
target_account = "0.0.XXXXX"  # Replace with target account ID
connection = agent.create_connection(target_account)

# Store the connection ID for future reference
connection_id = connection["id"]
```

### 4. Send an Audit Request

```python
# Prepare the smart contract code and metadata
contract_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract {
    // Contract code here
}
"""

contract_metadata = {
    "name": "MyContract",
    "version": "1.0.0",
    "author": "John Doe",
    "license": "MIT"
}

# Send the audit request
agent.send_audit_request(connection_id, contract_code, contract_metadata)
```

### 5. Process Incoming Audit Requests

```python
# Set up a message listener
def message_handler(message):
    """Handle incoming HCS-10 messages."""
    if message["type"] == "audit_request":
        # Extract contract code and metadata
        contract_code = message["content"]["code"]
        contract_metadata = message["content"]["metadata"]
        
        # Process the audit request
        audit_result = process_audit(contract_code, contract_metadata)
        
        # Send the audit result
        agent.send_audit_result(
            message["connection_id"],
            audit_result["result"],
            audit_result["file_id"]
        )

# Register the message handler
agent.register_message_handler(message_handler)

# Start listening for messages
agent.start_listening()
```

### 6. Send Audit Results

```python
# After completing the audit
audit_result = {
    "status": "completed",
    "findings": [
        {
            "severity": "high",
            "title": "Reentrancy vulnerability",
            "description": "The contract is vulnerable to reentrancy attacks",
            "line_number": 42,
            "recommendation": "Use ReentrancyGuard or check-effects-interactions pattern"
        }
    ]
}

# Store the audit report on Hedera File Service
file_id = hedera_service.store_file(
    "Audit Report for MyContract",
    "PDF report content here".encode(),
    "application/pdf"
)

# Send the audit result
agent.send_audit_result(connection_id, audit_result, file_id)
```

## Production Considerations

### Handling Timeouts

The HCS-10 agent initialization involves multiple network calls to the Hedera network, which can cause timeouts. To handle this:

1. **Initialize During Application Startup**: Initialize the agent during application startup, not during request handling.

2. **Use Asynchronous Initialization**: Initialize the agent asynchronously to avoid blocking the main thread.

3. **Implement Retry Logic**: Add retry logic for network operations that might fail.

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=2):
    """Retry decorator for functions that might fail due to network issues."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    print(f"Attempt {attempts} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def initialize_agent():
    # Agent initialization code here
    pass
```

### Monitoring and Logging

Implement comprehensive logging and monitoring for the HCS-10 agent:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hcs10_agent.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("hcs10_agent")

# Log important events
logger.info("Initializing HCS-10 agent")
logger.info(f"Using registry topic: {os.getenv('HCS10_REGISTRY_TOPIC_ID')}")
logger.info(f"Using contract ID: {os.getenv('AUDIT_REGISTRY_CONTRACT_ID')}")

try:
    # Initialize agent
    agent = HCS10Agent(...)
    logger.info("HCS-10 agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize HCS-10 agent: {e}")
```

### Security Considerations

1. **Secure Environment Variables**: Never hardcode sensitive information like private keys.

2. **Input Validation**: Validate all incoming messages before processing them.

3. **Rate Limiting**: Implement rate limiting to prevent abuse.

4. **Error Handling**: Implement proper error handling for all operations.

## Conclusion

The HCS-10 integration enables HederaAuditAI to communicate with other AI agents in a decentralized manner, following the OpenConvAI standard. By following this implementation guide, you can integrate the HCS-10 agent into your production applications and leverage the power of decentralized AI agent communication for smart contract auditing.

For more information, refer to:
- [HCS-10 OpenConvAI Standard](https://github.com/hashgraph/hedera-improvement-proposal/blob/master/HIP/hip-583.md)
- [Credential Guide](credential_guide.md)
- [HederaAuditAI Backend README](../README.md)
