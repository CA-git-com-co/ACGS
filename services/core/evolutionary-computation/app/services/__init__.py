
"""
Service modules for ACGS Evolutionary Computation Service.

This package contains service layer components for evolutionary computation,
including evolution services, fitness evaluation, HITL workflows, and
client integrations with constitutional compliance.
"""

from .ac_client import ac_service_client
from .data_integration_pipeline import DataIntegrationPipeline
from .evolution_service import EvolutionService
from .fitness_service import FitnessService
from .gs_client import gs_service_client
from .hitl_service import HITLService
from .pgc_client import pgc_service_client

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__all__ = [
    "ac_service_client",
    "DataIntegrationPipeline",
    "EvolutionService",
    "FitnessService",
    "gs_service_client",
    "HITLService",
    "pgc_service_client",
]
