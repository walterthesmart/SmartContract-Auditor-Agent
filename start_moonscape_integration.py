#!/usr/bin/env python3
"""
Start MoonScape Integration
Launches the HCS-10 service and API server for MoonScape integration
"""

import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.integrations.moonscape.moonscape_hcs10_service import MoonScapeHCS10Service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_moonscape_integration():
    """Start the complete MoonScape integration"""
    try:
        logger.info("🌙 Starting MoonScape Integration...")
        logger.info("=" * 70)
        
        # Check environment
        required_vars = ['HEDERA_OPERATOR_ID', 'HEDERA_OPERATOR_KEY', 'GROQ_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.error("Please check your config/.env file")
            return False
        
        logger.info("✅ Environment variables validated")
        
        # Start MoonScape HCS-10 service
        logger.info("🚀 Starting MoonScape HCS-10 Service...")
        service = MoonScapeHCS10Service()
        
        # Start the service
        await service.start_service()
        
    except KeyboardInterrupt:
        logger.info("👋 MoonScape integration stopped by user")
        return True
    except Exception as e:
        logger.error(f"💥 Failed to start MoonScape integration: {e}")
        return False

def start_api_server():
    """Start the FastAPI server in a separate process"""
    try:
        logger.info("🚀 Starting API server...")
        
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        process = subprocess.Popen(cmd, cwd=Path(__file__).parent)
        logger.info("✅ API server started at http://localhost:8000")
        logger.info("📚 API docs available at http://localhost:8000/docs")
        
        return process
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        return None

def main():
    """Main entry point"""
    try:
        logger.info("🌙 MoonScape Integration Launcher")
        logger.info("=" * 50)
        
        # Load environment
        from dotenv import load_dotenv
        env_path = Path("config/.env")
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"📋 Loaded environment from: {env_path}")
        else:
            logger.warning(f"⚠️  Environment file not found: {env_path}")
        
        # Start API server in background
        api_process = start_api_server()
        
        if not api_process:
            logger.error("❌ Failed to start API server")
            return 1
        
        # Wait a moment for API to start
        import time
        time.sleep(3)
        
        try:
            # Start MoonScape integration
            asyncio.run(start_moonscape_integration())
        finally:
            # Clean up API server
            if api_process:
                logger.info("🛑 Stopping API server...")
                api_process.terminate()
                api_process.wait()
        
        return 0
        
    except Exception as e:
        logger.error(f"💥 Launcher failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
