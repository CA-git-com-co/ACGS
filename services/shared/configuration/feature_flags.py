"""
Feature Flag Management System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Advanced feature flags with conditions, rollout strategies, and A/B testing.
"""

import hashlib
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from services.shared.resilience.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class FeatureFlagStatus(str, Enum):
    """Feature flag status."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    CONDITIONAL = "conditional"
    ROLLOUT = "rollout"


class RolloutStrategy(str, Enum):
    """Rollout strategies for feature flags."""

    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    USER_ATTRIBUTE = "user_attribute"
    TIME_BASED = "time_based"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"


@dataclass
class UserContext:
    """User context for feature flag evaluation."""

    user_id: str
    attributes: dict[str, Any] = field(default_factory=dict)
    groups: list[str] = field(default_factory=list)
    tenant_id: str | None = None
    session_id: str | None = None

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get user attribute."""
        return self.attributes.get(key, default)

    def has_group(self, group: str) -> bool:
        """Check if user belongs to group."""
        return group in self.groups

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "attributes": self.attributes,
            "groups": self.groups,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
        }


class FeatureFlagCondition(ABC):
    """Abstract base class for feature flag conditions."""

    @abstractmethod
    def evaluate(self, context: UserContext) -> bool:
        """Evaluate condition against user context."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert condition to dictionary."""


class PercentageCondition(FeatureFlagCondition):
    """Percentage-based rollout condition."""

    def __init__(self, percentage: float, salt: str = ""):
        self.percentage = max(0.0, min(100.0, percentage))
        self.salt = salt

    def evaluate(self, context: UserContext) -> bool:
        """Evaluate percentage condition."""
        # Create deterministic hash based on user ID and salt
        hash_input = f"{context.user_id}{self.salt}".encode()
        hash_value = hashlib.md5(hash_input).hexdigest()

        # Convert first 8 chars of hash to integer and get percentage
        hash_int = int(hash_value[:8], 16)
        user_percentage = (hash_int % 10000) / 100.0

        return user_percentage < self.percentage

    def to_dict(self) -> dict[str, Any]:
        return {"type": "percentage", "percentage": self.percentage, "salt": self.salt}


class UserListCondition(FeatureFlagCondition):
    """User list condition."""

    def __init__(self, user_ids: list[str], include: bool = True):
        self.user_ids = set(user_ids)
        self.include = include

    def evaluate(self, context: UserContext) -> bool:
        """Evaluate user list condition."""
        is_in_list = context.user_id in self.user_ids
        return is_in_list if self.include else not is_in_list

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "user_list",
            "user_ids": list(self.user_ids),
            "include": self.include,
        }


class AttributeCondition(FeatureFlagCondition):
    """User attribute condition."""

    def __init__(self, attribute: str, operator: str, value: Any):
        self.attribute = attribute
        self.operator = operator
        self.value = value

    def evaluate(self, context: UserContext) -> bool:
        """Evaluate attribute condition."""
        user_value = context.get_attribute(self.attribute)

        if user_value is None:
            return False

        if self.operator == "equals":
            return user_value == self.value
        if self.operator == "not_equals":
            return user_value != self.value
        if self.operator == "in":
            return (
                user_value in self.value
                if isinstance(self.value, (list, tuple, set))
                else False
            )
        if self.operator == "not_in":
            return (
                user_value not in self.value
                if isinstance(self.value, (list, tuple, set))
                else True
            )
        if self.operator == "greater_than":
            return user_value > self.value
        if self.operator == "less_than":
            return user_value < self.value
        if self.operator == "greater_equal":
            return user_value >= self.value
        if self.operator == "less_equal":
            return user_value <= self.value
        if self.operator == "contains":
            return str(self.value) in str(user_value)
        if self.operator == "starts_with":
            return str(user_value).startswith(str(self.value))
        if self.operator == "ends_with":
            return str(user_value).endswith(str(self.value))
        logger.warning(f"Unknown operator: {self.operator}")
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "attribute",
            "attribute": self.attribute,
            "operator": self.operator,
            "value": self.value,
        }


class GroupCondition(FeatureFlagCondition):
    """User group condition."""

    def __init__(self, groups: list[str], require_all: bool = False):
        self.groups = set(groups)
        self.require_all = require_all

    def evaluate(self, context: UserContext) -> bool:
        """Evaluate group condition."""
        user_groups = set(context.groups)

        if self.require_all:
            return self.groups.issubset(user_groups)
        return bool(self.groups.intersection(user_groups))

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "group",
            "groups": list(self.groups),
            "require_all": self.require_all,
        }


