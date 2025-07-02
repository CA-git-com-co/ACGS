"""Mock services for multi-agent testing."""

import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
import json


class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self._data = {}
        self._pub_sub_data = {}
        
    async def get(self, key: str) -> Optional[bytes]:
        return self._data.get(key)
        
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._data[key] = value if isinstance(value, bytes) else str(value).encode()
        return True
        
    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                deleted += 1
        return deleted
        
    async def exists(self, key: str) -> bool:
        return key in self._data
        
    async def keys(self, pattern: str = '*') -> List[str]:
        return list(self._data.keys())
    
    async def hset(self, key: str, field: Optional[str] = None, value: Optional[str] = None, mapping: Optional[Dict[str, Any]] = None, **kwargs) -> int:
        """Mock Redis hset operation"""
        if key not in self._data:
            self._data[key] = {}

        count = 0

        # Handle field/value pair
        if field is not None and value is not None:
            if not isinstance(self._data[key], dict):
                self._data[key] = {}
            self._data[key][field] = value
            count += 1

        # Handle mapping
        if mapping:
            if not isinstance(self._data[key], dict):
                self._data[key] = {}
            self._data[key].update(mapping)
            count += len(mapping)

        # Handle kwargs
        if kwargs:
            if not isinstance(self._data[key], dict):
                self._data[key] = {}
            self._data[key].update(kwargs)
            count += len(kwargs)

        return count
                
        return 1
        
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Mock Redis hget operation"""
        if key in self._data and isinstance(self._data[key], dict):
            return self._data[key].get(field)
        return None
        
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Mock Redis hgetall operation"""
        if key in self._data and isinstance(self._data[key], dict):
            return self._data[key]
        return {}
        
    async def hdel(self, key: str, *fields: str) -> int:
        """Mock Redis hdel operation"""
        if key in self._data and isinstance(self._data[key], dict):
            deleted = 0
            for field in fields:
                if field in self._data[key]:
                    del self._data[key][field]
                    deleted += 1
            return deleted
        return 0
        
    async def lpush(self, key: str, *values: Any) -> int:
        """Mock Redis lpush operation"""
        if key not in self._data:
            self._data[key] = []
        if not isinstance(self._data[key], list):
            self._data[key] = []
        
        for value in reversed(values):
            self._data[key].insert(0, value)
        return len(self._data[key])
        
    async def rpop(self, key: str) -> Optional[str]:
        """Mock Redis rpop operation"""
        if key in self._data and isinstance(self._data[key], list) and self._data[key]:
            return self._data[key].pop()
        return None
        
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Mock Redis lrange operation"""
        if key in self._data and isinstance(self._data[key], list):
            return self._data[key][start:end+1]
        return []
        
    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Mock Redis zadd operation"""
        if key not in self._data:
            self._data[key] = {}
        if not isinstance(self._data[key], dict):
            self._data[key] = {}
        
        added = 0
        for member, score in mapping.items():
            if member not in self._data[key]:
                added += 1
            self._data[key][member] = score
        return added
        
    async def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> List:
        """Mock Redis zrange operation"""
        if key not in self._data or not isinstance(self._data[key], dict):
            return []
        
        # Sort by score
        sorted_items = sorted(self._data[key].items(), key=lambda x: x[1])
        result_items = sorted_items[start:end+1 if end >= 0 else None]
        
        if withscores:
            return [(item[0], item[1]) for item in result_items]
        else:
            return [item[0] for item in result_items]
            
    async def zrem(self, key: str, *members: str) -> int:
        """Mock Redis zrem operation"""
        if key not in self._data or not isinstance(self._data[key], dict):
            return 0
        
        removed = 0
        for member in members:
            if member in self._data[key]:
                del self._data[key][member]
                removed += 1
        return removed
        
    async def expire(self, key: str, seconds: int) -> bool:
        """Mock Redis expire operation (simplified)"""
        # For testing purposes, we'll just pretend it worked
        return True
        
    async def sadd(self, key: str, *values: str) -> int:
        """Mock Redis sadd operation"""
        if key not in self._data:
            self._data[key] = set()
        if not isinstance(self._data[key], set):
            self._data[key] = set()
        
        added = 0
        for value in values:
            if value not in self._data[key]:
                self._data[key].add(value)
                added += 1
        return added
        
    async def smembers(self, key: str) -> set:
        """Mock Redis smembers operation"""
        if key in self._data and isinstance(self._data[key], set):
            return self._data[key].copy()
        return set()
        
    async def srem(self, key: str, *values: str) -> int:
        """Mock Redis srem operation"""
        if key not in self._data or not isinstance(self._data[key], set):
            return 0
        
        removed = 0
        for value in values:
            if value in self._data[key]:
                self._data[key].remove(value)
                removed += 1
        return removed
        
    async def publish(self, channel: str, message: str) -> int:
        if channel not in self._pub_sub_data:
            self._pub_sub_data[channel] = []
        self._pub_sub_data[channel].append(message)
        return 1
        
    def pubsub(self):
        return MockPubSub(self._pub_sub_data)

    def pipeline(self, transaction=True):
        """Mock Redis pipeline operation"""
        return MockRedisPipeline(self)

    async def zcard(self, key: str) -> int:
        """Mock Redis zcard operation"""
        if key in self._data and isinstance(self._data[key], list):
            return len(self._data[key])
        return 0

    async def close(self):
        """Mock Redis close operation"""
        pass


