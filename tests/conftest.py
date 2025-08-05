"""Common test fixtures and configurations for the HederaAuditAI backend tests."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        # Groq API settings
        "GROQ_API_KEY": "test_groq_api_key",
        "GROQ_MODEL": "llama3-8b-8192",
        
        # Hedera settings
        "HEDERA_NETWORK": "testnet",
        "HEDERA_OPERATOR_ID": "0.0.12345",
        "HEDERA_OPERATOR_KEY": "test_operator_key",
        
        # Slither settings
        "SLITHER_CUSTOM_RULES": "/path/to/custom/rules",
        "SLITHER_ANALYSIS_TIMEOUT": "60",
        
        # Report settings
        "REPORT_LOGO_PATH": "/path/to/logo.png"
    }):
        yield


@pytest.fixture
def sample_solidity_contract():
    """Sample Solidity contract for testing."""
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


@pytest.fixture
def sample_processed_vulnerabilities():
    """Sample processed vulnerabilities for testing."""
    return [
        {
            "id": "reentrancy-eth",
            "title": "Reentrancy",
            "description": "Reentrancy vulnerability in withdraw function",
            "severity": "High",
            "severity_level_value": 3,
            "line": 13,
            "code_snippet": "function withdraw(uint256 amount) public {",
            "explanation": "This function is vulnerable to reentrancy attacks because it sends Ether before updating the balance. An attacker contract could recursively call back into this function before the balance is updated.",
            "fixed_code": "function withdraw(uint256 amount) public {\n    uint256 amount = balances[msg.sender];\n    balances[msg.sender] = 0;\n    (bool success, ) = msg.sender.call{value: amount}(\"\");\n    require(success, \"Transfer failed\");\n}",
            "test_case": "function testReentrancy() public {\n    // Setup\n    address attacker = address(new ReentrancyAttacker());\n    vm.deal(attacker, 1 ether);\n    \n    // Deposit from attacker\n    vm.prank(attacker);\n    vulnerableContract.deposit{value: 1 ether}();\n    \n    // Attack\n    vm.prank(attacker);\n    vulnerableContract.withdraw(1 ether);\n    \n    // Assert\n    assertGt(attacker.balance, 1 ether);\n}"
        },
        {
            "id": "HED-002",
            "title": "Unsafe HBAR Handling",
            "description": "Payable function without HBAR amount validation",
            "severity": "Medium",
            "severity_level_value": 2,
            "line": 7,
            "code_snippet": "function deposit() public payable {",
            "explanation": "This function accepts HBAR without validating the amount. It's recommended to add validation to ensure the amount is within expected ranges.",
            "fixed_code": "function deposit() public payable {\n    require(msg.value > 0, \"Amount must be positive\");\n    require(msg.value <= maxDepositAmount, \"Amount exceeds maximum\");\n    balances[msg.sender] += msg.value;\n}",
            "test_case": "function testDeposit() public {\n    // Test zero amount\n    vm.expectRevert(\"Amount must be positive\");\n    vulnerableContract.deposit{value: 0}();\n    \n    // Test valid amount\n    vulnerableContract.deposit{value: 1 ether}();\n    assertEq(vulnerableContract.balances(address(this)), 1 ether);\n}"
        }
    ]


@pytest.fixture
def sample_audit_data(sample_processed_vulnerabilities):
    """Sample complete audit data for testing."""
    return {
        "contract_metadata": {
            "name": "VulnerableContract",
            "language": "solidity",
            "hash": "0x" + "1" * 64
        },
        "vulnerabilities": sample_processed_vulnerabilities,
        "audit_score": 75,
        "passed": False,
        "contract_metrics": {
            "complexity": 2,
            "loc": 20
        }
    }
