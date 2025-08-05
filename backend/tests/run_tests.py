#!/usr/bin/env python3
"""
Test runner script for HederaAuditAI backend.

This script provides a convenient way to run the test suite with various options.
"""

import argparse
import os
import sys
import subprocess


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run HederaAuditAI backend tests")
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "-k", "--filter", 
        type=str, 
        help="Only run tests matching the given substring expression"
    )
    parser.add_argument(
        "--cov", 
        action="store_true", 
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--html", 
        action="store_true", 
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "-m", "--module", 
        type=str, 
        help="Run tests for specific module (analyzer, llm, report, hedera, api)"
    )
    
    return parser.parse_args()


def run_tests(args):
    """Run the test suite with the specified options."""
    # Base pytest command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add test filter
    if args.filter:
        cmd.extend(["-k", args.filter])
    
    # Add module filter
    if args.module:
        valid_modules = ["analyzer", "llm", "report", "hedera", "api"]
        if args.module not in valid_modules:
            print(f"Error: Invalid module '{args.module}'. Valid options are: {', '.join(valid_modules)}")
            return 1
        
        cmd.extend([f"tests/test_{args.module}.py" if not args.module.startswith("test_") else f"tests/{args.module}.py"])
    
    # Add coverage options
    if args.cov:
        cmd.extend(["--cov=src", "--cov-report=term"])
        
        if args.html:
            cmd.append("--cov-report=html")
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    
    # Run tests
    return subprocess.call(cmd)


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_tests(args))
