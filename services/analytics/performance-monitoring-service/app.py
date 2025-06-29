#!/usr/bin/env python3
"""
ACGS Performance Monitoring Microservice

Focused microservice for system performance monitoring and analysis:
- RESTful API for performance metrics collection
- Real-time performance monitoring
- SLA compliance tracking
- Performance degradation alerts
- Integration with NATS message broker

Constitutional Hash: cdd01ef066bc6cf2
Port: 8012
"""

import asyncio
import logging
import json
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add core modules to path
sys.path.append('../../core/acgs-pgp-v8')
from nats_event_broker import NATSEventBroker, ACGSEvent

logger = logging.getLogger(__name__)

# Pydantic models for API
class PerformanceMetricsRequest(BaseModel):
    service_id: str = Field(..., description="Service identifier")
    metrics: Dict[str, float] = Field(..., description="Performance metrics")
    timestamp: Optional[str] = Field(None, description="Metric timestamp")
    constitutional_hash: str = Field(..., description="Constitutional hash for validation")

class PerformanceMetricsResponse(BaseModel):
    metric_id: str
    service_id: str
    sla_compliance: bool
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    constitutional_hash: str
    timestamp: str

class SLAConfigRequest(BaseModel):
    service_id: str = Field(..., description="Service identifier")
    sla_targets: Dict[str, float] = Field(..., description="SLA target values")
    constitutional_hash: str = Field(..., description="Constitutional hash for validation")

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    constitutional_hash: str
    timestamp: str

