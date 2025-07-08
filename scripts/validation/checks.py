"""
ACGS Validation Checks
Constitutional Hash: cdd01ef066bc6cf2

Specific validation check implementations.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config, HTTPClient
from core.utils import validate_port_number, validate_url, ensure_constitutional_hash
from .validator import BaseValidationCheck

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalComplianceCheck(BaseValidationCheck):
    """Check constitutional compliance across all services."""
    
    def __init__(self):
        super().__init__(
            "constitutional_compliance",
            "Validate constitutional hash presence and compliance"
        )
    
    async def validate(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate constitutional compliance."""
        config = get_config()
        results = {
            "services_checked": 0,
            "compliant_services": 0,
            "non_compliant_services": [],
            "errors": [],
        }
        
        async with HTTPClient() as client:
            for service in config.get_all_services():
                results["services_checked"] += 1
                
                try:
                    # Check service health endpoint for constitutional hash
                    response = await client.get(service.health_url)
                    
                    if ensure_constitutional_hash(response, strict=False):
                        results["compliant_services"] += 1
                    else:
                        results["non_compliant_services"].append({
                            "service": service.name,
                            "url": service.health_url,
                            "issue": "Missing constitutional hash"
                        })
                        
                except Exception as e:
                    results["errors"].append({
                        "service": service.name,
                        "error": str(e)
                    })
        
        # Check if all accessible services are compliant
        accessible_services = results["services_checked"] - len(results["errors"])
        all_compliant = (
            accessible_services > 0 and 
            results["compliant_services"] == accessible_services
        )
        
        if all_compliant:
            message = f"All {accessible_services} accessible services are constitutionally compliant"
        else:
            non_compliant_count = len(results["non_compliant_services"])
            message = f"{non_compliant_count} of {accessible_services} services are not compliant"
        
        return all_compliant, message, results


