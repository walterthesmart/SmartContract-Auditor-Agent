#!/usr/bin/env python3
"""
Debug script to compare manual Slither execution vs subprocess execution
"""

import subprocess
import tempfile
import os
import json

# Sample vulnerable contract
SAMPLE_CONTRACT = '''
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable to reentrancy - external call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;  // State update after external call
    }
    
    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}
'''

def test_subprocess_vs_manual():
    """Test Slither execution in subprocess vs manual"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
        f.write(SAMPLE_CONTRACT)
        temp_file = f.name
    
    try:
        print("🔍 Testing Slither execution methods...")
        print(f"Temporary file: {temp_file}")
        print()
        
        # Test 1: Subprocess with same working directory as manual test
        print("📋 Test 1: Subprocess from backend directory")
        cmd = ["slither", temp_file, "--detect", "reentrancy-eth", "--json", "-"]
        
        print(f"Command: {' '.join(cmd)}")
        print(f"Working directory: {os.getcwd()}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()  # Use current working directory
        )
        
        print(f"Exit code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr: {result.stderr}")
        
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout)
                print("✅ JSON parsing successful")
                detectors = output.get('results', {}).get('detectors', [])
                print(f"Found {len(detectors)} detectors")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw output: {result.stdout[:200]}...")
        else:
            print("❌ No stdout output")
        
        print()
        
        # Test 2: Subprocess from temp file directory
        print("📋 Test 2: Subprocess from temp file directory")
        temp_dir = os.path.dirname(temp_file)
        temp_filename = os.path.basename(temp_file)
        
        cmd2 = ["slither", temp_filename, "--detect", "reentrancy-eth", "--json", "-"]
        print(f"Command: {' '.join(cmd2)}")
        print(f"Working directory: {temp_dir}")
        
        result2 = subprocess.run(
            cmd2,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=temp_dir
        )
        
        print(f"Exit code: {result2.returncode}")
        print(f"Stdout length: {len(result2.stdout)}")
        print(f"Stderr: {result2.stderr}")
        
        if result2.stdout.strip():
            try:
                output2 = json.loads(result2.stdout)
                print("✅ JSON parsing successful")
                detectors2 = output2.get('results', {}).get('detectors', [])
                print(f"Found {len(detectors2)} detectors")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw output: {result2.stdout[:200]}...")
        else:
            print("❌ No stdout output")
        
        print()
        
        # Test 3: Check environment variables
        print("📋 Test 3: Environment variables")
        env_vars = ['PATH', 'PYTHONPATH', 'VIRTUAL_ENV']
        for var in env_vars:
            value = os.environ.get(var, 'Not set')
            print(f"{var}: {value}")
        
        print()
        
        # Test 4: Check Slither version and installation
        print("📋 Test 4: Slither version check")
        version_result = subprocess.run(
            ["slither", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"Version exit code: {version_result.returncode}")
        print(f"Version output: {version_result.stdout.strip()}")
        print(f"Version stderr: {version_result.stderr.strip()}")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    test_subprocess_vs_manual()
