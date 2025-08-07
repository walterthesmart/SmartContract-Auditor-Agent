#!/usr/bin/env python3
"""
Direct server runner for the Hedera Audit AI Backend
"""

import sys
import os
from pathlib import Path

# Change to the project directory
project_dir = Path(__file__).parent
os.chdir(project_dir)

# Add src to Python path
src_path = project_dir / "src"
sys.path.insert(0, str(src_path))

print("🚀 Starting Hedera Audit AI Backend...")
print("=" * 50)
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

try:
    # Import the FastAPI app
    from api.main import app
    print("✓ FastAPI app imported successfully")
    
    # Import uvicorn
    import uvicorn
    print("✓ Uvicorn imported successfully")
    
    # Start the server
    print("🌐 Starting server on http://localhost:8000")
    print("📖 API documentation will be available at http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
