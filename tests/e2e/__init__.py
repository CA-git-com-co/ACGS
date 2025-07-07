"""
ACGS End-to-End Test Framework

This module provides comprehensive end-to-end testing capabilities for the
Autonomous Coding Governance System (ACGS) project, validating production
readiness and maintaining established performance targets.

Key Features:
- Constitutional AI policy validation (hash: cdd01ef066bc6cf2)
- HITL decision processing with sub-5ms P99 latency
- Multi-agent coordination with blackboard architecture
- Policy governance with WINA optimization (O(1) lookups)
- Cache performance validation (>85% hit rate target)
- Infrastructure component validation
- Security compliance testing
- Performance benchmarking and regression detection

Testing Modes:
- Online: Test against live infrastructure (PostgreSQL/Redis/Auth services)
- Offline: Use mocked services and in-memory databases for CI/CD
- Hybrid: Mix of live and mocked components for specific test scenarios

Performance Targets:
- P99 latency: <5ms
- Cache hit rate: >85%
- Throughput: >100 RPS
- Test coverage: >80%
- Resource utilization: <80%
"""

__version__ = "1.0.0"
__author__ = "ACGS Team"
__constitutional_hash__ = "cdd01ef066bc6cf2"

from .framework.config import E2ETestConfig

# Export main testing components
from .framework.core import E2ETestFramework
from .framework.reporter import E2ETestReporter
from .framework.runner import E2ETestRunner

__all__ = [
    "E2ETestFramework",
    "E2ETestConfig",
    "E2ETestRunner",
    "E2ETestReporter",
]
