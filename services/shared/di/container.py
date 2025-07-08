"""
Lightweight Service Container for Dependency Injection
Constitutional Hash: cdd01ef066bc6cf2

This module provides a lightweight dependency injection container
compatible with FastAPI's Depends system, inspired by punq's design.
"""

import inspect
import logging
from collections.abc import Callable
from functools import cache
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
FactoryFunction = Callable[..., T]

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class DIException(Exception):
    """Base exception for dependency injection errors."""


class ServiceNotFound(DIException):
    """Raised when a requested service is not registered."""


class CircularDependency(DIException):
    """Raised when a circular dependency is detected."""


class ServiceLifetime:
    """Service lifetime scopes."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class ServiceDescriptor:
    """Describes how a service should be created and managed."""

    def __init__(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        factory: FactoryFunction | None = None,
        lifetime: str = ServiceLifetime.TRANSIENT,
        dependencies: dict[str, type] | None = None,
    ):
        self.service_type = service_type
        self.implementation = implementation or service_type
        self.factory = factory
        self.lifetime = lifetime
        self.dependencies = dependencies or {}
        self._instance: T | None = None
        self._creating = False  # For circular dependency detection


class Container:
    """
    Lightweight dependency injection container.

    Provides service registration, resolution, and lifetime management
    compatible with FastAPI's dependency injection system.
    """

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}
        self._singletons: dict[type, Any] = {}
        self._scoped_instances: dict[type, Any] = {}
        self._resolution_stack: list = []

        # Register the container itself
        self.register_instance(Container, self)

        logger.info(
            "✅ DI Container initialized with constitutional hash:"
            f" {CONSTITUTIONAL_HASH}"
        )

    def register(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
        lifetime: str = ServiceLifetime.TRANSIENT,
        dependencies: dict[str, type] | None = None,
    ) -> "Container":
        """Register a service with the container."""
        if service_type in self._services:
            logger.warning(
                f"Service {service_type.__name__} is already registered, overriding"
            )

        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=lifetime,
            dependencies=dependencies,
        )

        logger.debug(f"Registered service: {service_type.__name__} ({lifetime})")
        return self

    def register_factory(
        self,
        service_type: type[T],
        factory: FactoryFunction,
        lifetime: str = ServiceLifetime.TRANSIENT,
    ) -> "Container":
        """Register a factory function for creating a service."""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifetime=lifetime,
        )

        logger.debug(f"Registered factory for: {service_type.__name__} ({lifetime})")
        return self

    def register_instance(self, service_type: type[T], instance: T) -> "Container":
        """Register a pre-created instance as a singleton."""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            lifetime=ServiceLifetime.SINGLETON,
        )
        self._singletons[service_type] = instance

        logger.debug(f"Registered instance: {service_type.__name__}")
        return self

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service instance."""
        if service_type not in self._services:
            # Try auto-registration for concrete types
            if self._can_auto_register(service_type):
                self.register(service_type)
            else:
                raise ServiceNotFound(f"Service {service_type.__name__} not registered")

        descriptor = self._services[service_type]

        # Check for circular dependencies
        if service_type in self._resolution_stack:
            cycle = " -> ".join([t.__name__ for t in self._resolution_stack])
            raise CircularDependency(
                f"Circular dependency detected: {cycle} -> {service_type.__name__}"
            )

        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._resolve_singleton(service_type, descriptor)
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._resolve_scoped(service_type, descriptor)
        # TRANSIENT
        return self._create_instance(service_type, descriptor)

    def _resolve_singleton(
        self, service_type: type[T], descriptor: ServiceDescriptor
    ) -> T:
        """Resolve a singleton service."""
        if service_type not in self._singletons:
            self._singletons[service_type] = self._create_instance(
                service_type, descriptor
            )
        return self._singletons[service_type]

    def _resolve_scoped(
        self, service_type: type[T], descriptor: ServiceDescriptor
    ) -> T:
        """Resolve a scoped service."""
        if service_type not in self._scoped_instances:
            self._scoped_instances[service_type] = self._create_instance(
                service_type, descriptor
            )
        return self._scoped_instances[service_type]

    def _create_instance(
        self, service_type: type[T], descriptor: ServiceDescriptor
    ) -> T:
        """Create a new instance of the service."""
        self._resolution_stack.append(service_type)

        try:
            if descriptor.factory:
                # Use factory function
                instance = self._call_factory(descriptor.factory)
            else:
                # Create instance using constructor
                instance = self._create_from_constructor(descriptor.implementation)

            logger.debug(f"Created instance: {service_type.__name__}")
            return instance

        finally:
            self._resolution_stack.pop()

    def _call_factory(self, factory: FactoryFunction) -> Any:
        """Call a factory function with dependency injection."""
        sig = inspect.signature(factory)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                kwargs[param_name] = self.resolve(param.annotation)

        return factory(**kwargs)

    def _create_from_constructor(self, implementation: type[T]) -> T:
        """Create instance using constructor with dependency injection."""
        try:
            sig = inspect.signature(implementation.__init__)
            kwargs = {}

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                if param.annotation != inspect.Parameter.empty:
                    kwargs[param_name] = self.resolve(param.annotation)
                elif param.default == inspect.Parameter.empty:
                    # Required parameter without annotation
                    logger.warning(
                        f"Parameter {param_name} in {implementation.__name__} has no"
                        " type annotation"
                    )

            return implementation(**kwargs)

        except Exception as e:
            logger.error(f"Failed to create instance of {implementation.__name__}: {e}")
            raise

    def _can_auto_register(self, service_type: type) -> bool:
        """Check if a type can be auto-registered."""
        return (
            inspect.isclass(service_type)
            and not inspect.isabstract(service_type)
            and hasattr(service_type, "__init__")
        )

    def clear_scoped(self):
        """Clear scoped instances."""
        self._scoped_instances.clear()
        logger.debug("Cleared scoped instances")

    def get_dependency_provider(self, service_type: type[T]) -> Callable[[], T]:
        """Get a FastAPI-compatible dependency provider function."""

        @cache
        def dependency_provider() -> T:
            return self.resolve(service_type)

        return dependency_provider


# Global container instance
_container: Container | None = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def configure_container() -> Container:
    """Configure and return the global container."""
    container = get_container()

    # Register common infrastructure services
    from ..config.infrastructure_config import get_acgs_config

    # Register configuration
    container.register_factory(
        type(get_acgs_config()), get_acgs_config, ServiceLifetime.SINGLETON
    )

    logger.info("✅ Container configured with core services")
    return container


# FastAPI integration helpers
def Inject(service_type: type[T]) -> Callable[[], T]:
    """FastAPI dependency injection decorator."""
    container = get_container()
    return container.get_dependency_provider(service_type)


def injectable(
    lifetime: str = ServiceLifetime.TRANSIENT,
    interface: type | None = None,
) -> Callable[[type[T]], type[T]]:
    """Decorator to mark a class as injectable."""

    def decorator(cls: type[T]) -> type[T]:
        container = get_container()
        registration_type = interface or cls
        container.register(registration_type, cls, lifetime)
        return cls

    return decorator


# Service registration decorators
def singleton(interface: type | None = None):
    """Mark a class as a singleton service."""
    return injectable(ServiceLifetime.SINGLETON, interface)


def transient(interface: type | None = None):
    """Mark a class as a transient service."""
    return injectable(ServiceLifetime.TRANSIENT, interface)


def scoped(interface: type | None = None):
    """Mark a class as a scoped service."""
    return injectable(ServiceLifetime.SCOPED, interface)
