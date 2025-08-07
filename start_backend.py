#!/usr/bin/env python3
"""
Simple backend startup script for the Hedera Audit AI
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

if __name__ == "__main__":
    try:
        import uvicorn

        print("🚀 Starting Hedera Audit AI Backend...")
        print("=" * 50)
        print(f"Python path: {sys.path[0]}")

        # Test import
        from api.main import app
        print("✓ FastAPI app imported successfully")

        # Start the FastAPI server
        print("🌐 Starting server on http://0.0.0.0:8000")
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
