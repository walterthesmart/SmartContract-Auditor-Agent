#!/usr/bin/env python3
"""
Test script to verify SlitherAnalyzer fixes work correctly.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.analyzer.slither_analyzer import SlitherAnalyzer

# Sample vulnerable contract for testing
SAMPLE_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    // Vulnerable withdraw function (reentrancy)
    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount);
        
        // This is vulnerable to reentrancy
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        
        // State update after external call
        balances[msg.sender] -= _amount;
    }
    
    // Get the contract balance
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}
"""

def test_slither_analyzer():
    """Test the SlitherAnalyzer with the sample contract."""
    print("🔍 Testing SlitherAnalyzer...")
    
    try:
        # Initialize analyzer
        custom_rules_path = os.getenv("SLITHER_CUSTOM_RULES", "src/analyzer/hedera_rules.py")
        timeout = int(os.getenv("SLITHER_ANALYSIS_TIMEOUT", "300"))
        
        print(f"Custom rules path: {custom_rules_path}")
        print(f"Timeout: {timeout} seconds")
        
        analyzer = SlitherAnalyzer(custom_rules_path=custom_rules_path, timeout=timeout)
        
        # Test analysis
        print("\n📝 Analyzing sample contract...")
        result = analyzer.analyze_contract(SAMPLE_CONTRACT, "solidity")
        
        print(f"\n✅ Analysis completed!")
        print(f"Found {len(result.get('vulnerabilities', []))} vulnerabilities")
        print(f"Contract metrics: {result.get('contract_metrics', {})}")
        
        # Print vulnerabilities
        for i, vuln in enumerate(result.get('vulnerabilities', []), 1):
            print(f"\n🚨 Vulnerability {i}:")
            print(f"  ID: {vuln.get('id', 'N/A')}")
            print(f"  Title: {vuln.get('title', 'N/A')}")
            print(f"  Severity: {vuln.get('severity', 'N/A')} (Level: {vuln.get('severity_level_value', 'N/A')})")
            print(f"  Line: {vuln.get('line', 'N/A')}")
            print(f"  Description: {vuln.get('description', 'N/A')[:100]}...")
            if vuln.get('code_snippet'):
                print(f"  Code snippet preview: {vuln.get('code_snippet', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing SlitherAnalyzer: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the /analyze API endpoint."""
    print("\n🌐 Testing /analyze API endpoint...")
    
    try:
        import requests
        import json
        
        url = "http://localhost:8000/analyze"
        payload = {
            "contract_code": SAMPLE_CONTRACT,
            "contract_metadata": {
                "name": "VulnerableContract",
                "language": "solidity"
            }
        }
        
        print("Sending request to /analyze endpoint...")
        response = requests.post(url, json=payload, timeout=120)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API endpoint working!")
            print(f"Found {len(result.get('vulnerabilities', []))} vulnerabilities")
            print(f"Audit score: {result.get('audit_score', 'N/A')}")
            print(f"Passed: {result.get('passed', 'N/A')}")
            return True
        else:
            print(f"❌ API endpoint failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing API endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting SlitherAnalyzer tests...\n")
    
    # Test 1: Direct analyzer test
    analyzer_success = test_slither_analyzer()
    
    # Test 2: API endpoint test
    api_success = test_api_endpoint()
    
    print(f"\n📊 Test Results:")
    print(f"  SlitherAnalyzer: {'✅ PASS' if analyzer_success else '❌ FAIL'}")
    print(f"  API Endpoint: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if analyzer_success and api_success:
        print("\n🎉 All tests passed! The SlitherAnalyzer fixes are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)
