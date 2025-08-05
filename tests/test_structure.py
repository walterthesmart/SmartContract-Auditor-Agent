"""Test the new project structure and imports."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from src.core.analyzer.slither_analyzer import SlitherAnalyzer
        from src.core.models import __init__ as models_init
        assert SlitherAnalyzer is not None
        assert models_init is not None
    except ImportError as e:
        pytest.fail(f"Core imports failed: {e}")


def test_integration_imports():
    """Test that integration modules can be imported."""
    try:
        from src.integrations.hedera.integrator import HederaService
        from src.integrations.hcs10.hcs10_agent import HCS10Agent
        from src.integrations.moonscape import moonscape_integration
        assert HederaService is not None
        assert HCS10Agent is not None
        assert moonscape_integration is not None
    except ImportError as e:
        pytest.fail(f"Integration imports failed: {e}")


def test_utils_imports():
    """Test that utility modules can be imported."""
    try:
        from src.utils.config import Config
        from src.utils.logging import setup_logging
        from src.utils.validators import validate_contract_code
        assert Config is not None
        assert setup_logging is not None
        assert validate_contract_code is not None
    except ImportError as e:
        pytest.fail(f"Utils imports failed: {e}")


def test_project_structure():
    """Test that the project structure is correct."""
    project_root = Path(__file__).parent.parent
    
    # Check main directories exist
    assert (project_root / "src").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "scripts").exists()
    assert (project_root / "docs").exists()
    assert (project_root / "config").exists()
    assert (project_root / "assets").exists()
    assert (project_root / "contracts").exists()
    
    # Check core structure
    assert (project_root / "src" / "core").exists()
    assert (project_root / "src" / "integrations").exists()
    assert (project_root / "src" / "api").exists()
    assert (project_root / "src" / "utils").exists()
    
    # Check test structure
    assert (project_root / "tests" / "unit").exists()
    assert (project_root / "tests" / "integration").exists()
    assert (project_root / "tests" / "fixtures").exists()


def test_config_functionality():
    """Test that configuration utilities work."""
    from src.utils.config import Config
    
    # Test config initialization (should not raise errors)
    config = Config()
    assert config is not None
    
    # Test that methods exist
    assert hasattr(config, 'groq_model')
    assert hasattr(config, 'hedera_network')
    assert hasattr(config, 'slither_timeout')


def test_validators():
    """Test validation utilities."""
    from src.utils.validators import validate_contract_code, validate_hedera_account_id
    
    # Test contract validation
    result = validate_contract_code("")
    assert not result["valid"]
    assert "empty" in result["errors"][0].lower()
    
    # Test account ID validation
    assert validate_hedera_account_id("0.0.12345")
    assert not validate_hedera_account_id("invalid")
    assert not validate_hedera_account_id("")


if __name__ == "__main__":
    pytest.main([__file__])
