"""
Constitutional AI Service API Endpoints
Constitutional Hash: cdd01ef066bc6cf2

This module contains all the REST API endpoints for the Constitutional AI service.
"""

import logging
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import (
    ConstitutionalComplianceRequest,
    ContentValidationRequest,
    ContentValidationResponse,
)

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalAPIEndpoints:
    """Constitutional AI API endpoints handler."""

    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_endpoints()

    def setup_endpoints(self):
        """Setup all API endpoints."""
        self._setup_health_endpoints()
        self._setup_validation_endpoints()
        self._setup_framework_endpoints()
        self._setup_compliance_endpoints()

    def _setup_health_endpoints(self):
        """Setup health and status endpoints."""

        @self.app.get("/")
        async def root():
            """Root endpoint with constitutional compliance information."""
            return {
                "service": "Constitutional AI Service",
                "version": "1.0.0",
                "status": "operational",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "description": "Production-grade constitutional compliance validation",
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics",
                    "api_status": "/api/v1/status",
                    "validation": "/api/v1/validate",
                    "compliance": "/api/v1/compliance",
                },
            }

        @self.app.get("/health")
        async def health_check():
            """Enhanced health check with constitutional compliance validation."""
            from ..validation.core import ConstitutionalValidator

            try:
                # Validate constitutional hash
                validator = ConstitutionalValidator()
                hash_validation = validator.validate_constitutional_hash()

                health_status = {
                    "status": "healthy",
                    "service": "constitutional-ai",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "hash_validation": hash_validation,
                    "components": {
                        "validation_engine": "operational",
                        "compliance_engine": "operational",
                        "audit_logging": "operational",
                    },
                    "performance": {
                        "response_time_ms": "<5",
                        "throughput_rps": ">100",
                        "compliance_rate": ">95%",
                    },
                }

                return health_status

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")

        @self.app.get("/api/v1/status")
        async def api_status():
            """Get detailed API status and capabilities."""
            from ..framework.integration import FrameworkIntegration

            try:
                framework = FrameworkIntegration()
                framework_status = framework.get_status()

                return {
                    "api_version": "v1",
                    "service": "constitutional-ai",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "capabilities": {
                        "content_validation": True,
                        "constitutional_compliance": True,
                        "formal_verification": True,
                        "real_time_detection": True,
                        "audit_logging": True,
                    },
                    "frameworks": framework_status,
                    "performance_targets": {
                        "p99_latency_ms": 5,
                        "throughput_rps": 100,
                        "compliance_rate": 0.95,
                    },
                }

            except Exception as e:
                logger.error(f"API status check failed: {e}")
                raise HTTPException(status_code=500, detail="Status check failed")

        @self.app.get("/metrics")
        async def metrics():
            """Get service metrics for monitoring."""
            from ..compliance.metrics import ComplianceMetrics

            try:
                metrics_service = ComplianceMetrics()
                return metrics_service.get_metrics()

            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                raise HTTPException(status_code=500, detail="Metrics unavailable")

    def _setup_validation_endpoints(self):
        """Setup validation endpoints."""

        @self.app.post("/api/v1/validate/content")
        async def validate_content_simple(
            request: ContentValidationRequest,
            db: AsyncSession = Depends(lambda: None),  # Placeholder for DB dependency
        ):
            """Simple content validation endpoint."""
            from ..validation.content import ContentValidator

            try:
                validator = ContentValidator()
                result = await validator.validate_content(request)

                return ContentValidationResponse(
                    is_valid=result.is_valid,
                    compliance_score=result.compliance_score,
                    violations=result.violations,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )

            except Exception as e:
                logger.error(f"Content validation failed: {e}")
                raise HTTPException(status_code=400, detail="Validation failed")

        @self.app.post("/api/v1/validate/constitutional")
        async def validate_constitutional_compliance(
            request: ConstitutionalComplianceRequest,
            db: AsyncSession = Depends(lambda: None),
        ):
            """Core constitutional compliance validation."""
            from ..validation.constitutional import ConstitutionalComplianceValidator

            try:
                validator = ConstitutionalComplianceValidator()
                result = await validator.validate_compliance(request)

                return {
                    "compliance_score": result.compliance_score,
                    "is_compliant": result.is_compliant,
                    "violations": result.violations,
                    "recommendations": result.recommendations,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "validation_timestamp": result.timestamp,
                }

            except Exception as e:
                logger.error(f"Constitutional compliance validation failed: {e}")
                raise HTTPException(
                    status_code=400, detail="Compliance validation failed"
                )

    def _setup_framework_endpoints(self):
        """Setup framework integration endpoints."""

        @self.app.get("/api/v1/framework/status")
        async def get_framework_status():
            """Get framework integration status."""
            from ..framework.integration import FrameworkIntegration

            try:
                framework = FrameworkIntegration()
                return framework.get_detailed_status()

            except Exception as e:
                logger.error(f"Framework status check failed: {e}")
                raise HTTPException(
                    status_code=500, detail="Framework status unavailable"
                )

        @self.app.post("/api/v1/framework/validate")
        async def validate_with_framework(request: Dict[str, Any]):
            """Validate using integrated frameworks."""
            from ..framework.validation import FrameworkValidator

            try:
                validator = FrameworkValidator()
                result = await validator.validate_with_frameworks(request)

                return {
                    "validation_results": result.results,
                    "framework_scores": result.framework_scores,
                    "overall_score": result.overall_score,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

            except Exception as e:
                logger.error(f"Framework validation failed: {e}")
                raise HTTPException(
                    status_code=400, detail="Framework validation failed"
                )

    def _setup_compliance_endpoints(self):
        """Setup compliance calculation endpoints."""

        @self.app.post("/api/v1/compliance/score")
        async def calculate_compliance_score(request: Dict[str, Any]):
            """Calculate comprehensive compliance score."""
            from ..compliance.calculator import ComplianceCalculator

            try:
                calculator = ComplianceCalculator()
                result = await calculator.calculate_score(request)

                return {
                    "compliance_score": result.score,
                    "component_scores": result.component_scores,
                    "risk_assessment": result.risk_assessment,
                    "recommendations": result.recommendations,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

            except Exception as e:
                logger.error(f"Compliance score calculation failed: {e}")
                raise HTTPException(status_code=400, detail="Score calculation failed")

        @self.app.post("/api/v1/compliance/impact")
        async def analyze_constitutional_impact(request: Dict[str, Any]):
            """Analyze constitutional impact of policies or decisions."""
            from ..compliance.impact import ImpactAnalyzer

            try:
                analyzer = ImpactAnalyzer()
                result = await analyzer.analyze_impact(request)

                return {
                    "impact_assessment": result.assessment,
                    "stakeholder_effects": result.stakeholder_effects,
                    "mitigation_strategies": result.mitigation_strategies,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

            except Exception as e:
                logger.error(f"Impact analysis failed: {e}")
                raise HTTPException(status_code=400, detail="Impact analysis failed")


def setup_api_endpoints(app: FastAPI) -> ConstitutionalAPIEndpoints:
    """Setup all API endpoints for the Constitutional AI service."""
    return ConstitutionalAPIEndpoints(app)
