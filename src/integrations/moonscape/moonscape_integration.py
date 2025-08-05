#!/usr/bin/env python3
"""
MoonScape Integration for HederaAuditAI

This script provides integration between HederaAuditAI and MoonScape's platform,
allowing the audit AI to operate as an agent on the MoonScape ecosystem.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root directory to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

# Load environment variables
load_dotenv(os.path.join(project_root, 'config', '.env'))

# MoonScape API endpoints (these would be provided by MoonScape)
MOONSCAPE_API_BASE = os.getenv("MOONSCAPE_API_BASE", "https://api.hashgraphonline.com")
MOONSCAPE_AGENT_REGISTRY_ENDPOINT = f"{MOONSCAPE_API_BASE}/hcs10/registry"
MOONSCAPE_AGENT_CONNECTION_ENDPOINT = f"{MOONSCAPE_API_BASE}/hcs10/connect"
MOONSCAPE_AUDIT_ENDPOINT = f"{MOONSCAPE_API_BASE}/audit"


@dataclass
class AuditRequest:
    """Represents an audit request from MoonScape platform."""
    request_id: str
    contract_code: str
    contract_name: str
    language: str
    metadata: Optional[Dict[str, Any]] = None

class MoonScapeIntegrator:
    """
    Integrates HederaAuditAI with the MoonScape platform using HCS-10 protocol.
    """
    
    def __init__(self):
        """Initialize the MoonScape integrator."""
        # Load required environment variables
        self.api_key = os.getenv("MOONSCAPE_API_KEY")
        if not self.api_key:
            logger.warning("MOONSCAPE_API_KEY not set. Some features may be limited.")
        
        # Initialize Hedera service and HCS-10 agent
        self._init_hedera_service()
        self._init_hcs10_agent()
        
        # Initialize the audit service
        self._init_audit_service()
        
    def _init_hedera_service(self):
        """Initialize the Hedera service."""
        try:
            from src.integrations.hedera.integrator import HederaService
            
            # Get Hedera credentials from environment variables
            operator_id = os.getenv("HEDERA_OPERATOR_ID")
            operator_key = os.getenv("HEDERA_OPERATOR_KEY")
            
            if not operator_id or not operator_key:
                raise ValueError("Hedera credentials not found in environment variables")
            
            logger.info(f"Using Hedera account: {operator_id}")
            
            # Initialize the Hedera service
            self.hedera_service = HederaService(
                operator_id=operator_id,
                operator_key=operator_key,
                network="testnet"  # Change to "mainnet" for production
            )
            
            logger.info("✅ HederaService initialized successfully!")
        except Exception as e:
            logger.error(f"❌ Error initializing HederaService: {e}")
            raise
    
    def _init_hcs10_agent(self):
        """Initialize the HCS-10 agent."""
        try:
            from src.integrations.hcs10.hcs10_agent import HCS10Agent
            
            # Get configuration from environment variables
            registry_topic_id = os.getenv("HCS10_REGISTRY_TOPIC_ID")
            agent_name = os.getenv("HCS10_AGENT_NAME", "HederaAuditAI")
            agent_description = os.getenv("HCS10_AGENT_DESCRIPTION", 
                                         "AI-powered auditing tool for Hedera smart contracts")
            
            if not registry_topic_id:
                raise ValueError("HCS10_REGISTRY_TOPIC_ID not found in environment variables")
            
            logger.info(f"Using registry topic: {registry_topic_id}")
            
            # Initialize the HCS-10 agent
            logger.info("Initializing HCS-10 agent...")
            self.hcs10_agent = HCS10Agent(
                hedera_service=self.hedera_service,
                registry_topic_id=registry_topic_id,
                agent_name=agent_name,
                agent_description=agent_description
            )
            
            logger.info("✅ HCS-10 Agent initialized successfully!")
        except Exception as e:
            logger.error(f"❌ Error initializing HCS-10 Agent: {e}")
            raise
    
    def _init_audit_service(self):
        """Initialize the audit service."""
        try:
            from src.core.analyzer.slither_analyzer import SlitherAnalyzer
            from src.core.llm.processor import LLMProcessor
            from src.core.report.generator import ReportGenerator
            
            # Initialize SlitherAnalyzer
            custom_rules_path = os.getenv("SLITHER_CUSTOM_RULES")
            if not custom_rules_path:
                raise ValueError("SLITHER_CUSTOM_RULES not found in environment variables")
            
            # Resolve relative path if needed
            if not os.path.isabs(custom_rules_path):
                backend_dir = Path(__file__).parent / "backend"
                custom_rules_path = os.path.join(backend_dir, custom_rules_path)
            
            self.analyzer = SlitherAnalyzer(custom_rules_path)
            logger.info("✅ SlitherAnalyzer initialized successfully!")
            
            # Initialize LLMProcessor
            self.llm_processor = LLMProcessor()
            logger.info("✅ LLMProcessor initialized successfully!")
            
            # Initialize ReportGenerator
            logo_path = os.getenv("REPORT_LOGO_PATH")
            if logo_path and not os.path.isabs(logo_path):
                backend_dir = Path(__file__).parent / "backend"
                logo_path = os.path.join(backend_dir, logo_path)
            
            self.report_generator = ReportGenerator(logo_path=logo_path)
            logger.info("✅ ReportGenerator initialized successfully!")
        except Exception as e:
            logger.error(f"❌ Error initializing audit services: {e}")
            raise
    
    def register_with_moonscape(self):
        """
        Register the HederaAuditAI agent with MoonScape's registry.
        """
        if not self.api_key:
            logger.error("Cannot register with MoonScape: API key not set")
            return False
        
        try:
            # Prepare registration data
            registration_data = {
                "agent_name": self.hcs10_agent.agent_name,
                "agent_description": self.hcs10_agent.agent_description,
                "inbound_topic_id": self.hcs10_agent.inbound_topic_id,
                "outbound_topic_id": self.hcs10_agent.outbound_topic_id,
                "metadata_topic_id": self.hcs10_agent.metadata_topic_id,
                "capabilities": ["smart_contract_audit", "vulnerability_analysis", "report_generation"],
                "account_id": self.hedera_service.operator_id
            }
            
            # Send registration request to MoonScape
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Registering with MoonScape: {MOONSCAPE_AGENT_REGISTRY_ENDPOINT}")
            response = requests.post(
                MOONSCAPE_AGENT_REGISTRY_ENDPOINT,
                json=registration_data,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("✅ Successfully registered with MoonScape!")
                return response.json()
            else:
                logger.error(f"❌ Failed to register with MoonScape: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error registering with MoonScape: {e}")
            return False
    
    def listen_for_audit_requests(self):
        """
        Listen for audit requests from MoonScape.
        
        In a production environment, this would be implemented as a webhook
        or a long-polling mechanism. For this example, we'll simulate it.
        """
        logger.info("Starting to listen for audit requests from MoonScape...")
        
        # In a real implementation, this would be a webhook endpoint or a
        # continuous polling mechanism. For demonstration, we'll just
        # simulate receiving a request.
        
        # Simulated request processing would go here
        logger.info("Listening for audit requests. Press Ctrl+C to stop.")
        
        try:
            # This is where you'd implement the actual listening mechanism
            # For example, a Flask webhook endpoint or a polling loop
            while True:
                # Simulate checking for messages
                logger.info("Checking for new audit requests...")
                # In a real implementation, you'd check the HCS-10 topics
                # or a webhook endpoint for new messages
                
                # For demonstration, we'll just wait and then exit
                import time
                time.sleep(10)
                logger.info("No new requests. Waiting...")
        except KeyboardInterrupt:
            logger.info("Stopped listening for audit requests.")
    
    def process_audit_request(self, connection_id: int, contract_code: str, contract_metadata: Dict):
        """
        Process an audit request received from MoonScape.
        
        Args:
            connection_id: Connection ID from MoonScape
            contract_code: Smart contract code to audit
            contract_metadata: Metadata about the contract
        
        Returns:
            Dict containing the audit results
        """
        logger.info(f"Processing audit request for connection {connection_id}")
        
        try:
            # Step 1: Static analysis with Slither
            analysis_result = self.analyzer.analyze_contract(
                contract_code,
                contract_metadata.get("language", "solidity")
            )
            logger.info(f"Analysis completed with {len(analysis_result.get('vulnerabilities', []))} vulnerabilities")
            
            # Step 2: Process vulnerabilities with LLM
            vulnerabilities = analysis_result.get("vulnerabilities", [])
            processed_vulnerabilities = []
            
            if vulnerabilities:
                processed_vulnerabilities = self.llm_processor.process_vulnerabilities(
                    vulnerabilities,
                    contract_code
                )
                logger.info(f"LLM processing completed with {len(processed_vulnerabilities)} vulnerabilities")
            else:
                logger.info("No vulnerabilities to process")
            
            # Calculate audit score
            total_severity = 0
            for v in processed_vulnerabilities:
                severity_value = v.get("severity_level_value", 0)
                if isinstance(severity_value, (int, float)):
                    total_severity += max(0, 5 - severity_value) * 2
            
            audit_score = max(0, min(100, 100 - total_severity))
            logger.info(f"Calculated audit score: {audit_score}")
            
            # Create audit response
            audit_response = {
                "contract_metadata": contract_metadata,
                "vulnerabilities": processed_vulnerabilities,
                "audit_score": audit_score,
                "passed": audit_score >= 80
            }
            
            # Generate PDF report
            pdf_bytes = self.report_generator.generate_pdf(audit_response)
            logger.info(f"Generated PDF report with {len(pdf_bytes)} bytes")
            
            # Store report on Hedera
            file_id = self.hedera_service.store_file(pdf_bytes, f"audit-report-{connection_id}.pdf")
            logger.info(f"Stored report on Hedera with file ID: {file_id}")
            
            # Mint NFT if audit passed
            nft_id = None
            if audit_response["passed"]:
                nft_metadata = {
                    "name": f"Audit Certificate - {contract_metadata.get('name', 'Unknown')}",
                    "score": audit_score,
                    "timestamp": self.hedera_service.get_current_timestamp(),
                    "file_id": file_id
                }
                nft_id = self.hedera_service.mint_nft(nft_metadata)
                logger.info(f"Minted NFT with ID: {nft_id}")
            
            # Send audit result via HCS-10
            tx_id = self.hcs10_agent.send_audit_result(connection_id, audit_response, file_id, nft_id)
            logger.info(f"Sent audit result with transaction ID: {tx_id}")
            
            # Return the audit results
            return {
                "audit_response": audit_response,
                "file_id": file_id,
                "nft_id": nft_id,
                "transaction_id": tx_id
            }
            
        except Exception as e:
            logger.error(f"Error processing audit request: {e}")
            # Send error message via HCS-10
            error_message = {
                "error": str(e),
                "timestamp": self.hedera_service.get_current_timestamp()
            }
            self.hcs10_agent.send_audit_result(connection_id, {"error": str(e)}, None, None)
            raise
    
    def submit_to_moonscape(self, audit_result: Dict):
        """
        Submit audit results to MoonScape's platform.
        
        Args:
            audit_result: Audit result data
            
        Returns:
            Response from MoonScape
        """
        if not self.api_key:
            logger.error("Cannot submit to MoonScape: API key not set")
            return False
        
        try:
            # Prepare submission data
            submission_data = {
                "audit_result": audit_result["audit_response"],
                "file_id": audit_result["file_id"],
                "nft_id": audit_result["nft_id"],
                "transaction_id": audit_result["transaction_id"]
            }
            
            # Send submission to MoonScape
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Submitting audit results to MoonScape: {MOONSCAPE_AUDIT_ENDPOINT}")
            response = requests.post(
                MOONSCAPE_AUDIT_ENDPOINT,
                json=submission_data,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("✅ Successfully submitted audit results to MoonScape!")
                return response.json()
            else:
                logger.error(f"❌ Failed to submit audit results: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error submitting audit results to MoonScape: {e}")
            return False


def main():
    """Main function to run the MoonScape integration."""
    print("=" * 80)
    print("MoonScape Integration for HederaAuditAI")
    print("=" * 80)
    
    try:
        # Initialize the MoonScape integrator
        integrator = MoonScapeIntegrator()
        print("✅ MoonScape integrator initialized successfully!")
        
        # Register with MoonScape
        registration_result = integrator.register_with_moonscape()
        if registration_result:
            print("✅ Registered with MoonScape successfully!")
        else:
            print("⚠️ Registration with MoonScape failed or skipped.")
        
        # Start listening for audit requests
        print("\n📡 Starting to listen for audit requests...")
        integrator.listen_for_audit_requests()
        
    except Exception as e:
        print(f"❌ Error in MoonScape integration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