class PerformanceMonitoringMicroservice:
    """Performance Monitoring Microservice implementation."""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.service_name = "performance-monitoring-service"
        self.version = "v8.0.0"
        self.port = 8012
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="ACGS Performance Monitoring Service",
            description="Microservice for system performance monitoring and analysis",
            version=self.version,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.event_broker = NATSEventBroker()
        
        # Default SLA targets
        self.default_sla_targets = {
            'response_time_ms': 500,
            'availability_percent': 99.5,
            'error_rate_percent': 1.0,
            'throughput_rps': 100,
            'cpu_usage_percent': 80,
            'memory_usage_percent': 85
        }
        
        # Service-specific SLA configurations
        self.sla_configs: Dict[str, Dict[str, float]] = {}
        
        # Performance history storage
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Service metrics
        self.metrics = {
            'metrics_collected': 0,
            'sla_violations': 0,
            'alerts_generated': 0,
            'services_monitored': 0,
            'uptime_start': datetime.now().isoformat()
        }
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Performance Monitoring Microservice initialized on port {self.port}")
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthResponse(
                status="healthy",
                service=self.service_name,
                version=self.version,
                constitutional_hash=self.constitutional_hash,
                timestamp=datetime.now().isoformat()
            )
        
        @self.app.get("/metrics")
        async def get_service_metrics():
            """Get service metrics."""
            return {
                **self.metrics,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/sla/configure")
        async def configure_sla(request: SLAConfigRequest):
            """Configure SLA targets for a service."""
            
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403,
                    detail="Constitutional hash mismatch"
                )
            
            # Store SLA configuration
            self.sla_configs[request.service_id] = request.sla_targets
            
            logger.info(f"✅ SLA configured for {request.service_id}: {request.sla_targets}")
            
            return {
                "message": f"SLA configured for {request.service_id}",
                "targets": request.sla_targets,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/metrics/submit", response_model=PerformanceMetricsResponse)
        async def submit_metrics(
            request: PerformanceMetricsRequest,
            background_tasks: BackgroundTasks
        ):
            """Submit performance metrics for analysis."""
            
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403,
                    detail="Constitutional hash mismatch"
                )
            
            try:
                # Get SLA targets for service
                sla_targets = self.sla_configs.get(request.service_id, self.default_sla_targets)
                
                # Analyze metrics against SLA
                analysis_result = self._analyze_metrics(request.service_id, request.metrics, sla_targets)
                
                # Store metrics in history
                self._store_metrics_history(request.service_id, request.metrics, request.timestamp)
                
                # Update service metrics
                self.metrics['metrics_collected'] += 1
                if not analysis_result['sla_compliance']:
                    self.metrics['sla_violations'] += 1
                
                # Create response
                metric_id = f"perf-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                response = PerformanceMetricsResponse(
                    metric_id=metric_id,
                    service_id=request.service_id,
                    sla_compliance=analysis_result['sla_compliance'],
                    violations=analysis_result['violations'],
                    recommendations=analysis_result['recommendations'],
                    constitutional_hash=self.constitutional_hash,
                    timestamp=datetime.now().isoformat()
                )
                
                # Publish performance event in background
                background_tasks.add_task(
                    self._publish_performance_event,
                    metric_id,
                    request.service_id,
                    request.metrics,
                    analysis_result
                )
                
                logger.info(f"✅ Performance metrics submitted: {metric_id} "
                           f"(service: {request.service_id}, "
                           f"compliance: {analysis_result['sla_compliance']})")
                
                return response
                
            except Exception as e:
                logger.error(f"❌ Performance metrics submission failed: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Metrics submission failed: {str(e)}"
                )
        
        @self.app.get("/metrics/history/{service_id}")
        async def get_metrics_history(
            service_id: str,
            hours: int = 24,
            limit: int = 100
        ):
            """Get performance metrics history for a service."""
            
            if service_id not in self.performance_history:
                return {
                    "service_id": service_id,
                    "metrics": [],
                    "count": 0,
                    "constitutional_hash": self.constitutional_hash
                }
            
            # Filter by time range
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                metric for metric in self.performance_history[service_id]
                if datetime.fromisoformat(metric['timestamp']) > cutoff_time
            ]
            
            # Limit results
            recent_metrics = recent_metrics[-limit:]
            
            return {
                "service_id": service_id,
                "metrics": recent_metrics,
                "count": len(recent_metrics),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/sla/status")
        async def get_sla_status():
            """Get SLA compliance status for all services."""
            
            sla_status = {}
            
            for service_id in self.performance_history.keys():
                recent_metrics = self._get_recent_metrics(service_id, hours=1)
                
                if recent_metrics:
                    sla_targets = self.sla_configs.get(service_id, self.default_sla_targets)
                    compliance_rate = self._calculate_compliance_rate(recent_metrics, sla_targets)
                    
                    sla_status[service_id] = {
                        'compliance_rate': compliance_rate,
                        'recent_metrics_count': len(recent_metrics),
                        'sla_targets': sla_targets
                    }
            
            return {
                "sla_status": sla_status,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/monitor/start")
        async def start_monitoring(
            service_id: str,
            monitoring_interval: int = 60
        ):
            """Start continuous performance monitoring for a service."""
            
            # Start monitoring task
            asyncio.create_task(
                self._continuous_monitoring(service_id, monitoring_interval)
            )
            
            return {
                "message": f"Started performance monitoring for {service_id}",
                "interval_seconds": monitoring_interval,
                "constitutional_hash": self.constitutional_hash
            }
    
    def _analyze_metrics(self, 
                        service_id: str, 
                        metrics: Dict[str, float], 
                        sla_targets: Dict[str, float]) -> Dict[str, Any]:
        """Analyze metrics against SLA targets."""
        
        violations = []
        recommendations = []
        
        for metric_name, value in metrics.items():
            if metric_name not in sla_targets:
                continue
            
            target = sla_targets[metric_name]
            violation_detected = False
            severity = "LOW"
            
            # Check different types of metrics
            if metric_name in ['response_time_ms', 'error_rate_percent', 'cpu_usage_percent', 'memory_usage_percent']:
                # Lower is better
                if value > target:
                    violation_detected = True
                    severity = "CRITICAL" if value > target * 1.5 else "HIGH" if value > target * 1.2 else "MEDIUM"
            elif metric_name in ['availability_percent']:
                # Higher is better
                if value < target:
                    violation_detected = True
                    severity = "CRITICAL" if value < target * 0.95 else "HIGH" if value < target * 0.98 else "MEDIUM"
            elif metric_name in ['throughput_rps']:
                # Higher is better (but low throughput might not be critical)
                if value < target * 0.8:
                    violation_detected = True
                    severity = "MEDIUM" if value < target * 0.5 else "LOW"
            
            if violation_detected:
                violations.append({
                    "metric": metric_name,
                    "value": value,
                    "target": target,
                    "severity": severity,
                    "deviation_percent": abs((value - target) / target) * 100
                })
                
                # Generate recommendations
                if metric_name == 'response_time_ms':
                    recommendations.append(f"High response time ({value:.1f}ms). Consider caching, optimization, or scaling.")
                elif metric_name == 'error_rate_percent':
                    recommendations.append(f"High error rate ({value:.1f}%). Investigate error causes and improve error handling.")
                elif metric_name == 'cpu_usage_percent':
                    recommendations.append(f"High CPU usage ({value:.1f}%). Consider horizontal scaling or optimization.")
                elif metric_name == 'memory_usage_percent':
                    recommendations.append(f"High memory usage ({value:.1f}%). Check for memory leaks or increase resources.")
                elif metric_name == 'availability_percent':
                    recommendations.append(f"Low availability ({value:.1f}%). Improve redundancy and fault tolerance.")
                elif metric_name == 'throughput_rps':
                    recommendations.append(f"Low throughput ({value:.1f} RPS). Optimize processing or scale resources.")
        
        sla_compliance = len(violations) == 0
        
        return {
            'sla_compliance': sla_compliance,
            'violations': violations,
            'recommendations': recommendations
        }
    
    def _store_metrics_history(self, 
                             service_id: str, 
                             metrics: Dict[str, float], 
                             timestamp: Optional[str]):
        """Store metrics in history."""
        
        if service_id not in self.performance_history:
            self.performance_history[service_id] = []
            self.metrics['services_monitored'] += 1
        
        metric_entry = {
            'timestamp': timestamp or datetime.now().isoformat(),
            'metrics': metrics,
            'constitutional_hash': self.constitutional_hash
        }
        
        self.performance_history[service_id].append(metric_entry)
        
        # Keep only recent history (last 1000 entries)
        if len(self.performance_history[service_id]) > 1000:
            self.performance_history[service_id] = self.performance_history[service_id][-1000:]
    
    def _get_recent_metrics(self, service_id: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent metrics for a service."""
        
        if service_id not in self.performance_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in self.performance_history[service_id]
            if datetime.fromisoformat(metric['timestamp']) > cutoff_time
        ]
    
    def _calculate_compliance_rate(self, 
                                 metrics_history: List[Dict[str, Any]], 
                                 sla_targets: Dict[str, float]) -> float:
        """Calculate SLA compliance rate."""
        
        if not metrics_history:
            return 1.0
        
        compliant_count = 0
        
        for metric_entry in metrics_history:
            analysis = self._analyze_metrics("temp", metric_entry['metrics'], sla_targets)
            if analysis['sla_compliance']:
                compliant_count += 1
        
        return compliant_count / len(metrics_history)
    
    async def _publish_performance_event(self, 
                                       metric_id: str, 
                                       service_id: str,
                                       metrics: Dict[str, float],
                                       analysis_result: Dict[str, Any]):
        """Publish performance metrics event."""
        
        try:
            # Create performance event
            event = ACGSEvent(
                event_type="performance_metrics_submitted",
                timestamp=datetime.now().isoformat(),
                constitutional_hash=self.constitutional_hash,
                source_service=self.service_name,
                target_service=service_id,
                event_id=metric_id,
                payload={
                    "metrics": metrics,
                    "sla_compliance": analysis_result['sla_compliance'],
                    "violations": analysis_result['violations']
                },
                priority="CRITICAL" if not analysis_result['sla_compliance'] else "NORMAL"
            )
            
            # Publish event
            await self.event_broker.publish_event("acgs.performance.metrics", event)
            
            # If SLA violations, publish alert
            if not analysis_result['sla_compliance']:
                self.metrics['alerts_generated'] += 1
                
                alert_event = ACGSEvent(
                    event_type="performance_alert",
                    timestamp=datetime.now().isoformat(),
                    constitutional_hash=self.constitutional_hash,
                    source_service=self.service_name,
                    target_service=service_id,
                    event_id=f"alert-{metric_id}",
                    payload={
                        "service_id": service_id,
                        "violations": analysis_result['violations'],
                        "recommendations": analysis_result['recommendations']
                    },
                    priority="HIGH"
                )
                
                await self.event_broker.publish_event("acgs.performance.alert.high", alert_event)
            
        except Exception as e:
            logger.error(f"❌ Failed to publish performance event: {e}")
    
    async def _continuous_monitoring(self, service_id: str, interval_seconds: int):
        """Continuous performance monitoring for a service."""
        
        logger.info(f"🔍 Starting continuous performance monitoring for {service_id}")
        
        while True:
            try:
                # In production, would collect metrics from service
                # For demo, generate sample metrics
                sample_metrics = self._generate_sample_metrics()
                
                # Analyze metrics
                sla_targets = self.sla_configs.get(service_id, self.default_sla_targets)
                analysis_result = self._analyze_metrics(service_id, sample_metrics, sla_targets)
                
                # Store metrics
                self._store_metrics_history(service_id, sample_metrics, None)
                
                # Check for alerts
                if not analysis_result['sla_compliance']:
                    logger.warning(f"🚨 Performance alert for {service_id}: "
                                 f"{len(analysis_result['violations'])} violations")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Error in continuous performance monitoring: {e}")
                await asyncio.sleep(5)
    
    def _generate_sample_metrics(self) -> Dict[str, float]:
        """Generate sample performance metrics for monitoring demo."""
        
        return {
            'response_time_ms': np.random.lognormal(6, 0.5),
            'availability_percent': np.random.normal(99.7, 0.5),
            'error_rate_percent': np.random.exponential(0.5),
            'throughput_rps': np.random.normal(120, 20),
            'cpu_usage_percent': np.random.normal(60, 15),
            'memory_usage_percent': np.random.normal(70, 10)
        }
    
    async def startup(self):
        """Startup tasks for the microservice."""
        
        # Connect to event broker
        await self.event_broker.connect()
        
        logger.info(f"✅ Performance Monitoring Microservice started on port {self.port}")
    
    async def shutdown(self):
        """Shutdown tasks for the microservice."""
        
        # Disconnect from event broker
        await self.event_broker.disconnect()
        
        logger.info("✅ Performance Monitoring Microservice shutdown completed")

# Global service instance
service = PerformanceMonitoringMicroservice()

# FastAPI event handlers
@service.app.on_event("startup")
async def startup_event():
    await service.startup()

@service.app.on_event("shutdown")
async def shutdown_event():
    await service.shutdown()

# Main entry point
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the service
    uvicorn.run(
        "app:service.app",
        host="0.0.0.0",
        port=service.port,
        reload=False,
        log_level="info"
    )
