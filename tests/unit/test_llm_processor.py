"""Tests for the LLM processor module."""

import pytest
from unittest.mock import patch, MagicMock

from src.core.llm.processor import LLMProcessor


class TestLLMProcessor:
    """Test suite for the LLMProcessor class."""

    @pytest.fixture
    def mock_groq_client(self):
        """Mock Groq client for testing."""
        with patch("src.core.llm.processor.Groq") as mock_groq:
            mock_client = MagicMock()
            mock_groq.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def processor(self, mock_groq_client):
        """Create an LLMProcessor instance for testing."""
        with patch.dict("os.environ", {"GROQ_API_KEY": "test_key", "GROQ_MODEL": "test_model"}):
            return LLMProcessor()

    @pytest.fixture
    def sample_vulnerabilities(self):
        """Sample vulnerabilities for testing."""
        return [
            {
                "id": "reentrancy-eth",
                "title": "Reentrancy",
                "description": "Reentrancy vulnerability in withdraw function",
                "severity": "High",
                "severity_level_value": 3,
                "line": 13,
                "code_snippet": "function withdraw(uint256 amount) public {",
                "cwe": ["CWE-841"]
            },
            {
                "id": "HED-002",
                "title": "Unsafe HBAR Handling",
                "description": "Payable function without HBAR amount validation",
                "severity": "Medium",
                "severity_level_value": 2,
                "line": 7,
                "code_snippet": "function deposit() public payable {",
                "cwe": ["CWE-840"]
            }
        ]

    @pytest.fixture
    def sample_contract_code(self):
        """Sample contract code for testing."""
        return """
        pragma solidity ^0.8.0;

        contract VulnerableContract {
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

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError):
                LLMProcessor()

    def test_process_vulnerabilities_empty(self, processor):
        """Test processing empty vulnerabilities list."""
        result = processor.process_vulnerabilities([], "contract code")
        assert result == []

    def test_process_vulnerabilities(self, processor, mock_groq_client, sample_vulnerabilities, sample_contract_code):
        """Test processing vulnerabilities."""
        # Mock LLM responses
        mock_chat = MagicMock()
        mock_groq_client.chat.completions.create = mock_chat

        # Mock response for explanation
        mock_explanation_response = MagicMock()
        mock_explanation_response.choices = [
            MagicMock(message=MagicMock(content="Test explanation"))
        ]
        
        # Mock response for fix
        mock_fix_response = MagicMock()
        mock_fix_response.choices = [
            MagicMock(message=MagicMock(content="Test fix"))
        ]
        
        # Mock response for test case
        mock_test_response = MagicMock()
        mock_test_response.choices = [
            MagicMock(message=MagicMock(content="Test case"))
        ]
        
        # Set up mock to return different responses for each call
        mock_chat.side_effect = [
            mock_explanation_response, 
            mock_explanation_response,
            mock_fix_response, 
            mock_fix_response,
            mock_test_response, 
            mock_test_response
        ]

        # Process vulnerabilities
        result = processor.process_vulnerabilities(sample_vulnerabilities, sample_contract_code)

        # Verify results
        assert len(result) == 2
        
        for vuln in result:
            assert "explanation" in vuln
            assert vuln["explanation"] == "Test explanation"
            
            assert "fixed_code" in vuln
            assert vuln["fixed_code"] == "Test fix"
            
            assert "test_case" in vuln
            assert vuln["test_case"] == "Test case"

    def test_state_dict(self, processor):
        """Test state dictionary creation."""
        state = processor._state_dict()
        
        assert "vulnerabilities" in state
        assert isinstance(state["vulnerabilities"], list)
        assert len(state["vulnerabilities"]) == 0
        
        assert "contract_code" in state
        assert state["contract_code"] == ""
        
        assert "explanations" in state
        assert isinstance(state["explanations"], list)
        
        assert "fixes" in state
        assert isinstance(state["fixes"], list)
        
        assert "test_cases" in state
        assert isinstance(state["test_cases"], list)
        
        assert "processed_results" in state
        assert isinstance(state["processed_results"], list)
