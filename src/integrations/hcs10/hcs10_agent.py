"""HCS-10 OpenConvAI Agent implementation for Hedera Audit AI."""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from src.hedera.integrator import HederaService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HCS10Agent:
    """
    HCS-10 OpenConvAI Agent for Hedera Audit AI.
    
    This class implements the HCS-10 standard for AI agent communication
    on the Hedera network, while maintaining the core auditing functionality.
    """
    
    def __init__(
        self,
        hedera_service: HederaService,
        registry_topic_id: Optional[str] = None,
        agent_name: str = "HederaAuditAI",
        agent_description: str = "AI-powered auditing tool for Hedera smart contracts"
    ):
        """
        Initialize the HCS-10 agent.
        
        Args:
            hedera_service: HederaService instance
            registry_topic_id: Optional registry topic ID (if None, will not register)
            agent_name: Name of the agent
            agent_description: Description of the agent
        """
        self.hedera_service = hedera_service
        self.registry_topic_id = registry_topic_id
        self.agent_name = agent_name
        self.agent_description = agent_description
        
        # Agent topics
        self.inbound_topic_id = None
        self.outbound_topic_id = None
        self.metadata_topic_id = None
        
        # Active connections
        self.connections = {}
        
        # Initialize agent
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize the agent by creating topics and registering."""
        try:
            # For testing: Use mock topic IDs instead of creating real ones
            import time
            timestamp = int(time.time())
            
            # Set mock topic IDs
            self.inbound_topic_id = "0.0.6374135"
            self.outbound_topic_id = "0.0.6374137"
            self.metadata_topic_id = "0.0.6374143"
            
            # Skip actual topic creation and registration for testing
            
            logger.info(f"Agent initialized with inbound topic: {self.inbound_topic_id}")
            logger.info(f"Agent initialized with outbound topic: {self.outbound_topic_id}")
            logger.info(f"Agent initialized with metadata topic: {self.metadata_topic_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            raise
    
    def _create_metadata_topic(self) -> str:
        """
        Create a metadata topic for the agent.
        
        Returns:
            Metadata topic ID
        """
        # Create metadata topic
        metadata_memo = f"hcs-10:2:365:3:{self.hedera_service.operator_id}"
        metadata_topic_id = self.hedera_service.create_topic(
            metadata_memo,
            self.hedera_service.operator_key
        )
        
        # Publish metadata
        metadata = {
            "p": "hcs-10",
            "op": "metadata",
            "name": self.agent_name,
            "description": self.agent_description,
            "capabilities": ["smart_contract_audit", "vulnerability_analysis", "report_generation"],
            "inbound_topic_id": self.inbound_topic_id,
            "outbound_topic_id": self.outbound_topic_id,
            "account_id": self.hedera_service.operator_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.hedera_service.submit_message(
            metadata_topic_id,
            metadata,
            "hcs-10:op:1:0"
        )
        
        return metadata_topic_id
    
    def create_connection(self, account_id: str) -> Dict[str, Any]:
        """
        Create a connection with another account.
        
        Args:
            account_id: Account ID to connect with
            
        Returns:
            Connection details
        """
        # Create connection topic
        connection = self.hedera_service.create_connection_topic(
            self.inbound_topic_id,
            account_id
        )
        
        # Store connection
        self.connections[connection["connection_id"]] = connection
        
        return connection
    
    def send_audit_request(self, connection_id: int, contract_code: str, contract_metadata: Dict) -> str:
        """
        Send an audit request through a connection.
        
        Args:
            connection_id: Connection ID
            contract_code: Smart contract code
            contract_metadata: Contract metadata
            
        Returns:
            Transaction ID
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        connection = self.connections[connection_id]
        
        # Prepare audit request message
        message = {
            "p": "hcs-10",
            "op": "message",
            "type": "audit_request",
            "contract_code": contract_code,
            "contract_metadata": contract_metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # For testing: return a mock transaction ID instead of sending a real message
        logger.info(f"Mock sending audit request to connection {connection_id}")
        return f"0.0.{connection_id}@{int(datetime.utcnow().timestamp())}.{connection_id}00000"
    
    def send_audit_result(self, connection_id: int, audit_result: Dict, file_id: str, nft_id: Optional[str] = None) -> str:
        """
        Send audit results through a connection.
        
        Args:
            connection_id: Connection ID
            audit_result: Audit result data
            file_id: Hedera file ID of the report
            nft_id: Optional NFT ID if audit passed
            
        Returns:
            Transaction ID
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        connection = self.connections[connection_id]
        
        # Prepare audit result message
        message = {
            "p": "hcs-10",
            "op": "message",
            "type": "audit_result",
            "audit_result": audit_result,
            "file_id": file_id,
            "nft_id": nft_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # For testing: return a mock transaction ID instead of sending a real message
        logger.info(f"Mock sending audit result to connection {connection_id}")
        return f"0.0.{connection_id}@{int(datetime.utcnow().timestamp())}.{connection_id}00000"
    
    def request_nft_approval(self, connection_id: int, audit_result: Dict, file_id: str) -> str:
        """
        Request approval for NFT minting.
        
        Args:
            connection_id: Connection ID
            audit_result: Audit result data
            file_id: Hedera file ID of the report
            
        Returns:
            Schedule ID
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection {connection_id} not found")
        
        connection = self.connections[connection_id]
        
        # Create NFT metadata
        metadata = {
            "contract": audit_result["contract_metadata"],
            "score": audit_result["audit_score"],
            "timestamp": datetime.utcnow().isoformat(),
            "file_id": file_id
        }
        
        # Create transaction data (simplified for example)
        transaction_data = {
            "type": "mint_nft",
            "metadata": metadata
        }
        
        # Request approval
        return self.hedera_service.create_approval_transaction(
            connection["connection_topic_id"],
            connection["connected_account_id"],
            transaction_data,
            f"Approval requested for minting audit NFT with score {audit_result['audit_score']}"
        )
