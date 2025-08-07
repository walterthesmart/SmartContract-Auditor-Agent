#!/usr/bin/env python3
"""
Direct test of Slither analyzer to check vulnerability structure
"""

import sys
import os

# Add src to path
sys.path.append('src')

from core.analyzer.slither_analyzer import SlitherAnalyzer

def test_slither_analyzer():
    """Test Slither analyzer directly"""
    
    print("🔍 Testing Slither Analyzer Directly")
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
    
    try:
        # Create analyzer
        analyzer = SlitherAnalyzer()
        
        # Analyze contract
        result = analyzer.analyze_contract(contract_code)
        
        print(f"✅ Analysis completed")
        print(f"   Vulnerabilities found: {len(result.get('vulnerabilities', []))}")
        
        # Check vulnerability structure
        vulnerabilities = result.get('vulnerabilities', [])
        if vulnerabilities:
            print(f"\n🔍 First vulnerability structure:")
            vuln = vulnerabilities[0]
            for key, value in vuln.items():
                print(f"   {key}: {value}")
            
            # Check if location field exists
            if 'location' in vuln:
                print("✅ Location field found!")
                location = vuln['location']
                print(f"   Location structure: {location}")
            else:
                print("❌ Location field missing!")
                if 'line' in vuln:
                    print(f"   Found old 'line' field: {vuln['line']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_slither_analyzer()
    exit(0 if success else 1)
