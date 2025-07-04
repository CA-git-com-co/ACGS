"""
Event system for ACGS multi-agent coordination.

This module provides event bus functionality for decoupled communication
between agents and services in the ACGS system.
"""

from .bus import EventBus, Event, EventHandler

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = ['EventBus', 'Event', 'EventHandler']
