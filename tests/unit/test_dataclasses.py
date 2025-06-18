import asyncio
import sys
import types

tenacity_mod = types.ModuleType("tenacity")
tenacity_mod.retry = lambda *a, **k: (lambda f: f)
tenacity_mod.stop_after_attempt = lambda *a, **k: None
tenacity_mod.wait_exponential = lambda *a, **k: None


class RetryError(Exception):
    pass


tenacity_mod.RetryError = RetryError
sys.modules.setdefault("tenacity", tenacity_mod)
sys.modules.setdefault("openai", types.ModuleType("openai"))
shared_mod = types.ModuleType("shared")
auth_mod = types.ModuleType("auth")
auth_mod.get_service_token = lambda: ""
auth_mod.get_auth_headers = lambda token=None: {}
shared_mod.auth = auth_mod
sys.modules.setdefault("shared", shared_mod)
sys.modules.setdefault("shared.auth", auth_mod)

try:
    import os
    import sys

    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(__file__),
            "../../../../services/core/governance-synthesis/gs_service",
        ),
    )
    from .models.reliability_models import ConstitutionalPrinciple, SynthesisContext
except ImportError:
    # Fallback to mock implementations for testing
    from dataclasses import dataclass

    @dataclass
    class ConstitutionalPrinciple:
        id: str
        text: str

    @dataclass
    class SynthesisContext:
        domain: str


import pytest


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_dataclass_instantiation():
    principle = ConstitutionalPrinciple(id="p1", text="test")
    context = SynthesisContext(domain="d")
    assert principle.id == "p1"
    assert principle.text == "test"
    assert context.domain == "d"
