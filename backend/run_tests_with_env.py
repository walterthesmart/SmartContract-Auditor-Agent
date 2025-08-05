"""Run tests with environment variables loaded from .env file."""

import os
import sys
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Run the tests
if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "tests"]))
