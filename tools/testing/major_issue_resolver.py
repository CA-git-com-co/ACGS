#!/usr/bin/env python3
"""
Major Issue Resolution Framework for ACGS-2
Resolves major issues affecting system functionality, maintainability concerns,
and performance optimizations that don't meet critical thresholds.
"""

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@dataclass
class MajorResolutionResult:
    issue_id: str
    status: str  # RESOLVED, PARTIAL, FAILED, SKIPPED
    resolution_time: float
    actions_taken: list[str]
    verification_passed: bool
    remaining_work: list[str]
    details: dict[str, Any]


class MajorIssueResolver:
    def __init__(self):
        self.project_root = project_root
        self.resolution_results = []

    def load_major_issues(self) -> list[dict[str, Any]]:
        """Load major issues from the analysis results."""
        issue_file = self.project_root / "issue_analysis_results.json"

        if not issue_file.exists():
            print("❌ Issue analysis results not found. Run issue_analyzer.py first.")
            return []

        with open(issue_file) as f:
            data = json.load(f)

        # Filter for major issues
        major_issues = [
            issue
            for issue in data.get("prioritized_issues", [])
            if issue.get("severity") == "MAJOR"
        ]

        print(f"📋 Found {len(major_issues)} major issues to resolve")
        return major_issues

    def resolve_cache_performance_issue(
        self, issue: dict[str, Any]
    ) -> MajorResolutionResult:
        """Resolve cache performance optimization issues."""
        start_time = time.time()
        actions_taken = []

        try:
            # Create optimized cache implementation
            cache_optimization_code = '''"""
Optimized Cache Implementation for ACGS-2
Improves cache hit rates and performance characteristics.
"""

import time
import threading
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
import hashlib

class OptimizedCache:
    """High-performance cache with improved hit rates and eviction policies."""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()

        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }

    def _generate_key(self, key: Any) -> str:
        """Generate consistent cache key from any input."""
        if isinstance(key, str):
            return key
        elif isinstance(key, (int, float, bool)):
            return str(key)
        else:
            # Hash complex objects
            key_str = str(key)
            return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: Any) -> Optional[Any]:
        """Get value from cache with TTL check."""
        with self.lock:
            cache_key = self._generate_key(key)
            current_time = time.time()

            if cache_key in self.cache:
                value, timestamp = self.cache[cache_key]

                # Check TTL
                if current_time - timestamp <= self.ttl_seconds:
                    # Move to end (LRU)
                    self.cache.move_to_end(cache_key)
                    self.hit_count += 1
                    self.stats["hits"] += 1
                    return value
                else:
                    # Expired, remove
                    del self.cache[cache_key]
                    self.stats["size"] = len(self.cache)

            self.miss_count += 1
            self.stats["misses"] += 1
            return None

    def set(self, key: Any, value: Any) -> None:
        """Set value in cache with eviction if necessary."""
        with self.lock:
            cache_key = self._generate_key(key)
            current_time = time.time()

            # Remove if already exists
            if cache_key in self.cache:
                del self.cache[cache_key]

            # Evict oldest if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key, _ = self.cache.popitem(last=False)
                self.stats["evictions"] += 1

            # Add new entry
            self.cache[cache_key] = (value, current_time)
            self.stats["size"] = len(self.cache)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.stats["size"] = 0

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.hit_count + self.miss_count
        return (self.hit_count / total_requests * 100) if total_requests > 0 else 0

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            return {
                **self.stats,
                "hit_rate_percent": (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0,
                "total_requests": total_requests,
                "capacity_utilization": (self.stats["size"] / self.max_size * 100) if self.max_size > 0 else 0
            }

class RequestScopedCache:
    """Request-scoped cache for temporary data within request lifecycle."""

    def __init__(self):
        self.local_cache = {}
        self.request_id = None

    def start_request(self, request_id: str) -> None:
        """Start a new request scope."""
        self.request_id = request_id
        self.local_cache = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from request-scoped cache."""
        return self.local_cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in request-scoped cache."""
        self.local_cache[key] = value

    def end_request(self) -> Dict[str, Any]:
        """End request scope and return statistics."""
        stats = {
            "request_id": self.request_id,
            "cache_size": len(self.local_cache),
            "keys": list(self.local_cache.keys())
        }
        self.local_cache.clear()
        self.request_id = None
        return stats

# Global cache instances
global_cache = OptimizedCache(max_size=50000, ttl_seconds=1800)  # 30 minutes TTL
request_cache = RequestScopedCache()

def get_cached(key: Any, compute_func=None, use_request_cache=True):
    """
    Get value from cache with automatic computation and caching.

    Args:
        key: Cache key
        compute_func: Function to compute value if not in cache
        use_request_cache: Whether to use request-scoped cache

    Returns:
        Cached or computed value
    """
    # Try request cache first
    if use_request_cache:
        request_value = request_cache.get(str(key))
        if request_value is not None:
            return request_value

    # Try global cache
    global_value = global_cache.get(key)
    if global_value is not None:
        # Store in request cache for faster access
        if use_request_cache:
            request_cache.set(str(key), global_value)
        return global_value

    # Compute value if function provided
    if compute_func:
        computed_value = compute_func()
        global_cache.set(key, computed_value)
        if use_request_cache:
            request_cache.set(str(key), computed_value)
        return computed_value

    return None

def cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    return {
        "global_cache": global_cache.get_stats(),
        "request_cache_size": len(request_cache.local_cache),
        "request_id": request_cache.request_id
    }
'''

            # Save the optimized cache module
            cache_file = (
                self.project_root / "services" / "shared" / "optimized_cache.py"
            )
            cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(cache_file, "w") as f:
                f.write(cache_optimization_code)

            actions_taken.append("Created optimized cache implementation")

            # Create cache performance test
            cache_test_code = '''"""
Performance tests for optimized cache implementation.
"""

import time
import pytest
from services.shared.optimized_cache import OptimizedCache, get_cached, cache_stats

def test_cache_hit_rate_improvement():
    """Test that cache hit rate meets target."""
    cache = OptimizedCache(max_size=1000, ttl_seconds=60)

    # Populate cache
    for i in range(100):
        cache.set(f"key_{i}", f"value_{i}")

    # Access cached items multiple times
    for _ in range(5):
        for i in range(100):
            value = cache.get(f"key_{i}")
            assert value == f"value_{i}"

    # Check hit rate
    hit_rate = cache.get_hit_rate()
    assert hit_rate >= 80.0, f"Cache hit rate {hit_rate}% below 80% target"

def test_cache_performance_under_load():
    """Test cache performance under high load."""
    cache = OptimizedCache(max_size=10000, ttl_seconds=300)

    start_time = time.time()

    # Perform many cache operations
    for i in range(10000):
        cache.set(f"load_key_{i}", f"load_value_{i}")

    for i in range(10000):
        value = cache.get(f"load_key_{i}")
        assert value == f"load_value_{i}"

    end_time = time.time()
    total_time = end_time - start_time

    # Should complete within reasonable time
    assert total_time < 1.0, f"Cache operations took {total_time}s, expected < 1.0s"

def test_cache_eviction_policy():
    """Test LRU eviction policy."""
    cache = OptimizedCache(max_size=5, ttl_seconds=60)

    # Fill cache to capacity
    for i in range(5):
        cache.set(f"key_{i}", f"value_{i}")

    # Access some items to make them recently used
    cache.get("key_1")
    cache.get("key_3")

    # Add new item, should evict least recently used
    cache.set("key_new", "value_new")

    # Check that LRU items were evicted
    assert cache.get("key_0") is None  # Should be evicted
    assert cache.get("key_1") == "value_1"  # Should still exist
    assert cache.get("key_3") == "value_3"  # Should still exist
    assert cache.get("key_new") == "value_new"  # Should exist

def test_cache_ttl_expiration():
    """Test TTL-based expiration."""
    cache = OptimizedCache(max_size=100, ttl_seconds=0.1)  # 100ms TTL

    cache.set("ttl_key", "ttl_value")

    # Should be available immediately
    assert cache.get("ttl_key") == "ttl_value"

    # Wait for expiration
    time.sleep(0.15)

    # Should be expired
    assert cache.get("ttl_key") is None

def test_get_cached_function():
    """Test the get_cached utility function."""
    call_count = 0

    def expensive_computation():
        nonlocal call_count
        call_count += 1
        return f"computed_value_{call_count}"

    # First call should compute
    result1 = get_cached("test_key", expensive_computation)
    assert result1 == "computed_value_1"
    assert call_count == 1

    # Second call should use cache
    result2 = get_cached("test_key", expensive_computation)
    assert result2 == "computed_value_1"
    assert call_count == 1  # Should not increment
'''

            test_file = self.project_root / "tests" / "unit" / "test_optimized_cache.py"
            test_file.parent.mkdir(parents=True, exist_ok=True)

            with open(test_file, "w") as f:
                f.write(cache_test_code)

            actions_taken.append("Created cache performance tests")

            # Verify the implementation
            verification_passed = self._verify_cache_optimization()
            actions_taken.append("Verified cache optimization implementation")

            remaining_work = [
                "Integrate optimized cache into existing services",
                "Update cache configuration based on production metrics",
                "Implement cache warming strategies",
                "Add cache monitoring and alerting",
            ]

            return MajorResolutionResult(
                issue["id"],
                "RESOLVED" if verification_passed else "PARTIAL",
                time.time() - start_time,
                actions_taken,
                verification_passed,
                remaining_work,
                {
                    "cache_module_created": str(cache_file),
                    "test_file_created": str(test_file),
                    "optimization_features": [
                        "LRU_eviction",
                        "TTL_expiration",
                        "thread_safety",
                        "request_scoping",
                    ],
                },
            )

        except Exception as e:
            return MajorResolutionResult(
                issue["id"],
                "FAILED",
                time.time() - start_time,
                actions_taken,
                False,
                [],
                {"error": str(e)},
            )

    def _verify_cache_optimization(self) -> bool:
        """Verify that the cache optimization works correctly."""
        try:
            # Import the new cache module
            sys.path.insert(0, str(self.project_root / "services" / "shared"))
            from optimized_cache import OptimizedCache, get_cached

            # Test basic functionality
            cache = OptimizedCache(max_size=100, ttl_seconds=60)

            # Test set/get
            cache.set("test_key", "test_value")
            if cache.get("test_key") != "test_value":
                return False

            # Test hit rate calculation
            for i in range(10):
                cache.set(f"key_{i}", f"value_{i}")

            for i in range(10):
                cache.get(f"key_{i}")

            hit_rate = cache.get_hit_rate()
            if hit_rate < 50:  # Should have reasonable hit rate
                return False

            # Test get_cached function
            call_count = 0

            def test_func():
                nonlocal call_count
                call_count += 1
                return "computed"

            result1 = get_cached("func_key", test_func)
            result2 = get_cached("func_key", test_func)

            if result1 != result2 or call_count != 1:
                return False

            return True

        except Exception:
            return False

    def resolve_business_rule_edge_cases(
        self, issue: dict[str, Any]
    ) -> MajorResolutionResult:
        """Resolve business rule edge case handling issues."""
        start_time = time.time()
        actions_taken = []

        try:
            # Create enhanced business rule validation
            enhanced_rules_code = r'''"""
Enhanced Business Rule Validation for ACGS-2
Improves edge case handling and validation robustness.
"""

from typing import Any, Dict, List, Optional, Union
import re
import json
from datetime import datetime, timezone

class EnhancedBusinessRuleValidator:
    """Enhanced validator with comprehensive edge case handling."""

    def __init__(self):
        self.validation_errors = []
        self.warnings = []

    def validate_governance_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate governance proposal with enhanced edge case handling."""
        self.validation_errors.clear()
        self.warnings.clear()

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_proposal": proposal.copy()
        }

        # Enhanced title validation
        title = proposal.get("title", "")
        if not title or not isinstance(title, str):
            self.validation_errors.append("Title is required and must be a string")
        elif len(title.strip()) == 0:
            self.validation_errors.append("Title cannot be empty or whitespace only")
        elif len(title) > 200:
            self.validation_errors.append("Title cannot exceed 200 characters")
        elif len(title) < 5:
            self.warnings.append("Title is very short, consider adding more detail")

        # Enhanced description validation
        description = proposal.get("description", "")
        if not description or not isinstance(description, str):
            self.validation_errors.append("Description is required and must be a string")
        elif len(description.strip()) < 10:
            self.validation_errors.append("Description must be at least 10 characters")
        elif len(description) > 5000:
            self.validation_errors.append("Description cannot exceed 5000 characters")

        # Status validation with edge cases
        status = proposal.get("status", "")
        valid_statuses = ["draft", "submitted", "under_review", "approved", "rejected", "withdrawn"]
        if status not in valid_statuses:
            self.validation_errors.append(f"Status must be one of: {', '.join(valid_statuses)}")

        # Priority validation
        priority = proposal.get("priority", "")
        valid_priorities = ["low", "medium", "high", "critical"]
        if priority not in valid_priorities:
            self.validation_errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")

        # Date validation
        submitted_at = proposal.get("submitted_at")
        if submitted_at:
            try:
                if isinstance(submitted_at, str):
                    datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                elif not isinstance(submitted_at, datetime):
                    self.validation_errors.append("submitted_at must be a valid datetime or ISO string")
            except ValueError:
                self.validation_errors.append("submitted_at must be a valid ISO datetime string")

        # Approval validation edge cases
        if status == "approved":
            if not proposal.get("approved_by"):
                self.validation_errors.append("Approved proposals must have approved_by field")
            if not proposal.get("approved_at"):
                self.validation_errors.append("Approved proposals must have approved_at timestamp")

        # Sanitize proposal
        if "title" in result["sanitized_proposal"]:
            result["sanitized_proposal"]["title"] = title.strip()
        if "description" in result["sanitized_proposal"]:
            result["sanitized_proposal"]["description"] = description.strip()

        result["errors"] = self.validation_errors.copy()
        result["warnings"] = self.warnings.copy()
        result["is_valid"] = len(self.validation_errors) == 0

        return result

    def validate_policy_document(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate policy document with comprehensive checks."""
        self.validation_errors.clear()
        self.warnings.clear()

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_policy": policy.copy()
        }

        # Policy ID validation
        policy_id = policy.get("id")
        if not policy_id:
            self.validation_errors.append("Policy ID is required")
        elif not isinstance(policy_id, str):
            self.validation_errors.append("Policy ID must be a string")
        elif not re.match(r'^[A-Z]{3}-\d{4}$', policy_id):
            self.warnings.append("Policy ID should follow format: ABC-1234")

        # Version validation
        version = policy.get("version", "")
        if not version:
            self.validation_errors.append("Policy version is required")
        elif not re.match(r'^\d+\.\d+\.\d+$', str(version)):
            self.validation_errors.append("Version must follow semantic versioning (x.y.z)")

        # Content validation
        content = policy.get("content")
        if not content:
            self.validation_errors.append("Policy content is required")
        elif isinstance(content, str) and len(content.strip()) == 0:
            self.validation_errors.append("Policy content cannot be empty")
        elif isinstance(content, dict) and not content:
            self.validation_errors.append("Policy content cannot be empty object")

        # Effective date validation
        effective_date = policy.get("effective_date")
        if effective_date:
            try:
                if isinstance(effective_date, str):
                    parsed_date = datetime.fromisoformat(effective_date.replace('Z', '+00:00'))
                    if parsed_date < datetime.now(timezone.utc):
                        self.warnings.append("Effective date is in the past")
            except ValueError:
                self.validation_errors.append("effective_date must be a valid ISO datetime string")

        result["errors"] = self.validation_errors.copy()
        result["warnings"] = self.warnings.copy()
        result["is_valid"] = len(self.validation_errors) == 0

        return result

    def validate_constitutional_compliance(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Validate constitutional compliance with edge case handling."""
        self.validation_errors.clear()
        self.warnings.clear()

        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "compliance_score": 0.0
        }

        # Constitutional hash validation
        const_hash = document.get("constitutional_hash", "")
        if not const_hash:
            self.validation_errors.append("Constitutional hash is required")
        elif not isinstance(const_hash, str):
            self.validation_errors.append("Constitutional hash must be a string")
        elif not re.match(r'^[a-f0-9]{16}$', const_hash):
            self.validation_errors.append("Constitutional hash must be 16 hexadecimal characters")

        # Compliance level validation
        compliance_level = document.get("compliance_level", "")
        valid_levels = ["full", "partial", "non_compliant", "pending", "under_review"]
        if compliance_level not in valid_levels:
            self.validation_errors.append(f"Compliance level must be one of: {', '.join(valid_levels)}")

        # Required fields validation
        required_fields = ["constitutional_hash", "compliance_level", "validation_timestamp"]
        missing_fields = [field for field in required_fields if not document.get(field)]
        if missing_fields:
            self.validation_errors.append(f"Missing required fields: {', '.join(missing_fields)}")

        # High compliance validation
        if compliance_level == "full":
            if not document.get("approved_by"):
                self.validation_errors.append("Full compliance documents must have approved_by field")
            if not document.get("approval_timestamp"):
                self.validation_errors.append("Full compliance documents must have approval_timestamp")

        # Calculate compliance score
        score = 0.0
        if compliance_level == "full":
            score = 100.0
        elif compliance_level == "partial":
            score = 75.0
        elif compliance_level == "under_review":
            score = 50.0
        elif compliance_level == "pending":
            score = 25.0
        else:
            score = 0.0

        result["compliance_score"] = score
        result["errors"] = self.validation_errors.copy()
        result["warnings"] = self.warnings.copy()
        result["is_valid"] = len(self.validation_errors) == 0

        return result

# Global validator instance
enhanced_validator = EnhancedBusinessRuleValidator()

def validate_governance_proposal(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for validating governance proposals."""
    return enhanced_validator.validate_governance_proposal(proposal)

def validate_policy_document(policy: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for validating policy documents."""
    return enhanced_validator.validate_policy_document(policy)

def validate_constitutional_compliance(document: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for validating constitutional compliance."""
    return enhanced_validator.validate_constitutional_compliance(document)
'''

            # Save the enhanced business rules module
            rules_file = (
                self.project_root / "services" / "shared" / "enhanced_business_rules.py"
            )
            rules_file.parent.mkdir(parents=True, exist_ok=True)

            with open(rules_file, "w") as f:
                f.write(enhanced_rules_code)

            actions_taken.append("Created enhanced business rule validation")

            verification_passed = self._verify_business_rules_enhancement()
            actions_taken.append("Verified business rule enhancements")

            remaining_work = [
                "Integrate enhanced validation into existing workflows",
                "Add comprehensive logging for validation failures",
                "Implement validation result caching",
                "Create validation metrics and monitoring",
            ]

            return MajorResolutionResult(
                issue["id"],
                "RESOLVED" if verification_passed else "PARTIAL",
                time.time() - start_time,
                actions_taken,
                verification_passed,
                remaining_work,
                {
                    "rules_module_created": str(rules_file),
                    "validation_improvements": [
                        "edge_case_handling",
                        "sanitization",
                        "warnings",
                        "compliance_scoring",
                    ],
                },
            )

        except Exception as e:
            return MajorResolutionResult(
                issue["id"],
                "FAILED",
                time.time() - start_time,
                actions_taken,
                False,
                [],
                {"error": str(e)},
            )

    def _verify_business_rules_enhancement(self) -> bool:
        """Verify that the business rules enhancement works correctly."""
        try:
            # Import the new rules module
            sys.path.insert(0, str(self.project_root / "services" / "shared"))
            from enhanced_business_rules import (
                validate_governance_proposal,
                validate_policy_document,
            )

            # Test governance proposal validation
            valid_proposal = {
                "title": "Test Proposal",
                "description": "This is a valid test proposal with sufficient detail",
                "status": "draft",
                "priority": "medium",
            }

            result = validate_governance_proposal(valid_proposal)
            if not result["is_valid"]:
                return False

            # Test invalid proposal
            invalid_proposal = {
                "title": "",  # Invalid empty title
                "description": "Short",  # Too short
                "status": "invalid",  # Invalid status
                "priority": "unknown",  # Invalid priority
            }

            result = validate_governance_proposal(invalid_proposal)
            if result["is_valid"] or len(result["errors"]) == 0:
                return False

            # Test policy validation
            valid_policy = {
                "id": "POL-0001",
                "version": "1.0.0",
                "content": {"rules": ["rule1", "rule2"]},
                "effective_date": "2024-12-01T00:00:00Z",
            }

            result = validate_policy_document(valid_policy)
            if not result["is_valid"]:
                return False

            return True

        except Exception:
            return False

    def resolve_major_issues(self) -> dict[str, Any]:
        """Resolve all major issues."""
        print("Starting Major Issue Resolution...")
        print("=" * 60)

        major_issues = self.load_major_issues()

        if not major_issues:
            print("✅ No major issues found to resolve.")
            return {"total_issues": 0, "resolved": 0, "failed": 0, "results": []}

        resolved_count = 0
        failed_count = 0

        for issue in major_issues:
            print(f"\n🔧 Resolving: {issue['id']} - {issue['title']}")

            if (
                "performance" in issue["title"].lower()
                and "cache" in issue["title"].lower()
            ):
                result = self.resolve_cache_performance_issue(issue)
            elif (
                "business rule" in issue["title"].lower()
                or "edge case" in issue["title"].lower()
            ):
                result = self.resolve_business_rule_edge_cases(issue)
            else:
                # Generic resolution for other major issues
                result = MajorResolutionResult(
                    issue["id"],
                    "SKIPPED",
                    0.0,
                    ["Issue type not yet supported by automated resolution"],
                    False,
                    ["Manual resolution required"],
                    {"issue_type": issue["category"]},
                )

            self.resolution_results.append(result)

            # Log result
            status_symbol = {
                "RESOLVED": "✅",
                "PARTIAL": "🟡",
                "FAILED": "❌",
                "SKIPPED": "⊝",
            }
            symbol = status_symbol.get(result.status, "?")

            print(
                f"{symbol} {result.issue_id}: {result.status} ({result.resolution_time:.3f}s)"
            )
            print(f"   Actions: {len(result.actions_taken)}")
            print(f"   Verified: {'✓' if result.verification_passed else '✗'}")
            print(f"   Remaining: {len(result.remaining_work)}")

            if result.status == "RESOLVED":
                resolved_count += 1
            elif result.status == "FAILED":
                failed_count += 1

        # Generate summary
        summary = {
            "total_issues": len(major_issues),
            "resolved": resolved_count,
            "partial": sum(1 for r in self.resolution_results if r.status == "PARTIAL"),
            "failed": failed_count,
            "skipped": sum(1 for r in self.resolution_results if r.status == "SKIPPED"),
            "resolution_rate": (
                (resolved_count / len(major_issues) * 100) if major_issues else 0
            ),
            "results": [
                {
                    "issue_id": r.issue_id,
                    "status": r.status,
                    "resolution_time": r.resolution_time,
                    "actions_taken": r.actions_taken,
                    "verification_passed": r.verification_passed,
                    "remaining_work": r.remaining_work,
                    "details": r.details,
                }
                for r in self.resolution_results
            ],
        }

        print("\n" + "=" * 60)
        print("MAJOR ISSUE RESOLUTION SUMMARY")
        print("=" * 60)
        print(f"Total Major Issues: {summary['total_issues']}")
        print(f"Resolved: {summary['resolved']}")
        print(f"Partial: {summary['partial']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Resolution Rate: {summary['resolution_rate']:.1f}%")

        return summary


def main():
    resolver = MajorIssueResolver()
    summary = resolver.resolve_major_issues()

    # Save results
    output_file = project_root / "major_issue_resolution_results.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Return appropriate exit code
    if summary["failed"] > 0:
        print(f"\n⚠️  {summary['failed']} major issues failed to resolve!")
        return 1
    if summary["resolved"] < summary["total_issues"]:
        print(
            f"\n⚠️  {summary['total_issues'] - summary['resolved']} major issues need manual attention!"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
