"""
Enhanced Resource Management Module for ACGS

This module provides advanced resource management capabilities including:
- Dynamic resource allocation and optimization
- Intelligent monitoring and alerting
- Automatic scaling and load balancing
- Performance-based resource tuning
"""

from .enhanced_resource_manager import (
    EnhancedResourceManager,
    ResourceType,
    ResourceMetrics,
    ResourceThresholds,
    AlertLevel,
    AlertRule,
    ScalingPolicy,
)

__all__ = [
    "EnhancedResourceManager",
    "ResourceType",
    "ResourceMetrics", 
    "ResourceThresholds",
    "AlertLevel",
    "AlertRule",
    "ScalingPolicy",
]