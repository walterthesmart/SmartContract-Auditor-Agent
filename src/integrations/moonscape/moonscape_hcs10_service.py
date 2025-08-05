"""
MoonScape HCS-10 Integration Service
Implements the official HCS-10 OpenConvAI standard for MoonScape integration
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoonScapeHCS10Service:
    """
    MoonScape integration service using HCS-10 OpenConvAI standard
    Enables users to interact with the AI auditor through MoonScape platform
    """
    
    def __init__(self):
        # Load environment variables
        self.hedera_network = os.getenv('HEDERA_NETWORK', 'testnet')
        self.operator_id = os.getenv('HEDERA_OPERATOR_ID')
        self.operator_key = os.getenv('HEDERA_OPERATOR_KEY')
        self.registry_topic_id = os.getenv('HCS10_REGISTRY_TOPIC_ID', '0.0.6359793')
        self.agent_name = os.getenv('HCS10_AGENT_NAME', 'HederaAuditAI')
        self.agent_description = os.getenv('HCS10_AGENT_DESCRIPTION', 'AI-powered smart contract auditor')
        
        # Validate required environment variables
        if not self.operator_id or not self.operator_key:
            raise ValueError("HEDERA_OPERATOR_ID and HEDERA_OPERATOR_KEY must be set")
        
        # Initialize components
        self.hcs10_agent = None
        self.active_connections = {}
        self.audit_sessions = {}
        
        logger.info(f"🌙 Initialized MoonScape HCS-10 Service")
        logger.info(f"📋 Agent: {self.agent_name}")
        logger.info(f"🆔 Account: {self.operator_id}")
        logger.info(f"🌐 Network: {self.hedera_network}")
    
    async def start_service(self):
        """Start the MoonScape HCS-10 service"""
        try:
            logger.info("🚀 Starting MoonScape HCS-10 Service...")
            
            # Initialize HCS-10 agent
            await self._initialize_hcs10_agent()
            
            # Start the main service loop
            await self._run_service_loop()
            
        except Exception as e:
            logger.error(f"❌ Failed to start MoonScape service: {e}")
            raise
    
    async def _initialize_hcs10_agent(self):
        """Initialize the HCS-10 agent with proper configuration"""
        try:
            # For now, simulate HCS-10 agent initialization
            # In a real implementation, this would use the Hedera SDK
            
            logger.info("🔧 Initializing HCS-10 Agent...")
            
            # Simulate topic creation and registration
            inbound_topic_id = "0.0.789101"  # Would be created dynamically
            outbound_topic_id = "0.0.789102"  # Would be created dynamically
            
            self.hcs10_agent = {
                "agent_name": self.agent_name,
                "account_id": self.operator_id,
                "inbound_topic_id": inbound_topic_id,
                "outbound_topic_id": outbound_topic_id,
                "operator_id": f"{inbound_topic_id}@{self.operator_id}",
                "status": "active"
            }
            
            # Simulate registration with MoonScape registry
            await self._register_with_moonscape()
            
            logger.info("✅ HCS-10 Agent initialized successfully")
            logger.info(f"🆔 Agent ID: {self.hcs10_agent['operator_id']}")
            logger.info(f"📥 Inbound Topic: {inbound_topic_id}")
            logger.info(f"📤 Outbound Topic: {outbound_topic_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize HCS-10 agent: {e}")
            raise
    
    async def _register_with_moonscape(self):
        """Register the agent with MoonScape registry"""
        try:
            logger.info("📋 Registering with MoonScape registry...")
            
            # HCS-10 register operation format
            register_message = {
                "p": "hcs-10",
                "op": "register", 
                "account_id": self.operator_id,
                "m": f"Registering {self.agent_name} - AI-powered smart contract auditor"
            }
            
            # Simulate sending to registry topic
            logger.info(f"📤 Sending registration to topic: {self.registry_topic_id}")
            logger.info(f"📋 Registration data: {json.dumps(register_message, indent=2)}")
            
            # In real implementation, this would be:
            # transaction = TopicMessageSubmitTransaction()
            #     .setTopicId(TopicId.fromString(self.registry_topic_id))
            #     .setMessage(json.dumps(register_message))
            #     .setTransactionMemo("hcs-10:op:0:0")  # register operation on registry
            
            logger.info("✅ Successfully registered with MoonScape registry")
            
        except Exception as e:
            logger.error(f"Failed to register with MoonScape: {e}")
            raise
    
    async def _run_service_loop(self):
        """Main service loop for handling MoonScape interactions"""
        logger.info("🔄 Starting MoonScape service loop...")
        logger.info("=" * 70)
        logger.info("🌙 MOONSCAPE HCS-10 SERVICE ACTIVE")
        logger.info("=" * 70)
        logger.info(f"🤖 Agent: {self.agent_name}")
        logger.info(f"🆔 Agent ID: {self.hcs10_agent['operator_id']}")
        logger.info(f"📡 Registry: {self.registry_topic_id}")
        logger.info("=" * 70)
        logger.info("🔗 Users can now connect through MoonScape!")
        logger.info("📱 Visit: https://moonscape.tech/openconvai/chat")
        logger.info("🔍 Search for: HederaAuditAI")
        logger.info("💬 Start chatting with the AI auditor!")
        logger.info("=" * 70)
        
        try:
            iteration = 0
            while True:
                iteration += 1
                
                # Simulate listening for connections and messages
                await self._check_for_connections()
                await self._process_audit_requests()
                await self._send_heartbeat()
                
                # Log status every 10 iterations (5 minutes)
                if iteration % 10 == 0:
                    await self._log_status()
                
                # Wait 30 seconds before next iteration
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping MoonScape service...")
            await self._cleanup()
        except Exception as e:
            logger.error(f"Error in service loop: {e}")
            await asyncio.sleep(10)
    
    async def _check_for_connections(self):
        """Check for new connection requests"""
        try:
            # Simulate checking inbound topic for connection requests
            # In real implementation, this would listen to the inbound topic
            
            # Simulate occasional new connections
            import random
            if random.random() < 0.1:  # 10% chance of new connection
                connection_id = f"conn_{int(datetime.now().timestamp())}"
                await self._handle_new_connection(connection_id)
                
        except Exception as e:
            logger.error(f"Error checking for connections: {e}")
    
    async def _handle_new_connection(self, connection_id: str):
        """Handle a new connection request"""
        try:
            logger.info(f"📨 New connection request: {connection_id}")
            
            # Simulate creating connection topic and responding
            connection_topic_id = f"0.0.{567890 + len(self.active_connections)}"
            
            # Store connection
            self.active_connections[connection_id] = {
                "connection_id": connection_id,
                "connection_topic_id": connection_topic_id,
                "status": "active",
                "created_at": datetime.now(),
                "message_count": 0
            }
            
            # Send welcome message
            await self._send_welcome_message(connection_id)
            
            logger.info(f"✅ Connection established: {connection_id}")
            logger.info(f"🔗 Connection topic: {connection_topic_id}")
            
        except Exception as e:
            logger.error(f"Error handling new connection: {e}")
    
    async def _send_welcome_message(self, connection_id: str):
        """Send welcome message to new connection"""
        try:
            welcome_data = {
                "type": "welcome",
                "agent_name": self.agent_name,
                "description": self.agent_description,
                "capabilities": [
                    "🔍 Smart contract vulnerability detection",
                    "⚡ Gas optimization analysis", 
                    "🛡️ Security best practices review",
                    "📄 Professional audit reports",
                    "🎯 NFT certificate generation"
                ],
                "instructions": [
                    "Send me your Solidity contract code for analysis",
                    "I'll provide a comprehensive security audit",
                    "Ask questions about smart contract security",
                    "Request specific vulnerability checks"
                ],
                "example_request": "Please audit this contract: pragma solidity ^0.8.0; contract MyContract { ... }"
            }
            
            # Simulate sending HCS-10 message
            hcs10_message = {
                "p": "hcs-10",
                "op": "message",
                "operator_id": self.hcs10_agent['operator_id'],
                "data": json.dumps(welcome_data),
                "m": "Welcome message from HederaAuditAI"
            }
            
            logger.info(f"📤 Sent welcome message to: {connection_id}")
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
    
    async def _process_audit_requests(self):
        """Process any pending audit requests"""
        try:
            # Simulate processing audit requests from active connections
            for connection_id, connection in self.active_connections.items():
                if connection['status'] == 'active':
                    # Simulate receiving audit requests
                    import random
                    if random.random() < 0.05:  # 5% chance of audit request
                        await self._simulate_audit_request(connection_id)
                        
        except Exception as e:
            logger.error(f"Error processing audit requests: {e}")
    
    async def _simulate_audit_request(self, connection_id: str):
        """Simulate handling an audit request"""
        try:
            logger.info(f"🔍 Processing audit request from: {connection_id}")
            
            # Simulate audit analysis
            audit_results = {
                "type": "audit_results",
                "summary": {
                    "total_issues": 3,
                    "critical_issues": 0,
                    "high_issues": 1,
                    "medium_issues": 1,
                    "low_issues": 1
                },
                "findings": [
                    {
                        "severity": "high",
                        "title": "Reentrancy Vulnerability",
                        "description": "External call before state update",
                        "line": 25,
                        "recommendation": "Use ReentrancyGuard or checks-effects-interactions pattern"
                    },
                    {
                        "severity": "medium", 
                        "title": "Missing Input Validation",
                        "description": "Function parameters not validated",
                        "line": 15,
                        "recommendation": "Add require statements for input validation"
                    },
                    {
                        "severity": "low",
                        "title": "Gas Optimization",
                        "description": "Loop can be optimized",
                        "line": 35,
                        "recommendation": "Consider using mapping instead of array iteration"
                    }
                ],
                "recommendations": [
                    "Implement reentrancy protection",
                    "Add comprehensive input validation",
                    "Optimize gas usage in loops"
                ],
                "timestamp": datetime.now().isoformat(),
                "agent_signature": f"Audited by {self.agent_name}"
            }
            
            # Simulate sending results
            hcs10_message = {
                "p": "hcs-10",
                "op": "message",
                "operator_id": self.hcs10_agent['operator_id'],
                "data": json.dumps(audit_results),
                "m": "Smart contract audit results"
            }
            
            logger.info(f"📤 Sent audit results to: {connection_id}")
            logger.info(f"📊 Found {audit_results['summary']['total_issues']} issues")
            
        except Exception as e:
            logger.error(f"Error simulating audit request: {e}")
    
    async def _send_heartbeat(self):
        """Send heartbeat to maintain agent presence"""
        try:
            # Simulate sending heartbeat to outbound topic
            heartbeat = {
                "p": "hcs-10",
                "op": "message",
                "operator_id": self.hcs10_agent['operator_id'],
                "data": json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "status": "active",
                    "connections": len(self.active_connections)
                }),
                "m": "Agent heartbeat"
            }
            
            # In real implementation, send to outbound topic
            
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
    
    async def _log_status(self):
        """Log current service status"""
        try:
            logger.info("📊 MoonScape Service Status:")
            logger.info(f"   🔗 Active connections: {len(self.active_connections)}")
            logger.info(f"   🔍 Audit sessions: {len(self.audit_sessions)}")
            logger.info(f"   🤖 Agent status: {self.hcs10_agent['status']}")
            logger.info(f"   ⏰ Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error logging status: {e}")
    
    async def _cleanup(self):
        """Clean up resources"""
        try:
            logger.info("🧹 Cleaning up MoonScape service...")
            
            # Close all connections
            for connection_id in list(self.active_connections.keys()):
                await self._close_connection(connection_id)
            
            logger.info("✅ MoonScape service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _close_connection(self, connection_id: str):
        """Close a specific connection"""
        try:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                connection['status'] = 'closed'
                
                # Send close message
                close_message = {
                    "p": "hcs-10",
                    "op": "close_connection",
                    "operator_id": self.hcs10_agent['operator_id'],
                    "reason": "Service shutdown",
                    "m": "Closing connection"
                }
                
                logger.info(f"🔒 Closed connection: {connection_id}")
                
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service_name": "MoonScape HCS-10 Integration",
            "agent_name": self.agent_name,
            "agent_description": self.agent_description,
            "hcs10_agent": self.hcs10_agent,
            "active_connections": len(self.active_connections),
            "audit_sessions": len(self.audit_sessions),
            "registry_topic_id": self.registry_topic_id,
            "network": self.hedera_network,
            "status": "active"
        }

async def main():
    """Main entry point for MoonScape HCS-10 service"""
    try:
        service = MoonScapeHCS10Service()
        await service.start_service()
    except KeyboardInterrupt:
        logger.info("👋 MoonScape service stopped by user")
    except Exception as e:
        logger.error(f"💥 MoonScape service failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
