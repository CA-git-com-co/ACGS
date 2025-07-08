#!/usr/bin/env python3
"""
ACGS Environment Configuration Validator
Constitutional Hash: cdd01ef066bc6cf2

Validates environment configuration for:
- Port conflicts
- Constitutional hash consistency
- Service dependencies
- Security configuration
- Performance settings
"""

import os
import socket
import subprocess
import sys
from typing import Dict, List, Tuple, Any
import json
import logging
from datetime import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """Environment configuration validator."""
    
    def __init__(self, env_file_path: str):
        self.env_file_path = env_file_path
        self.env_vars = {}
        self.validation_results = []
        self.errors = []
        self.warnings = []
        
    def load_environment_file(self) -> bool:
        """Load environment variables from file."""
        try:
            with open(self.env_file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.env_vars[key.strip()] = value.strip()
            
            logger.info(f"Loaded {len(self.env_vars)} environment variables from {self.env_file_path}")
            return True
            
        except FileNotFoundError:
            self.errors.append(f"Environment file not found: {self.env_file_path}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading environment file: {e}")
            return False
    
    def validate_constitutional_hash(self) -> bool:
        """Validate constitutional hash consistency."""
        test_name = "Constitutional Hash Validation"
        
        hash_value = self.env_vars.get('CONSTITUTIONAL_HASH')
        if not hash_value:
            self.errors.append(f"{test_name}: CONSTITUTIONAL_HASH not defined")
            return False
        
        if hash_value != CONSTITUTIONAL_HASH:
            self.errors.append(f"{test_name}: Hash mismatch. Expected: {CONSTITUTIONAL_HASH}, Found: {hash_value}")
            return False
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS",
            "details": f"Constitutional hash validated: {hash_value}"
        })
        return True
    
    def validate_port_conflicts(self) -> bool:
        """Validate port configurations and check for conflicts."""
        test_name = "Port Conflict Detection"
        
        # Extract all port configurations
        port_vars = {k: v for k, v in self.env_vars.items() if 'PORT' in k}
        ports = {}
        conflicts = []
        
        for var, port_str in port_vars.items():
            try:
                port = int(port_str)
                if port in ports:
                    conflicts.append(f"Port {port} used by both {ports[port]} and {var}")
                else:
                    ports[port] = var
            except ValueError:
                self.warnings.append(f"Invalid port value for {var}: {port_str}")
        
        # Check if ports are currently in use
        in_use_ports = []
        acgs_service_ports = []
        for port in ports.keys():
            if self.is_port_in_use(port):
                if self.is_acgs_service_port(port):
                    acgs_service_ports.append(f"Port {port} ({ports[port]}) is used by ACGS service (expected)")
                else:
                    in_use_ports.append(f"Port {port} ({ports[port]}) is currently in use by non-ACGS process")

        if conflicts:
            self.errors.extend(conflicts)
            return False

        # Only warn about non-ACGS processes using ports
        if in_use_ports:
            self.warnings.extend(in_use_ports)

        # Log ACGS service ports as informational (not warnings)
        if acgs_service_ports:
            logger.info("ACGS services detected on expected ports:")
            for service_port in acgs_service_ports:
                logger.info(f"  ✅ {service_port}")
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS" if not conflicts else "FAIL",
            "details": {
                "ports_configured": len(ports),
                "conflicts": conflicts,
                "ports_in_use": in_use_ports
            }
        })
        return len(conflicts) == 0
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False

    def is_acgs_service_port(self, port: int) -> bool:
        """Check if a port is being used by a legitimate ACGS service."""
        try:
            # Check for ACGS service health endpoints
            if port == 8001:  # Constitutional AI Service
                response = subprocess.run(['curl', '-f', '-s', f'http://localhost:{port}/health'],
                                        capture_output=True, text=True, timeout=5)
                if response.returncode == 0 and 'constitutional_hash' in response.stdout:
                    return True
            elif port == 8020:  # Rules Engine Service
                response = subprocess.run(['curl', '-f', '-s', f'http://localhost:{port}/health'],
                                        capture_output=True, text=True, timeout=5)
                if response.returncode == 0 and 'constitutional_hash' in response.stdout:
                    return True
            elif port == 3001:  # Grafana Service
                response = subprocess.run(['curl', '-f', '-s', f'http://localhost:{port}/api/health'],
                                        capture_output=True, text=True, timeout=5)
                if response.returncode == 0 and 'database' in response.stdout:
                    return True
            elif port in [5440, 6390]:  # PostgreSQL and Redis
                # Check if Docker containers are running on these ports
                docker_check = subprocess.run(['docker', 'ps', '--format', '{{.Ports}}'],
                                            capture_output=True, text=True, timeout=5)
                if docker_check.returncode == 0 and f':{port}->' in docker_check.stdout:
                    return True

            return False
        except:
            return False
    
    def validate_database_configuration(self) -> bool:
        """Validate database configuration."""
        test_name = "Database Configuration"
        
        required_db_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_HOST', 'POSTGRES_PORT']
        missing_vars = [var for var in required_db_vars if var not in self.env_vars]
        
        if missing_vars:
            self.errors.append(f"{test_name}: Missing required variables: {missing_vars}")
            return False
        
        # Validate port
        try:
            port = int(self.env_vars['POSTGRES_PORT'])
            if port < 1024 or port > 65535:
                self.warnings.append(f"{test_name}: PostgreSQL port {port} outside recommended range")
        except ValueError:
            self.errors.append(f"{test_name}: Invalid PostgreSQL port: {self.env_vars['POSTGRES_PORT']}")
            return False
        
        # Check password strength
        password = self.env_vars['POSTGRES_PASSWORD']
        if len(password) < 12:
            self.warnings.append(f"{test_name}: PostgreSQL password is weak (length: {len(password)})")
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS",
            "details": {
                "host": self.env_vars['POSTGRES_HOST'],
                "port": self.env_vars['POSTGRES_PORT'],
                "database": self.env_vars['POSTGRES_DB'],
                "user": self.env_vars['POSTGRES_USER']
            }
        })
        return True
    
    def validate_redis_configuration(self) -> bool:
        """Validate Redis configuration."""
        test_name = "Redis Configuration"
        
        required_redis_vars = ['REDIS_HOST', 'REDIS_PORT']
        missing_vars = [var for var in required_redis_vars if var not in self.env_vars]
        
        if missing_vars:
            self.errors.append(f"{test_name}: Missing required variables: {missing_vars}")
            return False
        
        # Validate port
        try:
            port = int(self.env_vars['REDIS_PORT'])
            if port < 1024 or port > 65535:
                self.warnings.append(f"{test_name}: Redis port {port} outside recommended range")
        except ValueError:
            self.errors.append(f"{test_name}: Invalid Redis port: {self.env_vars['REDIS_PORT']}")
            return False
        
        # Check if password is set
        redis_password = self.env_vars.get('REDIS_PASSWORD', '')
        if not redis_password:
            self.warnings.append(f"{test_name}: Redis password not set (security risk)")
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS",
            "details": {
                "host": self.env_vars['REDIS_HOST'],
                "port": self.env_vars['REDIS_PORT'],
                "password_set": bool(redis_password)
            }
        })
        return True
    
    def validate_security_configuration(self) -> bool:
        """Validate security configuration."""
        test_name = "Security Configuration"
        
        security_issues = []
        
        # Check JWT secret key
        jwt_key = self.env_vars.get('JWT_SECRET_KEY', '')
        if len(jwt_key) < 32:
            security_issues.append("JWT secret key is too short (minimum 32 characters)")
        
        # Check auth secret key
        auth_key = self.env_vars.get('AUTH_SECRET_KEY', '')
        if len(auth_key) < 32:
            security_issues.append("Auth secret key is too short (minimum 32 characters)")
        
        # Check if JWT and Auth keys are the same
        if jwt_key and auth_key and jwt_key == auth_key:
            security_issues.append("JWT and Auth secret keys should be different")
        
        # Check Grafana admin password
        grafana_password = self.env_vars.get('GRAFANA_ADMIN_PASSWORD', '')
        if grafana_password in ['admin', 'admin123', 'password']:
            security_issues.append("Grafana admin password is weak/default")
        
        if security_issues:
            self.warnings.extend([f"{test_name}: {issue}" for issue in security_issues])
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS" if not security_issues else "WARNING",
            "details": {
                "security_issues": security_issues,
                "jwt_key_length": len(jwt_key),
                "auth_key_length": len(auth_key)
            }
        })
        return len(security_issues) == 0
    
    def validate_performance_settings(self) -> bool:
        """Validate performance configuration."""
        test_name = "Performance Settings"
        
        performance_vars = [
            'ACGS_PERFORMANCE_P99_TARGET',
            'ACGS_PERFORMANCE_RPS_TARGET',
            'ACGS_CACHE_HIT_RATE_TARGET'
        ]
        
        missing_vars = [var for var in performance_vars if var not in self.env_vars]
        if missing_vars:
            self.warnings.append(f"{test_name}: Missing performance variables: {missing_vars}")
        
        # Validate performance targets
        performance_config = {}
        for var in performance_vars:
            if var in self.env_vars:
                try:
                    value = float(self.env_vars[var])
                    performance_config[var] = value
                except ValueError:
                    self.warnings.append(f"{test_name}: Invalid value for {var}: {self.env_vars[var]}")
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS",
            "details": {
                "performance_config": performance_config,
                "missing_vars": missing_vars
            }
        })
        return True
    
    def validate_service_integration(self) -> bool:
        """Validate service integration configuration."""
        test_name = "Service Integration"
        
        required_services = [
            'CONSTITUTIONAL_AI_PORT',
            'INTEGRITY_SERVICE_PORT',
            'AUTH_SERVICE_PORT'
        ]
        
        missing_services = [var for var in required_services if var not in self.env_vars]
        if missing_services:
            self.warnings.append(f"{test_name}: Missing service ports: {missing_services}")
        
        # Check service discovery
        service_discovery = self.env_vars.get('ENABLE_SERVICE_DISCOVERY', 'false').lower() == 'true'
        
        self.validation_results.append({
            "test": test_name,
            "status": "PASS",
            "details": {
                "service_discovery_enabled": service_discovery,
                "missing_services": missing_services,
                "configured_services": len([var for var in required_services if var in self.env_vars])
            }
        })
        return True
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all validation tests."""
        logger.info(f"Starting ACGS Environment Configuration Validation")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        logger.info(f"Environment File: {self.env_file_path}")
        
        if not self.load_environment_file():
            return self.generate_report()
        
        # Run all validation tests
        tests = [
            self.validate_constitutional_hash,
            self.validate_port_conflicts,
            self.validate_database_configuration,
            self.validate_redis_configuration,
            self.validate_security_configuration,
            self.validate_performance_settings,
            self.validate_service_integration
        ]
        
        passed_tests = 0
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                self.errors.append(f"Test execution error: {e}")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        total_tests = len(self.validation_results)
        passed_tests = len([r for r in self.validation_results if r['status'] == 'PASS'])
        
        report = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now().isoformat(),
            "environment_file": self.env_file_path,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            },
            "validation_results": self.validation_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "environment_variables_count": len(self.env_vars)
        }
        
        return report

def main():
    """Main validation function."""
    env_file = "/home/dislove/ACGS-2/config/environments/.env.acgs"
    
    if len(sys.argv) > 1:
        env_file = sys.argv[1]
    
    validator = EnvironmentValidator(env_file)
    report = validator.run_validation()
    
    # Print summary
    summary = report['summary']
    print(f"\n=== ACGS Environment Validation Report ===")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Environment File: {env_file}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Errors: {summary['errors']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    
    # Print errors and warnings
    if report['errors']:
        print(f"\n❌ ERRORS:")
        for error in report['errors']:
            print(f"  - {error}")
    
    if report['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    # Save detailed report
    with open("environment_validation_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: environment_validation_report.json")
    
    # Return exit code
    return 0 if summary['errors'] == 0 else 1

if __name__ == "__main__":
    exit(main())
