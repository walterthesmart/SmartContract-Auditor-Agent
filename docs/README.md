# Smart Contract Auditor Agent Documentation

Welcome to the Smart Contract Auditor Agent documentation. This directory contains comprehensive documentation for the AI-powered auditing tool for Hedera smart contracts with HCS-10 OpenConvAI support.

## Documentation Structure

### API Documentation
- **[API Reference](api/)** - Complete API documentation and examples

### Integration Guides
- **[HCS-10 Integration Guide](integration/hcs10_implementation_guide.md)** - Complete guide for HCS-10 OpenConvAI integration
- **[HCS-10 Files Guide](integration/hcs10_files_guide.md)** - Understanding HCS-10 file structure
- **[Credential Guide](integration/credential_guide.md)** - Setting up credentials and authentication
- **[MoonScape Integration](integration/MOONSCAPE_INTEGRATION.md)** - Integration with MoonScape platform
- **[MoonScape Guide](integration/moonscape.md)** - Detailed MoonScape integration documentation

### Deployment Documentation
- **[Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md)** - Production deployment guide

### Development Documentation
- **[Research Notes](development/research.md)** - Research and development notes
- **[Logo Instructions](development/logo_instructions.md)** - Logo and branding guidelines
- **[Product Requirements](development/HederaAuditAI_PRD.ipynb)** - Product requirements document

## Quick Start

1. **Setup**: Follow the main [README](../README.md) for initial setup
2. **Configuration**: See [credential guide](integration/credential_guide.md) for configuration
3. **API Usage**: Check [API documentation](api/) for endpoint details
4. **Integration**: Use [HCS-10 guide](integration/hcs10_implementation_guide.md) for blockchain integration

## Key Features

- **Smart Contract Analysis**: Static analysis using Slither with custom Hedera rules
- **AI-Powered Explanations**: LLM-based vulnerability explanations and fix suggestions
- **Report Generation**: Professional PDF audit reports
- **Hedera Integration**: File storage and NFT certificate minting
- **HCS-10 OpenConvAI**: Decentralized AI agent communication protocol
- **MoonScape Platform**: Integration with MoonScape ecosystem

## Architecture Overview

The Smart Contract Auditor Agent follows a modular architecture:

```
src/
├── core/                    # Core auditing functionality
│   ├── analyzer/           # Static analysis engine
│   ├── llm/               # LLM processing
│   ├── report/            # Report generation
│   └── models/            # Data models
├── integrations/          # External integrations
│   ├── hedera/           # Hedera blockchain
│   ├── hcs10/            # HCS-10 protocol
│   └── moonscape/        # MoonScape platform
├── api/                  # REST API layer
└── utils/                # Shared utilities
```

## Contributing

When contributing to the documentation:

1. Follow the existing structure and naming conventions
2. Update this index when adding new documentation
3. Use clear, concise language with practical examples
4. Include code snippets and configuration examples where appropriate

## Support

For questions or issues:
- Check the relevant documentation section first
- Review the main [README](../README.md) for common setup issues
- Consult the [development documentation](development/) for technical details
