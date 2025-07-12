#!/usr/bin/env python3
"""
ACGS-2 Sentry Integration Setup Script

Automates the setup and configuration of Sentry monitoring for the ACGS-2
Constitutional AI Governance System with proper constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
import json
import requests
import subprocess
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path
import shutil
import yaml


CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
ACGS_ROOT = Path(__file__).parent.parent.parent


class SentrySetupManager:
    """Manages Sentry integration setup for ACGS-2"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.acgs_root = ACGS_ROOT
        self.sentry_config = {}
        self.services = self._discover_services()
        
    def _discover_services(self) -> List[Dict[str, str]]:
        """Discover all ACGS-2 services for Sentry integration"""
        services = []
        
        # Core services
        core_services_dir = self.acgs_root / "services" / "core"
        if core_services_dir.exists():
            for service_dir in core_services_dir.iterdir():
                if service_dir.is_dir() and (service_dir / "app").exists():
                    services.append({
                        "name": f"acgs-{service_dir.name}",
                        "path": str(service_dir),
                        "type": "core",
                        "main_file": str(service_dir / "app" / "main.py")
                    })
        
        # Platform services
        platform_services_dir = self.acgs_root / "services" / "platform_services"
        if platform_services_dir.exists():
            for service_dir in platform_services_dir.iterdir():
                if service_dir.is_dir():
                    services.append({
                        "name": f"acgs-{service_dir.name}",
                        "path": str(service_dir),
                        "type": "platform",
                        "main_file": str(service_dir / "app" / "main.py")
                    })
        
        return services
        
    def validate_environment(self) -> bool:
        """Validate the ACGS-2 environment for Sentry setup"""
        print(f"🔍 Validating ACGS-2 environment...")
        
        # Check constitutional hash presence
        constitutional_files = []
        for file_path in self.acgs_root.rglob("*.py"):
            try:
                content = file_path.read_text()
                if CONSTITUTIONAL_HASH in content:
                    constitutional_files.append(str(file_path))
            except Exception:
                continue
                
        print(f"✅ Found constitutional hash in {len(constitutional_files)} files")
        
        # Check required directories
        required_dirs = [
            "services/core",
            "services/platform_services", 
            "services/shared",
            "infrastructure/docker"
        ]
        
        for dir_path in required_dirs:
            full_path = self.acgs_root / dir_path
            if not full_path.exists():
                print(f"❌ Missing required directory: {dir_path}")
                return False
            print(f"✅ Found directory: {dir_path}")
            
        print(f"✅ Environment validation complete")
        return True
        
    def load_sentry_config(self) -> bool:
        """Load Sentry configuration from environment"""
        print(f"📋 Loading Sentry configuration...")
        
        # Load from .env.sentry if it exists
        env_file = self.acgs_root / ".env.sentry"
        if env_file.exists():
            print(f"📁 Loading from {env_file}")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value
        
        # Required configuration
        required_vars = [
            "SENTRY_DSN",
            "CONSTITUTIONAL_HASH"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            print(f"💡 Copy .env.sentry.example to .env.sentry and configure")
            return False
            
        self.sentry_config = {
            "dsn": os.getenv("SENTRY_DSN"),
            "environment": os.getenv("SENTRY_ENVIRONMENT", self.environment),
            "release": os.getenv("SENTRY_RELEASE", "acgs-2.0.0"),
            "traces_sample_rate": float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
            "profiles_sample_rate": float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0")),
            "constitutional_hash": os.getenv("CONSTITUTIONAL_HASH", CONSTITUTIONAL_HASH)
        }
        
        print(f"✅ Sentry configuration loaded")
        return True
        
    def install_dependencies(self) -> bool:
        """Install required Sentry dependencies"""
        print(f"📦 Installing Sentry dependencies...")
        
        # Check if sentry-sdk is already installed
        try:
            import sentry_sdk
            print(f"✅ sentry-sdk already installed: {sentry_sdk.VERSION}")
        except ImportError:
            print(f"📥 Installing sentry-sdk...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "sentry-sdk[fastapi,sqlalchemy,redis]"
                ], check=True, capture_output=True)
                print(f"✅ sentry-sdk installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install sentry-sdk: {e}")
                return False
                
        return True
        
    def create_sentry_configs(self) -> bool:
        """Create Sentry configuration files for each service"""
        print(f"📝 Creating Sentry configuration files...")
        
        for service in self.services:
            service_name = service["name"]
            service_path = Path(service["path"])
            
            # Create sentry initialization file
            sentry_init_file = service_path / "app" / "sentry_init.py"
            
            sentry_init_content = f'''"""
Sentry initialization for {service_name}
Constitutional Hash: {CONSTITUTIONAL_HASH}
"""

import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Try to import shared Sentry utilities
try:
    from services.shared.monitoring.sentry_integration import init_sentry
    SHARED_SENTRY_AVAILABLE = True
except ImportError:
    SHARED_SENTRY_AVAILABLE = False

CONSTITUTIONAL_HASH = "{CONSTITUTIONAL_HASH}"
SERVICE_NAME = "{service_name}"


def initialize_sentry():
    """Initialize Sentry for this service"""
    if SHARED_SENTRY_AVAILABLE:
        # Use shared integration
        init_sentry(
            service_name=SERVICE_NAME,
            environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
            sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
        )
    else:
        # Direct Sentry initialization
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
            release=os.getenv("SENTRY_RELEASE", "acgs-2.0.0"),
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0")),
            send_default_pii=False,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(level=None, event_level=None),
            ],
            before_send=lambda event, hint: add_constitutional_context(event, hint)
        )
        
        # Set service tags
        sentry_sdk.set_tag("service", SERVICE_NAME)
        sentry_sdk.set_tag("constitutional_hash", CONSTITUTIONAL_HASH)


def add_constitutional_context(event, hint):
    """Add constitutional context to all Sentry events"""
    event.setdefault("tags", {{}})["constitutional_hash"] = CONSTITUTIONAL_HASH
    event["tags"]["service"] = SERVICE_NAME
    
    event.setdefault("contexts", {{}})["constitutional"] = {{
        "hash": CONSTITUTIONAL_HASH,
        "service": SERVICE_NAME,
        "compliance_required": True
    }}
    
    return event


# Initialize on import if DSN is available
if os.getenv("SENTRY_DSN"):
    initialize_sentry()
'''
            
            # Write the file
            sentry_init_file.write_text(sentry_init_content)
            print(f"✅ Created {sentry_init_file}")
            
        return True
        
    def update_service_main_files(self) -> bool:
        """Update main.py files to include Sentry initialization"""
        print(f"🔧 Updating service main files...")
        
        for service in self.services:
            main_file_path = Path(service["main_file"])
            
            if not main_file_path.exists():
                print(f"⚠️  Main file not found: {main_file_path}")
                continue
                
            # Read current content
            try:
                current_content = main_file_path.read_text()
            except Exception as e:
                print(f"❌ Failed to read {main_file_path}: {e}")
                continue
                
            # Check if Sentry is already imported
            if "sentry_init" in current_content or "sentry_sdk.init" in current_content:
                print(f"✅ Sentry already configured in {main_file_path}")
                continue
                
            # Add Sentry import at the top (after existing imports)
            lines = current_content.split('\n')
            import_insert_index = 0
            
            # Find the last import line
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
                    import_insert_index = i + 1
                    
            # Insert Sentry import
            sentry_import = "from .sentry_init import initialize_sentry  # Sentry monitoring"
            lines.insert(import_insert_index, sentry_import)
            lines.insert(import_insert_index + 1, "")
            
            # Find FastAPI app creation and add Sentry call
            for i, line in enumerate(lines):
                if "FastAPI(" in line or "app = FastAPI" in line:
                    # Add Sentry initialization after app creation
                    lines.insert(i + 1, "")
                    lines.insert(i + 2, "# Initialize Sentry monitoring")
                    lines.insert(i + 3, "initialize_sentry()")
                    lines.insert(i + 4, "")
                    break
                    
            # Write updated content
            try:
                main_file_path.write_text('\n'.join(lines))
                print(f"✅ Updated {main_file_path}")
            except Exception as e:
                print(f"❌ Failed to update {main_file_path}: {e}")
                
        return True
        
    def create_monitoring_dashboard(self) -> bool:
        """Create Grafana dashboard for Sentry metrics"""
        print(f"📊 Creating monitoring dashboard...")
        
        dashboard_dir = self.acgs_root / "monitoring" / "dashboards"
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        sentry_dashboard = {
            "dashboard": {
                "title": "ACGS-2 Sentry Monitoring",
                "tags": ["acgs", "sentry", "constitutional"],
                "timezone": "browser",
                "panels": [
                    {
                        "title": "Constitutional Compliance Errors",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "increase(sentry_events_total{tags_constitutional_hash=\"" + CONSTITUTIONAL_HASH + "\"}[1h])",
                                "legendFormat": "{{service}}"
                            }
                        ]
                    },
                    {
                        "title": "Performance Issues by Service",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "sentry_transaction_duration_seconds{tags_constitutional_hash=\"" + CONSTITUTIONAL_HASH + "\"}",
                                "legendFormat": "{{service}}"
                            }
                        ]
                    },
                    {
                        "title": "Agent Coordination Failures",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "increase(sentry_events_total{tags_agent_failure=\"true\"}[24h])",
                                "legendFormat": "{{agent_type}}"
                            }
                        ]
                    }
                ]
            }
        }
        
        dashboard_file = dashboard_dir / "sentry_monitoring.json"
        with open(dashboard_file, 'w') as f:
            json.dump(sentry_dashboard, f, indent=2)
            
        print(f"✅ Created dashboard: {dashboard_file}")
        return True
        
    def setup_alert_rules(self) -> bool:
        """Setup Prometheus alert rules for Sentry metrics"""
        print(f"🚨 Setting up alert rules...")
        
        alerts_dir = self.acgs_root / "monitoring" / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        sentry_alerts = {
            "groups": [
                {
                    "name": "acgs_sentry_alerts",
                    "rules": [
                        {
                            "alert": "ConstitutionalComplianceViolation",
                            "expr": f"increase(sentry_events_total{{tags_constitutional_violation=\"true\",tags_constitutional_hash=\"{CONSTITUTIONAL_HASH}\"}}[5m]) > 0",
                            "for": "0m",
                            "labels": {
                                "severity": "critical",
                                "constitutional_hash": CONSTITUTIONAL_HASH
                            },
                            "annotations": {
                                "summary": "Constitutional compliance violation detected",
                                "description": "Service {{ $labels.service }} has constitutional violations"
                            }
                        },
                        {
                            "alert": "HighErrorRate",
                            "expr": "rate(sentry_events_total[5m]) > 0.1",
                            "for": "2m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High error rate in {{ $labels.service }}",
                                "description": "Error rate is {{ $value }} errors/second"
                            }
                        },
                        {
                            "alert": "AgentCoordinationFailure",
                            "expr": f"increase(sentry_events_total{{tags_agent_failure=\"true\",tags_constitutional_hash=\"{CONSTITUTIONAL_HASH}\"}}[10m]) > 2",
                            "for": "1m",
                            "labels": {
                                "severity": "high"
                            },
                            "annotations": {
                                "summary": "Multiple agent coordination failures",
                                "description": "{{ $value }} agent failures in the last 10 minutes"
                            }
                        }
                    ]
                }
            ]
        }
        
        alerts_file = alerts_dir / "sentry_alerts.yml"
        with open(alerts_file, 'w') as f:
            yaml.dump(sentry_alerts, f, default_flow_style=False)
            
        print(f"✅ Created alert rules: {alerts_file}")
        return True
        
    def test_sentry_integration(self) -> bool:
        """Test Sentry integration"""
        print(f"🧪 Testing Sentry integration...")
        
        # Test basic Sentry connectivity
        if not self.sentry_config.get("dsn"):
            print(f"❌ No Sentry DSN configured")
            return False
            
        try:
            # Try to send a test event
            import sentry_sdk
            sentry_sdk.init(dsn=self.sentry_config["dsn"])
            
            # Send test message
            sentry_sdk.capture_message(
                "ACGS-2 Sentry Integration Test",
                level="info",
                tags={
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "test": True,
                    "setup_script": True
                }
            )
            
            print(f"✅ Test event sent to Sentry")
            
        except Exception as e:
            print(f"❌ Failed to send test event: {e}")
            return False
            
        return True
        
    def run_setup(self) -> bool:
        """Run the complete Sentry setup process"""
        print(f"🚀 Starting ACGS-2 Sentry Integration Setup")
        print(f"📍 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"🌍 Environment: {self.environment}")
        print(f"📁 ACGS Root: {self.acgs_root}")
        print(f"🔧 Services Found: {len(self.services)}")
        print()
        
        setup_steps = [
            ("Validating Environment", self.validate_environment),
            ("Loading Sentry Config", self.load_sentry_config),
            ("Installing Dependencies", self.install_dependencies),
            ("Creating Sentry Configs", self.create_sentry_configs),
            ("Updating Service Files", self.update_service_main_files),
            ("Creating Dashboard", self.create_monitoring_dashboard),
            ("Setting up Alerts", self.setup_alert_rules),
            ("Testing Integration", self.test_sentry_integration)
        ]
        
        for step_name, step_function in setup_steps:
            print(f"🔄 {step_name}...")
            try:
                if not step_function():
                    print(f"❌ Failed: {step_name}")
                    return False
                print(f"✅ Completed: {step_name}")
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                return False
            print()
            
        print(f"🎉 ACGS-2 Sentry Integration Setup Complete!")
        print()
        print(f"📋 Next Steps:")
        print(f"1. Configure .env.sentry with your actual Sentry DSN")
        print(f"2. Start the monitoring stack: docker-compose -f infrastructure/docker/docker-compose.monitoring.yml up -d")
        print(f"3. Deploy ACGS-2 services with Sentry monitoring")
        print(f"4. Check Sentry dashboard for constitutional compliance monitoring")
        print()
        print(f"🔗 Useful URLs:")
        print(f"   - Sentry Project: {self.sentry_config.get('dsn', 'Configure DSN').split('@')[1] if '@' in self.sentry_config.get('dsn', '') else 'Configure DSN'}")
        print(f"   - Grafana Dashboard: http://localhost:3000")
        print(f"   - Prometheus Alerts: http://localhost:9090/alerts")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="Setup Sentry integration for ACGS-2")
    parser.add_argument(
        "--environment",
        default="development",
        choices=["development", "staging", "production"],
        help="Environment to configure"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing configurations"
    )
    
    args = parser.parse_args()
    
    setup_manager = SentrySetupManager(environment=args.environment)
    
    if setup_manager.run_setup():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()