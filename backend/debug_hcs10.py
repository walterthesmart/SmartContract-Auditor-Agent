#!/usr/bin/env python3
"""
HCS-10 Debug Script for HederaAuditAI

This script helps debug HCS-10 integration issues by initializing the agent
with retry logic and proper error handling.
"""

import os
import time
import asyncio
import logging
from dotenv import load_dotenv
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("hcs10_debug")

# Load environment variables
load_dotenv()

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

async def initialize_agent_async():
    """Initialize the HCS-10 agent asynchronously."""
    from src.hedera.integrator import HederaService
    from src.hedera.hcs10_agent import HCS10Agent
    
    logger.info("Starting HCS-10 agent initialization")
    
    # Check environment variables
    registry_topic_id = os.getenv("HCS10_REGISTRY_TOPIC_ID")
    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")
    
    if not registry_topic_id:
        logger.error("HCS10_REGISTRY_TOPIC_ID not set in environment variables")
        return None
    
    if not operator_id or not operator_key:
        logger.error("Hedera operator credentials not set in environment variables")
        return None
    
    logger.info(f"Using registry topic: {registry_topic_id}")
    logger.info(f"Using operator ID: {operator_id}")
    
    try:
        # Initialize Hedera service
        logger.info("Initializing Hedera service")
        hedera_service = HederaService(
            operator_id=operator_id,
            operator_key=operator_key,
            network=os.getenv("HEDERA_NETWORK", "testnet")
        )
        
        # Initialize HCS-10 agent with retry logic
        @retry(max_attempts=3, delay=5)
        def init_agent():
            logger.info("Initializing HCS-10 agent (with retry logic)")
            return HCS10Agent(
                hedera_service=hedera_service,
                registry_topic_id=registry_topic_id,
                agent_name=os.getenv("HCS10_AGENT_NAME", "HederaAuditAI"),
                agent_description=os.getenv("HCS10_AGENT_DESCRIPTION", 
                                          "AI-powered auditing tool for Hedera smart contracts")
            )
        
        agent = init_agent()
        logger.info("HCS-10 agent initialized successfully")
        logger.info(f"Inbound topic: {agent.inbound_topic_id}")
        logger.info(f"Outbound topic: {agent.outbound_topic_id}")
        logger.info(f"Metadata topic: {agent.metadata_topic_id}")
        
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize HCS-10 agent: {e}")
        return None

async def test_analyze_contract():
    """Test the Slither analyzer."""
    from src.analyzer.slither_analyzer import SlitherAnalyzer
    
    logger.info("Testing Slither analyzer")
    
    # Check environment variables
    custom_rules_path = os.getenv("SLITHER_CUSTOM_RULES")
    
    if not custom_rules_path:
        logger.error("SLITHER_CUSTOM_RULES not set in environment variables")
        return False
    
    logger.info(f"Using custom rules path: {custom_rules_path}")
    
    # Sample contract for testing
    sample_contract = """
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
    
    try:
        # Initialize analyzer
        logger.info("Initializing SlitherAnalyzer")
        analyzer = SlitherAnalyzer(custom_rules_path)
        
        # Analyze contract
        logger.info("Analyzing contract")
        result = analyzer.analyze_contract(sample_contract, "solidity")
        
        logger.info(f"Analysis completed with {len(result)} findings")
        for i, finding in enumerate(result):
            logger.info(f"Finding {i+1}: {finding['title']} - {finding['severity']}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to analyze contract: {e}")
        return False

async def main():
    """Main function to run the debug script."""
    logger.info("Starting HCS-10 debug script")
    
    # Test Slither analyzer
    analyzer_success = await test_analyze_contract()
    logger.info(f"Slither analyzer test {'succeeded' if analyzer_success else 'failed'}")
    
    # Initialize HCS-10 agent
    agent = await initialize_agent_async()
    if agent:
        logger.info("HCS-10 agent initialization successful")
    else:
        logger.error("HCS-10 agent initialization failed")
    
    logger.info("Debug script completed")

if __name__ == "__main__":
    asyncio.run(main())
