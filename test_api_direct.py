#!/usr/bin/env python3
"""
Direct test of the API function
"""

import sys
import os

# Add src to path
sys.path.append('src')

def test_api_direct():
    """Test the API function directly"""
    
    print("🔍 Testing API Function Directly")
    print("=" * 50)
    
    try:
        # Import the necessary modules
        from api.main import analyze_contract, AuditRequest, ContractMetadata
        from core.analyzer.slither_analyzer import SlitherAnalyzer
        from core.llm.processor import LLMProcessor
        
        # Create test data
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
        
        # Create request object
        metadata = ContractMetadata(
            name="SimpleStorage",
            language="solidity",
            hash="test-hash-123"
        )
        
        request = AuditRequest(
            contract_code=contract_code,
            contract_metadata=metadata
        )
        
        # Create dependencies
        analyzer = SlitherAnalyzer()
        llm_processor = LLMProcessor()
        
        print("✅ Modules imported successfully")
        
        # Call the function directly
        import asyncio
        
        async def run_test():
            result = await analyze_contract(request, analyzer, llm_processor)
            return result
        
        result = asyncio.run(run_test())
        
        print("✅ API function called successfully")
        print(f"   Result type: {type(result)}")
        
        if hasattr(result, 'vulnerabilities'):
            print(f"   Vulnerabilities: {len(result.vulnerabilities)}")
            if result.vulnerabilities:
                vuln = result.vulnerabilities[0]
                print(f"\n🔍 First vulnerability structure:")
                for attr in dir(vuln):
                    if not attr.startswith('_'):
                        value = getattr(vuln, attr)
                        if not callable(value):
                            print(f"   {attr}: {value}")
        else:
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_direct()
