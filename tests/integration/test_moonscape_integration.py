#!/usr/bin/env python3
"""
Tests for MoonScape integration functionality

This module contains pytest tests for the MoonScape integration
to ensure proper functionality of the integration components.
"""

import os
import sys
import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from pathlib import Path

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MoonScape integration module
from src.integrations.moonscape.moonscape_integration import MoonScapeIntegrator, AuditRequest

# Load environment variables for testing
load_dotenv()

# Sample contract for testing
SAMPLE_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 private storedData;
    
    function set(uint256 x) public {
        storedData = x;
    }
    
    function get() public view returns (uint256) {
        return storedData;
    }
}
"""

class MockResponse:
    """Mock response class for requests"""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data

@pytest.fixture
def mock_env_variables(monkeypatch):
    """Set up mock environment variables for testing"""
    monkeypatch.setenv("MOONSCAPE_API_KEY", "test_api_key")
    monkeypatch.setenv("MOONSCAPE_API_BASE", "https://api.test.com")
    monkeypatch.setenv("HEDERA_OPERATOR_ID", "0.0.12345")
    monkeypatch.setenv("HEDERA_OPERATOR_KEY", "302e020100300506032b65700422042012a74694f53cf3a43c0281b5721cd9f307098b0e2")
    monkeypatch.setenv("HCS10_REGISTRY_TOPIC_ID", "0.0.54321")
    monkeypatch.setenv("HCS10_AGENT_NAME", "TestAuditAI")
    monkeypatch.setenv("HCS10_AGENT_DESCRIPTION", "Test description")
    monkeypatch.setenv("SLITHER_CUSTOM_RULES", "src/analyzer/rules/hedera_rules.py")
    monkeypatch.setenv("REPORT_LOGO_PATH", "assets/logo.png")

@pytest.fixture
def mock_integrator():
    """Create a mock MoonScape integrator with mocked dependencies"""
    # Create mock objects for dependencies
    mock_hedera_service = MagicMock()
    mock_hcs10_agent = MagicMock()
    mock_slither_analyzer = MagicMock()
    mock_llm_processor = MagicMock()
    mock_report_generator = MagicMock()
    
    # Configure mock returns
    mock_hedera_service.get_operator_id.return_value = "0.0.12345"
    mock_hcs10_agent.inbound_topic_id = "0.0.inbound"
    mock_hcs10_agent.outbound_topic_id = "0.0.outbound"
    mock_hcs10_agent.metadata_topic_id = "0.0.metadata"
    
    # Create the integrator with mocked dependencies
    integrator = MoonScapeIntegrator(
        hedera_service=mock_hedera_service,
        hcs10_agent=mock_hcs10_agent,
        slither_analyzer=mock_slither_analyzer,
        llm_processor=mock_llm_processor,
        report_generator=mock_report_generator
    )
    
    return integrator

@pytest.mark.parametrize("success", [True, False])
def test_register_with_moonscape(mock_env_variables, mock_integrator, success):
    """Test registering with MoonScape"""
    # Mock the requests.post method
    with patch('requests.post') as mock_post:
        # Configure the mock response
        if success:
            mock_post.return_value = MockResponse({
                "success": True,
                "agent_id": "test-agent-id",
                "message": "Agent registered successfully"
            })
        else:
            mock_post.return_value = MockResponse({
                "success": False,
                "message": "Registration failed"
            }, status_code=400)
        
        # Call the method
        result = mock_integrator.register_with_moonscape()
        
        # Assertions
        assert mock_post.called
        if success:
            assert result["success"] is True
            assert "agent_id" in result
        else:
            assert result["success"] is False
            assert "message" in result

def test_process_audit_request(mock_env_variables, mock_integrator):
    """Test processing an audit request"""
    # Create a sample audit request
    audit_request = AuditRequest(
        request_id="test-request-id",
        contract_code=SAMPLE_CONTRACT,
        contract_name="SimpleStorage",
        language="solidity"
    )
    
    # Configure mock returns for the audit pipeline
    mock_integrator.slither_analyzer.analyze.return_value = {
        "vulnerabilities": [],
        "audit_score": 95
    }
    mock_integrator.llm_processor.process_vulnerabilities.return_value = {
        "vulnerabilities": [],
        "audit_score": 95,
        "recommendations": ["No issues found"]
    }
    mock_integrator.report_generator.generate_report.return_value = "report.pdf"
    mock_integrator.hedera_service.store_file.return_value = "0.0.file123"
    mock_integrator.hedera_service.mint_nft.return_value = "0.0.nft456"
    
    # Process the audit request
    result = mock_integrator.process_audit_request(audit_request)
    
    # Assertions
    assert result is not None
    assert mock_integrator.slither_analyzer.analyze.called
    assert mock_integrator.llm_processor.process_vulnerabilities.called
    assert mock_integrator.report_generator.generate_report.called
    assert mock_integrator.hedera_service.store_file.called
    assert mock_integrator.hedera_service.mint_nft.called

@pytest.mark.parametrize("success", [True, False])
def test_submit_audit_result(mock_env_variables, mock_integrator, success):
    """Test submitting audit results to MoonScape"""
    # Create a sample audit result
    audit_result = {
        "request_id": "test-request-id",
        "contract_name": "SimpleStorage",
        "audit_score": 95,
        "vulnerabilities": [],
        "recommendations": ["No issues found"],
        "file_id": "0.0.file123",
        "nft_id": "0.0.nft456"
    }
    
    # Mock the requests.post method
    with patch('requests.post') as mock_post:
        # Configure the mock response
        if success:
            mock_post.return_value = MockResponse({
                "success": True,
                "message": "Audit result submitted successfully"
            })
        else:
            mock_post.return_value = MockResponse({
                "success": False,
                "message": "Submission failed"
            }, status_code=400)
        
        # Call the method
        result = mock_integrator.submit_audit_result(audit_result)
        
        # Assertions
        assert mock_post.called
        if success:
            assert result["success"] is True
        else:
            assert result["success"] is False
            assert "message" in result

def test_listen_for_audit_requests(mock_env_variables, mock_integrator):
    """Test listening for audit requests"""
    # Mock the HCS10Agent's listen_for_messages method
    mock_integrator.hcs10_agent.listen_for_messages.return_value = [
        {
            "type": "audit_request",
            "request_id": "test-request-id",
            "contract_code": SAMPLE_CONTRACT,
            "contract_name": "SimpleStorage",
            "language": "solidity"
        }
    ]
    
    # Mock the process_audit_request method
    mock_integrator.process_audit_request = MagicMock()
    mock_integrator.process_audit_request.return_value = {
        "audit_score": 95,
        "file_id": "0.0.file123",
        "nft_id": "0.0.nft456"
    }
    
    # Mock the submit_audit_result method
    mock_integrator.submit_audit_result = MagicMock()
    
    # Call the method with a limit of 1 iteration
    mock_integrator.listen_for_audit_requests(max_iterations=1)
    
    # Assertions
    assert mock_integrator.hcs10_agent.listen_for_messages.called
    assert mock_integrator.process_audit_request.called
    assert mock_integrator.submit_audit_result.called

def test_handle_moonscape_webhook(mock_env_variables, mock_integrator):
    """Test handling a MoonScape webhook"""
    # Create a sample webhook payload
    webhook_payload = {
        "event_type": "audit_request",
        "request_id": "webhook-request-id",
        "contract_code": SAMPLE_CONTRACT,
        "contract_name": "SimpleStorage",
        "language": "solidity"
    }
    
    # Mock the process_audit_request method
    mock_integrator.process_audit_request = MagicMock()
    mock_integrator.process_audit_request.return_value = {
        "audit_score": 95,
        "file_id": "0.0.file123",
        "nft_id": "0.0.nft456"
    }
    
    # Mock the submit_audit_result method
    mock_integrator.submit_audit_result = MagicMock()
    
    # Call the method
    result = mock_integrator.handle_moonscape_webhook(webhook_payload)
    
    # Assertions
    assert result is not None
    assert mock_integrator.process_audit_request.called
    assert mock_integrator.submit_audit_result.called

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
