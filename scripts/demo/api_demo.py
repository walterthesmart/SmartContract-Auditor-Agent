#!/usr/bin/env python3
"""
API Demo Script for HederaAuditAI Backend

This script demonstrates how to interact with the HederaAuditAI backend API
using curl commands and Python requests. It tests all available endpoints
and provides examples of how to use them, including MoonScape integration.
"""

import os
import json
import time
import hashlib
import requests
import subprocess
from dotenv import load_dotenv
from pathlib import Path

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

# Colors for terminal output
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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_subheader(text):
    """Print a formatted subheader."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'-' * 60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'-' * 60}{Colors.ENDC}\n")

def print_command(command):
    """Print a formatted command."""
    print(f"{Colors.CYAN}$ {command}{Colors.ENDC}")

def print_response(response):
    """Print a formatted JSON response."""
    if isinstance(response, str):
        print(f"{Colors.GREEN}{response}{Colors.ENDC}")
    else:
        print(f"{Colors.GREEN}{json.dumps(response, indent=2)}{Colors.ENDC}")

def print_error(error):
    """Print a formatted error message."""
    print(f"{Colors.FAIL}ERROR: {error}{Colors.ENDC}")

def run_curl_command(command):
    """Run a curl command and return the response."""
    print_command(command)
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        try:
            response = json.loads(result.stdout)
            print_response(response)
            return response
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{result.stdout[:1000]}...{Colors.ENDC}")
            return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return None
    except Exception as e:
        print_error(str(e))
        return None

def run_python_request(method, endpoint, data=None, files=None):
    """Run a Python request and return the response."""
    url = f"{BASE_URL}{endpoint}"
    print_command(f"{method.upper()} {url}")
    
    try:
        if method.lower() == "get":
            response = requests.get(url, timeout=30)
        elif method.lower() == "post":
            if files:
                response = requests.post(url, files=files, data=data, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
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
            return response.text
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        print_error(str(e))
        return None

def check_server_running():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_server():
    """Start the API server if it's not running."""
    if check_server_running():
        print(f"{Colors.GREEN}API server is already running at {BASE_URL}{Colors.ENDC}")
        return True
    
    print(f"{Colors.WARNING}API server is not running. Starting server...{Colors.ENDC}")
    
    # Start the server in a new terminal window (macOS specific)
    try:
        subprocess.Popen([
            "osascript", "-e", 
            f'tell app "Terminal" to do script "cd {os.getcwd()} && source venv/bin/activate && uvicorn src.api.main:app --reload"'
        ])
        
        # Wait for the server to start
        for _ in range(10):
            time.sleep(1)
            if check_server_running():
                print(f"{Colors.GREEN}API server started successfully at {BASE_URL}{Colors.ENDC}")
                return True
        
        print_error("Failed to start API server")
        return False
    except Exception as e:
        print_error(f"Failed to start API server: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print_subheader("Testing Root Endpoint (GET /)")
    command = f'curl -s {BASE_URL}/'
    run_curl_command(command)

def test_health_endpoint():
    """Test the health check endpoint."""
    print_subheader("Testing Health Check Endpoint (GET /health)")
    command = f'curl -s {BASE_URL}/health'
    run_curl_command(command)

def test_analyze_endpoint():
    """Test the analyze endpoint."""
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
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=120)
        try:
            response_python = response.json()
            print_response(response_python)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            response_python = None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        response_python = None
    
    return response_python

