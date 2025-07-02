"""
Event system for ACGS multi-agent coordination.

This module provides event bus functionality for decoupled communication
between agents and services in the ACGS system.
"""

from .bus import EventBus, Event, EventHandler

__all__ = ['EventBus', 'Event', 'EventHandler']
