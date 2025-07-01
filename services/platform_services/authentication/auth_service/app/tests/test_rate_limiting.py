import sys
from types import ModuleType, SimpleNamespace

import pytest
from starlette.requests import Request

# Inject dummy modules to satisfy imports without loading full SQLAlchemy models
dummy_agent_mod = ModuleType("agent")
dummy_agent_mod.Agent = object
dummy_models_pkg = ModuleType("models")
dummy_models_pkg.__path__ = []  # mark as package
sys.modules["services.platform_services.authentication.auth_service.app.models"] = dummy_models_pkg
sys.modules[
    "services.platform_services.authentication.auth_service.app.models.agent"
] = dummy_agent_mod

dummy_service_mod = ModuleType("agent_service")
dummy_service_mod.AgentService = object
sys.modules[
    "services.platform_services.authentication.auth_service.app.services.agent_service"
] = dummy_service_mod

import runpy

mod = runpy.run_module(
    "services.platform_services.authentication.auth_service.app.middleware.agent_auth",
    run_name="agent_auth",
)
AgentAuthenticationMiddleware = mod["AgentAuthenticationMiddleware"]

class FakeRedis:
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.time = 0

    def _now(self):
        return self.time

    def advance(self, seconds: int):
        self.time += seconds

    def _cleanup(self):
        to_delete = [k for k, exp in list(self.expiry.items()) if exp <= self._now()]
        for k in to_delete:
            self.data.pop(k, None)
            self.expiry.pop(k, None)

    async def incr(self, key: str):
        self._cleanup()
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    async def expire(self, key: str, ttl: int):
        self.expiry[key] = self._now() + ttl

    async def close(self):
        pass

@pytest.mark.asyncio
async def test_agent_rate_limit_exceeded():
    redis = FakeRedis()
    mw = AgentAuthenticationMiddleware()
    mw.redis_client = redis
    agent = SimpleNamespace(agent_id="agent1", max_requests_per_minute=2)
    req = Request({"type": "http"})

    assert await mw._check_rate_limits(agent, req) is True
    assert await mw._check_rate_limits(agent, req) is True
    assert await mw._check_rate_limits(agent, req) is False

@pytest.mark.asyncio
async def test_rate_limit_reset_after_window():
    redis = FakeRedis()
    mw = AgentAuthenticationMiddleware()
    mw.redis_client = redis
    agent = SimpleNamespace(agent_id="agent2", max_requests_per_minute=1)
    req = Request({"type": "http"})

    assert await mw._check_rate_limits(agent, req) is True
    assert await mw._check_rate_limits(agent, req) is False
    redis.advance(61)
    assert await mw._check_rate_limits(agent, req) is True
