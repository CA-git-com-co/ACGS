#!/usr/bin/env python3
"""
ACGS-1 Health Metrics Exporter
Prometheus metrics exporter for health monitoring data
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path
import logging

from prometheus_client import start_http_server, Gauge, Counter, Histogram, Info
from prometheus_client.core import CollectorRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ACGSHealthMetricsExporter:
    """Prometheus metrics exporter for ACGS health monitoring."""
    
    def __init__(self, port: int = 9115):
        self.port = port
        self.registry = CollectorRegistry()
        
        # Service health metrics
        self.service_up = Gauge(
            'acgs_service_up',
            'Service availability (1=up, 0=down)',
            ['service_name'],
            registry=self.registry
        )
        
        self.service_response_time = Gauge(
            'acgs_service_response_time_seconds',
            'Service response time in seconds',
            ['service_name'],
            registry=self.registry
        )
        
        # Infrastructure health metrics
        self.infrastructure_up = Gauge(
            'acgs_infrastructure_up',
            'Infrastructure component availability (1=up, 0=down)',
            ['component'],
            registry=self.registry
        )
        
        self.postgresql_up = Gauge(
            'acgs_postgresql_up',
            'PostgreSQL database availability',
            registry=self.registry
        )
        
        self.redis_up = Gauge(
            'acgs_redis_up',
            'Redis cache availability',
            registry=self.registry
        )
        
        # Blockchain health metrics
        self.solana_network_up = Gauge(
            'acgs_solana_network_up',
            'Solana network connectivity',
            registry=self.registry
        )
        
        self.quantumagi_programs_healthy = Gauge(
            'acgs_quantumagi_programs_healthy',
            'Number of healthy Quantumagi programs',
            registry=self.registry
        )
        
        self.quantumagi_programs_total = Gauge(
            'acgs_quantumagi_programs_total',
            'Total number of Quantumagi programs',
            registry=self.registry
        )
        
        self.constitution_hash_valid = Gauge(
            'acgs_constitution_hash_valid',
            'Constitution hash validation status (1=valid, 0=invalid)',
            registry=self.registry
        )
        
        # System-wide metrics
        self.system_availability_percentage = Gauge(
            'acgs_system_availability_percentage',
            'Overall system availability percentage',
            registry=self.registry
        )
        
        self.average_response_time = Gauge(
            'acgs_average_response_time_seconds',
            'Average response time across all services',
            registry=self.registry
        )
        
        self.healthy_services_count = Gauge(
            'acgs_healthy_services_count',
            'Number of healthy services',
            registry=self.registry
        )
        
        self.total_services_count = Gauge(
            'acgs_total_services_count',
            'Total number of monitored services',
            registry=self.registry
        )
        
        # Alert metrics
        self.active_alerts = Gauge(
            'acgs_active_alerts_total',
            'Number of active alerts',
            ['severity'],
            registry=self.registry
        )
        
        # Constitutional compliance metrics
        self.constitutional_compliance_score = Gauge(
            'acgs_constitutional_compliance_score',
            'Constitutional compliance score (0-1)',
            registry=self.registry
        )
        
        # Governance workflow metrics
        self.policy_creation_failures = Counter(
            'acgs_policy_creation_failures_total',
            'Total policy creation failures',
            registry=self.registry
        )
        
        self.wina_oversight_failures = Counter(
            'acgs_wina_oversight_failures_total',
            'Total WINA oversight failures',
            registry=self.registry
        )
        
        self.audit_trail_failures = Counter(
            'acgs_audit_trail_failures_total',
            'Total audit trail failures',
            registry=self.registry
        )
        
        # Performance metrics
        self.concurrent_governance_actions = Gauge(
            'acgs_concurrent_governance_actions',
            'Current number of concurrent governance actions',
            registry=self.registry
        )
        
        # System info
        self.system_info = Info(
            'acgs_system_info',
            'ACGS system information',
            registry=self.registry
        )
        
        # Set system info
        self.system_info.info({
            'version': '1.0.0',
            'constitution_hash': 'cdd01ef066bc6cf2',
            'deployment': 'production',
            'blockchain': 'solana_devnet'
        })
    
    def update_metrics_from_health_report(self, health_report: Dict[str, Any]):
        """Update Prometheus metrics from health report."""
        try:
            services = health_report.get('services', {})
            
            # Update service metrics
            for service_name, service_data in services.items():
                status = service_data.get('status', 'unknown')
                response_time_ms = service_data.get('response_time_ms', 0)
                
                # Convert status to numeric
                up_value = 1 if status == 'healthy' else 0
                self.service_up.labels(service_name=service_name).set(up_value)
                
                # Convert response time to seconds
                response_time_seconds = response_time_ms / 1000.0
                self.service_response_time.labels(service_name=service_name).set(response_time_seconds)
                
                # Update infrastructure-specific metrics
                if service_name == 'postgresql':
                    self.postgresql_up.set(up_value)
                elif service_name == 'redis':
                    self.redis_up.set(up_value)
                elif service_name == 'solana_network':
                    self.solana_network_up.set(up_value)
                elif service_name == 'quantumagi_programs':
                    details = service_data.get('details', {})
                    healthy_programs = details.get('healthy_programs', 0)
                    total_programs = details.get('total_programs', 0)
                    
                    self.quantumagi_programs_healthy.set(healthy_programs)
                    self.quantumagi_programs_total.set(total_programs)
                elif service_name == 'constitution_hash':
                    self.constitution_hash_valid.set(up_value)
            
            # Update system-wide metrics
            healthy_services = health_report.get('healthy_services', 0)
            total_services = health_report.get('total_services', 0)
            avg_response_time_ms = health_report.get('average_response_time_ms', 0)
            
            self.healthy_services_count.set(healthy_services)
            self.total_services_count.set(total_services)
            self.average_response_time.set(avg_response_time_ms / 1000.0)
            
            # Calculate availability percentage
            availability = (healthy_services / total_services * 100) if total_services > 0 else 0
            self.system_availability_percentage.set(availability)
            
            # Set default values for governance metrics (would be updated by actual governance system)
            self.constitutional_compliance_score.set(0.95)  # Default 95%
            self.concurrent_governance_actions.set(0)  # Default 0
            
            logger.info(f"Updated metrics: {healthy_services}/{total_services} services healthy, "
                       f"{availability:.1f}% availability, {avg_response_time_ms:.1f}ms avg response time")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def load_latest_health_report(self) -> Dict[str, Any]:
        """Load the latest health report from disk."""
        try:
            reports_dir = Path("logs/health_reports")
            if not reports_dir.exists():
                return {}
            
            # Find the latest report file
            report_files = list(reports_dir.glob("health_report_*.json"))
            if not report_files:
                return {}
            
            latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_report, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading health report: {e}")
            return {}
    
    async def start_metrics_server(self):
        """Start the Prometheus metrics server."""
        try:
            # Start HTTP server for metrics
            start_http_server(self.port, registry=self.registry)
            logger.info(f"🚀 Health metrics exporter started on port {self.port}")
            logger.info(f"📊 Metrics available at http://localhost:{self.port}/metrics")
            
            # Continuously update metrics
            while True:
                health_report = self.load_latest_health_report()
                if health_report:
                    self.update_metrics_from_health_report(health_report)
                else:
                    logger.warning("No health report found, using default metrics")
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in metrics server: {e}")
    
    def run(self):
        """Run the metrics exporter."""
        asyncio.run(self.start_metrics_server())


if __name__ == "__main__":
    exporter = ACGSHealthMetricsExporter()
    try:
        exporter.run()
    except KeyboardInterrupt:
        logger.info("👋 Health metrics exporter stopped by user")
    except Exception as e:
        logger.error(f"❌ Health metrics exporter error: {e}")
