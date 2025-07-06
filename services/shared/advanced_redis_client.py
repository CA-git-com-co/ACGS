"""
Advanced Redis client for ACGS services.

This module provides an alias to the ACGSRedisClient for backward compatibility.
"""

# Re-export the main Redis client as AdvancedRedisClient
from .redis_client import ACGSRedisClient

# Create alias for backward compatibility
AdvancedRedisClient = ACGSRedisClient

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
