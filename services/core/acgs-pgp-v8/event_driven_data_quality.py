#!/usr/bin/env python3
"""
Event-Driven Data Quality Framework for ACGS-PGP v8

Extends the existing data quality framework with event-driven capabilities:
- NATS message broker integration
- Real-time quality monitoring
- Automated alert publishing
- Async/await patterns for non-blocking operations
- Event-driven quality threshold enforcement

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# Import existing data quality framework
from data_quality_framework import DataQualityAssessment, DataQualityMetrics

# NATS integration (placeholder - would use actual nats-py in production)
try:
    import nats
    from nats.aio.client import Client as NATS
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    print("⚠️ NATS not available - using mock implementation")

logger = logging.getLogger(__name__)

@dataclass
class QualityEvent:
    """Data quality event for message broker publishing."""
    event_type: str
    timestamp: str
    constitutional_hash: str
    service_id: str
    quality_score: float
    threshold: float
    violations: List[Dict[str, Any]]
    severity: str
    metadata: Dict[str, Any]

class EventDrivenDataQualityFramework:
    """Event-driven data quality framework with NATS integration."""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.nats_url = nats_url
        self.nats_client: Optional[NATS] = None
        self.quality_assessor = DataQualityAssessment()
        
        # Quality thresholds for event triggering
        self.quality_thresholds = {
            'critical': 0.6,   # Below this triggers critical alert
            'warning': 0.8,    # Below this triggers warning alert
            'target': 0.9      # Target quality score
        }
        
        # Event handlers registry
        self.event_handlers: Dict[str, List[Callable]] = {
            'quality_alert': [],
            'quality_degradation': [],
            'quality_improvement': [],
            'quality_violation': []
        }
        
        logger.info(f"Event-driven data quality framework initialized")
        logger.info(f"Constitutional hash: {self.constitutional_hash}")
        logger.info(f"NATS URL: {self.nats_url}")
    
    async def connect_to_nats(self) -> bool:
        """Connect to NATS message broker."""
        if not NATS_AVAILABLE:
            logger.warning("NATS not available - using mock mode")
            return False
        
        try:
            self.nats_client = await nats.connect(self.nats_url)
            logger.info(f"✅ Connected to NATS at {self.nats_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            return False
    
    async def disconnect_from_nats(self):
        """Disconnect from NATS message broker."""
        if self.nats_client:
            await self.nats_client.close()
            logger.info("Disconnected from NATS")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler for specific event types."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type} events")
    
    async def publish_event(self, event: QualityEvent):
        """Publish quality event to NATS message broker."""
        event_data = asdict(event)
        event_json = json.dumps(event_data, default=str)
        
        # Determine NATS subject based on event type and severity
        subject = f"acgs.quality.{event.event_type}.{event.severity.lower()}"
        
        if self.nats_client:
            try:
                await self.nats_client.publish(subject, event_json.encode())
                logger.info(f"📡 Published event to {subject}")
            except Exception as e:
                logger.error(f"❌ Failed to publish event: {e}")
        else:
            # Mock mode - just log the event
            logger.info(f"📡 [MOCK] Would publish to {subject}: {event.event_type}")
        
        # Trigger local event handlers
        await self._trigger_local_handlers(event)
    
    async def _trigger_local_handlers(self, event: QualityEvent):
        """Trigger local event handlers."""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"❌ Event handler failed: {e}")
    
    async def assess_quality_async(self, 
                                 df: pd.DataFrame,
                                 service_id: str = "unknown",
                                 target_column: str = None,
                                 timestamp_column: str = None) -> DataQualityMetrics:
        """Perform async data quality assessment with event publishing."""
        logger.info(f"Starting async quality assessment for {service_id}")
        
        # Perform quality assessment (non-blocking)
        metrics = await asyncio.get_event_loop().run_in_executor(
            None, 
            self.quality_assessor.comprehensive_assessment,
            df, target_column, timestamp_column
        )
        
        # Determine event type and severity based on quality score
        event_type, severity = self._determine_event_classification(metrics.overall_score)
        
        # Create quality event
        quality_event = QualityEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            constitutional_hash=self.constitutional_hash,
            service_id=service_id,
            quality_score=metrics.overall_score,
            threshold=self.quality_thresholds['target'],
            violations=self._extract_violations(metrics),
            severity=severity,
            metadata={
                'missing_rate': metrics.missing_value_rate,
                'outlier_rate': metrics.outlier_rate,
                'freshness_score': metrics.freshness_score,
                'record_count': len(df)
            }
        )
        
        # Publish event if significant
        if event_type != 'quality_normal':
            await self.publish_event(quality_event)
        
        logger.info(f"Quality assessment completed: {metrics.overall_score:.3f} ({severity})")
        return metrics
    
    def _determine_event_classification(self, quality_score: float) -> tuple[str, str]:
        """Determine event type and severity based on quality score."""
        if quality_score < self.quality_thresholds['critical']:
            return 'quality_alert', 'CRITICAL'
        elif quality_score < self.quality_thresholds['warning']:
            return 'quality_alert', 'WARNING'
        elif quality_score < self.quality_thresholds['target']:
            return 'quality_degradation', 'INFO'
        else:
            return 'quality_normal', 'INFO'
    
    def _extract_violations(self, metrics: DataQualityMetrics) -> List[Dict[str, Any]]:
        """Extract quality violations from metrics."""
        violations = []
        
        if metrics.missing_value_rate > 0.1:  # >10% missing values
            violations.append({
                'type': 'missing_values',
                'value': metrics.missing_value_rate,
                'threshold': 0.1,
                'description': 'High missing value rate detected'
            })
        
        if metrics.outlier_rate > 0.05:  # >5% outliers
            violations.append({
                'type': 'outliers',
                'value': metrics.outlier_rate,
                'threshold': 0.05,
                'description': 'High outlier rate detected'
            })
        
        if metrics.freshness_score < 0.8:  # Low data freshness
            violations.append({
                'type': 'freshness',
                'value': metrics.freshness_score,
                'threshold': 0.8,
                'description': 'Data freshness below threshold'
            })
        
        return violations
    
    async def start_real_time_monitoring(self, 
                                       data_stream: asyncio.Queue,
                                       service_id: str = "acgs_service",
                                       monitoring_interval: float = 5.0):
        """Start real-time data quality monitoring."""
        logger.info(f"🚀 Starting real-time quality monitoring for {service_id}")
        
        while True:
            try:
                # Wait for data with timeout
                data_batch = await asyncio.wait_for(
                    data_stream.get(), 
                    timeout=monitoring_interval
                )
                
                # Assess quality of the batch
                if isinstance(data_batch, pd.DataFrame) and not data_batch.empty:
                    await self.assess_quality_async(data_batch, service_id)
                
            except asyncio.TimeoutError:
                # No data received - continue monitoring
                logger.debug(f"No data received for {service_id} in {monitoring_interval}s")
                continue
            except Exception as e:
                logger.error(f"❌ Error in real-time monitoring: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying

# Example event handlers
async def handle_quality_alert(event: QualityEvent):
    """Handle quality alert events."""
    logger.warning(f"🚨 QUALITY ALERT: {event.service_id} score {event.quality_score:.3f}")
    
    if event.severity == 'CRITICAL':
        logger.critical(f"🔴 CRITICAL quality issue - immediate action required")
        # In production: trigger emergency response, notifications, etc.
    
async def handle_quality_degradation(event: QualityEvent):
    """Handle quality degradation events."""
    logger.info(f"📉 Quality degradation detected for {event.service_id}")
    # In production: trigger investigation, model retraining, etc.

# Example usage and testing
async def demo_event_driven_quality():
    """Demonstrate event-driven data quality monitoring."""
    
    # Initialize framework
    quality_framework = EventDrivenDataQualityFramework()
    
    # Register event handlers
    quality_framework.register_event_handler('quality_alert', handle_quality_alert)
    quality_framework.register_event_handler('quality_degradation', handle_quality_degradation)
    
    # Connect to NATS (optional)
    await quality_framework.connect_to_nats()
    
    # Generate sample data with varying quality
    print("📊 Generating sample data with varying quality...")
    
    # High quality data
    high_quality_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 1000),
        'feature2': np.random.normal(0, 1, 1000),
        'target': np.random.choice([0, 1], 1000),
        'timestamp': pd.date_range(start='2025-01-01', periods=1000, freq='1H')
    })
    
    # Low quality data (with issues)
    low_quality_data = high_quality_data.copy()
    # Introduce missing values
    low_quality_data.loc[0:200, 'feature1'] = np.nan
    # Introduce outliers
    low_quality_data.loc[800:900, 'feature2'] = np.random.normal(10, 1, 101)
    
    # Test quality assessment
    print("\n🔍 Testing high quality data...")
    await quality_framework.assess_quality_async(high_quality_data, "test_service_good")
    
    print("\n🔍 Testing low quality data...")
    await quality_framework.assess_quality_async(low_quality_data, "test_service_bad")
    
    # Cleanup
    await quality_framework.disconnect_from_nats()
    print("\n✅ Event-driven quality demo completed")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_event_driven_quality())
