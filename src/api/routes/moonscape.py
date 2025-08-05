"""
MoonScape API Routes
Provides REST API endpoints for MoonScape integration and HCS-10 communication
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ...integrations.moonscape.moonscape_hcs10_service import MoonScapeHCS10Service

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/moonscape", tags=["MoonScape Integration"])

# Global service instance
moonscape_service: Optional[MoonScapeHCS10Service] = None

# Pydantic models for API requests/responses
class MoonScapeStatus(BaseModel):
    """MoonScape service status response"""
    status: str
    agent_name: str
    agent_id: str
    active_connections: int
    registry_topic_id: str
    network: str
    uptime: str

class ConnectionRequest(BaseModel):
    """Request to create a new connection"""
    requester_account: str
    message: Optional[str] = None

class AuditRequest(BaseModel):
    """Audit request from MoonScape user"""
    connection_id: str
    contract_code: str
    contract_name: Optional[str] = None
    language: str = "solidity"
    metadata: Optional[Dict[str, Any]] = None

class MessageRequest(BaseModel):
    """Send message to connection"""
    connection_id: str
    message_type: str
    data: Dict[str, Any]
    memo: Optional[str] = None

@router.get("/status", response_model=MoonScapeStatus)
async def get_moonscape_status():
    """
    Get current MoonScape integration status
    
    Returns:
        MoonScapeStatus: Current service status and agent information
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            raise HTTPException(status_code=503, detail="MoonScape service not initialized")
        
        service_info = moonscape_service.get_service_info()
        
        return MoonScapeStatus(
            status=service_info.get("status", "unknown"),
            agent_name=service_info.get("agent_name", "HederaAuditAI"),
            agent_id=service_info.get("hcs10_agent", {}).get("operator_id", "unknown"),
            active_connections=service_info.get("active_connections", 0),
            registry_topic_id=service_info.get("registry_topic_id", "unknown"),
            network=service_info.get("network", "testnet"),
            uptime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        logger.error(f"Error getting MoonScape status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_moonscape_service(background_tasks: BackgroundTasks):
    """
    Start the MoonScape HCS-10 service
    
    Returns:
        Dict: Service startup confirmation
    """
    try:
        global moonscape_service
        
        if moonscape_service:
            return {"message": "MoonScape service already running", "status": "active"}
        
        # Initialize and start service in background
        moonscape_service = MoonScapeHCS10Service()
        background_tasks.add_task(moonscape_service.start_service)
        
        # Give it a moment to initialize
        await asyncio.sleep(2)
        
        return {
            "message": "MoonScape HCS-10 service started successfully",
            "status": "starting",
            "agent_name": moonscape_service.agent_name,
            "registry_topic": moonscape_service.registry_topic_id
        }
        
    except Exception as e:
        logger.error(f"Error starting MoonScape service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_moonscape_service():
    """
    Stop the MoonScape HCS-10 service
    
    Returns:
        Dict: Service shutdown confirmation
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            return {"message": "MoonScape service not running", "status": "stopped"}
        
        # Cleanup service
        await moonscape_service._cleanup()
        moonscape_service = None
        
        return {
            "message": "MoonScape service stopped successfully",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"Error stopping MoonScape service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections")
async def get_active_connections():
    """
    Get list of active HCS-10 connections
    
    Returns:
        Dict: List of active connections
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            raise HTTPException(status_code=503, detail="MoonScape service not running")
        
        connections = []
        for conn_id, conn_data in moonscape_service.active_connections.items():
            connections.append({
                "connection_id": conn_id,
                "connection_topic_id": conn_data.get("connection_topic_id"),
                "status": conn_data.get("status"),
                "created_at": conn_data.get("created_at").isoformat() if conn_data.get("created_at") else None,
                "message_count": conn_data.get("message_count", 0)
            })
        
        return {
            "total_connections": len(connections),
            "connections": connections
        }
        
    except Exception as e:
        logger.error(f"Error getting connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit")
async def process_audit_request(request: AuditRequest):
    """
    Process an audit request from MoonScape user
    
    Args:
        request: Audit request details
        
    Returns:
        Dict: Audit processing confirmation
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            raise HTTPException(status_code=503, detail="MoonScape service not running")
        
        # Validate connection exists
        if request.connection_id not in moonscape_service.active_connections:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Process audit request
        logger.info(f"Processing audit request from connection: {request.connection_id}")
        
        # Simulate audit processing (in real implementation, integrate with your audit engine)
        audit_results = {
            "request_id": f"audit_{int(datetime.now().timestamp())}",
            "connection_id": request.connection_id,
            "contract_name": request.contract_name or "Unknown",
            "language": request.language,
            "status": "processing",
            "estimated_completion": "5 minutes",
            "findings_preview": "Analyzing contract for vulnerabilities..."
        }
        
        # Store audit session
        moonscape_service.audit_sessions[request.connection_id] = {
            "request": request.dict(),
            "results": audit_results,
            "status": "processing",
            "created_at": datetime.now()
        }
        
        return {
            "message": "Audit request received and processing",
            "audit_info": audit_results
        }
        
    except Exception as e:
        logger.error(f"Error processing audit request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def send_message(request: MessageRequest):
    """
    Send a message to a specific HCS-10 connection
    
    Args:
        request: Message details
        
    Returns:
        Dict: Message sending confirmation
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            raise HTTPException(status_code=503, detail="MoonScape service not running")
        
        # Validate connection exists
        if request.connection_id not in moonscape_service.active_connections:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Create HCS-10 message
        hcs10_message = {
            "p": "hcs-10",
            "op": "message",
            "operator_id": moonscape_service.hcs10_agent['operator_id'],
            "data": json.dumps(request.data),
            "m": request.memo or f"{request.message_type} message"
        }
        
        # Simulate sending message
        logger.info(f"Sending {request.message_type} message to connection: {request.connection_id}")
        
        # Update connection message count
        connection = moonscape_service.active_connections[request.connection_id]
        connection['message_count'] = connection.get('message_count', 0) + 1
        
        return {
            "message": "Message sent successfully",
            "connection_id": request.connection_id,
            "message_type": request.message_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-info")
async def get_agent_info():
    """
    Get detailed agent information for MoonScape display
    
    Returns:
        Dict: Comprehensive agent information
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            raise HTTPException(status_code=503, detail="MoonScape service not running")
        
        agent_info = {
            "agent_name": moonscape_service.agent_name,
            "description": moonscape_service.agent_description,
            "account_id": moonscape_service.operator_id,
            "network": moonscape_service.hedera_network,
            "hcs10_info": moonscape_service.hcs10_agent,
            "capabilities": [
                "🔍 Smart contract vulnerability detection",
                "⚡ Gas optimization analysis",
                "🛡️ Security best practices review", 
                "📄 Professional audit reports",
                "🎯 NFT certificate generation",
                "💬 Interactive audit consultation",
                "🔗 HCS-10 OpenConvAI communication"
            ],
            "supported_languages": ["Solidity"],
            "features": [
                "Real-time vulnerability scanning",
                "AI-powered security analysis",
                "Comprehensive audit reports",
                "Best practices recommendations",
                "Gas optimization suggestions",
                "NFT audit certificates"
            ],
            "pricing": {
                "basic_audit": "5 HBAR",
                "comprehensive_audit": "10 HBAR",
                "consultation": "1 HBAR per message"
            },
            "response_time": "< 5 minutes",
            "availability": "24/7",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }
        
        return agent_info
        
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/registry-info")
async def get_registry_info():
    """
    Get HCS-10 registry information
    
    Returns:
        Dict: Registry and protocol information
    """
    try:
        global moonscape_service
        
        if not moonscape_service:
            raise HTTPException(status_code=503, detail="MoonScape service not running")
        
        registry_info = {
            "protocol": "HCS-10 OpenConvAI",
            "registry_topic_id": moonscape_service.registry_topic_id,
            "network": moonscape_service.hedera_network,
            "agent_registration": {
                "status": "registered",
                "operator_id": moonscape_service.hcs10_agent['operator_id'] if moonscape_service.hcs10_agent else None,
                "inbound_topic": moonscape_service.hcs10_agent['inbound_topic_id'] if moonscape_service.hcs10_agent else None,
                "outbound_topic": moonscape_service.hcs10_agent['outbound_topic_id'] if moonscape_service.hcs10_agent else None
            },
            "moonscape_integration": {
                "platform_url": "https://moonscape.tech/openconvai/chat",
                "agent_discovery": f"Search for '{moonscape_service.agent_name}' on MoonScape",
                "connection_method": "HCS-10 connection request",
                "communication": "Real-time messaging via HCS topics"
            },
            "documentation": {
                "hcs10_standard": "https://hashgraphonline.com/docs/standards/hcs-10",
                "moonscape_docs": "https://moonscape.tech/openconvai/learn",
                "agent_guide": "Connect through MoonScape platform to start auditing"
            }
        }
        
        return registry_info
        
    except Exception as e:
        logger.error(f"Error getting registry info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
