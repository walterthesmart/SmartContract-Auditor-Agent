#!/usr/bin/env python3
"""
Asynchronous API Demo Script for HederaAuditAI Backend

This script demonstrates how to interact with the HederaAuditAI backend API
using curl commands and Python requests with proper retry logic and
asynchronous initialization for HCS-10 agent.
"""

import os
import json
import time
import hashlib
import requests
import subprocess
import asyncio
import logging
from dotenv import load_dotenv
from pathlib import Path
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("api_demo")

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

# Sample smart contract for testing
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

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    border = "=" * 80
    print(f"\n{Colors.HEADER}{border}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{border}{Colors.ENDC}\n")

def print_subheader(text):
    """Print a formatted subheader."""
    print(f"\n{Colors.BLUE}{'-' * 60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'-' * 60}{Colors.ENDC}")

def print_command(command):
    """Print a formatted command."""
    print(f"\n{Colors.CYAN}$ {command}{Colors.ENDC}")

def print_response(response):
    """Print a formatted JSON response."""
    if response:
        print(f"{Colors.GREEN}{json.dumps(response, indent=2)}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}No response or empty response{Colors.ENDC}")

def print_error(error):
    """Print a formatted error message."""
    print(f"{Colors.FAIL}{error}{Colors.ENDC}")

