"""Run a specific test file with environment variables loaded from .env file."""

import os
import sys
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Run a specific test file
if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "tests/test_hedera_integrator.py::TestHederaService::test_init_with_env_vars", "--no-header"]))
