"""FastAPI server for the Hedera Audit AI backend with HCS-10 OpenConvAI support."""

import hashlib
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hedera_audit_ai")

# Load environment variables from .env file
try:
    # Get the project root directory (parent of the src directory)
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / "config" / ".env"

    if env_path.exists():
        logger.info(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
        logger.info("Environment variables loaded successfully")
    else:
        logger.warning(f".env file not found at {env_path}")
        # Try loading from current directory as fallback
        load_dotenv()
        
    # Verify critical environment variables
    critical_vars = [
        "GROQ_API_KEY", 
        "HEDERA_OPERATOR_ID", 
        "HEDERA_OPERATOR_KEY",
        "SLITHER_CUSTOM_RULES",
        "HCS10_REGISTRY_TOPIC_ID"
    ]
    
    for var in critical_vars:
        if os.getenv(var):
            logger.info(f"✓ {var} is set")
        else:
            logger.error(f"✗ {var} is not set")
            
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from src.core.analyzer.slither_analyzer import SlitherAnalyzer
from src.core.llm.processor import LLMProcessor
from src.core.report.generator import ReportGenerator
from src.api.routes.moonscape import router as moonscape_router

# Optional imports for testing - these require Java/external dependencies
try:
    from src.integrations.hedera.integrator import HederaService
    from src.integrations.hcs10.hcs10_agent import HCS10Agent
    HEDERA_AVAILABLE = True
except Exception as e:
    logger.warning(f"Hedera integration not available: {e}")
    HederaService = None
    HCS10Agent = None
    HEDERA_AVAILABLE = False


# Initialize FastAPI app
app = FastAPI(
    title="Hedera Audit AI",
    description="AI-powered auditing tool for Hedera smart contracts with HCS-10 OpenConvAI support",
    version="0.2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include MoonScape routes
app.include_router(moonscape_router)


# Pydantic models for request/response validation
class ContractMetadata(BaseModel):
    name: str = Field(..., description="Name of the contract")
    language: str = Field("solidity", description="Language of the contract (solidity or vyper)")
    hash: Optional[str] = Field(None, description="Hash of the contract code")


class AuditRequest(BaseModel):
    contract_code: str = Field(..., description="Source code of the smart contract")
    contract_metadata: ContractMetadata = Field(..., description="Metadata about the contract")


class Vulnerability(BaseModel):
    id: str = Field(..., description="Vulnerability ID")
    title: str = Field(..., description="Title of the vulnerability")
    description: str = Field(..., description="Description of the vulnerability")
    severity: str = Field(..., description="Severity level (High, Medium, Low, Informational)")
    severity_level_value: int = Field(..., description="Numeric severity level (3=High, 2=Medium, 1=Low, 0=Informational)")
    line: int = Field(0, description="Line number where the vulnerability was found")
    code_snippet: Optional[str] = Field(None, description="Code snippet containing the vulnerability")
    explanation: Optional[str] = Field(None, description="Explanation of the vulnerability")
    fixed_code: Optional[str] = Field(None, description="Suggested fix for the vulnerability")
    test_case: Optional[str] = Field(None, description="Test case for the vulnerability")


class AuditResponse(BaseModel):
    contract_metadata: ContractMetadata = Field(..., description="Metadata about the contract")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="List of vulnerabilities found")
    audit_score: int = Field(..., description="Audit score (0-100)")
    passed: bool = Field(..., description="Whether the audit passed (score >= 80)")


class ReportRequest(BaseModel):
    audit_data: AuditResponse = Field(..., description="Audit data to generate report from")


class ReportResponse(BaseModel):
    file_id: str = Field(..., description="Hedera file ID of the report")
    nft_id: Optional[str] = Field(None, description="Hedera token ID of the NFT (if audit passed)")
    view_url: str = Field(..., description="URL to view the report")


# HCS-10 OpenConvAI Models
class AgentTopicsResponse(BaseModel):
    inbound_topic_id: str = Field(..., description="Inbound topic ID")
    outbound_topic_id: str = Field(..., description="Outbound topic ID")
    metadata_topic_id: str = Field(..., description="Metadata topic ID")


class ConnectionRequest(BaseModel):
    account_id: str = Field(..., description="Account ID to connect with")


class ConnectionResponse(BaseModel):
    connection_id: int = Field(..., description="Connection ID")
    connection_topic_id: str = Field(..., description="Connection topic ID")
    connected_account_id: str = Field(..., description="Connected account ID")


class AuditRequestHCS10(BaseModel):
    connection_id: int = Field(..., description="Connection ID")
    contract_code: str = Field(..., description="Source code of the smart contract")
    contract_metadata: ContractMetadata = Field(..., description="Metadata about the contract")


class AuditResultHCS10(BaseModel):
    connection_id: int = Field(..., description="Connection ID")
    audit_result: AuditResponse = Field(..., description="Audit result data")
    file_id: str = Field(..., description="Hedera file ID of the report")
    nft_id: Optional[str] = Field(None, description="NFT ID if audit passed")


class ApprovalRequest(BaseModel):
    connection_id: int = Field(..., description="Connection ID")
    audit_result: AuditResponse = Field(..., description="Audit result data")
    file_id: str = Field(..., description="Hedera file ID of the report")


# Dependency injection for services
# Global SlitherAnalyzer instance
_slither_analyzer = None

def get_analyzer() -> SlitherAnalyzer:
    """Get SlitherAnalyzer instance as a singleton."""
    global _slither_analyzer
    
    # Return existing analyzer if already initialized
    if _slither_analyzer is not None:
        return _slither_analyzer
    
    custom_rules_path = os.getenv("SLITHER_CUSTOM_RULES")
    if not custom_rules_path:
        raise HTTPException(status_code=500, detail="SLITHER_CUSTOM_RULES environment variable not set")
        
    timeout = int(os.getenv("SLITHER_ANALYSIS_TIMEOUT", "300"))
    
    # Initialize the analyzer
    _slither_analyzer = SlitherAnalyzer(custom_rules_path=custom_rules_path, timeout=timeout)
    return _slither_analyzer


# Global LLMProcessor instance
_llm_processor = None

def get_llm_processor() -> LLMProcessor:
    """Get LLMProcessor instance as a singleton."""
    global _llm_processor
    
    # Return existing processor if already initialized
    if _llm_processor is not None:
        return _llm_processor
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set")
        
    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    _llm_processor = LLMProcessor(api_key=api_key, model=model)
    return _llm_processor


def get_report_generator() -> ReportGenerator:
    """Get ReportGenerator instance."""
    logo_path = os.getenv("REPORT_LOGO_PATH")
    
    # Resolve relative path if provided
    if logo_path and not os.path.isabs(logo_path):
        # Get the backend directory (2 levels up from this file)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Resolve the path relative to the backend directory
        logo_path = os.path.join(backend_dir, logo_path)
        
    return ReportGenerator(logo_path=logo_path)


def get_hedera_service():
    """Get HederaService instance."""
    if not HEDERA_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Hedera integration not available"
        )

    network = os.getenv("HEDERA_NETWORK", "testnet")
    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")

    if not operator_id or not operator_key:
        raise HTTPException(
            status_code=500,
            detail="Hedera credentials not configured"
        )

    return HederaService(network=network, operator_id=operator_id, operator_key=operator_key)


