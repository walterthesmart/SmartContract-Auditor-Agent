"""Basic test script for HederaAuditAI backend."""

import os
from src.hedera.integrator import HederaService
from src.analyzer.slither_analyzer import SlitherAnalyzer
from src.llm.processor import LLMProcessor
from src.report.generator import ReportGenerator

def test_hedera_service():
    """Test that HederaService can be initialized."""
    try:
        service = HederaService()
        print("✅ HederaService initialized successfully")
        print(f"Network: {service.network}")
        print(f"Operator ID: {service.operator_id}")
        return True
    except Exception as e:
        print(f"❌ HederaService initialization failed: {e}")
        return False

def test_slither_analyzer():
    """Test that SlitherAnalyzer can be initialized."""
    try:
        analyzer = SlitherAnalyzer()
        print("✅ SlitherAnalyzer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ SlitherAnalyzer initialization failed: {e}")
        return False

def test_llm_processor():
    """Test that LLMProcessor can be initialized."""
    try:
        processor = LLMProcessor()
        print("✅ LLMProcessor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ LLMProcessor initialization failed: {e}")
        return False

def test_report_generator():
    """Test that ReportGenerator can be initialized."""
    try:
        generator = ReportGenerator()
        print("✅ ReportGenerator initialized successfully")
        return True
    except Exception as e:
        print(f"❌ ReportGenerator initialization failed: {e}")
        return False

def test_hcs10_agent_optional():
    """Test that HCS10Agent is optional and doesn't break when not configured."""
    try:
        # Import the module to see if it loads without errors
        from src.hedera.hcs10_agent import HCS10Agent
        
        # Check if HCS10 environment variables are set
        has_topic_id = bool(os.environ.get("HCS10_REGISTRY_TOPIC_ID"))
        has_agent_name = bool(os.environ.get("HCS10_AGENT_NAME"))
        
        print(f"✅ HCS10Agent module loaded successfully")
        print(f"HCS10_REGISTRY_TOPIC_ID configured: {has_topic_id}")
        print(f"HCS10_AGENT_NAME configured: {has_agent_name}")
        return True
    except Exception as e:
        print(f"❌ HCS10Agent module failed to load: {e}")
        return False

if __name__ == "__main__":
    try:
        print("\n===== HederaAuditAI Basic Tests =====\n")
        
        print("\n----- Testing HederaService -----")
        hedera_result = test_hedera_service()
        print(f"HederaService test {'passed' if hedera_result else 'failed'}")
        
        print("\n----- Testing SlitherAnalyzer -----")
        slither_result = test_slither_analyzer()
        print(f"SlitherAnalyzer test {'passed' if slither_result else 'failed'}")
        
        print("\n----- Testing LLMProcessor -----")
        llm_result = test_llm_processor()
        print(f"LLMProcessor test {'passed' if llm_result else 'failed'}")
        
        print("\n----- Testing ReportGenerator -----")
        report_result = test_report_generator()
        print(f"ReportGenerator test {'passed' if report_result else 'failed'}")
        
        print("\n----- Testing HCS10Agent Optional Configuration -----")
        hcs10_result = test_hcs10_agent_optional()
        print(f"HCS10Agent test {'passed' if hcs10_result else 'failed'}")
        
        print("\n===== Tests Complete =====")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