class TimeBasedCondition(FeatureFlagCondition):
    """Time-based condition."""

    def __init__(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ):
        self.start_time = start_time
        self.end_time = end_time

    def evaluate(self, context: UserContext) -> bool:
        """Evaluate time-based condition."""
        now = datetime.utcnow()

        if self.start_time and now < self.start_time:
            return False

        return not (self.end_time and now > self.end_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "time_based",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class CompositeCondition(FeatureFlagCondition):
    """Composite condition combining multiple conditions."""

    def __init__(self, conditions: list[FeatureFlagCondition], operator: str = "and"):
        self.conditions = conditions
        self.operator = operator  # "and", "or"

    def evaluate(self, context: UserContext) -> bool:
        """Evaluate composite condition."""
        if not self.conditions:
            return True

        results = [condition.evaluate(context) for condition in self.conditions]

        if self.operator == "and":
            return all(results)
        if self.operator == "or":
            return any(results)
        logger.warning(f"Unknown composite operator: {self.operator}")
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "composite",
            "operator": self.operator,
            "conditions": [condition.to_dict() for condition in self.conditions],
        }


@dataclass
class FeatureFlag:
    """Feature flag definition."""

    name: str
    description: str = ""
    status: FeatureFlagStatus = FeatureFlagStatus.DISABLED
    conditions: list[FeatureFlagCondition] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize feature flag with constitutional compliance."""
        self.metadata["constitutional_hash"] = "cdd01ef066bc6cf2"

    def is_enabled_for_user(self, context: UserContext) -> bool:
        """Check if feature flag is enabled for user."""
        if self.status == FeatureFlagStatus.ENABLED:
            return True
        if self.status == FeatureFlagStatus.DISABLED:
            return False
        if self.status in {FeatureFlagStatus.CONDITIONAL, FeatureFlagStatus.ROLLOUT}:
            # Evaluate all conditions
            return all(condition.evaluate(context) for condition in self.conditions)
        return False

    def add_condition(self, condition: FeatureFlagCondition) -> None:
        """Add condition to feature flag."""
        self.conditions.append(condition)
        self.updated_at = datetime.utcnow()

    def remove_condition(self, condition_index: int) -> None:
        """Remove condition by index."""
        if 0 <= condition_index < len(self.conditions):
            self.conditions.pop(condition_index)
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert feature flag to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "conditions": [condition.to_dict() for condition in self.conditions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


class FeatureFlagManager:
    """Feature flag management system."""

    def __init__(self, name: str = "acgs_feature_flags"):
        self.name = name
        self._flags: dict[str, FeatureFlag] = {}
        self._evaluations: dict[str, int] = {}  # Track evaluation counts
        self._cache: dict[str, Tuple[bool, float]] = {}  # Simple cache with TTL
        self._cache_ttl = 300  # 5 minutes
        self._lock = threading.RLock()
        self._change_callbacks: list[Callable[[str, FeatureFlag], None]] = []

    def create_flag(
        self,
        name: str,
        description: str = "",
        status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
        tags: list[str] | None = None,
    ) -> FeatureFlag:
        """Create a new feature flag."""
        with self._lock:
            if name in self._flags:
                raise ConfigurationError(f"Feature flag '{name}' already exists")

            flag = FeatureFlag(
                name=name, description=description, status=status, tags=tags or []
            )

            self._flags[name] = flag
            self._evaluations[name] = 0

            # Notify change callbacks
            self._notify_change_callbacks(name, flag)

            logger.info(f"Created feature flag: {name}")
            return flag

    def update_flag(
        self,
        name: str,
        status: FeatureFlagStatus = None,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> FeatureFlag:
        """Update existing feature flag."""
        with self._lock:
            if name not in self._flags:
                raise ConfigurationError(f"Feature flag '{name}' not found")

            flag = self._flags[name]

            if status is not None:
                flag.status = status
            if description is not None:
                flag.description = description
            if tags is not None:
                flag.tags = tags

            flag.updated_at = datetime.utcnow()

            # Clear cache for this flag
            self._clear_flag_cache(name)

            # Notify change callbacks
            self._notify_change_callbacks(name, flag)

            logger.info(f"Updated feature flag: {name}")
            return flag

    def delete_flag(self, name: str) -> None:
        """Delete feature flag."""
        with self._lock:
            if name not in self._flags:
                raise ConfigurationError(f"Feature flag '{name}' not found")

            del self._flags[name]
            del self._evaluations[name]
            self._clear_flag_cache(name)

            logger.info(f"Deleted feature flag: {name}")

    def get_flag(self, name: str) -> FeatureFlag | None:
        """Get feature flag by name."""
        with self._lock:
            return self._flags.get(name)

    def list_flags(self) -> list[FeatureFlag]:
        """List all feature flags."""
        with self._lock:
            return list(self._flags.values())

    def is_enabled(
        self, flag_name: str, context: UserContext, use_cache: bool = True
    ) -> bool:
        """Check if feature flag is enabled for user."""
        # Check cache first
        if use_cache:
            cache_key = f"{flag_name}:{context.user_id}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result is not None:
                return cached_result

        with self._lock:
            flag = self._flags.get(flag_name)
            if flag is None:
                logger.warning(
                    f"Feature flag '{flag_name}' not found, defaulting to disabled"
                )
                return False

            # Evaluate flag
            result = flag.is_enabled_for_user(context)

            # Update evaluation count
            self._evaluations[flag_name] += 1

            # Cache result
            if use_cache:
                cache_key = f"{flag_name}:{context.user_id}"
                self._cache_result(cache_key, result)

            return result

    def add_percentage_rollout(
        self, flag_name: str, percentage: float, salt: str = ""
    ) -> None:
        """Add percentage rollout to feature flag."""
        flag = self.get_flag(flag_name)
        if not flag:
            raise ConfigurationError(f"Feature flag '{flag_name}' not found")

        condition = PercentageCondition(percentage, salt)
        flag.add_condition(condition)
        flag.status = FeatureFlagStatus.ROLLOUT

        self._clear_flag_cache(flag_name)
        self._notify_change_callbacks(flag_name, flag)

    def add_user_list(
        self, flag_name: str, user_ids: list[str], include: bool = True
    ) -> None:
        """Add user list condition to feature flag."""
        flag = self.get_flag(flag_name)
        if not flag:
            raise ConfigurationError(f"Feature flag '{flag_name}' not found")

        condition = UserListCondition(user_ids, include)
        flag.add_condition(condition)
        flag.status = FeatureFlagStatus.CONDITIONAL

        self._clear_flag_cache(flag_name)
        self._notify_change_callbacks(flag_name, flag)

    def add_attribute_condition(
        self, flag_name: str, attribute: str, operator: str, value: Any
    ) -> None:
        """Add attribute condition to feature flag."""
        flag = self.get_flag(flag_name)
        if not flag:
            raise ConfigurationError(f"Feature flag '{flag_name}' not found")

        condition = AttributeCondition(attribute, operator, value)
        flag.add_condition(condition)
        flag.status = FeatureFlagStatus.CONDITIONAL

        self._clear_flag_cache(flag_name)
        self._notify_change_callbacks(flag_name, flag)

    def _get_cached_result(self, cache_key: str) -> bool | None:
        """Get cached evaluation result."""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            del self._cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: bool) -> None:
        """Cache evaluation result."""
        self._cache[cache_key] = (result, time.time())

    def _clear_flag_cache(self, flag_name: str) -> None:
        """Clear cache entries for specific flag."""
        keys_to_remove = [key for key in self._cache if key.startswith(f"{flag_name}:")]
        for key in keys_to_remove:
            del self._cache[key]

    def clear_cache(self) -> None:
        """Clear all cached results."""
        with self._lock:
            self._cache.clear()

    def add_change_callback(self, callback: Callable[[str, FeatureFlag], None]) -> None:
        """Add callback for flag changes."""
        self._change_callbacks.append(callback)

    def _notify_change_callbacks(self, flag_name: str, flag: FeatureFlag) -> None:
        """Notify change callbacks."""
        for callback in self._change_callbacks:
            try:
                callback(flag_name, flag)
            except Exception as e:
                logger.exception(f"Error in feature flag change callback: {e}")

    def get_flag_stats(self, flag_name: str) -> dict[str, Any]:
        """Get statistics for specific flag."""
        with self._lock:
            flag = self._flags.get(flag_name)
            if not flag:
                return {}

            return {
                "name": flag_name,
                "status": flag.status.value,
                "conditions_count": len(flag.conditions),
                "evaluations": self._evaluations.get(flag_name, 0),
                "created_at": flag.created_at.isoformat(),
                "updated_at": flag.updated_at.isoformat(),
                "tags": flag.tags,
            }

    def get_overall_stats(self) -> dict[str, Any]:
        """Get overall feature flag statistics."""
        with self._lock:
            total_flags = len(self._flags)
            enabled_flags = sum(
                1 for f in self._flags.values() if f.status == FeatureFlagStatus.ENABLED
            )
            disabled_flags = sum(
                1
                for f in self._flags.values()
                if f.status == FeatureFlagStatus.DISABLED
            )
            conditional_flags = sum(
                1
                for f in self._flags.values()
                if f.status == FeatureFlagStatus.CONDITIONAL
            )
            rollout_flags = sum(
                1 for f in self._flags.values() if f.status == FeatureFlagStatus.ROLLOUT
            )

            total_evaluations = sum(self._evaluations.values())
            cache_size = len(self._cache)

            return {
                "manager_name": self.name,
                "total_flags": total_flags,
                "enabled_flags": enabled_flags,
                "disabled_flags": disabled_flags,
                "conditional_flags": conditional_flags,
                "rollout_flags": rollout_flags,
                "total_evaluations": total_evaluations,
                "cache_size": cache_size,
                "cache_ttl": self._cache_ttl,
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

    def export_flags(self) -> dict[str, Any]:
        """Export all feature flags to dictionary."""
        with self._lock:
            return {
                "flags": {name: flag.to_dict() for name, flag in self._flags.items()},
                "export_timestamp": datetime.utcnow().isoformat(),
                "constitutional_hash": "cdd01ef066bc6cf2",
            }

    def import_flags(self, data: dict[str, Any]) -> None:
        """Import feature flags from dictionary."""
        if "flags" not in data:
            raise ConfigurationError("Invalid import data: missing 'flags' key")

        with self._lock:
            for flag_name, flag_data in data["flags"].items():
                try:
                    # Create flag from data
                    flag = FeatureFlag(
                        name=flag_data["name"],
                        description=flag_data.get("description", ""),
                        status=FeatureFlagStatus(flag_data["status"]),
                        tags=flag_data.get("tags", []),
                    )

                    # Recreate conditions
                    for condition_data in flag_data.get("conditions", []):
                        condition = self._create_condition_from_dict(condition_data)
                        if condition:
                            flag.conditions.append(condition)

                    self._flags[flag_name] = flag
                    self._evaluations[flag_name] = 0

                except Exception as e:
                    logger.exception(f"Failed to import flag '{flag_name}': {e}")

    def _create_condition_from_dict(
        self, data: dict[str, Any]
    ) -> FeatureFlagCondition | None:
        """Create condition from dictionary data."""
        condition_type = data.get("type")

        if condition_type == "percentage":
            return PercentageCondition(data["percentage"], data.get("salt", ""))
        if condition_type == "user_list":
            return UserListCondition(data["user_ids"], data.get("include", True))
        if condition_type == "attribute":
            return AttributeCondition(
                data["attribute"], data["operator"], data["value"]
            )
        if condition_type == "group":
            return GroupCondition(data["groups"], data.get("require_all", False))
        if condition_type == "time_based":
            start_time = (
                datetime.fromisoformat(data["start_time"])
                if data.get("start_time")
                else None
            )
            end_time = (
                datetime.fromisoformat(data["end_time"])
                if data.get("end_time")
                else None
            )
            return TimeBasedCondition(start_time, end_time)
        if condition_type == "composite":
            conditions = []
            for cond_data in data.get("conditions", []):
                condition = self._create_condition_from_dict(cond_data)
                if condition:
                    conditions.append(condition)
            return CompositeCondition(conditions, data.get("operator", "and"))
        logger.warning(f"Unknown condition type: {condition_type}")
        return None


# Global feature flag manager
_global_feature_flag_manager = FeatureFlagManager()


def get_feature_flag_manager() -> FeatureFlagManager:
    """Get the global feature flag manager."""
    return _global_feature_flag_manager


# Convenience functions
def is_feature_enabled(flag_name: str, user_id: str, **user_attributes) -> bool:
    """Check if feature is enabled for user."""
    context = UserContext(user_id=user_id, attributes=user_attributes)
    return _global_feature_flag_manager.is_enabled(flag_name, context)


def create_feature_flag(
    name: str,
    description: str = "",
    enabled: bool = False,
    percentage: float | None = None,
    user_ids: list[str] | None = None,
) -> FeatureFlag:
    """Create a feature flag with optional rollout."""
    manager = get_feature_flag_manager()

    status = FeatureFlagStatus.ENABLED if enabled else FeatureFlagStatus.DISABLED
    flag = manager.create_flag(name, description, status)

    if percentage is not None:
        manager.add_percentage_rollout(name, percentage)

    if user_ids:
        manager.add_user_list(name, user_ids)

    return flag


# Setup default feature flags
def setup_default_feature_flags() -> None:
    """Set up default feature flags for ACGS."""
    manager = get_feature_flag_manager()

    # Core system features
    manager.create_flag(
        "constitutional_validation",
        "Enhanced constitutional validation with detailed reporting",
        FeatureFlagStatus.ENABLED,
    )

    manager.create_flag(
        "multi_agent_coordination",
        "Advanced multi-agent coordination features",
        FeatureFlagStatus.ENABLED,
    )

    manager.create_flag(
        "performance_monitoring",
        "Detailed performance monitoring and metrics",
        FeatureFlagStatus.ENABLED,
    )

    # Experimental features
    manager.create_flag(
        "ai_assisted_governance",
        "AI-assisted governance decision making",
        FeatureFlagStatus.DISABLED,
    )

    manager.create_flag(
        "advanced_caching",
        "Advanced caching strategies and optimizations",
        FeatureFlagStatus.ROLLOUT,
    )

    # Add percentage rollout for advanced caching (50% rollout)
    manager.add_percentage_rollout("advanced_caching", 50.0)

    logger.info("Default feature flags configured")
