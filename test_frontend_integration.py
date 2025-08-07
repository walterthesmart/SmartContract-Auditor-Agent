#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration
"""

import requests
import json

def test_frontend_backend_integration():
    """Test that the backend response matches frontend expectations"""
    
    print("🔗 Testing Frontend-Backend Integration")
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
    
    # Prepare request matching frontend format
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
        
        print(f"✅ API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify all expected fields are present
            required_fields = [
                'id', 'contract_metadata', 'vulnerabilities', 
                'audit_score', 'passed', 'timestamp', 'summary'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            
            print("✅ All required fields present")
            
            # Verify summary structure
            summary = result['summary']
            summary_fields = [
                'total_issues', 'critical_count', 'high_count', 
                'medium_count', 'low_count', 'info_count'
            ]
            
            missing_summary_fields = []
            for field in summary_fields:
                if field not in summary:
                    missing_summary_fields.append(field)
            
            if missing_summary_fields:
                print(f"❌ Missing summary fields: {missing_summary_fields}")
                return False
            
            print("✅ Summary structure correct")
            
            # Display results
            print("\n📊 Audit Results:")
            print(f"   ID: {result['id']}")
            print(f"   Timestamp: {result['timestamp']}")
            print(f"   Contract: {result['contract_metadata']['name']}")
            print(f"   Score: {result['audit_score']}/100")
            print(f"   Passed: {result['passed']}")
            print(f"   Total Issues: {summary['total_issues']}")
            print(f"   Breakdown:")
            print(f"     - Critical: {summary['critical_count']}")
            print(f"     - High: {summary['high_count']}")
            print(f"     - Medium: {summary['medium_count']}")
            print(f"     - Low: {summary['low_count']}")
            print(f"     - Info: {summary['info_count']}")
            
            # Verify vulnerabilities structure
            if result['vulnerabilities']:
                vuln = result['vulnerabilities'][0]
                print(f"\n🔍 First vulnerability structure:")
                for key, value in vuln.items():
                    print(f"   {key}: {value}")

                vuln_fields = ['id', 'severity', 'title', 'description', 'location']

                missing_vuln_fields = []
                for field in vuln_fields:
                    if field not in vuln:
                        missing_vuln_fields.append(field)

                if missing_vuln_fields:
                    print(f"❌ Missing vulnerability fields: {missing_vuln_fields}")
                    return False

                print("✅ Vulnerability structure correct")
            
            print("\n🎉 Frontend-Backend Integration Test PASSED!")
            return True
            
        else:
            print(f"❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_backend_integration()
    exit(0 if success else 1)
