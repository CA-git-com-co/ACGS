import pytest
from types import SimpleNamespace

pytestmark = pytest.mark.asyncio

class DummyRedisCore:
    def __init__(self):
        self.counts = {}
        self.expire_map = {}

    async def incrby(self, key, amount=1):
        self.counts[key] = self.counts.get(key, 0) + amount
        return self.counts[key]

    async def expire(self, key, ttl):
        self.expire_map[key] = ttl

    async def ttl(self, key):
        return self.expire_map.get(key, -1)

class DummyRedisClient:
    def __init__(self):
        self.redis_client = DummyRedisCore()

    def generate_key(self, *parts):
        return ':'.join(parts)

    async def increment(self, key, amount=1):
        return await self.redis_client.incrby(key, amount)

class SimpleRateLimiter:
    def __init__(self, client):
        self.redis_client = client

    async def _check_rate_limits(self, agent, request):
        max_requests = agent.max_requests_per_minute or 100
        window_seconds = 60
        redis_client = self.redis_client
        key = redis_client.generate_key("agent_rate", agent.agent_id)
        current_count = await redis_client.increment(key)
        if current_count == 1:
            await redis_client.redis_client.expire(key, window_seconds)
        if current_count > max_requests:
            ttl = await redis_client.redis_client.ttl(key)
            request.state.rate_limit_reset = ttl
            return False
        return True

class Agent:
    def __init__(self, agent_id, max_requests_per_minute=2):
        self.agent_id = agent_id
        self.max_requests_per_minute = max_requests_per_minute

async def test_rate_limit_enforced():
    client = DummyRedisClient()
    limiter = SimpleRateLimiter(client)
    agent = Agent("agent1", max_requests_per_minute=2)
    request = SimpleNamespace(state=SimpleNamespace())

    assert await limiter._check_rate_limits(agent, request) is True
    assert await limiter._check_rate_limits(agent, request) is True
    assert await limiter._check_rate_limits(agent, request) is False
