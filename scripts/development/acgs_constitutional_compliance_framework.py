#!/usr/bin/env python3
"""
ACGS Constitutional Compliance Framework
Constitutional Hash: cdd01ef066bc6cf2

Unified framework for constitutional compliance validation across all ACGS tools.

Features:
- Constitutional hash validation (cdd01ef066bc6cf2)
- ACGS service integration (Auth 8016, PostgreSQL 5439, Redis 6389)
- FastAPI + Pydantic v2 patterns
- Async/await throughout
- Comprehensive compliance checking
- Audit logging and reporting
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
import aioredis
import asyncpg
from pydantic import BaseModel, Field, validator

# Constitutional compliance hash - MUST be validated in all operations
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS service configuration
ACGS_SERVICES = {
    "auth": {
        "url": "http://localhost:8016",
        "name": "Auth Service",
        "required": True,
    },
    "postgresql": {
        "url": "postgresql://localhost:5439/acgs_db",
        "name": "PostgreSQL Database",
        "required": True,
    },
    "redis": {
        "url": "redis://localhost:6389/0",
        "name": "Redis Cache",
        "required": True,
    },
}

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConstitutionalComplianceError(Exception):
    """Exception raised for constitutional compliance violations."""

    pass


class ACGSServiceConfig(BaseModel):
    """ACGS service configuration model."""

    url: str = Field(..., description="Service URL")
    name: str = Field(..., description="Service name")
    required: bool = Field(True, description="Whether service is required")
    timeout: int = Field(10, description="Connection timeout in seconds")

    @validator("url")
    def validate_url(cls, v):
        """Validate service URL format."""
        if not v.startswith(("http://", "https://", "postgresql://", "redis://")):
            raise ValueError("Invalid URL format")
        return v


class ComplianceValidationRequest(BaseModel):
    """Request model for compliance validation."""

    constitutional_hash: str = Field(..., description="Constitutional hash to validate")
    service_name: str = Field(..., description="Name of the requesting service")
    operation: str = Field(..., description="Operation being performed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("constitutional_hash")
    def validate_constitutional_hash(cls, v):
        """Validate constitutional hash."""
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash: {v}")
        return v


class ComplianceValidationResponse(BaseModel):
    """Response model for compliance validation."""

    is_compliant: bool = Field(..., description="Whether request is compliant")
    constitutional_hash: str = Field(..., description="Validated constitutional hash")
    validation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    service_status: Dict[str, Any] = Field(default_factory=dict)
    compliance_score: float = Field(..., description="Compliance score (0-100)")
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


@dataclass
class ComplianceMetrics:
    """Compliance metrics tracking."""

    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    compliance_rate: float = 0.0
    avg_validation_time_ms: float = 0.0
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ACGSConstitutionalComplianceFramework:
    """Unified constitutional compliance framework for ACGS tools."""

    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.compliance_metrics = ComplianceMetrics()
        self.audit_log: List[Dict[str, Any]] = []

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    async def initialize(self):
        """Initialize compliance framework."""
        logger.info("🏛️ Initializing ACGS Constitutional Compliance Framework...")

        # Validate constitutional hash first
        if not self._validate_constitutional_hash(CONSTITUTIONAL_HASH):
            raise ConstitutionalComplianceError(
                f"Invalid constitutional hash: {CONSTITUTIONAL_HASH}"
            )

        # Initialize service connections
        await self._initialize_service_connections()

        # Setup compliance monitoring
        await self._setup_compliance_monitoring()

        logger.info("✅ Constitutional compliance framework initialized")

    async def cleanup(self):
        """Cleanup resources."""
        logger.info("🧹 Cleaning up compliance framework...")

        if self.session:
            await self.session.close()

        if self.redis_client:
            await self.redis_client.close()

        if self.db_pool:
            await self.db_pool.close()

        logger.info("✅ Cleanup completed")

    def _validate_constitutional_hash(self, hash_value: str) -> bool:
        """Validate constitutional hash."""
        return hash_value == CONSTITUTIONAL_HASH

    async def _initialize_service_connections(self):
        """Initialize connections to ACGS services."""
        logger.info("🔗 Initializing ACGS service connections...")

        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)

        # Initialize database connection
        try:
            db_config = {
                "host": "localhost",
                "port": 5439,
                "database": "acgs_db",
                "user": "acgs_user",
                "password": "acgs_secure_password",
                "min_size": 2,
                "max_size": 10,
                "command_timeout": 5,
            }
            self.db_pool = await asyncpg.create_pool(**db_config)
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")

        # Initialize Redis connection
        try:
            self.redis_client = await aioredis.from_url(
                "redis://localhost:6389/0", encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")

    async def _setup_compliance_monitoring(self):
        """Setup compliance monitoring infrastructure."""
        logger.info("📊 Setting up compliance monitoring...")

        try:
            # Store constitutional hash in Redis for validation
            if self.redis_client:
                await self.redis_client.set(
                    "constitutional:hash", CONSTITUTIONAL_HASH, ex=86400  # 24 hours
                )

                # Initialize compliance metrics
                await self.redis_client.set(
                    "compliance:metrics",
                    json.dumps(self.compliance_metrics.__dict__),
                    ex=3600,  # 1 hour
                )

            # Create compliance audit table if database available
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS compliance_audit (
                            id SERIAL PRIMARY KEY,
                            constitutional_hash VARCHAR(32) NOT NULL,
                            service_name VARCHAR(100) NOT NULL,
                            operation VARCHAR(100) NOT NULL,
                            is_compliant BOOLEAN NOT NULL,
                            compliance_score FLOAT NOT NULL,
                            violations TEXT[],
                            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            metadata JSONB
                        )
                    """
                    )

                    # Create index for performance
                    await conn.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_compliance_audit_hash 
                        ON compliance_audit(constitutional_hash)
                    """
                    )

                    await conn.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_compliance_audit_timestamp 
                        ON compliance_audit(timestamp)
                    """
                    )

            logger.info("✅ Compliance monitoring setup completed")

        except Exception as e:
            logger.error(f"❌ Compliance monitoring setup failed: {e}")

    async def validate_compliance(
        self, request: ComplianceValidationRequest
    ) -> ComplianceValidationResponse:
        """Validate constitutional compliance for a request."""
        start_time = time.perf_counter()

        logger.info(
            f"🔍 Validating compliance for {request.service_name}:{request.operation}"
        )

        try:
            # Validate constitutional hash
            if not self._validate_constitutional_hash(request.constitutional_hash):
                raise ConstitutionalComplianceError(
                    f"Invalid constitutional hash: {request.constitutional_hash}"
                )

            # Check service connectivity
            service_status = await self._check_service_connectivity()

            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(service_status, request)

            # Identify violations
            violations = self._identify_violations(service_status, request)

            # Generate recommendations
            recommendations = self._generate_recommendations(violations, service_status)

            # Determine overall compliance
            is_compliant = compliance_score >= 90.0 and len(violations) == 0

            # Create response
            response = ComplianceValidationResponse(
                is_compliant=is_compliant,
                constitutional_hash=CONSTITUTIONAL_HASH,
                service_status=service_status,
                compliance_score=compliance_score,
                violations=violations,
                recommendations=recommendations,
            )

            # Update metrics
            validation_time_ms = (time.perf_counter() - start_time) * 1000
            await self._update_compliance_metrics(is_compliant, validation_time_ms)

            # Log audit record
            await self._log_compliance_audit(request, response, validation_time_ms)

            logger.info(
                f"✅ Compliance validation completed: "
                f"{'COMPLIANT' if is_compliant else 'NON-COMPLIANT'} "
                f"(Score: {compliance_score:.1f}/100)"
            )

            return response

        except Exception as e:
            logger.error(f"❌ Compliance validation failed: {e}")

            # Create error response
            response = ComplianceValidationResponse(
                is_compliant=False,
                constitutional_hash=CONSTITUTIONAL_HASH,
                compliance_score=0.0,
                violations=[f"Validation error: {str(e)}"],
                recommendations=["Fix validation errors and retry"],
            )

            # Update metrics for failure
            validation_time_ms = (time.perf_counter() - start_time) * 1000
            await self._update_compliance_metrics(False, validation_time_ms)

            return response

    async def _check_service_connectivity(self) -> Dict[str, Any]:
        """Check connectivity to all ACGS services."""
        service_status = {}

        # Check Auth Service
        try:
            async with self.session.get("http://localhost:8016/health") as response:
                service_status["auth"] = {
                    "available": response.status == 200,
                    "status_code": response.status,
                    "response_time_ms": 0,  # Would measure in real implementation
                }
        except Exception as e:
            service_status["auth"] = {
                "available": False,
                "error": str(e),
            }

        # Check PostgreSQL
        service_status["postgresql"] = {
            "available": self.db_pool is not None,
            "pool_size": self.db_pool.get_size() if self.db_pool else 0,
        }

        # Check Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                service_status["redis"] = {"available": True}
            else:
                service_status["redis"] = {"available": False}
        except Exception as e:
            service_status["redis"] = {
                "available": False,
                "error": str(e),
            }

        return service_status

    def _calculate_compliance_score(
        self, service_status: Dict[str, Any], request: ComplianceValidationRequest
    ) -> float:
        """Calculate compliance score based on various factors."""
        score = 100.0

        # Constitutional hash validation (40 points)
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            score -= 40.0

        # Service availability (30 points total)
        auth_available = service_status.get("auth", {}).get("available", False)
        db_available = service_status.get("postgresql", {}).get("available", False)
        redis_available = service_status.get("redis", {}).get("available", False)

        if not auth_available:
            score -= 15.0
        if not db_available:
            score -= 10.0
        if not redis_available:
            score -= 5.0

        # Request format validation (20 points)
        if not request.service_name:
            score -= 10.0
        if not request.operation:
            score -= 10.0

        # Timestamp validation (10 points)
        time_diff = abs(
            (datetime.now(timezone.utc) - request.timestamp).total_seconds()
        )
        if time_diff > 300:  # More than 5 minutes old
            score -= 10.0

        return max(0.0, score)

    def _identify_violations(
        self, service_status: Dict[str, Any], request: ComplianceValidationRequest
    ) -> List[str]:
        """Identify compliance violations."""
        violations = []

        # Constitutional hash violations
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            violations.append(
                f"Invalid constitutional hash: {request.constitutional_hash}"
            )

        # Service availability violations
        if not service_status.get("auth", {}).get("available", False):
            violations.append("Auth Service (8016) not available")
        if not service_status.get("postgresql", {}).get("available", False):
            violations.append("PostgreSQL Database (5439) not available")
        if not service_status.get("redis", {}).get("available", False):
            violations.append("Redis Cache (6389) not available")

        # Request format violations
        if not request.service_name.strip():
            violations.append("Missing or empty service_name")
        if not request.operation.strip():
            violations.append("Missing or empty operation")

        # Timestamp violations
        time_diff = abs(
            (datetime.now(timezone.utc) - request.timestamp).total_seconds()
        )
        if time_diff > 300:
            violations.append(f"Request timestamp too old: {time_diff:.1f}s")

        return violations

    def _generate_recommendations(
        self, violations: List[str], service_status: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on violations and service status."""
        recommendations = []

        # Constitutional hash recommendations
        if any("constitutional hash" in v for v in violations):
            recommendations.append(
                f"Use correct constitutional hash: {CONSTITUTIONAL_HASH}"
            )

        # Service availability recommendations
        if not service_status.get("auth", {}).get("available", False):
            recommendations.append("Start Auth Service on port 8016")
        if not service_status.get("postgresql", {}).get("available", False):
            recommendations.append("Start PostgreSQL Database on port 5439")
        if not service_status.get("redis", {}).get("available", False):
            recommendations.append("Start Redis Cache on port 6389")

        # Request format recommendations
        if any("service_name" in v for v in violations):
            recommendations.append("Provide valid service_name in requests")
        if any("operation" in v for v in violations):
            recommendations.append("Provide valid operation in requests")

        # Timestamp recommendations
        if any("timestamp" in v for v in violations):
            recommendations.append("Use current timestamp in requests")

        # General recommendations
        if not violations:
            recommendations.append("Maintain current compliance standards")
        else:
            recommendations.append("Address all violations for full compliance")
            recommendations.append("Implement automated compliance monitoring")

        return recommendations

    async def _update_compliance_metrics(
        self, is_compliant: bool, validation_time_ms: float
    ):
        """Update compliance metrics."""
        self.compliance_metrics.total_validations += 1

        if is_compliant:
            self.compliance_metrics.successful_validations += 1
        else:
            self.compliance_metrics.failed_validations += 1

        # Update compliance rate
        self.compliance_metrics.compliance_rate = (
            self.compliance_metrics.successful_validations
            / self.compliance_metrics.total_validations
        )

        # Update average validation time
        total_time = (
            self.compliance_metrics.avg_validation_time_ms
            * (self.compliance_metrics.total_validations - 1)
            + validation_time_ms
        )
        self.compliance_metrics.avg_validation_time_ms = (
            total_time / self.compliance_metrics.total_validations
        )

        # Store metrics in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.set(
                    "compliance:metrics",
                    json.dumps(self.compliance_metrics.__dict__),
                    ex=3600,
                )
            except Exception as e:
                logger.error(f"Failed to update metrics in Redis: {e}")

    async def _log_compliance_audit(
        self,
        request: ComplianceValidationRequest,
        response: ComplianceValidationResponse,
        validation_time_ms: float,
    ):
        """Log compliance audit record."""
        audit_record = {
            "constitutional_hash": request.constitutional_hash,
            "service_name": request.service_name,
            "operation": request.operation,
            "is_compliant": response.is_compliant,
            "compliance_score": response.compliance_score,
            "violations": response.violations,
            "validation_time_ms": validation_time_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": request.metadata,
        }

        # Add to in-memory audit log
        self.audit_log.append(audit_record)

        # Keep only last 1000 records in memory
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

        # Store in database if available
        if self.db_pool:
            try:
                async with self.db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO compliance_audit (
                            constitutional_hash, service_name, operation,
                            is_compliant, compliance_score, violations,
                            timestamp, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                        request.constitutional_hash,
                        request.service_name,
                        request.operation,
                        response.is_compliant,
                        response.compliance_score,
                        response.violations,
                        datetime.now(timezone.utc),
                        json.dumps(request.metadata),
                    )
            except Exception as e:
                logger.error(f"Failed to log audit record to database: {e}")

        # Store in Redis if available
        if self.redis_client:
            try:
                # Store latest audit records
                await self.redis_client.lpush(
                    "compliance:audit_log", json.dumps(audit_record, default=str)
                )
                # Keep only last 100 records
                await self.redis_client.ltrim("compliance:audit_log", 0, 99)
            except Exception as e:
                logger.error(f"Failed to log audit record to Redis: {e}")

    async def get_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        logger.info("📋 Generating compliance report...")

        try:
            # Get current service status
            service_status = await self._check_service_connectivity()

            # Calculate overall system compliance
            system_compliance_score = self._calculate_system_compliance_score(
                service_status
            )

            # Get recent audit records
            recent_audits = self.audit_log[-50:] if self.audit_log else []

            # Calculate compliance trends
            compliance_trends = self._calculate_compliance_trends(recent_audits)

            report = {
                "report_timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "system_compliance": {
                    "overall_score": system_compliance_score,
                    "service_status": service_status,
                    "is_fully_compliant": system_compliance_score >= 90.0,
                },
                "metrics": self.compliance_metrics.__dict__,
                "trends": compliance_trends,
                "recent_audits": recent_audits,
                "recommendations": self._generate_system_recommendations(
                    service_status
                ),
            }

            # Save report
            await self._save_compliance_report(report)

            return report

        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {"error": str(e)}

    def _calculate_system_compliance_score(
        self, service_status: Dict[str, Any]
    ) -> float:
        """Calculate overall system compliance score."""
        score = 100.0

        # Service availability scoring
        if not service_status.get("auth", {}).get("available", False):
            score -= 30.0  # Auth service is critical
        if not service_status.get("postgresql", {}).get("available", False):
            score -= 25.0  # Database is critical
        if not service_status.get("redis", {}).get("available", False):
            score -= 15.0  # Cache is important

        # Compliance rate scoring
        compliance_rate = self.compliance_metrics.compliance_rate
        if compliance_rate < 0.95:  # Less than 95%
            score -= (0.95 - compliance_rate) * 100  # Proportional penalty

        # Performance scoring
        avg_validation_time = self.compliance_metrics.avg_validation_time_ms
        if avg_validation_time > 100:  # More than 100ms
            score -= min(
                20.0, (avg_validation_time - 100) / 10
            )  # Up to 20 point penalty

        return max(0.0, score)

    def _calculate_compliance_trends(
        self, recent_audits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate compliance trends from recent audit data."""
        if not recent_audits:
            return {"error": "No audit data available"}

        # Calculate compliance rate trend
        compliant_count = sum(
            1 for audit in recent_audits if audit.get("is_compliant", False)
        )
        compliance_rate = compliant_count / len(recent_audits)

        # Calculate average score trend
        scores = [audit.get("compliance_score", 0) for audit in recent_audits]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Calculate common violations
        all_violations = []
        for audit in recent_audits:
            all_violations.extend(audit.get("violations", []))

        violation_counts = {}
        for violation in all_violations:
            violation_counts[violation] = violation_counts.get(violation, 0) + 1

        # Sort violations by frequency
        common_violations = sorted(
            violation_counts.items(), key=lambda x: x[1], reverse=True
        )[
            :5
        ]  # Top 5

        return {
            "compliance_rate": round(compliance_rate, 3),
            "average_score": round(avg_score, 2),
            "total_audits": len(recent_audits),
            "compliant_audits": compliant_count,
            "common_violations": common_violations,
        }

    def _generate_system_recommendations(
        self, service_status: Dict[str, Any]
    ) -> List[str]:
        """Generate system-wide recommendations."""
        recommendations = []

        # Service recommendations
        if not service_status.get("auth", {}).get("available", False):
            recommendations.append("Critical: Start Auth Service on port 8016")
        if not service_status.get("postgresql", {}).get("available", False):
            recommendations.append("Critical: Start PostgreSQL Database on port 5439")
        if not service_status.get("redis", {}).get("available", False):
            recommendations.append("Important: Start Redis Cache on port 6389")

        # Performance recommendations
        if self.compliance_metrics.avg_validation_time_ms > 50:
            recommendations.append("Optimize compliance validation performance")

        # Compliance rate recommendations
        if self.compliance_metrics.compliance_rate < 0.95:
            recommendations.append("Improve compliance rate to >95%")

        # General recommendations
        recommendations.extend(
            [
                "Implement automated compliance monitoring",
                "Set up compliance alerting for violations",
                "Regular compliance audits and reviews",
                f"Maintain constitutional hash: {CONSTITUTIONAL_HASH}",
            ]
        )

        return recommendations

    async def _save_compliance_report(self, report: Dict[str, Any]):
        """Save compliance report to file and storage."""
        try:
            # Create reports directory
            reports_dir = Path("reports/compliance")
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"compliance_report_{timestamp}.json"
            filepath = reports_dir / filename

            # Save report
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"✅ Compliance report saved to {filepath}")

            # Also save latest report
            latest_filepath = reports_dir / "latest_compliance_report.json"
            with open(latest_filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save compliance report: {e}")


# Utility functions for easy integration
async def validate_constitutional_compliance(
    service_name: str, operation: str, metadata: Optional[Dict[str, Any]] = None
) -> ComplianceValidationResponse:
    """Utility function for quick compliance validation."""
    async with ACGSConstitutionalComplianceFramework() as framework:
        request = ComplianceValidationRequest(
            constitutional_hash=CONSTITUTIONAL_HASH,
            service_name=service_name,
            operation=operation,
            metadata=metadata or {},
        )
        return await framework.validate_compliance(request)


async def main():
    """Main function for testing compliance framework."""
    logger.info("🚀 ACGS Constitutional Compliance Framework Test...")

    async with ACGSConstitutionalComplianceFramework() as framework:
        try:
            # Test compliance validation
            request = ComplianceValidationRequest(
                constitutional_hash=CONSTITUTIONAL_HASH,
                service_name="test_service",
                operation="test_operation",
                metadata={"test": True},
            )

            response = await framework.validate_compliance(request)

            print("\n" + "=" * 60)
            print("🏛️ CONSTITUTIONAL COMPLIANCE TEST RESULTS")
            print("=" * 60)
            print(f"Compliant: {'✅' if response.is_compliant else '❌'}")
            print(f"Score: {response.compliance_score:.1f}/100")
            print(f"Violations: {len(response.violations)}")
            print(f"Constitutional Hash: {response.constitutional_hash}")

            if response.violations:
                print("\n🚨 VIOLATIONS:")
                for i, violation in enumerate(response.violations, 1):
                    print(f"  {i}. {violation}")

            if response.recommendations:
                print("\n📋 RECOMMENDATIONS:")
                for i, rec in enumerate(response.recommendations, 1):
                    print(f"  {i}. {rec}")

            print("=" * 60)

            # Generate compliance report
            report = await framework.get_compliance_report()
            print(
                f"\n📊 System Compliance Score: {report.get('system_compliance', {}).get('overall_score', 0):.1f}/100"
            )

        except Exception as e:
            logger.error(f"❌ Compliance test failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
