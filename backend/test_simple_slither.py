#!/usr/bin/env python3
"""
Simple test to debug Slither output directly.
"""

import subprocess
import tempfile
import os

# Sample contract
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
    
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}
"""

def test_slither_direct():
    """Test Slither directly with different command variations."""
    
    # Create temporary contract file
    with tempfile.NamedTemporaryFile(suffix=".sol", delete=False) as temp_file:
        temp_file.write(SAMPLE_CONTRACT.encode())
        temp_path = temp_file.name
    
    try:
        print(f"Testing Slither on: {temp_path}")
        
        # Test 1: Basic Slither
        print("\n=== Test 1: Basic Slither ===")
        result1 = subprocess.run(
            ["slither", temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"Exit code: {result1.returncode}")
        print(f"Stdout:\n{result1.stdout}")
        print(f"Stderr:\n{result1.stderr}")
        
        # Test 2: Slither with JSON
        print("\n=== Test 2: Slither with JSON ===")
        result2 = subprocess.run(
            ["slither", temp_path, "--json", "-"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"Exit code: {result2.returncode}")
        print(f"Stdout length: {len(result2.stdout)}")
        print(f"Stdout:\n{result2.stdout}")
        print(f"Stderr:\n{result2.stderr}")
        
        # Test 3: Slither with specific detector
        print("\n=== Test 3: Slither with reentrancy detector ===")
        result3 = subprocess.run(
            ["slither", temp_path, "--detect", "reentrancy-eth"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"Exit code: {result3.returncode}")
        print(f"Stdout:\n{result3.stdout}")
        print(f"Stderr:\n{result3.stderr}")
        
        # Test 4: Slither with reentrancy detector and JSON
        print("\n=== Test 4: Slither with reentrancy detector and JSON ===")
        result4 = subprocess.run(
            ["slither", temp_path, "--detect", "reentrancy-eth", "--json", "-"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"Exit code: {result4.returncode}")
        print(f"Stdout length: {len(result4.stdout)}")
        print(f"Stdout:\n{result4.stdout}")
        print(f"Stderr:\n{result4.stderr}")
        
    finally:
        # Clean up
        os.unlink(temp_path)

if __name__ == "__main__":
    test_slither_direct()
