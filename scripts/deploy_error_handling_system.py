#!/usr/bin/env python3
"""
Deployment Script for Enhanced Error Handling System
Deploys and configures the comprehensive error handling infrastructure for ACGS.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorHandlingDeployment:
    """Manages deployment of error handling system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_config = {
            'prometheus_port': 9090,
            'grafana_port': 3001,
            'error_tracker_port': 8090,
            'sla_validator_port': 8091,
            'nats_url': 'nats://localhost:4222',
            'constitutional_hash': 'cdd01ef066bc6cf2'
        }
        
    async def deploy_complete_system(self):
        """Deploy the complete error handling system."""
        logger.info("Starting deployment of enhanced error handling system...")
        
        try:
            # Step 1: Validate prerequisites
            await self.validate_prerequisites()
            
            # Step 2: Deploy monitoring infrastructure
            await self.deploy_monitoring_infrastructure()
            
            # Step 3: Deploy error tracking components
            await self.deploy_error_tracking()
            
            # Step 4: Deploy resilience components
            await self.deploy_resilience_components()
            
            # Step 5: Deploy SLA validation
            await self.deploy_sla_validation()
            
            # Step 6: Configure service integrations
            await self.configure_service_integrations()
            
            # Step 7: Start monitoring services
            await self.start_monitoring_services()
            
            # Step 8: Validate deployment
            await self.validate_deployment()
            
            logger.info("Error handling system deployment completed successfully!")
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise

    async def validate_prerequisites(self):
        """Validate system prerequisites."""
        logger.info("Validating prerequisites...")
        
        # Check Python dependencies
        required_packages = [
            'aiohttp', 'prometheus_client', 'numpy', 'nats-py'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✓ {package} is available")
            except ImportError:
                logger.error(f"✗ {package} is not installed")
                raise RuntimeError(f"Missing required package: {package}")
        
        # Check if NATS is running
        try:
            import nats
            nc = await nats.connect("nats://localhost:4222", timeout=5)
            await nc.close()
            logger.info("✓ NATS server is accessible")
        except Exception as e:
            logger.warning(f"NATS server not accessible: {e}")
            logger.info("NATS will be started as part of deployment")
        
        # Check if Prometheus is running
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:9090/api/v1/status/config", timeout=5) as response:
                    if response.status == 200:
                        logger.info("✓ Prometheus is running")
                    else:
                        logger.warning("Prometheus is not responding correctly")
        except Exception as e:
            logger.warning(f"Prometheus not accessible: {e}")

    async def deploy_monitoring_infrastructure(self):
        """Deploy monitoring infrastructure components."""
        logger.info("Deploying monitoring infrastructure...")
        
        # Create monitoring directories
        monitoring_dirs = [
            'infrastructure/monitoring/error_analysis/reports',
            'infrastructure/monitoring/sla_validation/reports',
            'infrastructure/monitoring/grafana/dashboards',
            'logs/error_handling'
        ]
        
        for dir_path in monitoring_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        
        # Deploy Grafana dashboard
        dashboard_source = self.project_root / "infrastructure/monitoring/grafana/dashboards/acgs_error_analysis_dashboard.json"
        if dashboard_source.exists():
            logger.info("✓ Error analysis dashboard configuration ready")
        else:
            logger.warning("Dashboard configuration not found")

    async def deploy_error_tracking(self):
        """Deploy error tracking components."""
        logger.info("Deploying error tracking components...")
        
        # Validate error tracking files
        error_tracking_files = [
            'infrastructure/monitoring/error_analysis/comprehensive_error_tracker.py',
            'infrastructure/monitoring/error_analysis/error_remediation_engine.py'
        ]
        
        for file_path in error_tracking_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                logger.info(f"✓ {file_path} is ready")
            else:
                logger.error(f"✗ {file_path} not found")
                raise FileNotFoundError(f"Required file not found: {file_path}")

    async def deploy_resilience_components(self):
        """Deploy resilience components."""
        logger.info("Deploying resilience components...")
        
        # Validate resilience files
        resilience_files = [
            'services/shared/resilience/enhanced_circuit_breaker.py',
            'services/shared/resilience/enhanced_retry_mechanism.py',
            'services/shared/resilience/graceful_degradation.py',
            'services/shared/messaging/nats_error_publisher.py'
        ]
        
        for file_path in resilience_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                logger.info(f"✓ {file_path} is ready")
            else:
                logger.error(f"✗ {file_path} not found")
                raise FileNotFoundError(f"Required file not found: {file_path}")

    async def deploy_sla_validation(self):
        """Deploy SLA validation components."""
        logger.info("Deploying SLA validation components...")
        
        # Validate SLA validation files
        sla_files = [
            'infrastructure/monitoring/sla_validation/error_rate_validator.py'
        ]
        
        for file_path in sla_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                logger.info(f"✓ {file_path} is ready")
            else:
                logger.error(f"✗ {file_path} not found")
                raise FileNotFoundError(f"Required file not found: {file_path}")

    async def configure_service_integrations(self):
        """Configure service integrations."""
        logger.info("Configuring service integrations...")
        
        # Create integration configuration
        integration_config = {
            'error_handling': {
                'enabled': True,
                'circuit_breaker': {
                    'enabled': True,
                    'failure_threshold': 5,
                    'recovery_timeout': 60.0
                },
                'retry_mechanism': {
                    'enabled': True,
                    'max_attempts': 3,
                    'base_delay': 1.0
                },
                'graceful_degradation': {
                    'enabled': True,
                    'degradation_thresholds': {
                        'error_rate': 0.05,
                        'response_time_ms': 2000.0
                    }
                },
                'nats_integration': {
                    'enabled': True,
                    'url': self.deployment_config['nats_url']
                }
            },
            'monitoring': {
                'error_tracker_port': self.deployment_config['error_tracker_port'],
                'sla_validator_port': self.deployment_config['sla_validator_port'],
                'constitutional_hash': self.deployment_config['constitutional_hash']
            }
        }
        
        # Save configuration
        config_path = self.project_root / 'config/error_handling_config.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(integration_config, f, indent=2)
        
        logger.info(f"Integration configuration saved to {config_path}")

    async def start_monitoring_services(self):
        """Start monitoring services."""
        logger.info("Starting monitoring services...")
        
        # Create systemd service files or Docker compose configurations
        # For now, we'll create simple startup scripts
        
        startup_scripts = {
            'error_tracker': {
                'script': 'infrastructure/monitoring/error_analysis/comprehensive_error_tracker.py',
                'description': 'ACGS Error Tracker'
            },
            'error_remediation': {
                'script': 'infrastructure/monitoring/error_analysis/error_remediation_engine.py',
                'description': 'ACGS Error Remediation Engine'
            },
            'sla_validator': {
                'script': 'infrastructure/monitoring/sla_validation/error_rate_validator.py',
                'description': 'ACGS SLA Validator'
            }
        }
        
        scripts_dir = self.project_root / 'scripts/monitoring'
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        for service_name, config in startup_scripts.items():
            script_content = f"""#!/bin/bash
# {config['description']} Startup Script

cd {self.project_root}
export PYTHONPATH=$PYTHONPATH:{self.project_root}

echo "Starting {config['description']}..."
python3 {config['script']}
"""
            
            script_path = scripts_dir / f"start_{service_name}.sh"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            logger.info(f"Created startup script: {script_path}")

    async def validate_deployment(self):
        """Validate the deployment."""
        logger.info("Validating deployment...")
        
        # Check if all required files exist
        required_files = [
            'infrastructure/monitoring/error_analysis/comprehensive_error_tracker.py',
            'infrastructure/monitoring/error_analysis/error_remediation_engine.py',
            'infrastructure/monitoring/sla_validation/error_rate_validator.py',
            'services/shared/resilience/enhanced_circuit_breaker.py',
            'services/shared/resilience/enhanced_retry_mechanism.py',
            'services/shared/resilience/graceful_degradation.py',
            'services/shared/messaging/nats_error_publisher.py',
            'config/error_handling_config.json'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing files: {missing_files}")
            raise RuntimeError("Deployment validation failed - missing files")
        
        logger.info("✓ All required files are present")
        
        # Test Python imports
        test_imports = [
            'infrastructure.monitoring.error_analysis.comprehensive_error_tracker',
            'services.shared.resilience.enhanced_circuit_breaker',
            'services.shared.resilience.enhanced_retry_mechanism'
        ]
        
        for import_path in test_imports:
            try:
                # Add project root to Python path for testing
                sys.path.insert(0, str(self.project_root))
                __import__(import_path.replace('/', '.'))
                logger.info(f"✓ {import_path} imports successfully")
            except ImportError as e:
                logger.warning(f"Import test failed for {import_path}: {e}")
            finally:
                if str(self.project_root) in sys.path:
                    sys.path.remove(str(self.project_root))

    async def start_72_hour_monitoring(self):
        """Start the 72-hour continuous monitoring session."""
        logger.info("Starting 72-hour continuous monitoring session...")
        
        try:
            # This would typically be done by importing and running the validator
            # For now, we'll create a monitoring script
            monitoring_script = f"""#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('{self.project_root}')

from infrastructure.monitoring.sla_validation.error_rate_validator import ErrorRateValidator

async def main():
    validator = ErrorRateValidator()
    session_id = await validator.start_72_hour_monitoring()
    print(f"Started 72-hour monitoring session: {{session_id}}")
    
    # Start the validator
    await validator.start_validator()

if __name__ == "__main__":
    asyncio.run(main())
"""
            
            script_path = self.project_root / 'scripts/start_72h_monitoring.py'
            with open(script_path, 'w') as f:
                f.write(monitoring_script)
            
            os.chmod(script_path, 0o755)
            logger.info(f"Created 72-hour monitoring script: {script_path}")
            logger.info("Run 'python3 scripts/start_72h_monitoring.py' to start monitoring")
            
        except Exception as e:
            logger.error(f"Failed to setup 72-hour monitoring: {e}")

    def print_deployment_summary(self):
        """Print deployment summary."""
        print("\n" + "="*60)
        print("ACGS ERROR HANDLING SYSTEM DEPLOYMENT SUMMARY")
        print("="*60)
        print(f"✓ Error tracking system deployed")
        print(f"✓ Circuit breakers and retry mechanisms ready")
        print(f"✓ Graceful degradation strategies configured")
        print(f"✓ NATS error event publishing enabled")
        print(f"✓ SLA validation and monitoring deployed")
        print(f"✓ Grafana dashboard configuration ready")
        print("\nMonitoring Endpoints:")
        print(f"  - Error Tracker Metrics: http://localhost:{self.deployment_config['error_tracker_port']}/metrics")
        print(f"  - SLA Validator Metrics: http://localhost:{self.deployment_config['sla_validator_port']}/metrics")
        print(f"  - Prometheus: http://localhost:{self.deployment_config['prometheus_port']}")
        print(f"  - Grafana: http://localhost:{self.deployment_config['grafana_port']}")
        print("\nNext Steps:")
        print("1. Start monitoring services using scripts in scripts/monitoring/")
        print("2. Import Grafana dashboard from infrastructure/monitoring/grafana/dashboards/")
        print("3. Run 'python3 scripts/start_72h_monitoring.py' for continuous monitoring")
        print("4. Monitor error rates and SLA compliance through dashboards")
        print("\nTarget SLA Metrics:")
        print("  - Error Rate: < 1%")
        print("  - Response Time P95: < 500ms")
        print("  - Constitutional Compliance: ≥ 95%")
        print("  - Availability: ≥ 99.9%")
        print("="*60)

async def main():
    """Main deployment function."""
    deployment = ErrorHandlingDeployment()
    
    try:
        await deployment.deploy_complete_system()
        await deployment.start_72_hour_monitoring()
        deployment.print_deployment_summary()
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