def test_upload_contract_endpoint():
    """Test the upload contract endpoint."""
    print_subheader("Testing Upload Contract Endpoint (POST /upload-contract)")
    
    # Create a temporary contract file
    temp_file_path = "temp_contract.sol"
    with open(temp_file_path, "w") as f:
        f.write(SAMPLE_CONTRACT)
    
    try:
        # Method 1: Using curl
        print("Method 1: Using curl")
        command = f"""curl -s -X POST {BASE_URL}/upload-contract \\
            -F "file=@{temp_file_path}" \\
            -F "contract_name=VulnerableContract" \\
            -F "language=solidity" """
        response_curl = run_curl_command(command)
        
        # Method 2: Using Python requests
        print("\nMethod 2: Using Python requests")
        with open(temp_file_path, "rb") as f:
            files = {"file": ("temp_contract.sol", f, "text/plain")}
            data = {"contract_name": "VulnerableContract", "language": "solidity"}
            response_python = run_python_request("post", "/upload-contract", data=data, files=files)
        
        return response_python
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def test_generate_report_endpoint(audit_response):
    """Test the generate report endpoint."""
    print_subheader("Testing Generate Report Endpoint (POST /generate-report)")
    
    if not audit_response:
        print_error("No audit response available. Skipping report generation.")
        return None
    
    # Create request payload
    payload = {
        "audit_data": audit_response
    }
    
    # Method 1: Using curl
    print("Method 1: Using curl")
    command = f"""curl -s -X POST {BASE_URL}/generate-report \\
        -H "Content-Type: application/json" \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests
    print("\nMethod 2: Using Python requests")
    response_python = run_python_request("post", "/generate-report", data=payload)
    
    return response_python

def test_hcs10_topics_endpoint():
    """Test the HCS-10 topics endpoint."""
    print_subheader("Testing HCS-10 Topics Endpoint (GET /hcs10/topics)")
    
    print(f"{Colors.WARNING}Note: This endpoint may take a while as it initializes the HCS-10 agent{Colors.ENDC}")
    print(f"{Colors.WARNING}If it fails, check that HCS10_REGISTRY_TOPIC_ID is set correctly in .env{Colors.ENDC}")
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 120s timeout)")
    command = f'curl -s -m 120 {BASE_URL}/hcs10/topics'
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 120s timeout)")
    try:
        response = requests.get(f"{BASE_URL}/hcs10/topics", timeout=120)
        try:
            response_python = response.json()
            print_response(response_python)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            response_python = None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        response_python = None
    
    return response_python

def test_hcs10_connections_endpoint():
    """Test the HCS-10 connections endpoint."""
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
    try:
        response = requests.post(f"{BASE_URL}/hcs10/connections", json=payload, timeout=120)
        try:
            response_python = response.json()
            print_response(response_python)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            response_python = None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        response_python = None
    
    return response_python

def test_hcs10_audit_request_endpoint(connection_response):
    """Test the HCS-10 audit request endpoint."""
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
    try:
        response = requests.post(f"{BASE_URL}/hcs10/audit-request", json=payload, timeout=120)
        try:
            response_python = response.json()
            print_response(response_python)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            response_python = None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        response_python = None
    
    return response_python


def test_moonscape_registration():
    """Test the MoonScape registration process."""
    print_subheader("Testing MoonScape Registration")
    
    # Check for required environment variables
    moonscape_api_key = os.getenv("MOONSCAPE_API_KEY")
    if not moonscape_api_key:
        print_error("MOONSCAPE_API_KEY not found in environment variables. Skipping MoonScape tests.")
        return None
    
    moonscape_api_base = os.getenv("MOONSCAPE_API_BASE", "https://api.hashgraphonline.com")
    
    # Create request payload for agent registration
    payload = {
        "agent_name": os.getenv("HCS10_AGENT_NAME", "HederaAuditAI"),
        "agent_description": os.getenv("HCS10_AGENT_DESCRIPTION", "AI-powered auditing tool for Hedera smart contracts"),
        "api_key": moonscape_api_key
    }
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 30s timeout)")
    command = f"""curl -s -m 30 -X POST {moonscape_api_base}/register-agent \\
        -H "Content-Type: application/json" \\
        -H "Authorization: Bearer {moonscape_api_key}" \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 30s timeout)")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {moonscape_api_key}"
        }
        response = requests.post(f"{moonscape_api_base}/register-agent", 
                               headers=headers,
                               json=payload, 
                               timeout=30)
        try:
            response_python = response.json()
            print_response(response_python)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            response_python = None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        response_python = None
    
    return response_python


