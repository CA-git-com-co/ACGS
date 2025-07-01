import types
import sys
import re
import time

import pytest

# Provide minimal schema stubs to satisfy imports
schema_stub = types.ModuleType("services.core.constitutional_ai.ac_service.app.schemas")

class ConstitutionalComplianceRequest:
    def __init__(self, policy=None, validation_mode="comprehensive", include_reasoning=False, principles=None):
        self.policy = policy or {}
        self.validation_mode = validation_mode
        self.include_reasoning = include_reasoning
        self.principles = principles

schema_stub.ConstitutionalComplianceRequest = ConstitutionalComplianceRequest
sys.modules["services.core.constitutional_ai.ac_service.app.schemas"] = schema_stub

# Prevent autouse fixtures from skipping tests due to missing async dependencies

from services.core.constitutional_ai.ac_service.app.services.constitutional_validation_service import (
    ConstitutionalValidationService,
)


@pytest.fixture()
def service():
    return ConstitutionalValidationService()


def test_generate_validation_id(service):
    vid = service._generate_validation_id({"policy": "demo"})
    assert vid.startswith("VAL-")
    parts = vid.split("-")
    assert len(parts) == 3
    assert re.fullmatch(r"\d+", parts[1])
    assert len(parts[2]) == 8


def test_get_rules_to_check_basic(service):
    assert service._get_rules_to_check(None, "basic") == ["CONST-001", "CONST-003"]


def test_get_rules_to_check_principles(service):
    assert service._get_rules_to_check([{"rule_id": "CONST-004"}], "comprehensive") == ["CONST-004"]


def test_calculate_average_severity_empty(service):
    assert service._calculate_average_severity([]) == "unknown"


def test_calculate_average_severity_mixed(service):
    results = [{"severity": "high"}, {"severity": "critical"}]
    assert service._calculate_average_severity(results) == "high"


def test_generate_next_steps_noncompliant(service):
    steps = service._generate_next_steps(False)
    assert steps and steps[0].startswith("Review failed")