class MockRedisPipeline:
    """Mock Redis pipeline for testing."""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.commands = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def watch(self, *keys):
        """Mock Redis watch operation"""
        pass

    async def multi(self):
        """Mock Redis multi operation"""
        pass

    async def get(self, key: str):
        """Mock Redis get in pipeline"""
        return await self.redis_client.get(key)

    async def hget(self, key: str, field: str):
        """Mock Redis hget in pipeline"""
        return await self.redis_client.hget(key, field)

    async def hset(self, key: str, field: str = None, value: str = None, mapping=None, **kwargs):
        """Mock Redis hset in pipeline"""
        return await self.redis_client.hset(key, field=field, value=value, mapping=mapping, **kwargs)

    async def zrem(self, key: str, *members):
        """Mock Redis zrem in pipeline"""
        return await self.redis_client.zrem(key, *members)

    async def zadd(self, key: str, mapping: dict, **kwargs):
        """Mock Redis zadd in pipeline"""
        return await self.redis_client.zadd(key, mapping, **kwargs)

    async def sadd(self, key: str, *members):
        """Mock Redis sadd in pipeline"""
        return await self.redis_client.sadd(key, *members)

    async def reset(self):
        """Mock Redis reset operation"""
        pass

    def multi(self):
        """Mock Redis multi operation (non-async)"""
        pass

    async def execute(self):
        """Mock Redis execute operation"""
        return [True] * len(self.commands)


class MockPubSub:
    """Mock Redis PubSub client."""

    def __init__(self, data: Dict[str, List[str]]):
        self._data = data
        self._subscribed_channels = set()
        
    async def subscribe(self, *channels: str):
        self._subscribed_channels.update(channels)
        
    async def get_message(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        for channel in self._subscribed_channels:
            if channel in self._data and self._data[channel]:
                message = self._data[channel].pop(0)
                return {
                    'type': 'message',
                    'channel': channel.encode(),
                    'data': message.encode()
                }
        return None


class MockWINACore:
    """Mock WINA core service for testing."""
    
    def __init__(self):
        self.optimization_history = []
        self.performance_metrics = {
            'response_time': 0.1,
            'throughput': 1000,
            'accuracy': 0.95,
            'memory_usage': 512
        }
        
    async def optimize_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Mock performance optimization."""
        self.optimization_history.append({
            'timestamp': datetime.utcnow(),
            'input_metrics': metrics,
            'optimization_applied': True
        })
        
        # Simulate improvement
        optimized_metrics = metrics.copy()
        optimized_metrics['response_time'] = max(0.05, metrics.get('response_time', 0.1) * 0.9)
        optimized_metrics['throughput'] = metrics.get('throughput', 1000) * 1.1
        
        return optimized_metrics
        
    async def get_performance_recommendations(self, current_metrics: Dict[str, Any]) -> List[str]:
        """Mock performance recommendations."""
        recommendations = []
        
        if current_metrics.get('response_time', 0) > 0.2:
            recommendations.append('Optimize query performance')
            
        if current_metrics.get('memory_usage', 0) > 1024:
            recommendations.append('Implement caching strategy')
            
        if current_metrics.get('throughput', 0) < 500:
            recommendations.append('Scale horizontally')
            
        return recommendations


class TestDataGenerator:
    """Generate test data for multi-agent scenarios."""

    @staticmethod
    def create_governance_request() -> Dict[str, Any]:
        """Create a sample governance request for testing"""
        return {
            "request_id": str(uuid4()),
            "model_info": {
                "model_type": "language_model",
                "parameters": "7B",
                "training_data": "web_crawl_filtered"
            },
            "deployment_context": {
                "environment": "production",
                "user_base": "general_public",
                "expected_volume": "high"
            },
            "constitutional_requirements": {
                "safety": True,
                "transparency": True,
                "consent": True,
                "data_privacy": True
            },
            "stakeholders": ["users", "developers", "society"],
            "risk_level": "medium"
        }

    @staticmethod
    def generate_knowledge_item(agent_id: str = 'test-agent', space: str = 'governance') -> Dict[str, Any]:
        """Generate a test knowledge item."""
        return {
            'id': f'knowledge-{datetime.utcnow().timestamp()}',
            'agent_id': agent_id,
            'space': space,
            'content': {'test': 'data', 'timestamp': datetime.utcnow().isoformat()},
            'tags': ['test', 'generated'],
            'created_at': datetime.utcnow().isoformat()
        }
        
    @staticmethod
    def generate_task(agent_id: str = 'test-agent', priority: int = 5) -> Dict[str, Any]:
        """Generate a test task."""
        return {
            'id': f'task-{datetime.utcnow().timestamp()}',
            'type': 'test_task',
            'agent_id': agent_id,
            'priority': priority,
            'data': {'test': 'task_data'},
            'created_at': datetime.utcnow().isoformat()
        }
        
    @staticmethod
    def generate_performance_metrics(agent_id: str = 'test-agent') -> Dict[str, Any]:
        """Generate test performance metrics."""
        return {
            'agent_id': agent_id,
            'response_time': 0.15,
            'throughput': 750,
            'memory_usage': 256,
            'cpu_usage': 45.5,
            'timestamp': datetime.utcnow().isoformat()
        }
