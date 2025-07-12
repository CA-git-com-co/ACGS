"""
Sentry Configuration for Constitutional AI Service

Integrates Sentry monitoring with constitutional compliance validation,
performance tracking, and governance principle enforcement.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
from typing import Optional, Dict, Any
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Import shared Sentry utilities
try:
    from services.shared.monitoring.sentry_integration import (
        init_sentry,
        track_constitutional_compliance,
        ConstitutionalViolationError,
        monitor_performance_target,
        capture_constitutional_event
    )
    from services.shared.monitoring.sentry_alerts import (
        AlertRules,
        ConstitutionalAlertManager
    )
    SENTRY_AVAILABLE = True
except ImportError:
    # Fallback for testing or when shared modules not available
    SENTRY_AVAILABLE = False
    print("Warning: Shared Sentry modules not available")


class ConstitutionalAISentryConfig:
    """Sentry configuration specific to Constitutional AI Service"""
    
    def __init__(self):
        self.service_name = "constitutional-ai-service"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.alert_manager = None
        self.initialized = False
        
    def initialize(self, environment: str = "development") -> None:
        """Initialize Sentry with Constitutional AI specific settings"""
        if not SENTRY_AVAILABLE:
            return
            
        if self.initialized:
            return
            
        # Initialize base Sentry configuration
        init_sentry(
            service_name=self.service_name,
            environment=environment,
            sample_rate=0.2 if environment == "production" else 1.0,
            enable_profiling=True
        )
        
        # Initialize alert manager
        self.alert_manager = ConstitutionalAlertManager(self.service_name)
        
        # Set service-specific context
        sentry_sdk.set_context("constitutional_ai_service", {
            "version": "2.0.0",
            "constitutional_hash": self.constitutional_hash,
            "governance_principles": [
                "democratic_participation",
                "transparency",
                "accountability",
                "rights_protection"
            ]
        })
        
        # Add breadcrumb for service initialization
        sentry_sdk.add_breadcrumb(
            message="Constitutional AI Service initialized",
            category="service.init",
            level="info",
            data={
                "service": self.service_name,
                "environment": environment,
                "constitutional_hash": self.constitutional_hash
            }
        )
        
        self.initialized = True
        
    def track_validation_performance(
        self,
        validation_time_ms: float,
        validation_type: str,
        success: bool,
        compliance_score: Optional[float] = None
    ) -> None:
        """Track constitutional validation performance metrics"""
        if not SENTRY_AVAILABLE:
            return
            
        # Monitor against performance targets
        monitor_performance_target(
            target_name="constitutional_validation_latency",
            target_value=5.0,  # 5ms target
            actual_value=validation_time_ms,
            unit="ms"
        )
        
        # Track validation event
        with sentry_sdk.start_span(
            op="constitutional.validation",
            name=validation_type
        ) as span:
            span.set_tag("validation_type", validation_type)
            span.set_tag("success", str(success))
            span.set_data("validation_time_ms", validation_time_ms)
            
            if compliance_score is not None:
                span.set_data("compliance_score", compliance_score)
                
                # Check compliance thresholds
                if self.alert_manager:
                    AlertRules.check_constitutional_compliance(
                        compliance_rate=compliance_score,
                        service_name=self.service_name
                    )
                    
    def report_governance_violation(
        self,
        principle: str,
        violation_details: str,
        severity: str = "high",
        request_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report constitutional governance principle violations"""
        if not SENTRY_AVAILABLE:
            return
            
        # Capture as constitutional event
        capture_constitutional_event(
            event_type="governance_violation",
            description=f"Violation of {principle} principle: {violation_details}",
            metadata={
                "principle": principle,
                "severity": severity,
                "request_context": request_context or {}
            },
            level="error" if severity == "high" else "warning"
        )
        
        # Trigger specific alert
        if self.alert_manager:
            self.alert_manager.trigger_constitutional_violation(
                violation_type=f"{principle}_violation",
                description=violation_details,
                affected_services=[self.service_name],
                remediation_steps=[
                    f"Review {principle} implementation",
                    "Check constitutional validation logic",
                    "Verify request compliance"
                ]
            )
            
    def track_principle_validation(
        self,
        principle: str,
        weight: float,
        score: float,
        passed: bool,
        evidence: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track individual constitutional principle validation"""
        if not SENTRY_AVAILABLE:
            return
            
        with sentry_sdk.start_span(
            op="constitutional.principle",
            name=f"validate_{principle}"
        ) as span:
            span.set_tag("principle", principle)
            span.set_tag("passed", str(passed))
            span.set_data("weight", weight)
            span.set_data("score", score)
            
            if evidence:
                span.set_data("evidence", evidence)
                
            # Alert on failed principles with high weight
            if not passed and weight > 0.2:
                sentry_sdk.capture_message(
                    f"High-weight principle validation failed: {principle}",
                    level="warning",
                    tags={
                        "principle_failure": True,
                        "principle": principle,
                        "weight": weight
                    },
                    extra={
                        "score": score,
                        "evidence": evidence or {}
                    }
                )
                
    def track_api_request(
        self,
        endpoint: str,
        method: str,
        request_id: str,
        constitutional_context: Dict[str, Any]
    ) -> None:
        """Track API request with constitutional context"""
        if not SENTRY_AVAILABLE:
            return
            
        sentry_sdk.set_context("api_request", {
            "endpoint": endpoint,
            "method": method,
            "request_id": request_id,
            "constitutional_hash": self.constitutional_hash,
            **constitutional_context
        })
        
        sentry_sdk.add_breadcrumb(
            message=f"{method} {endpoint}",
            category="api.request",
            level="info",
            data={
                "request_id": request_id,
                "constitutional_validation": "required"
            }
        )
        
    def handle_validation_error(
        self,
        error: Exception,
        validation_context: Dict[str, Any]
    ) -> None:
        """Handle and report validation errors with context"""
        if not SENTRY_AVAILABLE:
            return
            
        sentry_sdk.set_context("validation_error", {
            "error_type": type(error).__name__,
            "validation_context": validation_context,
            "constitutional_hash": self.constitutional_hash
        })
        
        # Check if it's a constitutional violation
        if isinstance(error, ConstitutionalViolationError):
            # Already reported by the error class
            pass
        else:
            # Capture with constitutional context
            sentry_sdk.capture_exception(
                error,
                tags={
                    "validation_error": True,
                    "service": self.service_name
                }
            )
            
    def create_performance_transaction(
        self,
        transaction_name: str,
        operation: str = "constitutional.validation"
    ):
        """Create a performance monitoring transaction"""
        if not SENTRY_AVAILABLE:
            return None
            
        transaction = sentry_sdk.start_transaction(
            op=operation,
            name=transaction_name
        )
        transaction.set_tag("service", self.service_name)
        transaction.set_tag("constitutional_hash", self.constitutional_hash)
        
        return transaction


# Global instance for easy access
sentry_config = ConstitutionalAISentryConfig()


# Utility functions for direct use
def init_constitutional_ai_sentry(environment: str = "development") -> None:
    """Initialize Sentry for Constitutional AI Service"""
    sentry_config.initialize(environment)
    

def track_validation(*args, **kwargs):
    """Track validation performance"""
    sentry_config.track_validation_performance(*args, **kwargs)
    

def report_violation(*args, **kwargs):
    """Report governance violations"""
    sentry_config.report_governance_violation(*args, **kwargs)