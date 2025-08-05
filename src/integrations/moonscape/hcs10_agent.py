"""
HCS-10 OpenConvAI Agent Implementation for MoonScape Integration
Based on the official HCS-10 standard: https://hashgraphonline.com/docs/standards/hcs-10
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from hedera import (
    Client, 
    TopicCreateTransaction, 
    TopicMessageSubmitTransaction,
    TopicMessageQuery,
    PrivateKey,
    AccountId,
    TopicId,
    Hbar
)

logger = logging.getLogger(__name__)

@dataclass
class HCS10Message:
    """Represents an HCS-10 protocol message"""
    p: str = "hcs-10"  # Protocol identifier
    op: str = ""       # Operation type
    operator_id: str = ""  # Agent identifier in format inboundTopicId@accountId
    data: str = ""     # Message content or HRL reference
    m: str = ""        # Optional memo

@dataclass
class AgentConnection:
    """Represents a connection between agents"""
    connection_id: str
    connection_topic_id: str
    connected_account_id: str
    status: str = "active"  # active, closed
    created_at: datetime = None

class HCS10Agent:
    """
    HCS-10 OpenConvAI Agent for Smart Contract Auditor
    Implements the full HCS-10 standard for MoonScape integration
    """
    
    def __init__(self, 
                 client: Client,
                 account_id: str,
                 private_key: str,
                 agent_name: str = "HederaAuditAI",
                 agent_description: str = "AI-powered smart contract auditor"):
        
        self.client = client
        self.account_id = AccountId.fromString(account_id)
        self.private_key = PrivateKey.fromStringECDSA(private_key)
        self.agent_name = agent_name
        self.agent_description = agent_description
        
        # HCS-10 Topics
        self.inbound_topic_id: Optional[TopicId] = None
        self.outbound_topic_id: Optional[TopicId] = None
        self.registry_topic_id: Optional[TopicId] = None
        
        # Connection management
        self.connections: Dict[str, AgentConnection] = {}
        self.message_handlers = {}
        
        # Set operator
        self.client.setOperator(self.account_id, self.private_key)
        
        logger.info(f"Initialized HCS-10 Agent: {agent_name}")

    async def initialize_agent(self, registry_topic_id: str = None) -> Dict[str, str]:
        """
        Initialize the agent by creating required topics and registering with MoonScape
        
        Returns:
            Dict containing topic IDs and registration status
        """
        try:
            logger.info("🚀 Initializing HCS-10 Agent for MoonScape...")
            
            # Step 1: Create Outbound Topic (agent's public activity log)
            await self._create_outbound_topic()
            
            # Step 2: Create Inbound Topic (for receiving connection requests)
            await self._create_inbound_topic()
            
            # Step 3: Register with MoonScape Registry
            if registry_topic_id:
                self.registry_topic_id = TopicId.fromString(registry_topic_id)
                await self._register_with_registry()
            
            # Step 4: Start listening for connection requests
            asyncio.create_task(self._listen_for_connections())
            
            result = {
                "status": "initialized",
                "agent_name": self.agent_name,
                "account_id": str(self.account_id),
                "inbound_topic_id": str(self.inbound_topic_id),
                "outbound_topic_id": str(self.outbound_topic_id),
                "registry_topic_id": str(self.registry_topic_id) if self.registry_topic_id else None,
                "operator_id": f"{self.inbound_topic_id}@{self.account_id}"
            }
            
            logger.info("✅ HCS-10 Agent initialized successfully")
            logger.info(f"📋 Agent ID: {result['operator_id']}")
            logger.info(f"📥 Inbound Topic: {result['inbound_topic_id']}")
            logger.info(f"📤 Outbound Topic: {result['outbound_topic_id']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize HCS-10 Agent: {e}")
            raise

    async def _create_outbound_topic(self):
        """Create outbound topic for public activity log"""
        try:
            # HCS-10 outbound topic memo format: hcs-10:0:{ttl}:1
            memo = "hcs-10:0:60:1"
            
            transaction = (TopicCreateTransaction()
                          .setTopicMemo(memo)
                          .setSubmitKey(self.private_key.getPublicKey())  # Only agent can write
                          .setMaxTransactionFee(Hbar.fromHbars(2)))
            
            response = await transaction.execute(self.client)
            receipt = await response.getReceipt(self.client)
            
            self.outbound_topic_id = receipt.topicId
            logger.info(f"📤 Created outbound topic: {self.outbound_topic_id}")
            
        except Exception as e:
            logger.error(f"Failed to create outbound topic: {e}")
            raise

    async def _create_inbound_topic(self):
        """Create inbound topic for receiving connection requests"""
        try:
            # HCS-10 inbound topic memo format: hcs-10:0:{ttl}:0:{accountId}
            memo = f"hcs-10:0:60:0:{self.account_id}"
            
            # Public topic - no submit key (anyone can send connection requests)
            transaction = (TopicCreateTransaction()
                          .setTopicMemo(memo)
                          .setMaxTransactionFee(Hbar.fromHbars(2)))
            
            response = await transaction.execute(self.client)
            receipt = await response.getReceipt(self.client)
            
            self.inbound_topic_id = receipt.topicId
            logger.info(f"📥 Created inbound topic: {self.inbound_topic_id}")
            
        except Exception as e:
            logger.error(f"Failed to create inbound topic: {e}")
            raise

    async def _register_with_registry(self):
        """Register agent with the MoonScape HCS-10 registry"""
        try:
            # HCS-10 register operation
            register_message = HCS10Message(
                op="register",
                account_id=str(self.account_id),
                m=f"Registering {self.agent_name} - AI-powered smart contract auditor"
            )
            
            # Submit to registry with proper transaction memo
            transaction = (TopicMessageSubmitTransaction()
                          .setTopicId(self.registry_topic_id)
                          .setMessage(json.dumps(register_message.__dict__))
                          .setTransactionMemo("hcs-10:op:0:0")  # register operation on registry
                          .setMaxTransactionFee(Hbar.fromHbars(1)))
            
            response = await transaction.execute(self.client)
            receipt = await response.getReceipt(self.client)
            
            logger.info(f"✅ Registered with MoonScape registry: {self.registry_topic_id}")
            logger.info(f"📋 Registration transaction: {response.transactionId}")
            
        except Exception as e:
            logger.error(f"Failed to register with registry: {e}")
            raise

    async def _listen_for_connections(self):
        """Listen for incoming connection requests on inbound topic"""
        try:
            logger.info(f"👂 Listening for connections on: {self.inbound_topic_id}")
            
            query = TopicMessageQuery().setTopicId(self.inbound_topic_id)
            
            def handle_message(message):
                try:
                    content = message.contents.decode('utf-8')
                    data = json.loads(content)
                    
                    if data.get('p') == 'hcs-10' and data.get('op') == 'connection_request':
                        asyncio.create_task(self._handle_connection_request(data, message))
                        
                except Exception as e:
                    logger.error(f"Error processing inbound message: {e}")
            
            query.subscribe(self.client, handle_message)
            
        except Exception as e:
            logger.error(f"Failed to listen for connections: {e}")

    async def _handle_connection_request(self, request_data: Dict, message):
        """Handle incoming connection request"""
        try:
            operator_id = request_data.get('operator_id', '')
            requester_info = operator_id.split('@')
            
            if len(requester_info) != 2:
                logger.warning(f"Invalid operator_id format: {operator_id}")
                return
            
            requester_inbound_topic, requester_account = requester_info
            connection_id = str(message.sequenceNumber)
            
            logger.info(f"📨 Connection request from: {operator_id}")
            
            # Create connection topic for private communication
            connection_topic_id = await self._create_connection_topic(
                requester_account, connection_id
            )
            
            # Send connection_created response
            await self._send_connection_created(
                connection_topic_id, requester_account, operator_id, connection_id
            )
            
            # Record connection in outbound topic
            await self._record_outbound_connection_created(
                connection_topic_id, requester_account, operator_id, connection_id
            )
            
            # Store connection
            self.connections[connection_id] = AgentConnection(
                connection_id=connection_id,
                connection_topic_id=str(connection_topic_id),
                connected_account_id=requester_account,
                created_at=datetime.now()
            )
            
            # Start listening on the connection topic
            asyncio.create_task(self._listen_on_connection(connection_topic_id, connection_id))
            
            logger.info(f"✅ Connection established: {connection_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle connection request: {e}")

    async def _create_connection_topic(self, requester_account: str, connection_id: str) -> TopicId:
        """Create a private connection topic with threshold key"""
        try:
            # HCS-10 connection topic memo format: hcs-10:1:{ttl}:2:{inboundTopicId}:{connectionId}
            memo = f"hcs-10:1:60:2:{self.inbound_topic_id}:{connection_id}"
            
            # Create threshold key for both parties
            requester_key = AccountId.fromString(requester_account).toSolidityAddress()
            agent_key = self.private_key.getPublicKey()
            
            transaction = (TopicCreateTransaction()
                          .setTopicMemo(memo)
                          .setSubmitKey(agent_key)  # For now, use agent's key
                          .setMaxTransactionFee(Hbar.fromHbars(2)))
            
            response = await transaction.execute(self.client)
            receipt = await response.getReceipt(self.client)
            
            logger.info(f"🔗 Created connection topic: {receipt.topicId}")
            return receipt.topicId
            
        except Exception as e:
            logger.error(f"Failed to create connection topic: {e}")
            raise

    async def send_audit_offer(self, connection_id: str, contract_code: str, 
                              estimated_cost: float = 0.0) -> bool:
        """
        Send an audit offer to a connected user
        
        Args:
            connection_id: The connection ID
            contract_code: The smart contract code to audit
            estimated_cost: Estimated cost in HBAR
            
        Returns:
            bool: Success status
        """
        try:
            if connection_id not in self.connections:
                logger.error(f"Connection {connection_id} not found")
                return False
            
            connection = self.connections[connection_id]
            
            # Prepare audit offer message
            offer_data = {
                "type": "audit_offer",
                "contract_preview": contract_code[:200] + "..." if len(contract_code) > 200 else contract_code,
                "estimated_cost_hbar": estimated_cost,
                "estimated_time_minutes": 5,
                "capabilities": [
                    "Vulnerability detection",
                    "Gas optimization analysis", 
                    "Best practices review",
                    "Security recommendations",
                    "Professional PDF report"
                ],
                "agent_info": {
                    "name": self.agent_name,
                    "description": self.agent_description,
                    "version": "1.0.0"
                }
            }
            
            message = HCS10Message(
                op="message",
                operator_id=f"{self.inbound_topic_id}@{self.account_id}",
                data=json.dumps(offer_data),
                m="Smart contract audit offer"
            )
            
            # Send message to connection topic
            topic_id = TopicId.fromString(connection.connection_topic_id)
            transaction = (TopicMessageSubmitTransaction()
                          .setTopicId(topic_id)
                          .setMessage(json.dumps(message.__dict__))
                          .setTransactionMemo("hcs-10:op:6:3")  # message operation on connection topic
                          .setMaxTransactionFee(Hbar.fromHbars(1)))
            
            response = await transaction.execute(self.client)
            await response.getReceipt(self.client)
            
            logger.info(f"📤 Sent audit offer to connection: {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send audit offer: {e}")
            return False

    async def send_audit_results(self, connection_id: str, audit_results: Dict, 
                                report_file_id: str = None) -> bool:
        """
        Send audit results to a connected user
        
        Args:
            connection_id: The connection ID
            audit_results: The audit analysis results
            report_file_id: Optional Hedera File ID for PDF report
            
        Returns:
            bool: Success status
        """
        try:
            if connection_id not in self.connections:
                logger.error(f"Connection {connection_id} not found")
                return False
            
            connection = self.connections[connection_id]
            
            # Prepare audit results message
            results_data = {
                "type": "audit_results",
                "summary": {
                    "total_issues": len(audit_results.get('findings', [])),
                    "critical_issues": len([f for f in audit_results.get('findings', []) if f.get('severity') == 'critical']),
                    "high_issues": len([f for f in audit_results.get('findings', []) if f.get('severity') == 'high']),
                    "medium_issues": len([f for f in audit_results.get('findings', []) if f.get('severity') == 'medium']),
                    "low_issues": len([f for f in audit_results.get('findings', []) if f.get('severity') == 'low'])
                },
                "findings": audit_results.get('findings', [])[:5],  # First 5 findings
                "recommendations": audit_results.get('recommendations', [])[:3],  # Top 3 recommendations
                "report_file_id": report_file_id,
                "timestamp": datetime.now().isoformat(),
                "agent_signature": f"Audited by {self.agent_name}"
            }
            
            # Use HRL reference if data is too large
            data_str = json.dumps(results_data)
            if len(data_str) > 1000:  # 1KB limit
                # TODO: Store large data using HCS-1 and use HRL reference
                data_content = f"Large audit results available. Report file: {report_file_id}"
            else:
                data_content = data_str
            
            message = HCS10Message(
                op="message",
                operator_id=f"{self.inbound_topic_id}@{self.account_id}",
                data=data_content,
                m="Smart contract audit results"
            )
            
            # Send message to connection topic
            topic_id = TopicId.fromString(connection.connection_topic_id)
            transaction = (TopicMessageSubmitTransaction()
                          .setTopicId(topic_id)
                          .setMessage(json.dumps(message.__dict__))
                          .setTransactionMemo("hcs-10:op:6:3")  # message operation on connection topic
                          .setMaxTransactionFee(Hbar.fromHbars(1)))
            
            response = await transaction.execute(self.client)
            await response.getReceipt(self.client)
            
            logger.info(f"📤 Sent audit results to connection: {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send audit results: {e}")
            return False

    async def _listen_on_connection(self, topic_id: TopicId, connection_id: str):
        """Listen for messages on a specific connection topic"""
        try:
            logger.info(f"👂 Listening on connection {connection_id}: {topic_id}")
            
            query = TopicMessageQuery().setTopicId(topic_id)
            
            def handle_message(message):
                try:
                    content = message.contents.decode('utf-8')
                    data = json.loads(content)
                    
                    if data.get('p') == 'hcs-10':
                        asyncio.create_task(self._process_connection_message(
                            data, connection_id, message
                        ))
                        
                except Exception as e:
                    logger.error(f"Error processing connection message: {e}")
            
            query.subscribe(self.client, handle_message)
            
        except Exception as e:
            logger.error(f"Failed to listen on connection: {e}")

    async def _process_connection_message(self, data: Dict, connection_id: str, message):
        """Process incoming message on connection topic"""
        try:
            op = data.get('op')
            operator_id = data.get('operator_id', '')
            message_data = data.get('data', '')
            
            logger.info(f"📨 Received {op} from {operator_id} on connection {connection_id}")
            
            if op == "message":
                # Handle user message - could be audit request, question, etc.
                await self._handle_user_message(connection_id, message_data, operator_id)
                
            elif op == "close_connection":
                # Handle connection closure
                await self._handle_connection_close(connection_id, operator_id)
                
        except Exception as e:
            logger.error(f"Error processing connection message: {e}")

    async def _handle_user_message(self, connection_id: str, message_data: str, operator_id: str):
        """Handle incoming user message"""
        try:
            # Parse message if it's JSON
            try:
                parsed_data = json.loads(message_data)
                message_type = parsed_data.get('type', 'text')
                
                if message_type == 'audit_request':
                    # Handle audit request
                    contract_code = parsed_data.get('contract_code', '')
                    if contract_code:
                        logger.info(f"🔍 Audit request received from {operator_id}")
                        # TODO: Integrate with your audit engine
                        # For now, send a sample offer
                        await self.send_audit_offer(connection_id, contract_code, 5.0)
                    
                elif message_type == 'audit_accept':
                    # User accepted audit offer
                    logger.info(f"✅ Audit accepted by {operator_id}")
                    # TODO: Start actual audit process
                    
            except json.JSONDecodeError:
                # Plain text message
                logger.info(f"💬 Text message from {operator_id}: {message_data[:100]}...")
                
        except Exception as e:
            logger.error(f"Error handling user message: {e}")

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for MoonScape display"""
        return {
            "agent_name": self.agent_name,
            "description": self.agent_description,
            "account_id": str(self.account_id),
            "inbound_topic_id": str(self.inbound_topic_id) if self.inbound_topic_id else None,
            "outbound_topic_id": str(self.outbound_topic_id) if self.outbound_topic_id else None,
            "operator_id": f"{self.inbound_topic_id}@{self.account_id}" if self.inbound_topic_id else None,
            "capabilities": [
                "Smart contract vulnerability detection",
                "Gas optimization analysis",
                "Security best practices review", 
                "Professional audit reports",
                "NFT certificate generation"
            ],
            "supported_languages": ["Solidity"],
            "status": "active",
            "connections": len(self.connections),
            "version": "1.0.0"
        }

    async def close(self):
        """Clean up resources"""
        try:
            # Close all connections
            for connection_id in list(self.connections.keys()):
                await self._handle_connection_close(connection_id, "system")
            
            logger.info("🔒 HCS-10 Agent closed")
            
        except Exception as e:
            logger.error(f"Error closing agent: {e}")