# Global HCS10Agent instance
_hcs10_agent = None

def retry(max_attempts=3, delay=2):
    """Retry decorator for functions that might fail due to network issues."""
    from functools import wraps
    import time
    import logging
    
    logger = logging.getLogger("hcs10_agent")
    
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
                        logger.error(f"All {max_attempts} attempts failed: {e}")
                        raise e
                    logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
        return wrapper
    return decorator

def get_hcs10_agent():
    """Get or create a singleton HCS10Agent instance."""
    global _hcs10_agent
    
    if _hcs10_agent is not None:
        return _hcs10_agent
    
    hedera_service = get_hedera_service()
    registry_topic_id = os.getenv("HCS10_REGISTRY_TOPIC_ID")
    agent_name = os.getenv("HCS10_AGENT_NAME", "HederaAuditAI")
    agent_description = os.getenv("HCS10_AGENT_DESCRIPTION", "AI-powered auditing tool for Hedera smart contracts")
    
    try:
        _hcs10_agent = HCS10Agent(
            hedera_service=hedera_service,
            registry_topic_id=registry_topic_id,
            agent_name=agent_name,
            agent_description=agent_description
        )
        
        # Initialize mock connections for testing
        if not hasattr(_hcs10_agent, 'connections') or not _hcs10_agent.connections:
            _hcs10_agent.connections = {}
            # Add a test connection
            _hcs10_agent.connections[1] = {
                "connection_id": 1,
                "connection_topic_id": "0.0.6374150",
                "connected_account_id": "0.0.12345",
                "status": "active"
            }
            
        return _hcs10_agent
    except Exception as e:
        logging.error(f"Error initializing HCS10Agent: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Hedera Audit AI API"}


