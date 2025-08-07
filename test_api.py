#!/usr/bin/env python3
"""
Test script for the Hedera Audit AI API
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Hedera Audit AI API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Root endpoint
    print("2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3: Contract analysis
    print("3. Testing contract analysis...")
    try:
        # Read the test contract
        with open("test_contract.sol", "r") as f:
            contract_code = f.read()
        
        audit_request = {
            "contract_code": contract_code,
            "contract_metadata": {
                "name": "SimpleStorage",
                "language": "solidity",
                "version": "0.8.0"
            }
        }
        
        response = requests.post(
            f"{base_url}/analyze",
            json=audit_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Analysis completed: {result.get('passed', 'Unknown')}")
            print(f"   Audit ID: {result.get('id', 'N/A')}")
            print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
            print(f"   Vulnerabilities found: {len(result.get('vulnerabilities', []))}")
            print(f"   Score: {result.get('audit_score', 'N/A')}")

            # Show summary if available
            summary = result.get('summary')
            if summary:
                print(f"   Summary:")
                print(f"     - Critical: {summary.get('critical_count', 0)}")
                print(f"     - High: {summary.get('high_count', 0)}")
                print(f"     - Medium: {summary.get('medium_count', 0)}")
                print(f"     - Low: {summary.get('low_count', 0)}")
                print(f"     - Info: {summary.get('info_count', 0)}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    print("✅ API testing completed!")

if __name__ == "__main__":
    test_api()