# Helper functions for message creation
async def _send_connection_created(self, topic_id: TopicId, requester_account: str, 
                                  operator_id: str, connection_id: str):
    """Send connection_created message to inbound topic"""
    message = HCS10Message(
        op="connection_created",
        connection_topic_id=str(topic_id),
        connected_account_id=requester_account,
        operator_id=f"{self.inbound_topic_id}@{self.account_id}",
        connection_id=int(connection_id),
        m="Connection established"
    )
    
    transaction = (TopicMessageSubmitTransaction()
                  .setTopicId(self.inbound_topic_id)
                  .setMessage(json.dumps(message.__dict__))
                  .setTransactionMemo("hcs-10:op:4:1")  # connection_created on inbound topic
                  .setMaxTransactionFee(Hbar.fromHbars(1)))
    
    await transaction.execute(self.client)

async def _record_outbound_connection_created(self, topic_id: TopicId, requester_account: str,
                                            operator_id: str, connection_id: str):
    """Record connection creation in outbound topic"""
    message = HCS10Message(
        op="connection_created", 
        connection_topic_id=str(topic_id),
        outbound_topic_id=str(self.outbound_topic_id),
        requestor_outbound_topic_id="unknown",  # Would need to look this up
        confirmed_request_id=int(connection_id),
        connection_request_id=int(connection_id),
        operator_id=operator_id,
        m="Connection created record"
    )
    
    transaction = (TopicMessageSubmitTransaction()
                  .setTopicId(self.outbound_topic_id)
                  .setMessage(json.dumps(message.__dict__))
                  .setTransactionMemo("hcs-10:op:4:2")  # connection_created on outbound topic
                  .setMaxTransactionFee(Hbar.fromHbars(1)))
    
    await transaction.execute(self.client)

# Add these methods to the HCS10Agent class
HCS10Agent._send_connection_created = _send_connection_created
HCS10Agent._record_outbound_connection_created = _record_outbound_connection_created