def retry(max_attempts=3, delay=2):
    """Retry decorator for functions that might fail due to network issues."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
                        raise e
                    logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
        return wrapper
    return decorator

def run_curl_command(command):
    """Run a curl command and return the response."""
    print_command(command)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        
        try:
            # Try to parse as JSON
            response = json.loads(output)
            print_response(response)
            return response
        except json.JSONDecodeError:
            # If not valid JSON, print as text
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{output[:1000]}...{Colors.ENDC}")
            return output
    except Exception as e:
        print_error(f"Command failed: {str(e)}")
        return None

def run_python_request(method, endpoint, data=None, files=None, timeout=120):
    """Run a Python request and return the response."""
    url = f"{BASE_URL}{endpoint}"
    print(f"$ {method.upper()} {url}")
    
    try:
        if method.lower() == "get":
            response = requests.get(url, timeout=timeout)
        elif method.lower() == "post":
            if files:
                response = requests.post(url, files=files, timeout=timeout)
            else:
                response = requests.post(url, json=data, timeout=timeout)
        else:
            print_error(f"Unsupported method: {method}")
            return None
        
        try:
            response_json = response.json()
            print_response(response_json)
            return response_json
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            return None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return None

def check_server_running():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_server():
    """Start the API server if it's not running."""
    if check_server_running():
        print(f"API server is already running at {BASE_URL}")
        return True
    
    print("API server is not running. Starting server...")
    try:
        # Start the server in the background
        subprocess.Popen(
            ["uvicorn", "src.api.main:app", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        # Wait for server to start
        for _ in range(10):
            time.sleep(1)
            if check_server_running():
                print(f"API server started successfully at {BASE_URL}")
                return True
        
        print_error("Failed to start API server")
        return False
    except Exception as e:
        print_error(f"Error starting server: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print_subheader("Testing Root Endpoint (GET /)")
    
    command = f"curl -s {BASE_URL}/"
    run_curl_command(command)

def test_health_endpoint():
    """Test the health check endpoint."""
    print_subheader("Testing Health Check Endpoint (GET /health)")
    
    command = f"curl -s {BASE_URL}/health"
    run_curl_command(command)

@retry(max_attempts=2, delay=5)
def test_analyze_endpoint():
    """Test the analyze endpoint with retry logic."""
    print_subheader("Testing Analyze Endpoint (POST /analyze)")
    
    print(f"{Colors.WARNING}Note: This endpoint may take a while to respond as it runs Slither analysis{Colors.ENDC}")
    print(f"{Colors.WARNING}If it fails, check that Slither is installed and SLITHER_CUSTOM_RULES is set correctly{Colors.ENDC}")
    
    # Create request payload
    contract_hash = hashlib.sha256(SAMPLE_CONTRACT.encode()).hexdigest()
    payload = {
        "contract_code": SAMPLE_CONTRACT,
        "contract_metadata": {
            "name": "VulnerableContract",
            "language": "solidity",
            "hash": contract_hash
        }
    }
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 120s timeout)")
    command = f"""curl -s -X POST {BASE_URL}/analyze \\
        -H "Content-Type: application/json" \\
        -m 120 \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 120s timeout)")
    response_python = run_python_request("post", "/analyze", data=payload, timeout=120)
    
    return response_python

def test_upload_contract_endpoint():
    """Test the upload contract endpoint."""
    print_subheader("Testing Upload Contract Endpoint (POST /upload-contract)")
    
    # Create a temporary contract file
    contract_path = Path("temp_contract.sol")
    contract_path.write_text(SAMPLE_CONTRACT)
    
    # Method 1: Using curl
    print("Method 1: Using curl")
    command = f"""curl -s -X POST {BASE_URL}/upload-contract \\
            -F "file=@{contract_path}" \\
            -F "contract_name=VulnerableContract" \\
            -F "language=solidity" """
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests
    print("\nMethod 2: Using Python requests")
    files = {
        "file": (contract_path.name, contract_path.read_text(), "text/plain")
    }
    data = {
        "contract_name": "VulnerableContract",
        "language": "solidity"
    }
    response_python = run_python_request("post", "/upload-contract", files={
        "file": (contract_path.name, contract_path.read_text(), "text/plain"),
        "contract_name": (None, data["contract_name"]),
        "language": (None, data["language"])
    })
    
    return response_python

@retry(max_attempts=2, delay=5)
def test_generate_report_endpoint(audit_response):
    """Test the generate report endpoint with retry logic."""
    print_subheader("Testing Generate Report Endpoint (POST /generate-report)")
    
    if not audit_response:
        print_error("No audit response available. Skipping report generation test.")
        return None
    
    # Create request payload
    payload = {
        "contract_metadata": audit_response["contract_metadata"],
        "vulnerabilities": audit_response["vulnerabilities"],
        "audit_score": audit_response["audit_score"]
    }
    
    # Method 1: Using curl
    print("Method 1: Using curl (with 120s timeout)")
    command = f"""curl -s -X POST {BASE_URL}/generate-report \\
        -H "Content-Type: application/json" \\
        -m 120 \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests
    print("\nMethod 2: Using Python requests (with 120s timeout)")
    response_python = run_python_request("post", "/generate-report", data=payload, timeout=120)
    
    return response_python

@retry(max_attempts=3, delay=10)
def test_hcs10_topics_endpoint():
    """Test the HCS-10 topics endpoint with retry logic."""
    print_subheader("Testing HCS-10 Topics Endpoint (GET /hcs10/topics)")
    
    print(f"{Colors.WARNING}Note: This endpoint may take a while as it initializes the HCS-10 agent{Colors.ENDC}")
    print(f"{Colors.WARNING}If it fails, check that HCS10_REGISTRY_TOPIC_ID is set correctly in .env{Colors.ENDC}")
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 180s timeout)")
    command = f'curl -s -m 180 {BASE_URL}/hcs10/topics'
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 180s timeout)")
    response_python = run_python_request("get", "/hcs10/topics", timeout=180)
    
    return response_python

