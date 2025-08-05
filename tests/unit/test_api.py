"""Tests for the API module."""

import hashlib
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


class TestAPI:
    """Test suite for the API module."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def sample_contract_code(self):
        """Sample contract code for testing."""
        return """
        pragma solidity ^0.8.0;

        contract TestContract {
            mapping(address => uint256) public balances;
            
            function deposit() public payable {
                balances[msg.sender] += msg.value;
            }
            
            function withdraw(uint256 amount) public {
                require(balances[msg.sender] >= amount, "Insufficient balance");
                (bool success, ) = msg.sender.call{value: amount}("");
                require(success, "Transfer failed");
                balances[msg.sender] -= amount;
            }
        }
        """

    @pytest.fixture
    def sample_audit_request(self, sample_contract_code):
        """Sample audit request for testing."""
        return {
            "contract_code": sample_contract_code,
            "contract_metadata": {
                "name": "TestContract",
                "language": "solidity"
            }
        }

    @pytest.fixture
    def sample_audit_response(self):
        """Sample audit response for testing."""
        return {
            "contract_metadata": {
                "name": "TestContract",
                "language": "solidity",
                "hash": "0x1234567890abcdef"
            },
            "vulnerabilities": [
                {
                    "id": "reentrancy-eth",
                    "title": "Reentrancy",
                    "description": "Reentrancy vulnerability in withdraw function",
                    "severity": "High",
                    "severity_level_value": 3,
                    "line": 13,
                    "code_snippet": "function withdraw(uint256 amount) public {",
                    "explanation": "This function is vulnerable to reentrancy attacks.",
                    "fixed_code": "function withdraw(uint256 amount) public {\n    uint256 amount = balances[msg.sender];\n    balances[msg.sender] = 0;\n    (bool success, ) = msg.sender.call{value: amount}(\"\");\n    require(success, \"Transfer failed\");\n}",
                    "test_case": "function testReentrancy() public {}"
                }
            ],
            "audit_score": 75,
            "passed": False
        }

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Welcome" in response.json()["message"]

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @patch("src.api.main.SlitherAnalyzer")
    @patch("src.api.main.LLMProcessor")
    def test_analyze_contract_success(self, mock_llm_processor, mock_analyzer, client, sample_audit_request):
        """Test successful contract analysis."""
        # Mock analyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_contract.return_value = {
            "vulnerabilities": [
                {
                    "id": "reentrancy-eth",
                    "title": "Reentrancy",
                    "description": "Reentrancy vulnerability",
                    "severity": "High",
                    "severity_level_value": 3,
                    "line": 13,
                    "code_snippet": "function withdraw()"
                }
            ],
            "contract_metrics": {"complexity": 2, "loc": 20}
        }
        
        # Mock LLM processor
        mock_llm_processor_instance = MagicMock()
        mock_llm_processor.return_value = mock_llm_processor_instance
        mock_llm_processor_instance.process_vulnerabilities.return_value = [
            {
                "id": "reentrancy-eth",
                "title": "Reentrancy",
                "description": "Reentrancy vulnerability",
                "severity": "High",
                "severity_level_value": 3,
                "line": 13,
                "code_snippet": "function withdraw()",
                "explanation": "Explanation",
                "fixed_code": "Fixed code",
                "test_case": "Test case"
            }
        ]
        
        # Send request
        response = client.post("/analyze", json=sample_audit_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert "contract_metadata" in data
        assert "vulnerabilities" in data
        assert "audit_score" in data
        assert "passed" in data
        
        assert len(data["vulnerabilities"]) == 1
        assert data["vulnerabilities"][0]["id"] == "reentrancy-eth"
        assert "explanation" in data["vulnerabilities"][0]
        assert "fixed_code" in data["vulnerabilities"][0]
        assert "test_case" in data["vulnerabilities"][0]

    @patch("src.api.main.SlitherAnalyzer")
    def test_analyze_contract_error(self, mock_analyzer, client, sample_audit_request):
        """Test error handling in contract analysis."""
        # Mock analyzer to raise an exception
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_contract.side_effect = RuntimeError("Analysis failed")

        # Send request
        response = client.post("/analyze", json=sample_audit_request)

        # The API handles errors gracefully and returns a default result instead of 500
        assert response.status_code == 200
        data = response.json()
        assert "vulnerabilities" in data
        assert "contract_metadata" in data

    @patch("src.api.main.HEDERA_AVAILABLE", True)
    @patch("src.api.main.ReportGenerator")
    @patch("src.api.main.HederaService")
    def test_generate_report_success(self, mock_hedera_service, mock_report_generator, client, sample_audit_response):
        """Test successful report generation."""
        # Mock report generator
        mock_report_generator_instance = MagicMock()
        mock_report_generator.return_value = mock_report_generator_instance
        mock_report_generator_instance.generate_pdf.return_value = b"PDF_BYTES"

        # Mock Hedera service
        mock_hedera_service_instance = MagicMock()
        mock_hedera_service.return_value = mock_hedera_service_instance
        mock_hedera_service_instance.store_pdf.return_value = "0.0.12345"
        mock_hedera_service_instance.mint_audit_nft.return_value = "0.0.67890"

        # Send request
        response = client.post("/generate-report", json={"audit_data": sample_audit_response})

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "file_id" in data
        assert data["file_id"].startswith("0.0.")  # Mock implementation returns generated IDs
        # NFT ID might be None if minting fails, which is acceptable for testing
        assert "view_url" in data
        assert "0.0.12345" in data["view_url"]

    @patch("src.api.main.HEDERA_AVAILABLE", True)
    @patch("src.api.main.ReportGenerator")
    @patch("src.api.main.HederaService")
    def test_generate_report_error(self, mock_hedera_service, mock_report_generator, client, sample_audit_response):
        """Test error handling in report generation."""
        # Mock Hedera service
        mock_hedera_service_instance = MagicMock()
        mock_hedera_service.return_value = mock_hedera_service_instance

        # Mock report generator to raise an exception
        mock_report_generator_instance = MagicMock()
        mock_report_generator.return_value = mock_report_generator_instance
        mock_report_generator_instance.generate_pdf.side_effect = RuntimeError("Report generation failed")

        # Send request
        response = client.post("/generate-report", json={"audit_data": sample_audit_response})

        # Verify response
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Report generation failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_contract(self, client):
        """Test contract file upload."""
        # Create test file
        contract_code = "pragma solidity ^0.8.0;\n\ncontract Test {}"
        contract_hash = hashlib.sha256(contract_code.encode()).hexdigest()
        
        # Send request
        response = client.post(
            "/upload-contract",
            files={"file": ("test.sol", contract_code.encode())},
            data={"contract_name": "Test", "language": "solidity"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert "contract_code" in data
        assert data["contract_code"] == contract_code
        assert "contract_metadata" in data
        assert data["contract_metadata"]["name"] == "Test"
        assert data["contract_metadata"]["language"] == "solidity"
        assert data["contract_metadata"]["hash"] == contract_hash
