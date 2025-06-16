#!/usr/bin/env python3
"""
ACGS-1 Health Check Exporter for Prometheus
Monitors all 8 ACGS services and exports metrics in Prometheus format
"""

import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ACGS Services Configuration
ACGS_SERVICES = {
    'auth': {'port': 8000, 'name': 'Authentication Service'},
    'ac': {'port': 8001, 'name': 'Constitutional AI Service'},
    'integrity': {'port': 8002, 'name': 'Integrity Service'},
    'fv': {'port': 8003, 'name': 'Formal Verification Service'},
    'gs': {'port': 8004, 'name': 'Governance Synthesis Service'},
    'pgc': {'port': 8005, 'name': 'Policy Governance Control Service'},
    'ec': {'port': 8006, 'name': 'Evolutionary Computation Service'},
    'self_evolving_ai': {'port': 8007, 'name': 'Self-Evolving AI Service'}
}

class HealthMetrics:
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def update_service_health(self, service, is_healthy, response_time, status_code):
        with self.lock:
            self.metrics[service] = {
                'healthy': 1 if is_healthy else 0,
                'response_time': response_time,
                'status_code': status_code,
                'last_check': time.time()
            }
    
    def get_prometheus_metrics(self):
        with self.lock:
            metrics = []
            
            # Service health metrics
            for service, data in self.metrics.items():
                metrics.append(f'acgs_service_up{{service="{service}"}} {data["healthy"]}')
                metrics.append(f'acgs_service_response_time_seconds{{service="{service}"}} {data["response_time"]}')
                metrics.append(f'acgs_service_status_code{{service="{service}"}} {data["status_code"]}')
                metrics.append(f'acgs_service_last_check_timestamp{{service="{service}"}} {data["last_check"]}')
            
            # Overall system health
            total_services = len(ACGS_SERVICES)
            healthy_services = sum(1 for data in self.metrics.values() if data["healthy"] == 1)
            system_health = healthy_services / total_services if total_services > 0 else 0

            metrics.append(f'acgs_system_health_ratio {system_health}')
            metrics.append(f'acgs_total_services {total_services}')
            metrics.append(f'acgs_healthy_services {healthy_services}')

            # SLA Metrics
            uptime_sla = 1.0 if system_health >= 0.995 else 0.0
            response_time_sla = 1.0 if all(data["response_time"] < 0.5 for data in self.metrics.values() if data["healthy"]) else 0.0

            metrics.append(f'acgs_sla_uptime_compliance {uptime_sla}')
            metrics.append(f'acgs_sla_response_time_compliance {response_time_sla}')
            metrics.append(f'acgs_sla_uptime_target 0.995')
            metrics.append(f'acgs_sla_response_time_target 0.5')

            # Performance metrics
            avg_response_time = sum(data["response_time"] for data in self.metrics.values()) / len(self.metrics) if self.metrics else 0
            max_response_time = max((data["response_time"] for data in self.metrics.values()), default=0)

            metrics.append(f'acgs_avg_response_time_seconds {avg_response_time}')
            metrics.append(f'acgs_max_response_time_seconds {max_response_time}')

            return '\n'.join(metrics) + '\n'

class HealthChecker:
    def __init__(self, metrics):
        self.metrics = metrics
        self.running = True
    
    def check_service_health(self, service, config):
        try:
            url = f"http://localhost:{config['port']}/health"
            start_time = time.time()
            
            response = requests.get(url, timeout=5)
            response_time = time.time() - start_time
            
            is_healthy = response.status_code == 200
            self.metrics.update_service_health(service, is_healthy, response_time, response.status_code)
            
            logger.debug(f"Service {service}: {'✅' if is_healthy else '❌'} ({response.status_code}) - {response_time:.3f}s")
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.metrics.update_service_health(service, False, response_time, 0)
            logger.debug(f"Service {service}: ❌ Connection failed - {str(e)}")
    
    def run_health_checks(self):
        while self.running:
            logger.info("Running health checks for all ACGS services...")
            
            threads = []
            for service, config in ACGS_SERVICES.items():
                thread = threading.Thread(target=self.check_service_health, args=(service, config))
                thread.start()
                threads.append(thread)
            
            # Wait for all checks to complete
            for thread in threads:
                thread.join()
            
            # Log summary
            healthy_count = sum(1 for data in self.metrics.metrics.values() if data["healthy"] == 1)
            logger.info(f"Health check complete: {healthy_count}/{len(ACGS_SERVICES)} services healthy")
            
            time.sleep(10)  # Check every 10 seconds
    
    def stop(self):
        self.running = False

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, metrics, *args, **kwargs):
        self.metrics = metrics
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            metrics_output = self.metrics.get_prometheus_metrics()
            self.wfile.write(metrics_output.encode('utf-8'))
        
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'services_monitored': len(ACGS_SERVICES),
                'last_check': max((data.get('last_check', 0) for data in self.metrics.metrics.values()), default=0)
            }
            self.wfile.write(json.dumps(health_data).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP logging
        pass

def main():
    # Initialize metrics and health checker
    metrics = HealthMetrics()
    health_checker = HealthChecker(metrics)
    
    # Start health checking in background thread
    health_thread = threading.Thread(target=health_checker.run_health_checks)
    health_thread.daemon = True
    health_thread.start()
    
    # Create HTTP server for metrics endpoint
    def handler(*args, **kwargs):
        return MetricsHandler(metrics, *args, **kwargs)
    
    server = HTTPServer(('localhost', 9115), handler)
    
    logger.info("ACGS Health Check Exporter started on http://localhost:9115")
    logger.info("Metrics available at: http://localhost:9115/metrics")
    logger.info("Health status at: http://localhost:9115/health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down health check exporter...")
        health_checker.stop()
        server.shutdown()

if __name__ == '__main__':
    main()