def test_moonscape_audit_submission():
    """Test submitting an audit result to MoonScape."""
    print_subheader("Testing MoonScape Audit Submission")
    
    # Check for required environment variables
    moonscape_api_key = os.getenv("MOONSCAPE_API_KEY")
    if not moonscape_api_key:
        print_error("MOONSCAPE_API_KEY not found in environment variables. Skipping MoonScape tests.")
        return None
    
    moonscape_api_base = os.getenv("MOONSCAPE_API_BASE", "https://api.hashgraphonline.com")
    
    # Create a sample audit result
    contract_hash = hashlib.sha256(SAMPLE_CONTRACT.encode()).hexdigest()
    audit_result = {
        "contract_metadata": {
            "name": "VulnerableContract",
            "language": "solidity",
            "hash": contract_hash
        },
        "audit_score": 75,
        "vulnerabilities": [
            {
                "name": "Reentrancy",
                "severity": "High",
                "description": "The withdraw function is vulnerable to reentrancy attacks",
                "line_numbers": [38, 42]
            }
        ],
        "timestamp": int(time.time())
    }
    
    # Create request payload
    payload = {
        "audit_result": audit_result,
        "file_id": f"0.0.{int(time.time())}",  # Mock file ID
        "api_key": moonscape_api_key
    }
    
    # Method 1: Using curl with increased timeout
    print("Method 1: Using curl (with 30s timeout)")
    command = f"""curl -s -m 30 -X POST {moonscape_api_base}/submit-audit \\
        -H "Content-Type: application/json" \\
        -H "Authorization: Bearer {moonscape_api_key}" \\
        -d '{json.dumps(payload)}'"""
    response_curl = run_curl_command(command)
    
    # Method 2: Using Python requests with increased timeout
    print("\nMethod 2: Using Python requests (with 30s timeout)")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {moonscape_api_key}"
        }
        response = requests.post(f"{moonscape_api_base}/submit-audit", 
                               headers=headers,
                               json=payload, 
                               timeout=30)
        try:
            response_python = response.json()
            print_response(response_python)
        except json.JSONDecodeError:
            print(f"{Colors.WARNING}Raw response (not JSON):{Colors.ENDC}")
            print(f"{Colors.GREEN}{response.text[:1000]}...{Colors.ENDC}")
            if response.status_code != 200:
                print(f"{Colors.FAIL}HTTP Status Code: {response.status_code}{Colors.ENDC}")
            response_python = None
    except requests.RequestException as e:
        print_error(f"Request failed: {str(e)}")
        response_python = None
    
    return response_python

def check_env_variables():
    """Check if all required environment variables are set."""
    print_subheader("Checking Environment Variables")
    
    required_vars = {
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
        "AUDIT_REGISTRY_CONTRACT_ID": "Required for audit registry",
        "MOONSCAPE_API_KEY": "Required for MoonScape integration",
        "MOONSCAPE_API_BASE": "Default is https://api.hashgraphonline.com"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"{Colors.GREEN}✓ {var}: {description}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}✗ {var}: {description} - NOT SET{Colors.ENDC}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n{Colors.WARNING}Warning: Some required environment variables are not set.{Colors.ENDC}")
        print(f"{Colors.WARNING}This may cause some API endpoints to fail.{Colors.ENDC}")
    else:
        print(f"\n{Colors.GREEN}All required environment variables are set.{Colors.ENDC}")

def main():
    """Main function to run the API demo."""
    print_header("HederaAuditAI API Demo")
    
    # Check environment variables
    check_env_variables()
    
    # Check if the server is running and start it if needed
    if not start_server():
        return
    
    # Test basic endpoints
    test_root_endpoint()
    test_health_endpoint()
    
    # Test core auditing endpoints
    upload_response = test_upload_contract_endpoint()
    
    # Ask user if they want to continue with more complex endpoints
    print(f"\n{Colors.BOLD}The following endpoints may take longer to respond or may fail due to missing dependencies:{Colors.ENDC}")
    print(f"1. /analyze - Requires Slither and custom rules")
    print(f"2. /generate-report - Requires successful analyze response")
    print(f"3. /hcs10/* endpoints - Require HCS-10 configuration")
    print(f"4. MoonScape integration - Requires MoonScape API key")
    
    choice = input(f"\n{Colors.BOLD}Do you want to continue testing these endpoints? (y/n): {Colors.ENDC}")
    if choice.lower() != 'y':
        print_header("API Demo Completed")
        print(f"{Colors.GREEN}Basic endpoints tested successfully.{Colors.ENDC}")
        return
    
    # Test more complex endpoints
    audit_response = test_analyze_endpoint()
    if audit_response:
        report_response = test_generate_report_endpoint(audit_response)
    
    # Test HCS-10 OpenConvAI endpoints
    topics_response = test_hcs10_topics_endpoint()
    if topics_response:
        connection_response = test_hcs10_connections_endpoint()
        if connection_response:
            audit_request_response = test_hcs10_audit_request_endpoint(connection_response)
    
    # Ask user if they want to test MoonScape integration
    print(f"\n{Colors.BOLD}Do you want to test the MoonScape integration? (y/n): {Colors.ENDC}")
    choice = input()
    if choice.lower() == 'y':
        # Test MoonScape integration
        registration_response = test_moonscape_registration()
        if registration_response:
            audit_submission_response = test_moonscape_audit_submission()
    
    print_header("API Demo Completed")
    print(f"{Colors.GREEN}All API endpoints have been tested.{Colors.ENDC}")
    print(f"{Colors.GREEN}Check the output above for the results of each test.{Colors.ENDC}")

if __name__ == "__main__":
    main()
