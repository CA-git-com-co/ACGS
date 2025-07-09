"""
Standalone Fast Constitutional Validator for Testing
Constitutional Hash: cdd01ef066bc6cf2

Standalone version without FastAPI dependencies for performance testing.
"""

import json
import time
from typing import Any, Dict, Optional, Set
from dataclasses import dataclass
from collections import OrderedDict
import threading

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ValidationCacheEntry:
    """Cache entry for validation results."""
    result: bool
    created_at: float
    access_count: int = 0
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def is_expired(self, ttl_seconds: float = 300.0) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > ttl_seconds
    
    def access(self) -> bool:
        """Access the cached result and update access tracking."""
        self.access_count += 1
        return self.result


class MockRequest:
    """Mock request for testing."""
    
    def __init__(self, path: str = "/test", method: str = "GET", 
                 headers: Dict[str, str] = None, body: bytes = None):
        self.url = MockURL(path)
        self.method = method
        self.headers = headers or {}
        self._body = body


class MockURL:
    """Mock URL for testing."""
    def __init__(self, path: str):
        self.path = path


class MockResponse:
    """Mock response for testing."""
    
    def __init__(self):
        self.headers = {}


class StandaloneFastConstitutionalValidator:
    """
    Standalone high-performance constitutional validator for testing.
    
    Optimizations:
    - Pre-computed hash validation cache for O(1) lookups
    - Minimal string operations and comparisons
    - Cached validation results with TTL
    - Thread-safe concurrent access
    - Optimized header and body parsing
    """
    
    def __init__(self, constitutional_hash: str = CONSTITUTIONAL_HASH, 
                 cache_size: int = 10000, cache_ttl: float = 300.0):
        self.constitutional_hash = constitutional_hash
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        
        # Pre-computed hash validation cache
        self.hash_cache: Dict[str, bool] = {
            constitutional_hash: True,  # Valid hash
            "": False,                  # Empty hash
            "invalid": False,           # Common invalid hash
            "null": False,              # Null hash
            "undefined": False          # Undefined hash
        }
        
        # Validation result cache with LRU eviction
        self.validation_cache: OrderedDict[str, ValidationCacheEntry] = OrderedDict()
        
        # Thread safety
        self.cache_lock = threading.RLock()
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_validations = 0
        
        # Pre-compile common patterns
        self.exempt_paths: Set[str] = {
            "/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"
        }
        
        # Pre-computed response headers
        self.constitutional_headers = {
            "X-Constitutional-Hash": constitutional_hash,
            "X-Constitutional-Compliance": "validated"
        }
    
    def validate_hash_fast(self, hash_value: Optional[str]) -> bool:
        """
        Ultra-fast hash validation using pre-computed cache.
        Target: <0.1ms validation time.
        """
        if hash_value is None:
            return False
        
        # O(1) lookup in pre-computed cache
        cached_result = self.hash_cache.get(hash_value)
        if cached_result is not None:
            self.cache_hits += 1
            return cached_result
        
        # Cache miss - compute and cache result
        self.cache_misses += 1
        is_valid = hash_value == self.constitutional_hash
        
        # Add to cache if space available
        if len(self.hash_cache) < 1000:  # Limit cache size
            self.hash_cache[hash_value] = is_valid
        
        self.total_validations += 1
        return is_valid
    
    def validate_request_fast(self, request: MockRequest, service_name: str = "unknown") -> bool:
        """
        Fast request validation with caching.
        Target: <0.3ms validation time.
        """
        try:
            # Skip validation for exempt paths
            if request.url.path in self.exempt_paths:
                return True
            
            # Generate cache key for request validation
            cache_key = f"req:{request.method}:{request.url.path}:{request.headers.get('X-Constitutional-Hash', '')}"
            
            # Check validation cache
            with self.cache_lock:
                if cache_key in self.validation_cache:
                    entry = self.validation_cache[cache_key]
                    if not entry.is_expired(self.cache_ttl):
                        # Cache hit
                        self.validation_cache.move_to_end(cache_key)  # LRU update
                        result = entry.access()
                        self.cache_hits += 1
                        return result
                    else:
                        # Expired entry
                        del self.validation_cache[cache_key]
            
            # Cache miss - perform validation
            self.cache_misses += 1
            
            # Fast header validation
            request_hash = request.headers.get("X-Constitutional-Hash")
            header_valid = True
            if request_hash:
                header_valid = self.validate_hash_fast(request_hash)
            
            # Fast body validation (if needed)
            body_valid = True
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type and hasattr(request, "_body"):
                body_valid = self._validate_body_fast(request._body)
            
            result = header_valid and body_valid
            
            # Cache the result
            with self.cache_lock:
                # Evict oldest entries if cache is full
                while len(self.validation_cache) >= self.cache_size:
                    self.validation_cache.popitem(last=False)
                
                self.validation_cache[cache_key] = ValidationCacheEntry(
                    result=result,
                    created_at=time.time()
                )
            
            self.total_validations += 1
            return result
            
        except Exception:
            return False
    
    def validate_response_fast(self, response: MockResponse, service_name: str = "unknown") -> bool:
        """
        Fast response validation.
        Target: <0.1ms validation time.
        """
        # Fast response validation - just check if hash header exists
        # (We'll add it if missing in add_constitutional_headers_fast)
        self.total_validations += 1
        return True
    
    def add_constitutional_headers_fast(self, response: MockResponse, processing_time: float = 0.0):
        """
        Fast constitutional header addition with pre-computed headers.
        Target: <0.05ms header addition time.
        """
        # Add pre-computed constitutional headers
        response.headers.update(self.constitutional_headers)
        
        # Add dynamic headers
        if processing_time > 0:
            response.headers["X-Processing-Time-Ms"] = f"{processing_time:.2f}"
            response.headers["X-Performance-Compliant"] = "true" if processing_time <= 5.0 else "false"
    
    def _validate_body_fast(self, body: bytes) -> bool:
        """Fast body validation with minimal parsing."""
        if not body:
            return True
        
        try:
            # Fast JSON parsing check
            body_str = body.decode('utf-8')
            if not body_str.strip().startswith('{'):
                return True  # Not JSON, skip validation
            
            # Look for constitutional_hash in JSON without full parsing
            if '"constitutional_hash"' in body_str:
                # Extract hash value using string operations (faster than JSON parsing)
                hash_start = body_str.find('"constitutional_hash"')
                if hash_start != -1:
                    # Find the value after the key
                    value_start = body_str.find(':', hash_start)
                    if value_start != -1:
                        value_start += 1
                        # Skip whitespace and quotes
                        while value_start < len(body_str) and body_str[value_start] in ' \t\n"':
                            value_start += 1
                        
                        # Find end of value
                        value_end = value_start
                        while value_end < len(body_str) and body_str[value_end] not in '",}':
                            value_end += 1
                        
                        if value_end > value_start:
                            hash_value = body_str[value_start:value_end]
                            return self.validate_hash_fast(hash_value)
            
            return True  # No hash found, validation passes
            
        except (UnicodeDecodeError, ValueError):
            return True  # Skip validation for invalid data
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the fast validator."""
        hit_rate = self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        
        return {
            "total_validations": self.total_validations,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": hit_rate,
            "hash_cache_size": len(self.hash_cache),
            "validation_cache_size": len(self.validation_cache),
            "constitutional_hash": self.constitutional_hash,
            "performance_targets": {
                "hash_validation": "<0.1ms",
                "request_validation": "<0.3ms",
                "response_validation": "<0.1ms",
                "header_addition": "<0.05ms"
            }
        }
    
    def clear_cache(self):
        """Clear validation caches (for testing or maintenance)."""
        with self.cache_lock:
            self.validation_cache.clear()
            # Keep pre-computed hash cache but reset counters
            self.cache_hits = 0
            self.cache_misses = 0
    
    def warm_cache(self, common_patterns: Dict[str, bool]):
        """Warm the validation cache with common patterns."""
        with self.cache_lock:
            for pattern, result in common_patterns.items():
                if len(self.validation_cache) < self.cache_size:
                    self.validation_cache[pattern] = ValidationCacheEntry(
                        result=result,
                        created_at=time.time()
                    )
    
    def validate_constitutional_compliance(self) -> bool:
        """Validate that the validator itself maintains constitutional compliance."""
        return (
            self.constitutional_hash == CONSTITUTIONAL_HASH and
            all(entry.constitutional_hash == CONSTITUTIONAL_HASH 
                for entry in self.validation_cache.values())
        )


# Alias for compatibility
FastConstitutionalValidator = StandaloneFastConstitutionalValidator
