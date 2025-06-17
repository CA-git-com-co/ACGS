"""
Service Registry for ACGS-PGP Dependency Injection

Provides service registration and discovery capabilities for the
dependency injection framework.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ServiceScope(Enum):
    """Service registration scopes."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceRegistration:
    """Service registration information."""

    interface: type
    implementation: type
    scope: ServiceScope
    factory: callable | None = None
    instance: Any | None = None
    dependencies: list[type] = None

    def __post_init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if self.dependencies is None:
            self.dependencies = []


class ServiceRegistry:
    """
    Service registry for dependency injection.

    Manages service registrations and provides lookup capabilities
    for the dependency injection container.
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize service registry."""
        self._registrations: dict[type, ServiceRegistration] = {}
        self._instances: dict[type, Any] = {}

    def register(
        self,
        interface: type,
        implementation: type = None,
        scope: ServiceScope = ServiceScope.TRANSIENT,
        factory: callable = None,
    ) -> "ServiceRegistry":
        """
        Register a service.

        Args:
            interface: Service interface
            implementation: Service implementation
            scope: Service scope
            factory: Optional factory function

        Returns:
            Self for method chaining
        """
        if implementation is None and factory is None:
            implementation = interface

        registration = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            scope=scope,
            factory=factory,
        )

        self._registrations[interface] = registration
        logger.debug(f"Registered {interface} -> {implementation or factory}")

        return self

    def register_singleton(
        self, interface: type, implementation: type = None
    ) -> "ServiceRegistry":
        """Register a singleton service."""
        return self.register(interface, implementation, ServiceScope.SINGLETON)

    def register_transient(
        self, interface: type, implementation: type = None
    ) -> "ServiceRegistry":
        """Register a transient service."""
        return self.register(interface, implementation, ServiceScope.TRANSIENT)

    def register_scoped(
        self, interface: type, implementation: type = None
    ) -> "ServiceRegistry":
        """Register a scoped service."""
        return self.register(interface, implementation, ServiceScope.SCOPED)

    def register_instance(self, interface: type, instance: Any) -> "ServiceRegistry":
        """
        Register a pre-created instance.

        Args:
            interface: Service interface
            instance: Service instance

        Returns:
            Self for method chaining
        """
        registration = ServiceRegistration(
            interface=interface,
            implementation=type(instance),
            scope=ServiceScope.SINGLETON,
            instance=instance,
        )

        self._registrations[interface] = registration
        self._instances[interface] = instance

        logger.debug(f"Registered instance {interface} -> {instance}")
        return self

    def get_registration(self, interface: type) -> ServiceRegistration | None:
        """
        Get service registration.

        Args:
            interface: Service interface

        Returns:
            Service registration or None
        """
        return self._registrations.get(interface)

    def is_registered(self, interface: type) -> bool:
        """
        Check if service is registered.

        Args:
            interface: Service interface

        Returns:
            True if registered
        """
        return interface in self._registrations

    def get_all_registrations(self) -> dict[type, ServiceRegistration]:
        """Get all service registrations."""
        return self._registrations.copy()

    def unregister(self, interface: type) -> bool:
        """
        Unregister a service.

        Args:
            interface: Service interface

        Returns:
            True if service was unregistered
        """
        if interface in self._registrations:
            del self._registrations[interface]
            self._instances.pop(interface, None)
            logger.debug(f"Unregistered {interface}")
            return True
        return False

    def clear(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Clear all registrations."""
        self._registrations.clear()
        self._instances.clear()
        logger.debug("Cleared all registrations")

    def get_dependency_graph(self) -> dict[type, list[type]]:
        """
        Get dependency graph for all registered services.

        Returns:
            Dictionary mapping interfaces to their dependencies
        """
        return {
            interface: registration.dependencies
            for interface, registration in self._registrations.items()
        }

    def validate_registrations(self) -> list[str]:
        """
        Validate all registrations for missing dependencies.

        Returns:
            List of validation errors
        """
        errors = []

        for interface, registration in self._registrations.items():
            for dependency in registration.dependencies:
                if not self.is_registered(dependency):
                    errors.append(
                        f"Service {interface} depends on unregistered {dependency}"
                    )

        return errors

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        scope_counts = {}
        for registration in self._registrations.values():
            scope = registration.scope.value
            scope_counts[scope] = scope_counts.get(scope, 0) + 1

        return {
            "total_registrations": len(self._registrations),
            "singleton_instances": len(self._instances),
            "registrations_by_scope": scope_counts,
        }


# Global registry instance
_registry: ServiceRegistry | None = None


def get_service_registry() -> ServiceRegistry:
    """
    Get the global service registry.

    Returns:
        Service registry instance
    """
    global _registry

    if _registry is None:
        _registry = ServiceRegistry()

    return _registry


def configure_registry(registry: ServiceRegistry):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Configure the global service registry.

    Args:
        registry: Service registry to set as global
    """
    global _registry
    _registry = registry
