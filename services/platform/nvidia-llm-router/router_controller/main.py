"""
NVIDIA LLM Router Controller

Main entry point for the router controller service.
Manages routing policies, model configurations, and health monitoring.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yaml

from api_key_manager import get_api_key_manager
from services.shared.utils import get_logger
from services.shared.database import init_database

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LLM_ROUTER_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = get_logger(__name__)

# Global configuration
config = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting NVIDIA LLM Router Controller")
    
    # Initialize database
    await init_database()
    
    # Load configuration
    await load_configuration()
    
    # Initialize API key manager
    api_key_manager = get_api_key_manager()
    
    logger.info("Router Controller started successfully")
    yield
    
    # Cleanup
    await api_key_manager.close()
    logger.info("Router Controller shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="NVIDIA LLM Router Controller",
    description="Manages routing policies and model configurations for NVIDIA LLM Router",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def load_configuration():
    """Load routing configuration from YAML file"""
    global config
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.yml")
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        # Use default configuration
        config = {
            "global": {"version": "1.0.0"},
            "models": {"standard": []},
            "task_routing": {},
            "complexity_routing": {}
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nvidia-llm-router-controller"}

@app.get("/config")
async def get_configuration():
    """Get current routing configuration"""
    return config

@app.post("/config/reload")
async def reload_configuration():
    """Reload routing configuration"""
    try:
        await load_configuration()
        return {"status": "success", "message": "Configuration reloaded"}
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload configuration")

@app.get("/models/status")
async def get_models_status():
    """Get model health and availability status"""
    # This would typically check model endpoints
    # For now, return mock status
    models_status = {}
    
    for tier, models in config.get("models", {}).items():
        for model in models:
            model_name = model.get("name", "unknown")
            models_status[model_name] = {
                "status": "available",
                "tier": tier,
                "latency_ms": model.get("latency_target_ms", 1000),
                "capabilities": model.get("capabilities", [])
            }
    
    return {"models": models_status}

@app.get("/metrics")
async def get_controller_metrics():
    """Get controller metrics"""
    return {
        "requests_processed": 0,  # Would be tracked in real implementation
        "configuration_reloads": 0,
        "active_models": len([
            model for tier_models in config.get("models", {}).values() 
            for model in tier_models
        ]),
        "uptime_seconds": 0  # Would track actual uptime
    }

if __name__ == "__main__":
    port = int(os.getenv("LLM_ROUTER_CONTROLLER_PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("LLM_ROUTER_DEBUG_MODE", "false").lower() == "true",
        log_level=os.getenv("LLM_ROUTER_LOG_LEVEL", "info").lower()
    )
