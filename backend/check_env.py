"""Simple script to check environment variables and component initialization."""

import os
import sys

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

print("\n===== Environment Variables =====\n")

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
except Exception as e:
    print(f"❌ HederaService import error: {e}")

try:
    from src.analyzer.slither_analyzer import SlitherAnalyzer
    print("✅ SlitherAnalyzer module imported successfully")
except Exception as e:
    print(f"❌ SlitherAnalyzer import error: {e}")

try:
    from src.llm.processor import LLMProcessor
    print("✅ LLMProcessor module imported successfully")
except Exception as e:
    print(f"❌ LLMProcessor import error: {e}")

try:
    from src.report.generator import ReportGenerator
    print("✅ ReportGenerator module imported successfully")
except Exception as e:
    print(f"❌ ReportGenerator import error: {e}")

try:
    from src.hedera.hcs10_agent import HCS10Agent
    print("✅ HCS10Agent module imported successfully")
except Exception as e:
    print(f"❌ HCS10Agent import error: {e}")

print("\n===== Check Complete =====")
