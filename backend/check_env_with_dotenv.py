"""Script to check environment variables after loading from .env file."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def print_env_var(name):
    """Print an environment variable if it exists."""
    value = os.environ.get(name)
    if value:
        # Mask API keys for security
        if "KEY" in name and len(value) > 8:
            masked = value[:4] + "..." + value[-4:]
            print(f"{name}: {masked}")
        else:
            print(f"{name}: {value}")
    else:
        print(f"{name}: Not set")

print("\n===== Environment Variables (after loading .env) =====\n")

# Hedera configuration
print("Hedera Configuration:")
print_env_var("HEDERA_NETWORK")
print_env_var("HEDERA_ACCOUNT_ID")
print_env_var("HEDERA_PRIVATE_KEY")

# LLM configuration
print("\nLLM Configuration:")
print_env_var("GROQ_API_KEY")
print_env_var("GROQ_MODEL")

# Slither configuration
print("\nSlither Configuration:")
print_env_var("SLITHER_CUSTOM_RULES")
print_env_var("SLITHER_ANALYSIS_TIMEOUT")

# Report configuration
print("\nReport Configuration:")
print_env_var("REPORT_LOGO_PATH")

# HCS-10 configuration
print("\nHCS-10 Configuration:")
print_env_var("HCS10_REGISTRY_TOPIC_ID")
print_env_var("HCS10_AGENT_NAME")
print_env_var("HCS10_AGENT_DESCRIPTION")

# Check if we can import key modules
print("\n===== Module Import Check =====\n")

try:
    from src.hedera.integrator import HederaService
    print("✅ HederaService module imported successfully")
    
    # Try to initialize HederaService
    try:
        service = HederaService()
        print(f"✅ HederaService initialized successfully")
        print(f"   Network: {service.network}")
        print(f"   Operator ID: {service.operator_id}")
    except Exception as e:
        print(f"❌ HederaService initialization error: {e}")
        
except Exception as e:
    print(f"❌ HederaService import error: {e}")

try:
    from src.analyzer.slither_analyzer import SlitherAnalyzer
    print("✅ SlitherAnalyzer module imported successfully")
    
    # Try to initialize SlitherAnalyzer
    try:
        analyzer = SlitherAnalyzer()
        print(f"✅ SlitherAnalyzer initialized successfully")
    except Exception as e:
        print(f"❌ SlitherAnalyzer initialization error: {e}")
        
except Exception as e:
    print(f"❌ SlitherAnalyzer import error: {e}")

try:
    from src.llm.processor import LLMProcessor
    print("✅ LLMProcessor module imported successfully")
    
    # Try to initialize LLMProcessor
    try:
        processor = LLMProcessor()
        print(f"✅ LLMProcessor initialized successfully")
        print(f"   Model: {processor.model}")
    except Exception as e:
        print(f"❌ LLMProcessor initialization error: {e}")
        
except Exception as e:
    print(f"❌ LLMProcessor import error: {e}")

try:
    from src.report.generator import ReportGenerator
    print("✅ ReportGenerator module imported successfully")
    
    # Try to initialize ReportGenerator
    try:
        generator = ReportGenerator()
        print(f"✅ ReportGenerator initialized successfully")
    except Exception as e:
        print(f"❌ ReportGenerator initialization error: {e}")
        
except Exception as e:
    print(f"❌ ReportGenerator import error: {e}")

try:
    from src.hedera.hcs10_agent import HCS10Agent
    print("✅ HCS10Agent module imported successfully")
    
    # Check if HCS10 environment variables are set
    has_topic_id = bool(os.environ.get("HCS10_REGISTRY_TOPIC_ID"))
    has_agent_name = bool(os.environ.get("HCS10_AGENT_NAME"))
    
    print(f"   HCS10_REGISTRY_TOPIC_ID configured: {has_topic_id}")
    print(f"   HCS10_AGENT_NAME configured: {has_agent_name}")
    
except Exception as e:
    print(f"❌ HCS10Agent import error: {e}")

print("\n===== Check Complete =====")
