"""
ACGS-1 Lightweight Enhancement Framework

This framework provides standardized enhancement patterns for all ACGS-1 services,
ensuring consistent performance, constitutional compliance, and monitoring across
the entire system.

Key Features:
- Standardized FastAPI service creation
- Constitutional compliance validation (cdd01ef066bc6cf2)
- Performance optimization (<500ms response times)
- Prometheus metrics integration
- Redis caching integration
- Circuit breaker patterns
- Service registry integration

Usage:
    from services.shared.enhancement_framework import ACGSServiceEnhancer

    enhancer = ACGSServiceEnhancer("pgc_service", port=8005)
    app = await enhancer.create_enhanced_service()
"""

from .cache_enhancer import CacheEnhancer
from .constitutional_validator import ConstitutionalComplianceValidator
from .monitoring_integrator import MonitoringIntegrator
from .performance_optimizer import PerformanceEnhancer
from .service_enhancer import ACGSServiceEnhancer
from .service_template import ACGSServiceTemplate

__version__ = "1.0.0"
__author__ = "ACGS-1 Development Team"

__all__ = [
    "ACGSServiceEnhancer",
    "ACGSServiceTemplate",
    "CacheEnhancer",
    "ConstitutionalComplianceValidator",
    "MonitoringIntegrator",
    "PerformanceEnhancer",
]
