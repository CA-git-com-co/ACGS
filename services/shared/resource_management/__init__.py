"""
Enhanced Resource Management Module for ACGS

This module provides advanced resource management capabilities including:
- Dynamic resource allocation and optimization
- Intelligent monitoring and alerting
- Automatic scaling and load balancing
- Performance-based resource tuning
"""
# Constitutional Hash: cdd01ef066bc6cf2

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