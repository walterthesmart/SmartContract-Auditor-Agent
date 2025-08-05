# HederaAuditAI Backend

## Overview

HederaAuditAI is an AI-powered auditing tool for Hedera smart contracts that provides vulnerability detection, automated suggestions, plain-English reports, and NFT audit certificates. It now supports the HCS-10 OpenConvAI standard for decentralized AI agent communication.

This backend system implements:

- **Static Analysis Engine**: Integrates Slither with custom Hedera rules
- **LLM Processing**: Uses LLaMA 3 (via Groq) for vulnerability explanations and fix suggestions
- **Audit Report Generation**: Creates professional PDF reports
- **Hedera Integration**: Stores reports on Hedera File Service and mints NFT certificates
- **HCS-10 OpenConvAI**: Implements the standard for decentralized AI agent communication

## HCS-10 Integration Status

The HederaAuditAI backend has been successfully integrated with the HCS-10 OpenConvAI standard. The following components have been deployed and configured:

1. **Registry Topic**: Created on Hedera testnet
   - Topic ID: `0.0.6359793`
   - Purpose: Serves as the registry for HCS-10 agents

2. **AuditRegistry Smart Contract**: Deployed on Hedera testnet
   - Contract ID: `0.0.6359980`
   - Purpose: Manages audit registrations, approvals, and NFT minting

3. **Environment Configuration**: Updated in `.env`
   - HCS10_REGISTRY_TOPIC_ID=0.0.6359793
   - HCS10_AGENT_NAME=HederaAuditAI
   - HCS10_AGENT_DESCRIPTION=AI-powered auditing tool for Hedera smart contracts
   - AUDIT_REGISTRY_CONTRACT_ID=0.0.6359980

For detailed instructions on using the HCS-10 integration, see the [credential guide](docs/credential_guide.md).

### Using the HCS-10 Agent in Your Application

To use the HCS-10 agent in your application, follow these steps:

```python
from src.hedera.hcs10_agent import HCS10Agent
from src.hedera.integrator import HederaService

# Initialize the Hedera service
hedera_service = HederaService(
    operator_id=os.getenv("HEDERA_OPERATOR_ID"),
    operator_key=os.getenv("HEDERA_OPERATOR_KEY"),
    network="testnet"
)

# Initialize the agent (note: this may take some time due to network calls)
try:
    agent = HCS10Agent(
        hedera_service=hedera_service,
        registry_topic_id=os.getenv("HCS10_REGISTRY_TOPIC_ID"),
        agent_name=os.getenv("HCS10_AGENT_NAME"),
        agent_description=os.getenv("HCS10_AGENT_DESCRIPTION")
    )
    
    # Create a connection with another account
    connection = agent.create_connection("0.0.XXXXX")  # Replace with target account ID
    
    # Send an audit request
    contract_code = "..."  # Smart contract code
    contract_metadata = {"name": "MyContract", "version": "1.0.0"}
    agent.send_audit_request(connection["id"], contract_code, contract_metadata)
    
    # Later, send audit results
    audit_result = {"status": "passed", "findings": []}
    file_id = "0.0.YYYYY"  # Hedera File ID of the audit report
    agent.send_audit_result(connection["id"], audit_result, file_id)
    
except Exception as e:
    print(f"Error initializing HCS-10 agent: {e}")
```

**Note**: The agent initialization involves several network calls to the Hedera network and may take some time to complete. Consider implementing retry logic or increasing timeouts for production use.

## Architecture

```
backend/
├── src/                      # Source code
│   ├── analyzer/             # Static analysis module
│   ├── llm/                  # LLM processing module
│   ├── report/               # Report generation module
│   ├── hedera/               # Hedera integration module
│   │   ├── integrator.py     # Core Hedera services
│   │   └── hcs10_agent.py    # HCS-10 OpenConvAI agent
│   └── api/                  # API endpoints
├── tests/                    # Test suite
├── docs/                     # Documentation
├── pyproject.toml            # Project configuration
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
└── Dockerfile                # Containerization
```

## Features

- **Smart Contract Analysis**: Scan Solidity/Vyper contracts for vulnerabilities
- **AI-Powered Explanations**: Get plain-English descriptions of issues
- **Automated Fix Suggestions**: Receive code fixes with inline comments
- **Test Case Generation**: Get example test cases to verify fixes
- **PDF Report Generation**: Generate comprehensive audit reports
- **Hedera Integration**: Store reports on Hedera and mint NFT certificates
- **HCS-10 OpenConvAI**: Decentralized AI agent communication
  - Agent identity and discovery
  - Secure communication channels
  - Approval-required transactions

## Installation

### Prerequisites

- Python 3.8+
- Slither and its dependencies
- Access to Groq API (for LLaMA 3)
- Hedera account credentials

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/HederaAuditAI.git
   cd HederaAuditAI/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Create a `.env` file with your credentials (see `.env.example` for a template):
   ```
   # Groq API (for Llama 3)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama3-70b-8192

   # Hedera Network
   HEDERA_NETWORK=testnet
   HEDERA_OPERATOR_ID=0.0.1234
   HEDERA_OPERATOR_KEY=your_private_key_here
   
   # HCS-10 OpenConvAI Configuration
   HCS10_REGISTRY_TOPIC_ID=0.0.123456  # Optional, for agent registration
   HCS10_AGENT_NAME=HederaAuditAI
   HCS10_AGENT_DESCRIPTION=AI-powered auditing tool for Hedera smart contracts
   ```

## Usage

### Running the API Server

```bash
uvicorn src.api.main:app --reload
```

The API will be available at http://localhost:8000

### API Endpoints

#### Core Auditing Endpoints
- `POST /analyze`: Submit a smart contract for analysis
- `POST /generate-report`: Generate audit reports
- `POST /upload-contract`: Upload a contract file for analysis

#### HCS-10 OpenConvAI Endpoints
- `GET /hcs10/topics`: Get agent topic IDs
- `POST /hcs10/connections`: Create a connection with another account
- `POST /hcs10/audit-request`: Send an audit request through HCS-10
- `POST /hcs10/audit-result`: Send audit results through HCS-10
- `POST /hcs10/request-approval`: Request approval for NFT minting

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Type checking
mypy src

# Linting
flake8 src tests
```

## Docker

Build and run the Docker container:

```bash
docker build -t hedera-audit-ai .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key hedera-audit-ai
```

## License

MIT
