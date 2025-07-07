
#!/usr/bin/env python3
"""
Constitutional AI Service - Main Entry Point
Constitutional Hash: cdd01ef066bc6cf2

This is the main entry point for the Constitutional AI service.
The actual application logic is implemented in the app/ directory
using a modular, refactored architecture.

Key Features:
- Constitutional compliance validation with hash verification
- Cache optimization for 85% hit rate target
- Service discovery and health monitoring
- Comprehensive API endpoints for governance operations
- Integration with ACGS shared services

Performance Targets:
- P99 Latency: <5ms for constitutional operations
- Throughput: >1000 RPS with constitutional compliance
- Cache Hit Rate: >85% for constitutional data
- Availability: 99.99% uptime with monitoring
"""

import logging
import sys
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def main():
    """Main entry point for the Constitutional AI service."""
    try:
        # Import the FastAPI app from the refactored structure
        from app.main import app
        
        logger.info("🚀 Starting Constitutional AI Service")
        logger.info(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        logger.info("🏗️ Using refactored modular architecture")
        
        # Run the service
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info",
            access_log=True,
            reload_excludes=["*.log", "*.backup", "__pycache__/*"]
        )
        
    except ImportError as e:
        logger.error(f"Failed to import refactored app: {e}")
        logger.error("Please ensure all dependencies are installed and the app/ structure is complete")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start Constitutional AI service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