@retry(max_attempts=2, delay=5)
def test_hcs10_connections_endpoint():
    """Test the HCS-10 connections endpoint with retry logic."""
    print_subheader("Testing HCS-10 Connections Endpoint (POST /hcs10/connections)")
    
    # Get the operator ID from environment variables
    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    if not operator_id:
        print_error("HEDERA_OPERATOR_ID not found in environment variables. Skipping connections test.")
        return None
    
    # Create request payload
    payload = {
        "account_id": operator_id  # Connect with self for testing
    }
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 120s timeout)")
    command = f"""curl -s -m 120 -X POST {BASE_URL}/hcs10/connections \\
        -H "Content-Type: application/json" \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 120s timeout)")
    response_python = run_python_request("post", "/hcs10/connections", data=payload, timeout=120)
    
    return response_python

@retry(max_attempts=2, delay=5)
def test_hcs10_audit_request_endpoint(connection_response):
    """Test the HCS-10 audit request endpoint with retry logic."""
    print_subheader("Testing HCS-10 Audit Request Endpoint (POST /hcs10/audit-request)")
    
    if not connection_response:
        print_error("No connection response available. Skipping audit request test.")
        return None
    
    # Create request payload
    contract_hash = hashlib.sha256(SAMPLE_CONTRACT.encode()).hexdigest()
    payload = {
        "connection_id": connection_response.get("connection_id"),
        "contract_code": SAMPLE_CONTRACT,
        "contract_metadata": {
            "name": "VulnerableContract",
            "language": "solidity",
            "hash": contract_hash
        }
    }
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 120s timeout)")
    command = f"""curl -s -m 120 -X POST {BASE_URL}/hcs10/audit-request \\
        -H "Content-Type: application/json" \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 120s timeout)")
    response_python = run_python_request("post", "/hcs10/audit-request", data=payload, timeout=120)
    
    return response_python

def check_env_variables():
    """Check if all required environment variables are set."""
    print_subheader("Checking Environment Variables")
    
    # Define required environment variables with descriptions
    env_vars = {
        "GROQ_API_KEY": "Required for LLM processing",
        "GROQ_MODEL": "Default is llama3-70b-8192",
        "HEDERA_NETWORK": "Default is testnet",
        "HEDERA_OPERATOR_ID": "Required for Hedera integration",
        "HEDERA_OPERATOR_KEY": "Required for Hedera integration",
        "SLITHER_CUSTOM_RULES": "Path to custom Slither rules",
        "REPORT_LOGO_PATH": "Path to logo for reports",
        "HCS10_REGISTRY_TOPIC_ID": "Required for HCS-10 integration",
        "HCS10_AGENT_NAME": "Default is HederaAuditAI",
        "HCS10_AGENT_DESCRIPTION": "Default is provided",
        "AUDIT_REGISTRY_CONTRACT_ID": "Required for audit registry"
    }
    
    all_set = True
    
    # Check each environment variable
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {description}")
        else:
            print(f"✗ {Colors.FAIL}{var}: {description} - NOT SET{Colors.ENDC}")
            all_set = False
    
    if all_set:
        print("\nAll required environment variables are set.")
    else:
        print(f"\n{Colors.FAIL}Some required environment variables are missing.{Colors.ENDC}")
    
    return all_set

async def main():
    """Main function to run the API demo."""
    print_header("HederaAuditAI API Demo (Async Version)")
    
    # Check environment variables
    check_env_variables()
    
    # Start the server if not running
    if not start_server():
        return
    
    # Test basic endpoints
    test_root_endpoint()
    test_health_endpoint()
    
    # Test upload contract endpoint
    upload_response = test_upload_contract_endpoint()
    
    # Ask user if they want to continue with more complex tests
    print("\nThe following endpoints may take longer to respond or may fail due to missing dependencies:")
    print("1. /analyze - Requires Slither and custom rules")
    print("2. /generate-report - Requires successful analyze response")
    print("3. /hcs10/* endpoints - Require HCS-10 configuration")
    
    choice = input("\nDo you want to continue testing these endpoints? (y/n): ")
    if choice.lower() != 'y':
        print_header("API Demo Completed (Basic Tests Only)")
        return
    
    # Test analyze endpoint
    audit_response = test_analyze_endpoint()
    
    # Test generate report endpoint if analyze was successful
    if audit_response and "vulnerabilities" in audit_response:
        report_response = test_generate_report_endpoint(audit_response)
    
    # Test HCS-10 endpoints
    topics_response = test_hcs10_topics_endpoint()
    
    if topics_response:
        connection_response = test_hcs10_connections_endpoint()
        
        if connection_response:
            audit_request_response = test_hcs10_audit_request_endpoint(connection_response)
    
    print_header("API Demo Completed")
    print("All API endpoints have been tested.")
    print("Check the output above for the results of each test.")

if __name__ == "__main__":
    asyncio.run(main())
