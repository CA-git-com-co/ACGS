#!/usr/bin/env python3
"""
Constitutional Trainer Service - ACGS-1 Lite Integration
Production-ready FastAPI service for constitutional AI training with NVIDIA Data Flywheel integration.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import torch
import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field, validator
from starlette.responses import Response

# Import constitutional training components
from .constitutional_trainer import ConstitutionalConfig, ConstitutionalTrainer
from .metrics import ConstitutionalMetrics
from .privacy_engine import ConstitutionalPrivacyEngine
from .validators import ACGSConstitutionalValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Prometheus metrics
TRAINING_REQUESTS_TOTAL = Counter(
    "constitutional_training_requests_total",
    "Total constitutional training requests",
    ["model_type", "status", "constitutional_hash"],
)

TRAINING_DURATION = Histogram(
    "constitutional_training_duration_seconds",
    "Time spent on constitutional training",
    ["model_type", "training_phase"],
)

CONSTITUTIONAL_COMPLIANCE_SCORE = Gauge(
    "constitutional_compliance_score_current",
    "Current constitutional compliance score",
    ["model_id", "training_session"],
)

ACTIVE_TRAINING_SESSIONS = Gauge(
    "constitutional_training_sessions_active",
    "Number of active constitutional training sessions",
)


# Configuration
class ServiceConfig:
    """Service configuration with environment variable support."""

    def __init__(self):
        self.constitutional_hash = os.getenv("CONSTITUTIONAL_HASH", "cdd01ef066bc6cf2")
        self.policy_engine_url = os.getenv(
            "POLICY_ENGINE_URL", "http://policy-engine:8001"
        )
        self.audit_engine_url = os.getenv(
            "AUDIT_ENGINE_URL", "http://audit-engine:8003"
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
        self.compliance_threshold = float(os.getenv("COMPLIANCE_THRESHOLD", "0.95"))
        self.max_critique_iterations = int(os.getenv("MAX_CRITIQUE_ITERATIONS", "3"))
        self.enable_differential_privacy = (
            os.getenv("ENABLE_DIFFERENTIAL_PRIVACY", "true").lower() == "true"
        )
        self.privacy_epsilon = float(os.getenv("PRIVACY_EPSILON", "8.0"))
        self.privacy_delta = float(os.getenv("PRIVACY_DELTA", "1e-5"))


config = ServiceConfig()


# Pydantic models
class TrainingRequest(BaseModel):
    """Constitutional training request model."""

    model_name: str = Field(..., description="Base model name for training")
    training_data: List[Dict[str, Any]] = Field(
        ..., description="Training data with prompts and responses"
    )
    model_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique model identifier"
    )
    constitutional_constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Constitutional constraints"
    )
    lora_config: Optional[Dict[str, Any]] = Field(
        default=None, description="LoRA configuration parameters"
    )
    privacy_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Differential privacy configuration"
    )
    max_training_time: int = Field(
        default=3600, description="Maximum training time in seconds"
    )

    @validator("training_data")
    def validate_training_data(cls, v):
        if not v:
            raise ValueError("Training data cannot be empty")
        for item in v:
            if "prompt" not in item or "response" not in item:
                raise ValueError(
                    "Each training item must have 'prompt' and 'response' fields"
                )
        return v


class TrainingResponse(BaseModel):
    """Constitutional training response model."""

    training_id: str
    status: str
    message: str
    constitutional_compliance_score: Optional[float] = None
    model_artifacts: Optional[Dict[str, str]] = None
    training_metrics: Optional[Dict[str, Any]] = None
    privacy_metrics: Optional[Dict[str, float]] = None


class TrainingStatus(BaseModel):
    """Training status model."""

    training_id: str
    status: str
    progress: float
    constitutional_compliance_score: float
    current_phase: str
    estimated_completion: Optional[str] = None
    error_message: Optional[str] = None


# Global state management
class TrainingSessionManager:
    """Manage active training sessions."""

    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = asyncio.Lock()

    async def create_session(self, training_id: str, session_data: Dict) -> bool:
        """Create a new training session."""
        async with self.session_lock:
            if len(self.active_sessions) >= config.max_concurrent_sessions:
                return False
            self.active_sessions[training_id] = session_data
            ACTIVE_TRAINING_SESSIONS.set(len(self.active_sessions))
            return True

    async def get_session(self, training_id: str) -> Optional[Dict]:
        """Get training session data."""
        async with self.session_lock:
            return self.active_sessions.get(training_id)

    async def update_session(self, training_id: str, updates: Dict):
        """Update training session data."""
        async with self.session_lock:
            if training_id in self.active_sessions:
                self.active_sessions[training_id].update(updates)

    async def remove_session(self, training_id: str):
        """Remove training session."""
        async with self.session_lock:
            if training_id in self.active_sessions:
                del self.active_sessions[training_id]
                ACTIVE_TRAINING_SESSIONS.set(len(self.active_sessions))


session_manager = TrainingSessionManager()


# Authentication and authorization
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict[str, Any]:
    """Verify JWT token and extract user information."""
    try:
        # In production, implement proper JWT validation
        # For now, basic token validation
        token = credentials.credentials
        if not token or len(token) < 10:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Mock user data - replace with actual JWT validation
        return {
            "user_id": "constitutional-trainer-user",
            "groups": ["constitutional-ai-users"],
            "permissions": ["model_training", "constitutional_validation"],
        }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Constitutional Trainer Service")
    logger.info(f"Constitutional Hash: {config.constitutional_hash}")

    # Initialize components
    try:
        # Verify connectivity to ACGS-1 Lite services
        async with aiohttp.ClientSession() as session:
            # Test Policy Engine connectivity
            async with session.get(f"{config.policy_engine_url}/health") as resp:
                if resp.status != 200:
                    logger.warning(f"Policy Engine health check failed: {resp.status}")

            # Test Audit Engine connectivity
            async with session.get(f"{config.audit_engine_url}/health") as resp:
                if resp.status != 200:
                    logger.warning(f"Audit Engine health check failed: {resp.status}")

        logger.info("Constitutional Trainer Service started successfully")
        yield

    except Exception as e:
        logger.error(f"Failed to start Constitutional Trainer Service: {e}")
        raise
    finally:
        logger.info("Shutting down Constitutional Trainer Service")


# FastAPI application
app = FastAPI(
    title="Constitutional Trainer Service",
    description="ACGS-1 Lite Constitutional AI Training Service with NVIDIA Data Flywheel Integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://human-review-dashboard:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "constitutional-trainer", "*.acgs-lite.local"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "constitutional-trainer",
        "version": "1.0.0",
        "constitutional_hash": config.constitutional_hash,
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(session_manager.active_sessions),
    }


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Constitutional training endpoints
@app.post("/api/v1/train", response_model=TrainingResponse)
async def start_constitutional_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(verify_token),
):
    """Start constitutional training with ACGS-1 Lite integration."""
    training_id = str(uuid.uuid4())

    try:
        # Validate user permissions
        if "model_training" not in user.get("permissions", []):
            raise HTTPException(
                status_code=403, detail="Insufficient permissions for model training"
            )

        # Check concurrent session limit
        session_created = await session_manager.create_session(
            training_id,
            {
                "status": "initializing",
                "user_id": user["user_id"],
                "model_name": request.model_name,
                "start_time": datetime.utcnow().isoformat(),
                "constitutional_hash": config.constitutional_hash,
            },
        )

        if not session_created:
            raise HTTPException(
                status_code=429,
                detail=f"Maximum concurrent training sessions ({config.max_concurrent_sessions}) reached",
            )

        # Start background training task
        background_tasks.add_task(
            execute_constitutional_training, training_id, request, user
        )

        # Record metrics
        TRAINING_REQUESTS_TOTAL.labels(
            model_type=request.model_name,
            status="started",
            constitutional_hash=config.constitutional_hash,
        ).inc()

        logger.info(f"Started constitutional training session: {training_id}")

        return TrainingResponse(
            training_id=training_id,
            status="started",
            message="Constitutional training initiated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start training: {e}")
        await session_manager.remove_session(training_id)
        raise HTTPException(
            status_code=500, detail=f"Training initialization failed: {str(e)}"
        )


@app.get("/api/v1/train/{training_id}/status", response_model=TrainingStatus)
async def get_training_status(
    training_id: str, user: Dict[str, Any] = Depends(verify_token)
):
    """Get constitutional training status."""
    session_data = await session_manager.get_session(training_id)

    if not session_data:
        raise HTTPException(status_code=404, detail="Training session not found")

    # Verify user access
    if session_data.get("user_id") != user["user_id"] and "admin" not in user.get(
        "groups", []
    ):
        raise HTTPException(status_code=403, detail="Access denied to training session")

    return TrainingStatus(
        training_id=training_id,
        status=session_data.get("status", "unknown"),
        progress=session_data.get("progress", 0.0),
        constitutional_compliance_score=session_data.get("compliance_score", 0.0),
        current_phase=session_data.get("current_phase", "initializing"),
        estimated_completion=session_data.get("estimated_completion"),
        error_message=session_data.get("error_message"),
    )


@app.delete("/api/v1/train/{training_id}")
async def cancel_training(
    training_id: str, user: Dict[str, Any] = Depends(verify_token)
):
    """Cancel constitutional training session."""
    session_data = await session_manager.get_session(training_id)

    if not session_data:
        raise HTTPException(status_code=404, detail="Training session not found")

    # Verify user access
    if session_data.get("user_id") != user["user_id"] and "admin" not in user.get(
        "groups", []
    ):
        raise HTTPException(status_code=403, detail="Access denied to training session")

    # Mark session for cancellation
    await session_manager.update_session(
        training_id,
        {
            "status": "cancelling",
            "cancellation_requested": datetime.utcnow().isoformat(),
        },
    )

    logger.info(f"Training cancellation requested: {training_id}")

    return {"message": "Training cancellation requested", "training_id": training_id}


# Background training execution
async def execute_constitutional_training(
    training_id: str, request: TrainingRequest, user: Dict[str, Any]
):
    """Execute constitutional training in background."""
    start_time = time.time()

    try:
        await session_manager.update_session(
            training_id,
            {"status": "running", "current_phase": "initialization", "progress": 0.1},
        )

        # Initialize constitutional trainer
        constitutional_config = ConstitutionalConfig(
            constitutional_hash=config.constitutional_hash,
            compliance_threshold=config.compliance_threshold,
            policy_engine_url=config.policy_engine_url,
            audit_engine_url=config.audit_engine_url,
            max_critique_iterations=config.max_critique_iterations,
        )

        trainer = ConstitutionalTrainer(request.model_name, constitutional_config)

        await session_manager.update_session(
            training_id, {"current_phase": "constitutional_validation", "progress": 0.2}
        )

        # Execute constitutional training with critique-revision cycles
        training_results = await trainer.train_with_constitutional_constraints(
            training_data=request.training_data,
            lora_config=request.lora_config,
            privacy_config=(
                request.privacy_config if config.enable_differential_privacy else None
            ),
            progress_callback=lambda progress: asyncio.create_task(
                session_manager.update_session(training_id, {"progress": progress})
            ),
        )

        # Update final metrics
        compliance_score = training_results.get("constitutional_compliance_score", 0.0)
        CONSTITUTIONAL_COMPLIANCE_SCORE.labels(
            model_id=request.model_id, training_session=training_id
        ).set(compliance_score)

        # Record completion metrics
        training_duration = time.time() - start_time
        TRAINING_DURATION.labels(
            model_type=request.model_name, training_phase="complete"
        ).observe(training_duration)

        TRAINING_REQUESTS_TOTAL.labels(
            model_type=request.model_name,
            status="completed",
            constitutional_hash=config.constitutional_hash,
        ).inc()

        # Update session with results
        await session_manager.update_session(
            training_id,
            {
                "status": "completed",
                "current_phase": "finished",
                "progress": 1.0,
                "compliance_score": compliance_score,
                "training_results": training_results,
                "completion_time": datetime.utcnow().isoformat(),
                "duration_seconds": training_duration,
            },
        )

        logger.info(
            f"Constitutional training completed: {training_id}, compliance: {compliance_score:.3f}"
        )

    except Exception as e:
        logger.error(f"Constitutional training failed: {training_id}, error: {e}")

        # Record failure metrics
        TRAINING_REQUESTS_TOTAL.labels(
            model_type=request.model_name,
            status="failed",
            constitutional_hash=config.constitutional_hash,
        ).inc()

        # Update session with error
        await session_manager.update_session(
            training_id,
            {
                "status": "failed",
                "current_phase": "error",
                "error_message": str(e),
                "failure_time": datetime.utcnow().isoformat(),
            },
        )

    finally:
        # Clean up session after delay
        await asyncio.sleep(300)  # Keep session data for 5 minutes
        await session_manager.remove_session(training_id)


if __name__ == "__main__":
    import os

    # SECURITY: Configurable host binding - secure by default
    # Use 127.0.0.1 for development, 0.0.0.0 only in production with proper firewall
    host = os.getenv("HOST", "127.0.0.1")  # Secure default: localhost only
    port = int(os.getenv("PORT", "8010"))
    log_level = os.getenv("LOG_LEVEL", "info")

    # Production-grade server configuration
    config = {
        "host": host,
        "port": port,
        "reload": False,
        "log_level": log_level,
        "access_log": True,
        "workers": int(os.getenv("WORKERS", "1")),  # Single worker for development
        "loop": "asyncio",
        "http": "httptools",
        "lifespan": "on",
    }

    logger.info(f"🚀 Starting Constitutional Trainer Service on {host}:{port}")
    logger.info(
        f"🔒 Security: Host binding = {host} ({'SECURE' if host == '127.0.0.1' else 'PRODUCTION'})"
    )

    uvicorn.run("main:app", **config)