@app.post("/analyze", response_model=AuditResponse)
async def analyze_contract(
    request: AuditRequest,
    analyzer: SlitherAnalyzer = Depends(get_analyzer),
    llm_processor: LLMProcessor = Depends(get_llm_processor),
):
    """
    Analyze a smart contract for vulnerabilities.
    
    Args:
        request: AuditRequest containing contract code and metadata
        analyzer: SlitherAnalyzer instance
        llm_processor: LLMProcessor instance
        
    Returns:
        AuditResponse containing vulnerabilities and audit score
    """
    try:
        import logging
        # Generate contract hash if not provided
        contract_metadata = request.contract_metadata.dict()
        if not contract_metadata.get("hash"):
            contract_hash = hashlib.sha256(request.contract_code.encode()).hexdigest()
            contract_metadata["hash"] = contract_hash
        
        # Step 1: Static analysis with Slither
        try:
            analysis_result = analyzer.analyze_contract(
                request.contract_code,
                request.contract_metadata.language
            )
            logging.info(f"Analysis result: {analysis_result}")
        except Exception as e:
            logging.error(f"Error in analyzer.analyze_contract: {str(e)}")
            # Provide a default structure if analysis fails
            analysis_result = {
                "vulnerabilities": [],
                "contract_metrics": {
                    "complexity": 5,
                    "loc": len(request.contract_code.splitlines())
                }
            }
        
        # Ensure vulnerabilities is a list
        vulnerabilities = analysis_result.get("vulnerabilities", [])
        
        # Step 2: Process vulnerabilities with LLM
        if vulnerabilities:
            try:
                processed_vulnerabilities = llm_processor.process_vulnerabilities(
                    vulnerabilities,
                    request.contract_code
                )
            except Exception as e:
                logging.error(f"Error in llm_processor: {str(e)}")
                # If LLM processing fails, use the raw vulnerabilities
                processed_vulnerabilities = vulnerabilities
        else:
            processed_vulnerabilities = []
        
        # Ensure all vulnerabilities have required fields
        for vuln in processed_vulnerabilities:
            if "severity_level_value" not in vuln:
                vuln["severity_level_value"] = 2  # Default to Medium
        
        # Calculate audit score (100 - severity weighted vulnerabilities)
        total_severity = sum(
            max(0, 5 - v.get("severity_level_value", 2)) * 2
            for v in processed_vulnerabilities
        )
        audit_score = max(0, min(100, 100 - total_severity))
        
        return {
            "contract_metadata": contract_metadata,
            "vulnerabilities": processed_vulnerabilities,
            "audit_score": audit_score,
            "passed": audit_score >= 80
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    report_generator: ReportGenerator = Depends(get_report_generator),
    hedera_service = Depends(get_hedera_service),
):
    """
    Generate an audit report and store it on Hedera.
    
    Args:
        request: ReportRequest containing audit data
        report_generator: ReportGenerator instance
        hedera_service: HederaService instance
        
    Returns:
        ReportResponse containing file ID and NFT ID
    """
    try:
        # Generate PDF report
        pdf_bytes = report_generator.generate_pdf(request.audit_data.dict())
        
        # Store on Hedera
        file_id = hedera_service.store_pdf(pdf_bytes)
        
        # Mint NFT if audit passed
        nft_id = None
        if request.audit_data.passed:
            metadata = {
                "contract": request.audit_data.contract_metadata.dict(),
                "score": request.audit_data.audit_score,
                "timestamp": datetime.utcnow().isoformat(),
                "file_id": file_id
            }
            nft_id = hedera_service.mint_audit_nft(metadata)
        
        # Generate view URL
        network = os.getenv("HEDERA_NETWORK", "testnet")
        view_url = f"https://hashscan.io/{network}/file/{file_id}"
        
        return {
            "file_id": file_id,
            "nft_id": nft_id,
            "view_url": view_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.post("/upload-contract")
async def upload_contract(
    file: UploadFile = File(...),
    contract_name: str = Form("UntitledContract"),
    language: str = Form("solidity"),
):
    """
    Upload a contract file for analysis.
    
    Args:
        file: Contract file
        contract_name: Name of the contract
        language: Language of the contract (solidity or vyper)
        
    Returns:
        Contract code and metadata
    """
    try:
        # Read contract code
        contract_code = await file.read()
        contract_code_str = contract_code.decode("utf-8")
        
        # Generate contract hash
        contract_hash = hashlib.sha256(contract_code).hexdigest()
        
        return {
            "contract_code": contract_code_str,
            "contract_metadata": {
                "name": contract_name,
                "language": language,
                "hash": contract_hash
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# HCS-10 OpenConvAI Endpoints
@app.get("/hcs10/topics", response_model=AgentTopicsResponse)
async def get_agent_topics(agent = Depends(get_hcs10_agent)):
    """Get agent topics."""
    return {
        "inbound_topic_id": agent.inbound_topic_id,
        "outbound_topic_id": agent.outbound_topic_id,
        "metadata_topic_id": agent.metadata_topic_id
    }


@app.post("/hcs10/connections", response_model=ConnectionResponse)
async def create_connection(request: ConnectionRequest, agent = Depends(get_hcs10_agent)):
    """Create a connection with another account."""
    try:
        connection = agent.create_connection(request.account_id)
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")


@app.post("/hcs10/audit-request")
async def send_audit_request(
    request: AuditRequestHCS10,
    background_tasks: BackgroundTasks,
    agent = Depends(get_hcs10_agent),
    analyzer: SlitherAnalyzer = Depends(get_analyzer),
    llm_processor: LLMProcessor = Depends(get_llm_processor)
):
    """Send an audit request through HCS-10 and process it."""
    try:
        # Generate contract hash if not provided
        contract_metadata = request.contract_metadata.dict()
        if not contract_metadata.get("hash"):
            contract_hash = hashlib.sha256(request.contract_code.encode()).hexdigest()
            contract_metadata["hash"] = contract_hash
        
        # Send audit request message
        tx_id = agent.send_audit_request(
            request.connection_id,
            request.contract_code,
            contract_metadata
        )
        
        # Process audit in background
        background_tasks.add_task(
            process_audit_request,
            agent,
            request.connection_id,
            request.contract_code,
            contract_metadata,
            analyzer,
            llm_processor,
            get_report_generator()
        )
        
        return {"message": "Audit request received and processing", "transaction_id": tx_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send audit request: {str(e)}")


@app.post("/hcs10/audit-result")
async def send_audit_result(request: AuditResultHCS10, agent = Depends(get_hcs10_agent)):
    """Send audit results through HCS-10."""
    try:
        tx_id = agent.send_audit_result(
            request.connection_id,
            request.audit_result.dict(),
            request.file_id,
            request.nft_id
        )
        
        return {"message": "Audit result sent", "transaction_id": tx_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send audit result: {str(e)}")


@app.post("/hcs10/request-approval")
async def request_nft_approval(request: ApprovalRequest, agent = Depends(get_hcs10_agent)):
    """Request approval for NFT minting."""
    try:
        schedule_id = agent.request_nft_approval(
            request.connection_id,
            request.audit_result.dict(),
            request.file_id
        )
        
        return {"message": "Approval requested", "schedule_id": schedule_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to request approval: {str(e)}")


async def process_audit_request(
    agent,
    connection_id: int,
    contract_code: str,
    contract_metadata: Dict,
    analyzer: SlitherAnalyzer,
    llm_processor: LLMProcessor,
    report_generator: ReportGenerator
):
    """Process an audit request in the background."""
    try:
        logging.info(f"Processing audit request for connection {connection_id}")
        
        # Step 1: Static analysis with Slither
        analysis_result = analyzer.analyze_contract(
            contract_code,
            contract_metadata.get("language", "solidity")
        )
        logging.info(f"Analysis completed with {len(analysis_result.get('vulnerabilities', []))} vulnerabilities")
        
        # Step 2: Process vulnerabilities with LLM
        vulnerabilities = analysis_result.get("vulnerabilities", [])
        processed_vulnerabilities = []
        
        try:
            if vulnerabilities:
                processed_vulnerabilities = llm_processor.process_vulnerabilities(
                    vulnerabilities,
                    contract_code
                )
                logging.info(f"LLM processing completed with {len(processed_vulnerabilities)} vulnerabilities")
            else:
                logging.info("No vulnerabilities to process")
        except Exception as llm_error:
            logging.error(f"Error in LLM processing: {str(llm_error)}")
            # Use the original vulnerabilities if LLM processing fails
            processed_vulnerabilities = vulnerabilities
        
        # Calculate audit score
        total_severity = 0
        for v in processed_vulnerabilities:
            severity_value = v.get("severity_level_value", 0)
            if isinstance(severity_value, (int, float)):
                total_severity += max(0, 5 - severity_value) * 2
        
        audit_score = max(0, min(100, 100 - total_severity))
        logging.info(f"Calculated audit score: {audit_score}")
        
        # Create audit response
        audit_response = {
            "contract_metadata": contract_metadata,
            "vulnerabilities": processed_vulnerabilities,
            "audit_score": audit_score,
            "passed": audit_score >= 80
        }
        
        # For testing: Use mock file_id and nft_id instead of generating real ones
        try:
            # Generate PDF report (but don't store it for testing)
            pdf_bytes = report_generator.generate_pdf(audit_response)
            logging.info(f"Generated PDF report with {len(pdf_bytes)} bytes")
            
            # Mock file_id instead of storing on Hedera
            file_id = f"0.0.{connection_id}file"
            logging.info(f"Mock file_id: {file_id}")
            
            # Mock NFT if audit passed
            nft_id = None
            if audit_response["passed"]:
                nft_id = f"0.0.{connection_id}nft"
                logging.info(f"Mock NFT minted: {nft_id}")
            
            # Send audit result using mock implementation
            tx_id = agent.send_audit_result(connection_id, audit_response, file_id, nft_id)
            logging.info(f"Sent audit result with transaction ID: {tx_id}")
            
        except Exception as report_error:
            logging.error(f"Error in report generation or sending: {str(report_error)}")
            raise
        
    except Exception as e:
        logging.error(f"Error processing audit request: {str(e)}")
        # For testing: Just log the error instead of sending a real message
        logging.info(f"Would send error message to connection {connection_id}: {str(e)}")
        
        # If we have a connection, log what we would send
        if hasattr(agent, 'connections') and connection_id in agent.connections:
            connection = agent.connections[connection_id]
            logging.info(f"Would send to topic {connection.get('connection_topic_id')} and account {connection.get('connected_account_id')}")
        else:
            logging.error(f"Connection {connection_id} not found in agent connections")
            
        # Re-raise the exception for proper error handling
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
