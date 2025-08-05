#!/usr/bin/env python3
"""
Deployment Readiness Checker for MoonScape Integration
This script verifies that all prerequisites are met for deploying to MoonScape.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_check(description, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {description}")
    if details:
        print(f"   {details}")

def check_file_exists(file_path, description):
    exists = Path(file_path).exists()
    print_check(description, exists, f"Path: {file_path}")
    return exists

def check_command_exists(command, description):
    try:
        # Handle Windows npm.cmd specifically
        if command == "npm" and os.name == 'nt':
            command = "npm.cmd"

        result = subprocess.run([command, "--version"],
                              capture_output=True, text=True, timeout=10)
        exists = result.returncode == 0
        version = result.stdout.strip().split('\n')[0] if exists else "Not found"
        print_check(description, exists, f"Version: {version}")
        return exists
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_check(description, False, "Command not found")
        return False

def check_env_var(var_name, description, required=True):
    value = os.getenv(var_name)
    exists = value is not None and value.strip() != ""
    
    if exists:
        # Mask sensitive values
        if "KEY" in var_name or "PRIVATE" in var_name:
            display_value = f"{value[:8]}..." if len(value) > 8 else "***"
        else:
            display_value = value
        print_check(description, True, f"Value: {display_value}")
    else:
        status_text = "Required" if required else "Optional"
        print_check(f"{description} ({status_text})", not required, "Not set")
    
    return exists or not required

def check_python_package(package_name, description):
    try:
        __import__(package_name)
        print_check(description, True, f"Package: {package_name}")
        return True
    except ImportError:
        print_check(description, False, f"Package not found: {package_name}")
        return False

def check_node_package(package_name, description):
    try:
        # Handle Windows npm.cmd specifically
        npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
        result = subprocess.run([npm_cmd, "list", package_name],
                              capture_output=True, text=True, timeout=10)
        exists = package_name in result.stdout
        print_check(description, exists, f"Package: {package_name}")
        return exists
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_check(description, False, f"npm not available or package not found: {package_name}")
        return False

def main():
    print_header("MoonScape Deployment Readiness Check")
    
    # Load environment variables
    env_path = Path("config/.env")
    if env_path.exists():
        load_dotenv(env_path)
        print(f"📋 Loaded environment from: {env_path}")
    else:
        print(f"⚠️  Environment file not found: {env_path}")
    
    all_checks_passed = True
    
    # Check system requirements
    print_header("System Requirements")
    checks = [
        check_command_exists("node", "Node.js"),
        check_command_exists("npm", "npm"),
        check_command_exists("python", "Python"),
        check_command_exists("pip", "pip"),
    ]
    all_checks_passed &= all(checks)
    
    # Check project files
    print_header("Project Files")
    checks = [
        check_file_exists("contracts/AuditRegistry.sol", "AuditRegistry contract"),
        check_file_exists("config/.env", "Environment configuration"),
        check_file_exists("package.json", "Node.js package configuration"),
        check_file_exists("requirements.txt", "Python requirements"),
        check_file_exists("src/core/analyzer/hedera_rules.py", "Slither custom rules"),
        check_file_exists("assets/images/logo.png", "Logo file"),
    ]
    all_checks_passed &= all(checks)
    
    # Check environment variables
    print_header("Environment Variables")
    checks = [
        check_env_var("HEDERA_OPERATOR_ID", "Hedera Operator ID", required=True),
        check_env_var("HEDERA_OPERATOR_KEY", "Hedera Operator Key", required=True),
        check_env_var("HEDERA_NETWORK", "Hedera Network", required=False),
        check_env_var("GROQ_API_KEY", "Groq API Key", required=True),
        check_env_var("HCS10_REGISTRY_TOPIC_ID", "HCS-10 Registry Topic", required=True),
        check_env_var("MOONSCAPE_API_KEY", "MoonScape API Key", required=False),
        check_env_var("MOONSCAPE_API_BASE", "MoonScape API Base", required=False),
    ]
    all_checks_passed &= all(checks)
    
    # Check Node.js dependencies
    print_header("Node.js Dependencies")
    checks = [
        check_node_package("@hashgraph/sdk", "Hedera SDK"),
        check_node_package("@openzeppelin/contracts", "OpenZeppelin Contracts"),
        check_node_package("dotenv", "Environment Variables"),
        check_node_package("solc", "Solidity Compiler"),
    ]
    # Node packages are not critical for basic functionality
    
    # Check Python dependencies
    print_header("Python Dependencies")
    checks = [
        check_python_package("fastapi", "FastAPI"),
        check_python_package("slither", "Slither Analyzer"),
        check_python_package("groq", "Groq Client"),
        check_python_package("dotenv", "Python dotenv"),
        check_python_package("reportlab", "Report Generator"),
    ]
    # Python packages are not critical for contract deployment
    
    # Final summary
    print_header("Deployment Readiness Summary")
    
    if all_checks_passed:
        print("🎉 All critical checks passed! You're ready to deploy to MoonScape.")
        print("\n🚀 To deploy your contract, run:")
        print("   Windows: deploy_to_moonscape.bat")
        print("   Linux/Mac: ./deploy_to_moonscape.sh")
        print("   Manual: node scripts/setup/deploy_audit_registry.js")
        
        print("\n📋 Next steps after deployment:")
        print("1. Verify contract on HashScan")
        print("2. Test MoonScape integration")
        print("3. Start the backend API")
        print("4. Run audit tests")
        
    else:
        print("❌ Some critical requirements are missing.")
        print("\n🔧 Please fix the issues above before deploying.")
        print("\n📋 Common fixes:")
        print("- Install missing system requirements")
        print("- Create and configure config/.env file")
        print("- Install Node.js dependencies: npm install")
        print("- Install Python dependencies: pip install -r requirements.txt")
    
    print(f"\n📊 Overall Status: {'✅ READY' if all_checks_passed else '❌ NOT READY'}")
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
