"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the Smart Contract Auditor Agent."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to environment file. If None, looks for .env in config directory.
        """
        if env_file is None:
            # Default to config/.env in project root
            project_root = Path(__file__).parent.parent.parent
            env_file = project_root / "config" / ".env"
        
        if Path(env_file).exists():
            load_dotenv(env_file)
    
    @property
    def groq_api_key(self) -> str:
        """Get Groq API key."""
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        return key
    
    @property
    def groq_model(self) -> str:
        """Get Groq model name."""
        return os.getenv("GROQ_MODEL", "llama3-70b-8192")
    
    @property
    def hedera_network(self) -> str:
        """Get Hedera network."""
        return os.getenv("HEDERA_NETWORK", "testnet")
    
    @property
    def hedera_operator_id(self) -> str:
        """Get Hedera operator ID."""
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        if not operator_id:
            raise ValueError("HEDERA_OPERATOR_ID environment variable not set")
        return operator_id
    
    @property
    def hedera_operator_key(self) -> str:
        """Get Hedera operator key."""
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")
        if not operator_key:
            raise ValueError("HEDERA_OPERATOR_KEY environment variable not set")
        return operator_key
    
    @property
    def slither_custom_rules(self) -> Optional[str]:
        """Get Slither custom rules path."""
        return os.getenv("SLITHER_CUSTOM_RULES")
    
    @property
    def slither_timeout(self) -> int:
        """Get Slither analysis timeout."""
        return int(os.getenv("SLITHER_ANALYSIS_TIMEOUT", "300"))
    
    @property
    def hcs10_registry_topic_id(self) -> Optional[str]:
        """Get HCS-10 registry topic ID."""
        return os.getenv("HCS10_REGISTRY_TOPIC_ID")
    
    @property
    def hcs10_agent_name(self) -> str:
        """Get HCS-10 agent name."""
        return os.getenv("HCS10_AGENT_NAME", "HederaAuditAI")
    
    @property
    def hcs10_agent_description(self) -> str:
        """Get HCS-10 agent description."""
        return os.getenv("HCS10_AGENT_DESCRIPTION", "AI-powered auditing tool for Hedera smart contracts")


# Global configuration instance
config = Config()
