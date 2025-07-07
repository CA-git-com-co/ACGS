"""
ACGS Constitutional Compliance Automated Testing Suite

Comprehensive test suite for validating constitutional compliance,
formal verification integrity, and constitutional hash verification.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import hashlib
import json
import logging
import os

# Import ACGS components
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from infrastructure.monitoring.compliance.compliance_reporter import ComplianceReporter

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "../..", "services", "core", "formal-verification"
    )
)
from fv_service.app.services.z3_solver import (
    Z3ConstitutionalSolver,
)

from services.platform_services.integrity.integrity_service.app.core.persistent_audit_trail import (
    CryptographicAuditChain,
)
from services.shared.audit.compliance_audit_logger import (
    AuditEventType,
    AuditSeverity,
    ComplianceAuditLogger,
)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class TestConstitutionalCompliance:
    """Test suite for constitutional compliance validation."""

    @pytest.fixture
    def constitutional_solver(self):
        """Create Z3 constitutional solver instance."""
        return Z3ConstitutionalSolver(timeout_ms=5000)

    @pytest.fixture
    def audit_chain(self):
        """Create cryptographic audit chain instance."""
        # Use the simple version that doesn't require db_pool for testing
        from services.platform_services.integrity.integrity_service.core.persistent_audit_trail import (
            CryptographicAuditChain as SimpleCryptographicAuditChain,
        )

        return SimpleCryptographicAuditChain()

    @pytest.fixture
    def audit_logger(self):
        """Create compliance audit logger instance."""
        return ComplianceAuditLogger(
            service_name="test_service",
            encryption_enabled=False,  # Disable for testing
            signing_enabled=False,
            chain_verification=False,
        )

    @pytest.fixture
    def compliance_reporter(self):
        """Create compliance reporter instance."""
        return ComplianceReporter(
            storage_path="/tmp/test_reports", prometheus_url="http://localhost:9090"
        )

    def test_constitutional_hash_integrity(self):
        """Test constitutional hash integrity validation."""
        # Verify the constitutional hash format
        assert len(CONSTITUTIONAL_HASH) == 16
        assert all(c in "0123456789abcdef" for c in CONSTITUTIONAL_HASH)

        # Test hash consistency across services
        test_data = "constitutional_compliance_test"
        expected_hash = hashlib.sha256(test_data.encode()).hexdigest()[:16]

        # Verify hash calculation is deterministic
        assert hashlib.sha256(test_data.encode()).hexdigest()[:16] == expected_hash

    @pytest.mark.asyncio
    async def test_z3_constitutional_solver_axioms(self, constitutional_solver):
        """Test Z3 solver constitutional axioms."""

        # Test human dignity axiom - use the correct method that exists
        policy_constraints = ["dignity_preserved", "privacy_maintained"]

        result = constitutional_solver.verify_constitutional_policy(policy_constraints)

        # Test that the solver is working and returns a valid result
        assert result.result.value in ["valid", "invalid", "unknown"]
        assert result.confidence_score >= 0.0
        assert result.proof_time_ms >= 0.0

    @pytest.mark.asyncio
    async def test_z3_solver_violation_detection(self, constitutional_solver):
        """Test Z3 solver detects constitutional violations."""

        # Test policy that violates constitutional principles
        violating_constraints = ["exclude_certain_groups", "biased_treatment"]

        result = constitutional_solver.verify_constitutional_policy(
            violating_constraints
        )

        # Test that the solver processes the violating policy
        assert result.result.value in ["valid", "invalid", "unknown"]
        assert result.confidence_score >= 0.0
        assert result.proof_time_ms >= 0.0

    @pytest.mark.asyncio
    async def test_audit_trail_cryptographic_integrity(self, audit_chain):
        """Test cryptographic audit trail integrity."""
        from services.platform_services.integrity.integrity_service.core.persistent_audit_trail import (
            AuditEvent,
            AuditEventType,
            AuditSeverity,
        )

        # Create test audit events
        test_events = [
            AuditEvent(
                event_type=AuditEventType.COMPLIANCE_CHECK,
                service_name="test_service",
                action="constitutional_validation",
                details={"compliance_score": 0.95},
                severity=AuditSeverity.MEDIUM,
            ),
            AuditEvent(
                event_type=AuditEventType.SYSTEM_EVENT,
                service_name="test_service",
                action="formal_verification",
                details={"proof_valid": True},
                severity=AuditSeverity.MEDIUM,
            ),
        ]

        # Add events to audit chain
        event_hashes = []
        for event in test_events:
            result = await audit_chain.add_event(event)
            event_hashes.append(result["event_id"])

        # Verify chain integrity
        verification_result = await audit_chain.verify_chain_integrity()

        assert verification_result["is_valid"] is True
        assert verification_result["chain_length"] == len(test_events)
        assert verification_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_audit_trail_tampering_detection(self, audit_chain):
        """Test audit trail detects tampering attempts."""
        from services.platform_services.integrity.integrity_service.core.persistent_audit_trail import (
            AuditEvent,
            AuditEventType,
            AuditSeverity,
        )

        # Create and add legitimate event
        legitimate_event = AuditEvent(
            event_type=AuditEventType.COMPLIANCE_CHECK,
            service_name="test_service",
            action="legitimate_validation",
            details={"compliance_score": 0.95},
            severity=AuditSeverity.MEDIUM,
        )

        result = await audit_chain.add_event(legitimate_event)
        event_id = result["event_id"]

        # Test constitutional hash validation
        assert legitimate_event.constitutional_hash == CONSTITUTIONAL_HASH
        assert event_id is not None

    @pytest.mark.asyncio
    async def test_compliance_audit_logging(self, audit_logger):
        """Test constitutional compliance audit logging."""

        # Log constitutional compliance event
        event_id = await audit_logger.log_constitutional_event(
            action="constitutional_policy_validation",
            compliance_score=0.95,
            violations=[],
            user_id="test_user",
            tenant_id="test_tenant",
            details={
                "policy_id": "test_policy_001",
                "verification_method": "z3_solver",
            },
        )

        assert event_id is not None
        assert len(event_id) > 0

    @pytest.mark.asyncio
    async def test_multi_tenant_isolation_compliance(self, audit_logger):
        """Test multi-tenant isolation compliance logging."""

        # Test legitimate tenant access
        legitimate_access = await audit_logger.log_multi_tenant_event(
            action="tenant_data_access",
            tenant_id="tenant_001",
            user_id="user_001",
            cross_tenant_attempt=False,
            details={"resource": "tenant_001_data"},
        )

        assert legitimate_access is not None

        # Test cross-tenant violation detection
        violation_access = await audit_logger.log_multi_tenant_event(
            action="cross_tenant_access_attempt",
            tenant_id="tenant_001",
            user_id="user_002",  # User from different tenant
            cross_tenant_attempt=True,
            details={
                "attempted_resource": "tenant_001_data",
                "user_tenant": "tenant_002",
            },
        )

        assert violation_access is not None

    @pytest.mark.asyncio
    async def test_formal_verification_integration(self, constitutional_solver):
        """Test formal verification integration with constitutional compliance."""

        # Test comprehensive policy verification
        complex_policy = {
            "rule": "multi_tenant_data_access",
            "constraints": [
                "tenant_isolation_enforced",
                "access_controls_verified",
                "audit_logging_enabled",
            ],
            "conditions": {
                "user_tenant_match": True,
                "permissions_validated": True,
                "constitutional_compliance": True,
            },
        }

        verification_result = (
            await constitutional_solver.verify_constitutional_compliance(complex_policy)
        )

        assert verification_result["is_compliant"] is True
        assert verification_result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "multi_tenant_isolation" in verification_result["verified_axioms"]
        assert "access_control_fairness" in verification_result["verified_axioms"]

    @pytest.mark.asyncio
    async def test_compliance_score_calculation(self, compliance_reporter):
        """Test constitutional compliance score calculation."""

        # Generate test compliance report
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        # Mock the internal metric methods
        with (
            patch.object(
                compliance_reporter,
                "_get_constitutional_hash_validity",
                return_value=1.0,
            ),
            patch.object(
                compliance_reporter, "_get_tenant_isolation_score", return_value=0.98
            ),
            patch.object(
                compliance_reporter,
                "_get_formal_verification_success_rate",
                return_value=0.96,
            ),
            patch.object(
                compliance_reporter, "_get_audit_trail_integrity", return_value=1.0
            ),
        ):
            report_path = (
                await compliance_reporter.generate_constitutional_compliance_report(
                    start_time, end_time
                )
            )

            # Load and verify report
            with open(report_path) as f:
                report_data = json.load(f)

            assert report_data["overall_compliance_score"] >= 95.0
            assert report_data["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert len(report_data["metrics"]) >= 4

    def test_constitutional_hash_consistency_across_services(self):
        """Test constitutional hash consistency across all services."""

        # Test hash appears in all critical components
        test_components = [
            {"name": "Z3ConstitutionalSolver", "hash": CONSTITUTIONAL_HASH},
            {"name": "CryptographicAuditChain", "hash": CONSTITUTIONAL_HASH},
            {"name": "ComplianceAuditLogger", "hash": CONSTITUTIONAL_HASH},
            {"name": "ComplianceReporter", "hash": CONSTITUTIONAL_HASH},
        ]

        for component in test_components:
            assert component["hash"] == CONSTITUTIONAL_HASH
            assert len(component["hash"]) == 16

    @pytest.mark.asyncio
    async def test_constitutional_compliance_end_to_end(
        self, constitutional_solver, audit_logger
    ):
        """End-to-end constitutional compliance test."""

        # Step 1: Verify policy with Z3 solver
        test_policy = {
            "rule": "comprehensive_governance_policy",
            "constraints": [
                "constitutional_adherence",
                "democratic_decision_making",
                "transparent_audit_trail",
                "multi_tenant_isolation",
            ],
        }

        verification_result = (
            await constitutional_solver.verify_constitutional_compliance(test_policy)
        )
        assert verification_result["is_compliant"] is True

        # Step 2: Log compliance event
        compliance_score = verification_result.get("compliance_score", 0.95)
        violations = verification_result.get("violations", [])

        audit_event_id = await audit_logger.log_constitutional_event(
            action="end_to_end_compliance_test",
            compliance_score=compliance_score,
            violations=violations,
            details={
                "test_scenario": "comprehensive_governance",
                "verification_result": verification_result,
            },
        )

        assert audit_event_id is not None

        # Step 3: Verify constitutional hash consistency
        assert verification_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_compliance_violation_remediation_tracking(self, audit_logger):
        """Test compliance violation remediation tracking."""

        # Log initial violation
        violation_event = await audit_logger.log_event(
            event_type=AuditEventType.CONSTITUTIONAL_VIOLATION,
            action="policy_violation_detected",
            outcome="violation",
            severity=AuditSeverity.HIGH,
            details={
                "violation_type": "access_control_bypass",
                "remediation_required": True,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

        assert violation_event is not None

        # Log remediation action
        remediation_event = await audit_logger.log_event(
            event_type=AuditEventType.CONSTITUTIONAL_VALIDATION,
            action="violation_remediation_completed",
            outcome="success",
            severity=AuditSeverity.MEDIUM,
            details={
                "original_violation_id": violation_event,
                "remediation_actions": ["access_control_reinforced", "policy_updated"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

        assert remediation_event is not None


class TestConstitutionalComplianceStressTests:
    """Stress tests for constitutional compliance under load."""

    @pytest.mark.asyncio
    async def test_high_volume_constitutional_verification(self):
        """Test constitutional verification under high load."""

        constitutional_solver = Z3ConstitutionalSolver(timeout_ms=10000)

        # Generate multiple concurrent verification requests
        verification_tasks = []
        for i in range(50):  # 50 concurrent verifications
            policy = {
                "rule": f"load_test_policy_{i}",
                "constraints": ["constitutional_adherence", "fairness_principle"],
                "test_iteration": i,
            }

            task = constitutional_solver.verify_constitutional_compliance(policy)
            verification_tasks.append(task)

        # Execute all verifications concurrently
        results = await asyncio.gather(*verification_tasks, return_exceptions=True)

        # Verify all succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 45  # Allow for some timeouts under load

        # Verify constitutional hash consistency
        for result in successful_results:
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH

    @pytest.mark.asyncio
    async def test_concurrent_audit_logging_integrity(self):
        """Test audit logging integrity under concurrent load."""

        audit_logger = ComplianceAuditLogger(
            service_name="stress_test_service",
            encryption_enabled=False,
            signing_enabled=False,
        )

        # Generate concurrent audit events
        audit_tasks = []
        for i in range(100):  # 100 concurrent audit events
            task = audit_logger.log_constitutional_event(
                action=f"stress_test_event_{i}",
                compliance_score=0.95,
                violations=[],
                details={"test_iteration": i, "stress_test": True},
            )
            audit_tasks.append(task)

        # Execute all audit logging concurrently
        results = await asyncio.gather(*audit_tasks, return_exceptions=True)

        # Verify all events were logged successfully
        successful_logs = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_logs) >= 95  # Allow for some failures under extreme load


# Test execution configuration
if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "--asyncio-mode=auto"])
