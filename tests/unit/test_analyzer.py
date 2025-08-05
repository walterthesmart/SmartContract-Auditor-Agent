"""Tests for the analyzer module."""

import pytest
from unittest.mock import patch, MagicMock

from src.core.analyzer.slither_analyzer import SlitherAnalyzer


class TestSlitherAnalyzer:
    """Test suite for the SlitherAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a SlitherAnalyzer instance for testing."""
        return SlitherAnalyzer()

    @pytest.fixture
    def sample_contract(self):
        """Sample Solidity contract with vulnerabilities."""
        return """
        pragma solidity ^0.8.0;

        contract VulnerableContract {
            mapping(address => uint256) public balances;
            
            // Missing input validation
            function deposit() public payable {
                balances[msg.sender] += msg.value;
            }
            
            // Reentrancy vulnerability
            function withdraw(uint256 amount) public {
                require(balances[msg.sender] >= amount, "Insufficient balance");
                (bool success, ) = msg.sender.call{value: amount}("");
                require(success, "Transfer failed");
                balances[msg.sender] -= amount;
            }
        }
        """

    @patch("src.analyzer.slither_analyzer.subprocess.run")
    def test_analyze_contract_success(self, mock_run, analyzer, sample_contract):
        """Test successful contract analysis."""
        # Mock subprocess.run to return a valid JSON response
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = """
        {
            "detectors": [
                {
                    "id": "reentrancy-eth",
                    "check": "Reentrancy",
                    "impact": "High",
                    "description": "Reentrancy vulnerability in withdraw function",
                    "first_markdown_element": {
                        "line": 13,
                        "code_snippet": "function withdraw(uint256 amount) public {"
                    },
                    "cwe": ["CWE-841"]
                }
            ],
            "metrics": {
                "complexity": 2,
                "nLines": 20
            }
        }
        """
        mock_run.return_value = mock_process

        # Run analysis
        result = analyzer.analyze_contract(sample_contract)

        # Verify results
        assert "vulnerabilities" in result
        assert len(result["vulnerabilities"]) >= 1  # At least one from Slither
        
        # Check for Hedera-specific checks
        hedera_vulns = [v for v in result["vulnerabilities"] if v["id"].startswith("HED-")]
        assert len(hedera_vulns) > 0
        
        # Check contract metrics
        assert "contract_metrics" in result
        assert result["contract_metrics"]["complexity"] == 2
        assert result["contract_metrics"]["loc"] == 20

    @patch("src.analyzer.slither_analyzer.subprocess.run")
    def test_analyze_contract_slither_error(self, mock_run, analyzer, sample_contract):
        """Test handling of Slither errors."""
        # Mock subprocess.run to return an error
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Error analyzing contract"
        mock_run.return_value = mock_process

        # Check that RuntimeError is raised
        with pytest.raises(RuntimeError):
            analyzer.analyze_contract(sample_contract)

    def test_severity_to_value(self, analyzer):
        """Test severity string to numeric value conversion."""
        assert analyzer._severity_to_value("High") == 3
        assert analyzer._severity_to_value("Medium") == 2
        assert analyzer._severity_to_value("Low") == 1
        assert analyzer._severity_to_value("Informational") == 0
        assert analyzer._severity_to_value("Unknown") == 0

    def test_check_hedera_specific(self, analyzer, sample_contract):
        """Test Hedera-specific vulnerability checks."""
        vulnerabilities = analyzer._check_hedera_specific(sample_contract)
        
        # The sample contract has payable function without validation
        assert any(v["id"] == "HED-002" for v in vulnerabilities)
        
        # Test contract with token association
        contract_with_association = """
        pragma solidity ^0.8.0;
        
        contract SafeContract {
            function associateToken(address token) public {
                // Token association logic
            }
        }
        """
        vulnerabilities = analyzer._check_hedera_specific(contract_with_association)
        assert not any(v["id"] == "HED-001" for v in vulnerabilities)
