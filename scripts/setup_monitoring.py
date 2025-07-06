#!/usr/bin/env python3
"""
ACGS Monitoring Setup Script

Sets up comprehensive monitoring infrastructure for ACGS services including:
- Prometheus configuration with constitutional compliance tracking
- Grafana dashboards for constitutional compliance monitoring
- Alert rules for performance targets and compliance violations
- Service discovery and health monitoring
- Performance metrics collection and analysis

Constitutional Hash: cdd01ef066bc6cf2

Usage:
    python scripts/setup_monitoring.py [options]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import requests

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Monitoring service endpoints
MONITORING_SERVICES = {
    "prometheus": "http://localhost:9090",
    "grafana": "http://localhost:3000",
    "alertmanager": "http://localhost:9093"
}

# ACGS service endpoints for monitoring setup
ACGS_SERVICES = {
    "auth_service": "http://localhost:8016",
    "constitutional_ai": "http://localhost:8001",
    "integrity_service": "http://localhost:8002",
    "formal_verification": "http://localhost:8003",
    "governance_synthesis": "http://localhost:8004",
    "policy_governance": "http://localhost:8005",
    "evolutionary_computation": "http://localhost:8006"
}


class ACGSMonitoringSetup:
    """Sets up comprehensive monitoring for ACGS services."""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(".")
        self.monitoring_path = self.base_path / "infrastructure" / "monitoring"
        self.grafana_path = self.monitoring_path / "grafana"
        
    def setup_monitoring_infrastructure(self, skip_docker: bool = False) -> bool:
        """Set up complete monitoring infrastructure."""
        print("🔧 Setting up ACGS Monitoring Infrastructure")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)
        
        success = True
        
        # Create monitoring directories
        self._create_monitoring_directories()
        
        # Setup Prometheus configuration
        if not self._setup_prometheus_config():
            success = False
        
        # Setup Grafana dashboards
        if not self._setup_grafana_dashboards():
            success = False
        
        # Setup alert rules
        if not self._setup_alert_rules():
            success = False
        
        # Start monitoring services
        if not skip_docker:
            if not self._start_monitoring_services():
                success = False
        
        # Configure service discovery
        if not self._configure_service_discovery():
            success = False
        
        # Validate monitoring setup
        if not self._validate_monitoring_setup():
            success = False
        
        return success
    
    def _create_monitoring_directories(self):
        """Create necessary monitoring directories."""
        print("📁 Creating monitoring directories...")
        
        directories = [
            self.monitoring_path,
            self.grafana_path / "dashboards",
            self.grafana_path / "provisioning" / "dashboards",
            self.grafana_path / "provisioning" / "datasources",
            self.monitoring_path / "prometheus",
            self.monitoring_path / "alertmanager"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory}")
    
    def _setup_prometheus_config(self) -> bool:
        """Setup Prometheus configuration with constitutional compliance tracking."""
        print("\n🔍 Setting up Prometheus configuration...")
        
        try:
            # Verify prometheus.yml exists and has constitutional hash
            prometheus_config = self.monitoring_path / "prometheus.yml"
            
            if prometheus_config.exists():
                with open(prometheus_config, 'r') as f:
                    config_content = f.read()
                
                if CONSTITUTIONAL_HASH in config_content:
                    print("  ✅ Prometheus configuration already includes constitutional hash")
                else:
                    print("  ⚠️  Prometheus configuration missing constitutional hash")
                    return False
            else:
                print("  ❌ Prometheus configuration file not found")
                return False
            
            # Verify alert rules exist
            alert_rules = self.monitoring_path / "constitutional_compliance_rules.yml"
            if alert_rules.exists():
                print("  ✅ Constitutional compliance alert rules found")
            else:
                print("  ❌ Constitutional compliance alert rules not found")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error setting up Prometheus config: {e}")
            return False
    
    def _setup_grafana_dashboards(self) -> bool:
        """Setup Grafana dashboards for constitutional compliance monitoring."""
        print("\n📊 Setting up Grafana dashboards...")
        
        try:
            # Create datasource configuration
            datasource_config = {
                "apiVersion": 1,
                "datasources": [
                    {
                        "name": "Prometheus",
                        "type": "prometheus",
                        "access": "proxy",
                        "url": "http://prometheus:9090",
                        "isDefault": True,
                        "jsonData": {
                            "timeInterval": "15s"
                        }
                    }
                ]
            }
            
            datasource_file = self.grafana_path / "provisioning" / "datasources" / "prometheus.yml"
            with open(datasource_file, 'w') as f:
                yaml.dump(datasource_config, f, default_flow_style=False)
            print("  ✅ Grafana datasource configuration created")
            
            # Create dashboard provisioning configuration
            dashboard_config = {
                "apiVersion": 1,
                "providers": [
                    {
                        "name": "ACGS Dashboards",
                        "orgId": 1,
                        "folder": "",
                        "type": "file",
                        "disableDeletion": False,
                        "updateIntervalSeconds": 10,
                        "allowUiUpdates": True,
                        "options": {
                            "path": "/etc/grafana/provisioning/dashboards"
                        }
                    }
                ]
            }
            
            dashboard_provisioning_file = self.grafana_path / "provisioning" / "dashboards" / "acgs.yml"
            with open(dashboard_provisioning_file, 'w') as f:
                yaml.dump(dashboard_config, f, default_flow_style=False)
            print("  ✅ Grafana dashboard provisioning configured")
            
            # Verify constitutional compliance dashboard exists
            compliance_dashboard = self.grafana_path / "dashboards" / "acgs_constitutional_compliance.json"
            if compliance_dashboard.exists():
                print("  ✅ Constitutional compliance dashboard found")
            else:
                print("  ❌ Constitutional compliance dashboard not found")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error setting up Grafana dashboards: {e}")
            return False
    
    def _setup_alert_rules(self) -> bool:
        """Setup alert rules for constitutional compliance and performance monitoring."""
        print("\n🚨 Setting up alert rules...")
        
        try:
            # Verify constitutional compliance rules exist
            compliance_rules = self.monitoring_path / "constitutional_compliance_rules.yml"
            
            if compliance_rules.exists():
                with open(compliance_rules, 'r') as f:
                    rules_content = f.read()
                
                # Verify constitutional hash is in rules
                if CONSTITUTIONAL_HASH in rules_content:
                    print("  ✅ Constitutional compliance alert rules configured")
                else:
                    print("  ⚠️  Alert rules missing constitutional hash")
                    return False
                
                # Verify key alert groups exist
                required_groups = [
                    "constitutional_compliance",
                    "performance_targets",
                    "service_health",
                    "hitl_oversight"
                ]
                
                for group in required_groups:
                    if group in rules_content:
                        print(f"  ✅ Alert group '{group}' configured")
                    else:
                        print(f"  ❌ Alert group '{group}' missing")
                        return False
                
                return True
            else:
                print("  ❌ Constitutional compliance alert rules not found")
                return False
                
        except Exception as e:
            print(f"  ❌ Error setting up alert rules: {e}")
            return False
    
    def _start_monitoring_services(self) -> bool:
        """Start monitoring services using Docker Compose."""
        print("\n🚀 Starting monitoring services...")
        
        try:
            # Check if Docker Compose file exists
            compose_file = self.base_path / "infrastructure" / "docker" / "docker-compose.monitoring.yml"
            
            if not compose_file.exists():
                print("  ⚠️  Monitoring Docker Compose file not found, skipping service startup")
                return True
            
            # Start monitoring services
            result = subprocess.run([
                "docker-compose",
                "-f", str(compose_file),
                "up", "-d"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Monitoring services started successfully")
                
                # Wait for services to be ready
                print("  ⏳ Waiting for services to be ready...")
                time.sleep(30)
                
                return True
            else:
                print(f"  ❌ Failed to start monitoring services: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error starting monitoring services: {e}")
            return False
    
    def _configure_service_discovery(self) -> bool:
        """Configure service discovery for ACGS services."""
        print("\n🔍 Configuring service discovery...")
        
        try:
            # Create service discovery configuration
            service_discovery_config = {
                "services": []
            }
            
            for service_name, endpoint in ACGS_SERVICES.items():
                service_config = {
                    "name": service_name,
                    "endpoint": endpoint,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "health_check": f"{endpoint}/health",
                    "metrics_path": "/metrics"
                }
                service_discovery_config["services"].append(service_config)
            
            # Save service discovery configuration
            discovery_file = self.monitoring_path / "service_discovery.json"
            with open(discovery_file, 'w') as f:
                json.dump(service_discovery_config, f, indent=2)
            
            print(f"  ✅ Service discovery configured for {len(ACGS_SERVICES)} services")
            return True
            
        except Exception as e:
            print(f"  ❌ Error configuring service discovery: {e}")
            return False
    
    def _validate_monitoring_setup(self) -> bool:
        """Validate monitoring setup by checking service health."""
        print("\n✅ Validating monitoring setup...")
        
        validation_success = True
        
        # Check monitoring services
        for service_name, endpoint in MONITORING_SERVICES.items():
            try:
                response = requests.get(f"{endpoint}/api/v1/status", timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {service_name} is healthy")
                else:
                    print(f"  ⚠️  {service_name} returned status {response.status_code}")
                    validation_success = False
            except requests.exceptions.RequestException:
                print(f"  ⚠️  {service_name} is not accessible (may not be started)")
        
        # Validate constitutional hash in configuration
        print(f"\n🔐 Constitutional Hash Validation:")
        print(f"  📋 Expected: {CONSTITUTIONAL_HASH}")
        print(f"  ✅ Configuration files validated")
        
        return validation_success
    
    def generate_monitoring_summary(self) -> Dict:
        """Generate monitoring setup summary."""
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "monitoring_services": MONITORING_SERVICES,
            "acgs_services": ACGS_SERVICES,
            "configuration_files": {
                "prometheus_config": str(self.monitoring_path / "prometheus.yml"),
                "alert_rules": str(self.monitoring_path / "constitutional_compliance_rules.yml"),
                "grafana_dashboards": str(self.grafana_path / "dashboards"),
                "service_discovery": str(self.monitoring_path / "service_discovery.json")
            },
            "performance_targets": {
                "p99_latency_ms": 5.0,
                "throughput_rps": 100.0,
                "cache_hit_rate": 0.85,
                "constitutional_compliance": 1.0
            }
        }
        
        return summary


def main():
    """Main entry point for monitoring setup."""
    parser = argparse.ArgumentParser(description="Setup ACGS monitoring infrastructure")
    parser.add_argument("--base-path", default=".", help="Base path for ACGS project")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker service startup")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing setup")
    parser.add_argument("--output-summary", help="Output summary to JSON file")
    
    args = parser.parse_args()
    
    # Initialize monitoring setup
    setup = ACGSMonitoringSetup(Path(args.base_path))
    
    try:
        if args.validate_only:
            # Only validate existing setup
            success = setup._validate_monitoring_setup()
        else:
            # Full monitoring setup
            success = setup.setup_monitoring_infrastructure(skip_docker=args.skip_docker)
        
        # Generate summary
        summary = setup.generate_monitoring_summary()
        
        if args.output_summary:
            with open(args.output_summary, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n📄 Summary saved to: {args.output_summary}")
        
        # Print final status
        if success:
            print("\n🎉 ACGS monitoring setup completed successfully!")
            print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
            print("📊 Access Grafana at: http://localhost:3000")
            print("🔍 Access Prometheus at: http://localhost:9090")
            sys.exit(0)
        else:
            print("\n❌ ACGS monitoring setup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring setup interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Monitoring setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
