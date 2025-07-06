#!/usr/bin/env python3
"""
ACGS Enterprise Monitoring Dashboard Deployment Script

This script deploys the enterprise monitoring dashboard with real-time tracking
of P99 latency (<5ms), cache hit rates (>85%), and constitutional compliance.
"""
# Constitutional Hash: cdd01ef066bc6cf2

import os
import sys
import json
import time
import requests
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path


class EnterpriseMonitoringDeployer:
    """Deploys and configures enterprise monitoring dashboard."""
    
    def __init__(self, grafana_url: str = "http://localhost:3000", 
                 grafana_user: str = "admin", grafana_password: str = "admin"):
        self.grafana_url = grafana_url.rstrip('/')
        self.grafana_user = grafana_user
        self.grafana_password = grafana_password
        self.session = requests.Session()
        self.session.auth = (grafana_user, grafana_password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def check_grafana_health(self) -> bool:
        """Check if Grafana is accessible and healthy."""
        try:
            response = self.session.get(f"{self.grafana_url}/api/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Grafana health check passed: {health_data.get('database', 'unknown')}")
                return True
            else:
                print(f"❌ Grafana health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to Grafana: {e}")
            return False
    
    def setup_prometheus_datasource(self) -> bool:
        """Set up Prometheus datasource in Grafana."""
        print("🔧 Setting up Prometheus datasource...")
        
        datasource_config = {
            "name": "ACGS-Prometheus",
            "type": "prometheus",
            "url": "http://localhost:9090",
            "access": "proxy",
            "isDefault": True,
            "jsonData": {
                "httpMethod": "POST",
                "queryTimeout": "60s",
                "timeInterval": "5s"
            }
        }
        
        try:
            # Check if datasource already exists
            response = self.session.get(f"{self.grafana_url}/api/datasources/name/ACGS-Prometheus")
            if response.status_code == 200:
                print("✅ Prometheus datasource already exists")
                return True
            
            # Create new datasource
            response = self.session.post(f"{self.grafana_url}/api/datasources", 
                                       json=datasource_config)
            if response.status_code == 200:
                print("✅ Prometheus datasource created successfully")
                return True
            else:
                print(f"❌ Failed to create Prometheus datasource: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up Prometheus datasource: {e}")
            return False
    
    def create_enterprise_folder(self) -> Optional[int]:
        """Create enterprise monitoring folder in Grafana."""
        print("📁 Creating enterprise monitoring folder...")
        
        folder_config = {
            "title": "ACGS Enterprise Monitoring",
            "uid": "acgs-enterprise"
        }
        
        try:
            # Check if folder already exists
            response = self.session.get(f"{self.grafana_url}/api/folders/acgs-enterprise")
            if response.status_code == 200:
                folder_data = response.json()
                print("✅ Enterprise monitoring folder already exists")
                return folder_data.get("id")
            
            # Create new folder
            response = self.session.post(f"{self.grafana_url}/api/folders", 
                                       json=folder_config)
            if response.status_code == 200:
                folder_data = response.json()
                print("✅ Enterprise monitoring folder created successfully")
                return folder_data.get("id")
            else:
                print(f"❌ Failed to create enterprise folder: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating enterprise folder: {e}")
            return None
    
    def deploy_dashboard(self, dashboard_path: str, folder_id: Optional[int] = None) -> bool:
        """Deploy the enterprise monitoring dashboard."""
        print("📊 Deploying enterprise monitoring dashboard...")
        
        try:
            # Load dashboard configuration
            with open(dashboard_path, 'r') as f:
                dashboard_config = json.load(f)
            
            # Prepare dashboard for deployment
            deployment_config = {
                "dashboard": dashboard_config["dashboard"],
                "folderId": folder_id,
                "overwrite": True,
                "message": "Enterprise monitoring dashboard deployment"
            }
            
            # Set datasource to our Prometheus instance
            self._update_dashboard_datasources(deployment_config["dashboard"])
            
            # Deploy dashboard
            response = self.session.post(f"{self.grafana_url}/api/dashboards/db", 
                                       json=deployment_config)
            
            if response.status_code == 200:
                result = response.json()
                dashboard_url = f"{self.grafana_url}{result.get('url', '')}"
                print(f"✅ Enterprise dashboard deployed successfully")
                print(f"🔗 Dashboard URL: {dashboard_url}")
                return True
            else:
                print(f"❌ Failed to deploy dashboard: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error deploying dashboard: {e}")
            return False
    
    def _update_dashboard_datasources(self, dashboard: Dict[str, Any]) -> None:
        """Update dashboard panels to use the correct datasource."""
        for panel in dashboard.get("panels", []):
            for target in panel.get("targets", []):
                target["datasource"] = "ACGS-Prometheus"
    
    def setup_alerting_rules(self) -> bool:
        """Set up alerting rules for enterprise monitoring."""
        print("🚨 Setting up enterprise alerting rules...")
        
        alert_rules = [
            {
                "alert": "ACGS_High_P99_Latency",
                "expr": "histogram_quantile(0.99, rate(acgs_request_duration_seconds_bucket[5m])) * 1000 > 5",
                "for": "2m",
                "labels": {"severity": "critical", "service": "acgs"},
                "annotations": {
                    "summary": "ACGS P99 latency exceeds 5ms threshold",
                    "description": "P99 latency is {{ $value }}ms, exceeding the 5ms enterprise threshold"
                }
            },
            {
                "alert": "ACGS_Low_Cache_Hit_Rate",
                "expr": "acgs_cache_hit_rate_percent < 85",
                "for": "5m",
                "labels": {"severity": "warning", "service": "acgs"},
                "annotations": {
                    "summary": "ACGS cache hit rate below 85% threshold",
                    "description": "Cache hit rate is {{ $value }}%, below the 85% enterprise threshold"
                }
            },
            {
                "alert": "ACGS_Constitutional_Compliance_Failure",
                "expr": "acgs_constitutional_compliance_score < 0.95",
                "for": "1m",
                "labels": {"severity": "critical", "service": "acgs"},
                "annotations": {
                    "summary": "ACGS constitutional compliance failure",
                    "description": "Constitutional compliance score is {{ $value }}, below required threshold"
                }
            },
            {
                "alert": "ACGS_Low_Throughput",
                "expr": "sum(rate(acgs_requests_total[5m])) < 100",
                "for": "5m",
                "labels": {"severity": "warning", "service": "acgs"},
                "annotations": {
                    "summary": "ACGS throughput below 100 RPS threshold",
                    "description": "Current throughput is {{ $value }} RPS, below the 100 RPS enterprise threshold"
                }
            }
        ]
        
        try:
            # Create alert rules file
            rules_config = {
                "groups": [
                    {
                        "name": "acgs_enterprise_alerts",
                        "rules": alert_rules
                    }
                ]
            }
            
            # Save rules to file
            rules_path = Path("infrastructure/monitoring/rules/enterprise_alerts.yml")
            rules_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(rules_path, 'w') as f:
                import yaml
                yaml.dump(rules_config, f, default_flow_style=False)
            
            print(f"✅ Alert rules saved to {rules_path}")
            print("⚠️ Note: Restart Prometheus to load new alert rules")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up alert rules: {e}")
            return False
    
    def validate_deployment(self) -> Dict[str, bool]:
        """Validate the enterprise monitoring deployment."""
        print("🔍 Validating enterprise monitoring deployment...")
        
        validation_results = {
            "grafana_accessible": False,
            "prometheus_datasource": False,
            "dashboard_deployed": False,
            "metrics_available": False
        }
        
        try:
            # Check Grafana accessibility
            validation_results["grafana_accessible"] = self.check_grafana_health()
            
            # Check Prometheus datasource
            response = self.session.get(f"{self.grafana_url}/api/datasources/name/ACGS-Prometheus")
            validation_results["prometheus_datasource"] = response.status_code == 200
            
            # Check dashboard deployment
            response = self.session.get(f"{self.grafana_url}/api/search?query=ACGS%20Enterprise")
            if response.status_code == 200:
                dashboards = response.json()
                validation_results["dashboard_deployed"] = len(dashboards) > 0
            
            # Check if metrics are available (basic check)
            try:
                prometheus_response = requests.get("http://localhost:9090/api/v1/query?query=up", timeout=5)
                validation_results["metrics_available"] = prometheus_response.status_code == 200
            except:
                validation_results["metrics_available"] = False
            
            # Print validation summary
            print("\n📊 Validation Summary:")
            for check, result in validation_results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {check.replace('_', ' ').title()}: {status}")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return validation_results
    
    def generate_deployment_report(self, validation_results: Dict[str, bool]) -> str:
        """Generate a deployment report."""
        all_passed = all(validation_results.values())
        
        report = [
            "# ACGS Enterprise Monitoring Dashboard Deployment Report",
            f"**Deployment Status:** {'✅ SUCCESS' if all_passed else '❌ PARTIAL/FAILED'}",
            f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
            "",
            "## Validation Results",
            ""
        ]
        
        for check, result in validation_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            report.append(f"- **{check.replace('_', ' ').title()}:** {status}")
        
        report.extend([
            "",
            "## Dashboard Access",
            f"- **Grafana URL:** {self.grafana_url}",
            "- **Username:** admin",
            "- **Dashboard:** ACGS Enterprise Monitoring",
            "",
            "## Key Metrics Monitored",
            "- 🎯 P99 Latency (Target: <5ms)",
            "- 💾 Cache Hit Rate (Target: >85%)",
            "- 🏛️ Constitutional Compliance",
            "- 🚀 Throughput (Target: >100 RPS)",
            "- ⚡ Service Health & Availability",
            "",
            "## Next Steps" if not all_passed else "## ✅ Deployment Complete",
        ])
        
        if not all_passed:
            report.extend([
                "1. Ensure Prometheus is running on localhost:9090",
                "2. Verify ACGS services are exposing metrics",
                "3. Check Grafana configuration and permissions",
                "4. Restart monitoring services if needed"
            ])
        else:
            report.extend([
                "1. Monitor dashboard for real-time metrics",
                "2. Set up alert notifications",
                "3. Configure additional custom panels as needed",
                "4. Review performance against enterprise targets"
            ])
        
        return "\n".join(report)


def main():
    """Main function to deploy enterprise monitoring dashboard."""
    print("🚀 ACGS Enterprise Monitoring Dashboard Deployment")
    print("=" * 55)
    
    # Configuration
    grafana_url = os.getenv("GRAFANA_URL", "http://localhost:3000")
    grafana_user = os.getenv("GRAFANA_USER", "admin")
    grafana_password = os.getenv("GRAFANA_PASSWORD", "admin")
    
    # Initialize deployer
    deployer = EnterpriseMonitoringDeployer(grafana_url, grafana_user, grafana_password)
    
    # Dashboard path
    dashboard_path = Path("infrastructure/monitoring/dashboards/enterprise-monitoring-dashboard.json")
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        sys.exit(1)
    
    # Deployment steps
    success = True
    
    # 1. Check Grafana health
    if not deployer.check_grafana_health():
        print("❌ Grafana is not accessible. Please ensure Grafana is running.")
        success = False
    
    # 2. Set up Prometheus datasource
    if success and not deployer.setup_prometheus_datasource():
        print("❌ Failed to set up Prometheus datasource")
        success = False
    
    # 3. Create enterprise folder
    folder_id = None
    if success:
        folder_id = deployer.create_enterprise_folder()
        if folder_id is None:
            print("⚠️ Could not create enterprise folder, deploying to default location")
    
    # 4. Deploy dashboard
    if success and not deployer.deploy_dashboard(str(dashboard_path), folder_id):
        print("❌ Failed to deploy enterprise dashboard")
        success = False
    
    # 5. Set up alerting rules
    if success:
        deployer.setup_alerting_rules()
    
    # 6. Validate deployment
    validation_results = deployer.validate_deployment()
    
    # 7. Generate report
    report = deployer.generate_deployment_report(validation_results)
    
    # Save report
    report_path = Path("enterprise-monitoring-deployment-report.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📋 Deployment report saved to: {report_path}")
    
    # Final status
    all_passed = all(validation_results.values())
    if all_passed:
        print("\n🎉 Enterprise monitoring dashboard deployed successfully!")
        print(f"🔗 Access dashboard at: {grafana_url}")
        return True
    else:
        print("\n⚠️ Enterprise monitoring deployment completed with issues")
        print("📋 Check the deployment report for details")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
