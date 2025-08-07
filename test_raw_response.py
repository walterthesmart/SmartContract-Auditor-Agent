#!/usr/bin/env python3
"""
Test script to see the raw API response
"""

import requests
import json

def test_raw_response():
    """Test the raw API response"""
    
    print("🔍 Testing Raw API Response")
    print("=" * 50)
    
    # Test contract code
    contract_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 private storedData;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function set(uint256 x) public {
        storedData = x;
    }
    
    function get() public view returns (uint256) {
        return storedData;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Only owner can withdraw");
        payable(owner).transfer(address(this).balance);
    }
}
"""
    
    # Prepare request
    audit_request = {
        "contract_code": contract_code,
        "contract_metadata": {
            "name": "SimpleStorage",
            "language": "solidity",
            "hash": "test-hash-123"
        }
    }
    
    try:
        # Make API call
        response = requests.post(
            "http://localhost:8001/analyze",
            json=audit_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n📄 Raw Response:")
            print(json.dumps(result, indent=2))
            
            print(f"\n📊 Summary:")
            print(f"   Vulnerabilities: {len(result.get('vulnerabilities', []))}")
            
            if result.get('vulnerabilities'):
                vuln = result['vulnerabilities'][0]
                print(f"\n🔍 First Vulnerability Raw Structure:")
                print(json.dumps(vuln, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_response()