class EnvironmentConfigCheck(BaseValidationCheck):
    """Check environment configuration."""
    
    def __init__(self):
        super().__init__(
            "environment_config",
            "Validate environment configuration and required variables"
        )
    
    async def validate(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate environment configuration."""
        required_vars = [
            "ACGS_ENVIRONMENT",
            "ACGS_DB_HOST",
            "ACGS_REDIS_HOST",
        ]
        
        optional_vars = [
            "ACGS_LOG_LEVEL",
            "ACGS_DEBUG",
            "ACGS_TARGET_P99_LATENCY_MS",
            "ACGS_TARGET_THROUGHPUT_RPS",
        ]
        
        results = {
            "required_present": 0,
            "required_missing": [],
            "optional_present": 0,
            "optional_missing": [],
            "invalid_values": [],
        }
        
        # Check required variables
        for var in required_vars:
            if os.getenv(var):
                results["required_present"] += 1
            else:
                results["required_missing"].append(var)
        
        # Check optional variables
        for var in optional_vars:
            if os.getenv(var):
                results["optional_present"] += 1
            else:
                results["optional_missing"].append(var)
        
        # Validate specific variable formats
        if db_port := os.getenv("ACGS_DB_PORT"):
            try:
                validate_port_number(db_port)
            except ValueError as e:
                results["invalid_values"].append({"var": "ACGS_DB_PORT", "error": str(e)})
        
        if redis_port := os.getenv("ACGS_REDIS_PORT"):
            try:
                validate_port_number(redis_port)
            except ValueError as e:
                results["invalid_values"].append({"var": "ACGS_REDIS_PORT", "error": str(e)})
        
        # Check environment value
        env = os.getenv("ACGS_ENVIRONMENT", "").lower()
        if env and env not in ["development", "staging", "production"]:
            results["invalid_values"].append({
                "var": "ACGS_ENVIRONMENT",
                "error": f"Invalid environment: {env}"
            })
        
        all_valid = (
            len(results["required_missing"]) == 0 and
            len(results["invalid_values"]) == 0
        )
        
        if all_valid:
            message = f"Environment configuration valid ({results['required_present']} required, {results['optional_present']} optional)"
        else:
            issues = len(results["required_missing"]) + len(results["invalid_values"])
            message = f"Environment configuration has {issues} issues"
        
        return all_valid, message, results


class InfrastructureIntegrationCheck(BaseValidationCheck):
    """Check infrastructure integration and connectivity."""
    
    def __init__(self):
        super().__init__(
            "infrastructure_integration",
            "Validate infrastructure connectivity and integration"
        )
    
    async def validate(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate infrastructure integration."""
        config = get_config()
        results = {
            "services_total": 0,
            "services_healthy": 0,
            "services_unhealthy": [],
            "database_accessible": False,
            "redis_accessible": False,
            "response_times": {},
        }
        
        async with HTTPClient() as client:
            # Check all services
            service_configs = config.get_all_services()
            results["services_total"] = len(service_configs)
            
            health_results = await client.health_check_multiple(service_configs)
            
            for result in health_results:
                if result.get("healthy", False):
                    results["services_healthy"] += 1
                    if "response_time_ms" in result:
                        results["response_times"][result["service"]] = result["response_time_ms"]
                else:
                    results["services_unhealthy"].append({
                        "service": result["service"],
                        "error": result.get("error", "Unknown error")
                    })
        
        # Calculate health percentage
        if results["services_total"] > 0:
            health_percentage = (results["services_healthy"] / results["services_total"]) * 100
        else:
            health_percentage = 0
        
        # Consider healthy if at least 70% of services are accessible
        is_healthy = health_percentage >= 70
        
        if is_healthy:
            message = f"Infrastructure healthy: {results['services_healthy']}/{results['services_total']} services ({health_percentage:.1f}%)"
        else:
            message = f"Infrastructure issues: only {results['services_healthy']}/{results['services_total']} services healthy ({health_percentage:.1f}%)"
        
        return is_healthy, message, results


class MonitoringCheck(BaseValidationCheck):
    """Check monitoring and observability systems."""
    
    def __init__(self):
        super().__init__(
            "monitoring",
            "Validate monitoring and observability systems"
        )
    
    async def validate(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate monitoring systems."""
        results = {
            "prometheus_accessible": False,
            "grafana_accessible": False,
            "metrics_endpoints": 0,
            "metrics_accessible": 0,
            "errors": [],
        }
        
        # Check Prometheus (default port 9090)
        prometheus_url = "http://localhost:9090/api/v1/targets"
        grafana_url = "http://localhost:3000/api/health"
        
        async with HTTPClient(validate_constitutional_compliance=False) as client:
            # Check Prometheus
            try:
                await client.get(prometheus_url)
                results["prometheus_accessible"] = True
            except Exception as e:
                results["errors"].append({"service": "prometheus", "error": str(e)})
            
            # Check Grafana
            try:
                await client.get(grafana_url)
                results["grafana_accessible"] = True
            except Exception as e:
                results["errors"].append({"service": "grafana", "error": str(e)})
            
            # Check metrics endpoints on services
            config = get_config()
            for service in config.get_all_services():
                results["metrics_endpoints"] += 1
                metrics_url = f"{service.base_url}/metrics"
                
                try:
                    await client.get(metrics_url)
                    results["metrics_accessible"] += 1
                except Exception as e:
                    results["errors"].append({
                        "service": f"{service.name}-metrics", 
                        "error": str(e)
                    })
        
        # Consider monitoring healthy if core systems are accessible
        monitoring_healthy = (
            results["prometheus_accessible"] or 
            results["grafana_accessible"] or
            results["metrics_accessible"] > 0
        )
        
        if monitoring_healthy:
            accessible_systems = []
            if results["prometheus_accessible"]:
                accessible_systems.append("Prometheus")
            if results["grafana_accessible"]:
                accessible_systems.append("Grafana")
            if results["metrics_accessible"] > 0:
                accessible_systems.append(f"{results['metrics_accessible']} service metrics")
            
            message = f"Monitoring systems accessible: {', '.join(accessible_systems)}"
        else:
            message = "No monitoring systems accessible"
        
        return monitoring_healthy, message, results


class PerformanceTargetsCheck(BaseValidationCheck):
    """Check performance targets and metrics."""
    
    def __init__(self):
        super().__init__(
            "performance_targets",
            "Validate performance targets and current metrics"
        )
    
    async def validate(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate performance targets."""
        config = get_config()
        results = {
            "target_p99_latency_ms": config.target_p99_latency_ms,
            "target_throughput_rps": config.target_throughput_rps,
            "measured_response_times": {},
            "slow_services": [],
            "fast_services": [],
            "avg_response_time_ms": 0,
        }
        
        async with HTTPClient() as client:
            # Measure response times for all services
            service_configs = config.get_all_services()
            health_results = await client.health_check_multiple(service_configs)
            
            response_times = []
            for result in health_results:
                service_name = result["service"]
                if result.get("healthy", False) and "response_time_ms" in result:
                    response_time = result["response_time_ms"]
                    results["measured_response_times"][service_name] = response_time
                    response_times.append(response_time)
                    
                    if response_time > config.target_p99_latency_ms:
                        results["slow_services"].append({
                            "service": service_name,
                            "response_time_ms": response_time,
                            "target_ms": config.target_p99_latency_ms
                        })
                    else:
                        results["fast_services"].append(service_name)
            
            # Calculate average response time
            if response_times:
                results["avg_response_time_ms"] = sum(response_times) / len(response_times)
        
        # Consider performance good if average is within target and no more than 20% of services are slow
        total_measured = len(results["measured_response_times"])
        slow_count = len(results["slow_services"])
        
        performance_good = (
            total_measured > 0 and
            results["avg_response_time_ms"] <= config.target_p99_latency_ms and
            (slow_count / total_measured) <= 0.2 if total_measured > 0 else True
        )
        
        if performance_good:
            message = f"Performance targets met: avg {results['avg_response_time_ms']:.1f}ms (target: {config.target_p99_latency_ms}ms)"
        else:
            message = f"Performance issues: avg {results['avg_response_time_ms']:.1f}ms, {slow_count} slow services"
        
        return performance_good, message, results


class PortNumbersCheck(BaseValidationCheck):
    """Check port number configurations and conflicts."""
    
    def __init__(self):
        super().__init__(
            "port_numbers",
            "Validate port number configurations and detect conflicts"
        )
    
    async def validate(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate port numbers."""
        config = get_config()
        results = {
            "services_checked": 0,
            "valid_ports": 0,
            "invalid_ports": [],
            "port_conflicts": [],
            "port_usage": {},
        }
        
        # Check service ports
        for service in config.get_all_services():
            results["services_checked"] += 1
            
            try:
                # Validate port number
                port = validate_port_number(service.port)
                results["valid_ports"] += 1
                
                # Track port usage for conflict detection
                if port in results["port_usage"]:
                    results["port_conflicts"].append({
                        "port": port,
                        "services": [results["port_usage"][port], service.name]
                    })
                else:
                    results["port_usage"][port] = service.name
                    
            except ValueError as e:
                results["invalid_ports"].append({
                    "service": service.name,
                    "port": service.port,
                    "error": str(e)
                })
        
        # Check database and Redis ports
        for db_type, db_config in [("database", config.database), ("redis", config.redis)]:
            try:
                port = validate_port_number(db_config.port)
                results["valid_ports"] += 1
                results["services_checked"] += 1
                
                if port in results["port_usage"]:
                    existing_service = results["port_usage"][port]
                    if existing_service != db_type:
                        results["port_conflicts"].append({
                            "port": port,
                            "services": [existing_service, db_type]
                        })
                else:
                    results["port_usage"][port] = db_type
                    
            except ValueError as e:
                results["invalid_ports"].append({
                    "service": db_type,
                    "port": db_config.port,
                    "error": str(e)
                })
                results["services_checked"] += 1
        
        # Check for conflicts with well-known ports
        well_known_ports = {22: "SSH", 80: "HTTP", 443: "HTTPS", 5432: "PostgreSQL", 6379: "Redis"}
        for port, service in results["port_usage"].items():
            if port in well_known_ports and service != well_known_ports[port].lower():
                results["port_conflicts"].append({
                    "port": port,
                    "services": [well_known_ports[port], service],
                    "type": "well_known_conflict"
                })
        
        all_valid = (
            len(results["invalid_ports"]) == 0 and
            len(results["port_conflicts"]) == 0
        )
        
        if all_valid:
            message = f"All {results['valid_ports']} port configurations are valid"
        else:
            issues = len(results["invalid_ports"]) + len(results["port_conflicts"])
            message = f"Port configuration has {issues} issues"
        
        return all_valid, message, results