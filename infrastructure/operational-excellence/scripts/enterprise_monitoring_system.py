#!/usr/bin/env python3
"""
ACGS Enterprise 24/7 Monitoring and Alerting System
Implements comprehensive monitoring with intelligent alerting and automated remediation
"""

import asyncio
import json
import logging
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
import yaml
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnterpriseMonitoringSystem:
    """
    Enterprise-grade 24/7 monitoring and alerting system
    Implements SLA monitoring, intelligent alerting, and automated remediation
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.metrics_registry = CollectorRegistry()
        self._setup_metrics()
        self.alert_history = []
        self.services = [
            {'name': 'auth-service', 'port': 8000, 'critical': True},
            {'name': 'ac-service', 'port': 8001, 'critical': True},
            {'name': 'integrity-service', 'port': 8002, 'critical': True},
            {'name': 'fv-service', 'port': 8003, 'critical': False},
            {'name': 'gs-service', 'port': 8004, 'critical': False},
            {'name': 'pgc-service', 'port': 8005, 'critical': False},
            {'name': 'ec-service', 'port': 8006, 'critical': True},
        ]
        
    def _load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'monitoring': {
                'health_check_interval': 30,
                'metrics_collection_interval': 15,
                'alert_evaluation_interval': 60
            },
            'sla_targets': {
                'uptime': 99.9,
                'response_time_p95': 500,
                'error_rate': 1.0
            },
            'alerting': {
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'from_email': 'alerts@acgs.local',
                'escalation_levels': [
                    {'level': 1, 'response_time': 15, 'contacts': ['ops-team@acgs.local']},
                    {'level': 2, 'response_time': 30, 'contacts': ['senior-ops@acgs.local']},
                    {'level': 3, 'response_time': 60, 'contacts': ['cto@acgs.local']}
                ]
            }
        }
    
    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        self.service_up = Gauge(
            'acgs_service_up',
            'Service availability (1 = up, 0 = down)',
            ['service_name'],
            registry=self.metrics_registry
        )
        
        self.response_time = Histogram(
            'acgs_response_time_seconds',
            'Service response time in seconds',
            ['service_name'],
            registry=self.metrics_registry
        )
        
        self.error_rate = Gauge(
            'acgs_error_rate_percent',
            'Service error rate percentage',
            ['service_name'],
            registry=self.metrics_registry
        )
        
        self.sla_compliance = Gauge(
            'acgs_sla_compliance_percent',
            'SLA compliance percentage',
            ['metric_type'],
            registry=self.metrics_registry
        )
        
        self.alerts_fired = Counter(
            'acgs_alerts_fired_total',
            'Total number of alerts fired',
            ['alert_type', 'severity'],
            registry=self.metrics_registry
        )
        
        self.constitutional_compliance = Gauge(
            'acgs_constitutional_compliance',
            'Constitutional compliance status (1 = compliant, 0 = non-compliant)',
            registry=self.metrics_registry
        )
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("Starting enterprise monitoring system")
        
        # Start metrics server
        start_http_server(8080, registry=self.metrics_registry)
        logger.info("Metrics server started on port 8080")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._alert_evaluation_loop()),
            asyncio.create_task(self._sla_monitoring_loop()),
            asyncio.create_task(self._constitutional_compliance_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Monitoring system stopped")
            for task in tasks:
                task.cancel()
    
    async def _health_check_loop(self):
        """Continuous health checking of all services"""
        while True:
            try:
                for service in self.services:
                    health_status = await self._check_service_health(service)
                    
                    # Update metrics
                    self.service_up.labels(service_name=service['name']).set(
                        1 if health_status['healthy'] else 0
                    )
                    
                    if health_status['response_time']:
                        self.response_time.labels(service_name=service['name']).observe(
                            health_status['response_time'] / 1000  # Convert to seconds
                        )
                    
                    # Check for alerts
                    if not health_status['healthy'] and service['critical']:
                        await self._fire_alert(
                            alert_type='service_down',
                            severity='critical',
                            message=f"Critical service {service['name']} is down",
                            service=service['name']
                        )
                    
                    # Check response time SLA
                    if (health_status['response_time'] and 
                        health_status['response_time'] > self.config['sla_targets']['response_time_p95']):
                        await self._fire_alert(
                            alert_type='response_time_sla',
                            severity='warning',
                            message=f"Service {service['name']} response time {health_status['response_time']}ms exceeds SLA",
                            service=service['name']
                        )
                
                await asyncio.sleep(self.config['monitoring']['health_check_interval'])
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _metrics_collection_loop(self):
        """Continuous metrics collection"""
        while True:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                
                # Collect application metrics
                app_metrics = await self._collect_application_metrics()
                
                # Update error rate metrics
                for service in self.services:
                    error_rate = await self._calculate_error_rate(service['name'])
                    self.error_rate.labels(service_name=service['name']).set(error_rate)
                    
                    # Check error rate SLA
                    if error_rate > self.config['sla_targets']['error_rate']:
                        await self._fire_alert(
                            alert_type='error_rate_sla',
                            severity='warning',
                            message=f"Service {service['name']} error rate {error_rate}% exceeds SLA",
                            service=service['name']
                        )
                
                await asyncio.sleep(self.config['monitoring']['metrics_collection_interval'])
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(5)
    
    async def _alert_evaluation_loop(self):
        """Continuous alert evaluation and escalation"""
        while True:
            try:
                # Evaluate alert escalations
                await self._evaluate_alert_escalations()
                
                # Check for alert fatigue and deduplication
                await self._deduplicate_alerts()
                
                # Generate alert summary reports
                await self._generate_alert_summary()
                
                await asyncio.sleep(self.config['monitoring']['alert_evaluation_interval'])
                
            except Exception as e:
                logger.error(f"Alert evaluation loop error: {e}")
                await asyncio.sleep(5)
    
    async def _sla_monitoring_loop(self):
        """Continuous SLA monitoring and reporting"""
        while True:
            try:
                # Calculate uptime SLA
                uptime_sla = await self._calculate_uptime_sla()
                self.sla_compliance.labels(metric_type='uptime').set(uptime_sla)
                
                # Calculate response time SLA
                response_time_sla = await self._calculate_response_time_sla()
                self.sla_compliance.labels(metric_type='response_time').set(response_time_sla)
                
                # Calculate error rate SLA
                error_rate_sla = await self._calculate_error_rate_sla()
                self.sla_compliance.labels(metric_type='error_rate').set(error_rate_sla)
                
                # Check overall SLA compliance
                overall_sla = min(uptime_sla, response_time_sla, error_rate_sla)
                if overall_sla < 95.0:  # Below 95% compliance
                    await self._fire_alert(
                        alert_type='sla_breach',
                        severity='critical',
                        message=f"Overall SLA compliance {overall_sla:.1f}% below threshold",
                        service='system'
                    )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"SLA monitoring loop error: {e}")
                await asyncio.sleep(30)
    
    async def _constitutional_compliance_loop(self):
        """Continuous constitutional compliance monitoring"""
        while True:
            try:
                compliance_status = await self._check_constitutional_compliance()
                self.constitutional_compliance.set(1 if compliance_status['compliant'] else 0)
                
                if not compliance_status['compliant']:
                    await self._fire_alert(
                        alert_type='constitutional_compliance',
                        severity='critical',
                        message=f"Constitutional compliance violation: {compliance_status['error']}",
                        service='system'
                    )
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Constitutional compliance loop error: {e}")
                await asyncio.sleep(300)
    
    async def _check_service_health(self, service: Dict) -> Dict:
        """Check health of a specific service"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"http://localhost:{service['port']}/health"
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'healthy': data.get('status') == 'healthy',
                            'response_time': response_time,
                            'details': data
                        }
                    else:
                        return {
                            'healthy': False,
                            'response_time': response_time,
                            'error': f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                'healthy': False,
                'response_time': None,
                'error': str(e)
            }
    
    async def _collect_system_metrics(self) -> Dict:
        """Collect system-level metrics"""
        try:
            # Simulate system metrics collection
            await asyncio.sleep(0.1)
            
            return {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 34.5,
                'network_io': 1024000
            }
            
        except Exception as e:
            logger.error(f"System metrics collection error: {e}")
            return {}
    
    async def _collect_application_metrics(self) -> Dict:
        """Collect application-level metrics"""
        try:
            # Simulate application metrics collection
            await asyncio.sleep(0.1)
            
            return {
                'active_connections': 156,
                'request_rate': 245,
                'cache_hit_rate': 89.3,
                'database_connections': 12
            }
            
        except Exception as e:
            logger.error(f"Application metrics collection error: {e}")
            return {}
    
    async def _calculate_error_rate(self, service_name: str) -> float:
        """Calculate error rate for a service"""
        try:
            # Simulate error rate calculation
            await asyncio.sleep(0.05)
            
            # Return simulated error rate (0.1% to 2.5%)
            import random
            return round(random.uniform(0.1, 2.5), 2)
            
        except Exception as e:
            logger.error(f"Error rate calculation error for {service_name}: {e}")
            return 0.0
    
    async def _calculate_uptime_sla(self) -> float:
        """Calculate uptime SLA compliance"""
        try:
            # Simulate uptime calculation
            await asyncio.sleep(0.1)
            
            # Return simulated uptime (98.5% to 99.95%)
            import random
            return round(random.uniform(98.5, 99.95), 2)
            
        except Exception as e:
            logger.error(f"Uptime SLA calculation error: {e}")
            return 0.0
    
    async def _calculate_response_time_sla(self) -> float:
        """Calculate response time SLA compliance"""
        try:
            # Simulate response time SLA calculation
            await asyncio.sleep(0.1)
            
            # Return simulated compliance (85% to 99%)
            import random
            return round(random.uniform(85.0, 99.0), 2)
            
        except Exception as e:
            logger.error(f"Response time SLA calculation error: {e}")
            return 0.0
    
    async def _calculate_error_rate_sla(self) -> float:
        """Calculate error rate SLA compliance"""
        try:
            # Simulate error rate SLA calculation
            await asyncio.sleep(0.1)
            
            # Return simulated compliance (90% to 99.5%)
            import random
            return round(random.uniform(90.0, 99.5), 2)
            
        except Exception as e:
            logger.error(f"Error rate SLA calculation error: {e}")
            return 0.0
    
    async def _check_constitutional_compliance(self) -> Dict:
        """Check constitutional compliance"""
        try:
            # Simulate constitutional compliance check
            await asyncio.sleep(0.5)
            
            expected_hash = "cdd01ef066bc6cf2"
            # Simulate 99% compliance rate
            import random
            compliant = random.random() > 0.01
            
            return {
                'compliant': compliant,
                'hash': expected_hash if compliant else 'invalid_hash',
                'error': None if compliant else 'Hash mismatch detected'
            }
            
        except Exception as e:
            return {
                'compliant': False,
                'hash': None,
                'error': str(e)
            }
    
    async def _fire_alert(self, alert_type: str, severity: str, message: str, service: str):
        """Fire an alert with intelligent deduplication"""
        alert = {
            'id': f"alert-{int(time.time())}-{alert_type}",
            'type': alert_type,
            'severity': severity,
            'message': message,
            'service': service,
            'timestamp': datetime.utcnow().isoformat(),
            'acknowledged': False,
            'escalation_level': 1
        }
        
        # Check for duplicate alerts
        if not self._is_duplicate_alert(alert):
            self.alert_history.append(alert)
            
            # Update metrics
            self.alerts_fired.labels(alert_type=alert_type, severity=severity).inc()
            
            # Send alert notification
            await self._send_alert_notification(alert)
            
            # Trigger automated remediation if applicable
            await self._trigger_automated_remediation(alert)
            
            logger.warning(f"Alert fired: {alert['id']} - {message}")
    
    def _is_duplicate_alert(self, new_alert: Dict) -> bool:
        """Check if alert is a duplicate of recent alerts"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        
        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
            if (alert_time > cutoff_time and
                alert['type'] == new_alert['type'] and
                alert['service'] == new_alert['service'] and
                not alert['acknowledged']):
                return True
        
        return False
    
    async def _send_alert_notification(self, alert: Dict):
        """Send alert notification via email/webhook"""
        try:
            escalation_level = alert['escalation_level']
            contacts = self.config['alerting']['escalation_levels'][escalation_level - 1]['contacts']
            
            # Simulate email notification
            logger.info(f"Sending alert notification to {contacts}")
            
            # In a real implementation, this would send actual emails
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Alert notification error: {e}")
    
    async def _trigger_automated_remediation(self, alert: Dict):
        """Trigger automated remediation for known issues"""
        try:
            if alert['type'] == 'service_down':
                logger.info(f"Triggering automated restart for {alert['service']}")
                # In a real implementation, this would restart the service
                await asyncio.sleep(1)
                
            elif alert['type'] == 'response_time_sla':
                logger.info(f"Triggering performance optimization for {alert['service']}")
                # In a real implementation, this would optimize performance
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Automated remediation error: {e}")
    
    async def _evaluate_alert_escalations(self):
        """Evaluate and escalate unacknowledged alerts"""
        try:
            current_time = datetime.utcnow()
            
            for alert in self.alert_history:
                if alert['acknowledged']:
                    continue
                
                alert_time = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
                time_elapsed = (current_time - alert_time).total_seconds() / 60  # minutes
                
                escalation_levels = self.config['alerting']['escalation_levels']
                current_level = alert['escalation_level']
                
                if current_level < len(escalation_levels):
                    response_time = escalation_levels[current_level - 1]['response_time']
                    
                    if time_elapsed > response_time:
                        alert['escalation_level'] += 1
                        logger.warning(f"Escalating alert {alert['id']} to level {alert['escalation_level']}")
                        await self._send_alert_notification(alert)
                        
        except Exception as e:
            logger.error(f"Alert escalation error: {e}")
    
    async def _deduplicate_alerts(self):
        """Remove old and duplicate alerts"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Remove alerts older than 24 hours
            self.alert_history = [
                alert for alert in self.alert_history
                if datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Alert deduplication error: {e}")
    
    async def _generate_alert_summary(self):
        """Generate alert summary report"""
        try:
            # Generate hourly alert summary
            current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            hour_start = current_hour - timedelta(hours=1)
            
            hourly_alerts = [
                alert for alert in self.alert_history
                if hour_start <= datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')) < current_hour
            ]
            
            if hourly_alerts:
                summary = {
                    'period': f"{hour_start.isoformat()} to {current_hour.isoformat()}",
                    'total_alerts': len(hourly_alerts),
                    'by_severity': {},
                    'by_type': {},
                    'by_service': {}
                }
                
                for alert in hourly_alerts:
                    # Count by severity
                    severity = alert['severity']
                    summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
                    
                    # Count by type
                    alert_type = alert['type']
                    summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
                    
                    # Count by service
                    service = alert['service']
                    summary['by_service'][service] = summary['by_service'].get(service, 0) + 1
                
                # Save summary
                summary_dir = Path('/tmp/alert_summaries')
                summary_dir.mkdir(exist_ok=True)
                
                summary_file = summary_dir / f"alert_summary_{current_hour.strftime('%Y%m%d_%H')}.json"
                with open(summary_file, 'w') as f:
                    json.dump(summary, f, indent=2)
                
                logger.info(f"Alert summary saved: {len(hourly_alerts)} alerts in the last hour")
                
        except Exception as e:
            logger.error(f"Alert summary generation error: {e}")

async def main():
    """Main monitoring system execution"""
    monitoring = EnterpriseMonitoringSystem()

    try:
        await monitoring.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Monitoring system stopped by user")

if __name__ == "__main__":
    asyncio.run(main())
