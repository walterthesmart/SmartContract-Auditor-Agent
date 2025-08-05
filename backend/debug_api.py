#!/usr/bin/env python3
"""
Debug script to test the /analyze API endpoint directly and capture error details
"""

import requests
import json
import sys
import traceback

# Sample vulnerable contract
SAMPLE_CONTRACT = '''
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        
        // Vulnerable to reentrancy - external call before state update
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= _amount;  # State update after external call
    }
    
    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}
'''

def test_api_endpoint():
    """Test the /analyze API endpoint with detailed error reporting"""
    
    print("🌐 Testing /analyze API endpoint with detailed error capture...")
    
    # Prepare request payload
    payload = {
        "contract_code": SAMPLE_CONTRACT,
        "contract_metadata": {
            "name": "VulnerableContract",
            "language": "solidity",
            "version": "0.8.0"
        }
    }
    
    try:
        # Make request to API
        print("📤 Sending request to /analyze endpoint...")
        response = requests.post(
            "http://localhost:8000/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API endpoint successful!")
            result = response.json()
            print(f"Found {len(result.get('vulnerabilities', []))} vulnerabilities")
            print(f"Audit score: {result.get('audit_score', 'N/A')}")
            return True
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the FastAPI server running?")
        print("Start the server with: uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        traceback.print_exc()
        return False

def test_server_health():
    """Test if the server is running and responsive"""
    print("🔍 Testing server health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking server health: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API debug test...")
    print()
    
    # Test server health first
    if not test_server_health():
        print("\n💡 Please start the FastAPI server first:")
        print("uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print()
    
    # Test the analyze endpoint
    success = test_api_endpoint()
    
    print()
    print("📊 Debug Results:")
    print(f"  Server Health: ✅")
    print(f"  API Endpoint: {'✅' if success else '❌'}")
    
    if not success:
        print("\n🔧 Next steps:")
        print("1. Check the FastAPI server logs for detailed error messages")
        print("2. Verify all dependencies are installed")
        print("3. Check environment variables in .env file")
