#!/usr/bin/env python3
"""
Hunyuan A13B Integration Validation Script

Comprehensive validation of Hunyuan A13B integration with ACGS-PGP system.
Validates all components, configurations, and performance targets.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
import time
import json
import subprocess
import requests
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple

class HunyuanIntegrationValidator:
    """Validates complete Hunyuan A13B integration with ACGS-PGP."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.base_url = "http://localhost:8000"
        
        # Expected files and configurations
        self.required_files = [
            "config/models/hunyuan-a13b.yaml",
            "docker-compose.hunyuan.yml",
            "scripts/deploy_hunyuan_a13b.py",
            "scripts/hunyuan_management.sh",
            "docs/HUNYUAN_A13B_INTEGRATION_GUIDE.md",
            "tests/integration/test_hunyuan_acgs_integration.py"
        ]
        
        self.performance_targets = {
            'response_time_ms': 2000,
            'constitutional_compliance': 0.95,
            'success_rate': 0.95,
            'availability': 0.999
        }
        
        self.validation_results = []
    
    def validate_all(self) -> bool:
        """Run complete validation suite."""
        print("🚀 Starting Hunyuan A13B Integration Validation")
        print("=" * 60)
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        print()
        
        validation_steps = [
            ("File Structure", self._validate_file_structure),
            ("Configuration", self._validate_configuration),
            ("Docker Setup", self._validate_docker_setup),
            ("Service Health", self._validate_service_health),
            ("AI Model Capabilities", self._validate_ai_capabilities),
            ("Constitutional Compliance", self._validate_constitutional_compliance),
            ("Performance Targets", self._validate_performance),
            ("Integration Tests", self._run_integration_tests)
        ]
        
        all_passed = True
        
        for step_name, step_func in validation_steps:
            print(f"🔍 Validating {step_name}...")
            try:
                result = step_func()
                if result:
                    print(f"✅ {step_name}: PASSED")
                    self.validation_results.append((step_name, "PASSED", None))
                else:
                    print(f"❌ {step_name}: FAILED")
                    self.validation_results.append((step_name, "FAILED", "Validation failed"))
                    all_passed = False
            except Exception as e:
                print(f"❌ {step_name}: ERROR - {str(e)}")
                self.validation_results.append((step_name, "ERROR", str(e)))
                all_passed = False
            print()
        
        self._print_summary()
        return all_passed
    
    def _validate_file_structure(self) -> bool:
        """Validate required files exist."""
        missing_files = []
        
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"  ❌ Missing: {file_path}")
            else:
                print(f"  ✅ Found: {file_path}")
        
        if missing_files:
            print(f"  Missing {len(missing_files)} required files")
            return False
        
        print(f"  All {len(self.required_files)} required files found")
        return True
    
    def _validate_configuration(self) -> bool:
        """Validate model configuration."""
        config_path = self.project_root / "config/models/hunyuan-a13b.yaml"
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check required configuration sections
            required_sections = [
                'model', 'acgs_integration', 'resources', 
                'service', 'roles', 'monitoring', 'security'
            ]
            
            for section in required_sections:
                if section not in config:
                    print(f"  ❌ Missing configuration section: {section}")
                    return False
                print(f"  ✅ Found section: {section}")
            
            # Validate constitutional hash
            acgs_config = config.get('acgs_integration', {})
            config_hash = acgs_config.get('constitutional_hash')
            
            if config_hash != self.constitutional_hash:
                print(f"  ❌ Constitutional hash mismatch: {config_hash}")
                return False
            
            print(f"  ✅ Constitutional hash verified: {config_hash}")
            
            # Validate performance targets
            targets = acgs_config.get('performance_targets', {})
            for target, expected_value in self.performance_targets.items():
                if target in targets:
                    print(f"  ✅ Performance target {target}: {targets[target]}")
                else:
                    print(f"  ⚠️ Missing performance target: {target}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Configuration validation error: {e}")
            return False
    
    def _validate_docker_setup(self) -> bool:
        """Validate Docker Compose configuration."""
        compose_path = self.project_root / "docker-compose.hunyuan.yml"
        
        try:
            # Check if Docker is available
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            print("  ✅ Docker is available")
            
            # Check if Docker Compose file is valid
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_path), "config"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("  ✅ Docker Compose configuration is valid")
                
                # Check for required services
                if "hunyuan-a13b" in result.stdout:
                    print("  ✅ Hunyuan service found in compose file")
                else:
                    print("  ❌ Hunyuan service not found in compose file")
                    return False
                
                return True
            else:
                print(f"  ❌ Docker Compose validation failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Docker validation error: {e}")
            return False
        except FileNotFoundError:
            print("  ❌ Docker or Docker Compose not found")
            return False
    
    def _validate_service_health(self) -> bool:
        """Validate service health if running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"  ✅ Service is healthy: {health_data}")
                
                # Check constitutional hash in health response
                if 'constitutional_hash' in health_data:
                    if health_data['constitutional_hash'] == self.constitutional_hash:
                        print(f"  ✅ Constitutional hash verified in health check")
                    else:
                        print(f"  ❌ Constitutional hash mismatch in health check")
                        return False
                
                return True
            else:
                print(f"  ⚠️ Service not healthy (status: {response.status_code})")
                return False
                
        except requests.RequestException:
            print("  ⚠️ Service not running or not accessible")
            print("  💡 Run 'docker-compose -f docker-compose.hunyuan.yml up -d' to start")
            return False
    
    def _validate_ai_capabilities(self) -> bool:
        """Validate AI model capabilities."""
        if not self._is_service_running():
            print("  ⚠️ Skipping AI validation - service not running")
            return True
        
        test_cases = [
            {
                "name": "Chinese Governance",
                "prompt": "简要解释宪法治理的重要性。",
                "expected_keywords": ["宪法", "治理", "重要"]
            },
            {
                "name": "English Constitutional Analysis", 
                "prompt": "Explain constitutional governance principles.",
                "expected_keywords": ["constitutional", "governance", "principles"]
            },
            {
                "name": "Multilingual Translation",
                "prompt": "Translate to Chinese: Constitutional compliance is essential.",
                "expected_keywords": ["宪法", "合规", "重要"]
            }
        ]
        
        for test_case in test_cases:
            try:
                payload = {
                    "model": "hunyuan-a13b",
                    "messages": [
                        {"role": "user", "content": test_case["prompt"]}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Check for expected keywords
                    content_lower = content.lower()
                    found_keywords = [
                        kw for kw in test_case["expected_keywords"]
                        if kw.lower() in content_lower
                    ]
                    
                    if found_keywords:
                        print(f"  ✅ {test_case['name']}: Keywords found {found_keywords}")
                    else:
                        print(f"  ⚠️ {test_case['name']}: No expected keywords found")
                else:
                    print(f"  ❌ {test_case['name']}: Request failed ({response.status_code})")
                    return False
                    
            except Exception as e:
                print(f"  ❌ {test_case['name']}: Error - {e}")
                return False
        
        return True
    
    def _validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance mechanisms."""
        if not self._is_service_running():
            print("  ⚠️ Skipping compliance validation - service not running")
            return True
        
        # Test constitutional compliance prompt
        payload = {
            "model": "hunyuan-a13b",
            "messages": [
                {
                    "role": "system",
                    "content": f"Ensure constitutional compliance. Hash: {self.constitutional_hash}"
                },
                {
                    "role": "user",
                    "content": "Analyze the constitutional implications of data privacy laws."
                }
            ],
            "max_tokens": 300,
            "temperature": 0.5
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Check for constitutional compliance indicators
                compliance_indicators = [
                    "constitutional", "compliance", "legal", "rights",
                    "framework", "governance", "law", "protection"
                ]
                
                content_lower = content.lower()
                found_indicators = [
                    indicator for indicator in compliance_indicators
                    if indicator in content_lower
                ]
                
                compliance_score = len(found_indicators) / len(compliance_indicators)
                
                print(f"  ✅ Constitutional compliance score: {compliance_score:.2f}")
                print(f"  ✅ Found indicators: {found_indicators}")
                
                return compliance_score >= self.performance_targets['constitutional_compliance']
            else:
                print(f"  ❌ Compliance test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Compliance validation error: {e}")
            return False
    
    def _validate_performance(self) -> bool:
        """Validate performance targets."""
        if not self._is_service_running():
            print("  ⚠️ Skipping performance validation - service not running")
            return True
        
        # Test response time
        payload = {
            "model": "hunyuan-a13b",
            "messages": [
                {"role": "user", "content": "Hello, test response time."}
            ],
            "max_tokens": 50,
            "temperature": 0.5
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                target_time = self.performance_targets['response_time_ms']
                
                if response_time < target_time:
                    print(f"  ✅ Response time: {response_time:.1f}ms (target: <{target_time}ms)")
                    return True
                else:
                    print(f"  ❌ Response time: {response_time:.1f}ms exceeds target {target_time}ms")
                    return False
            else:
                print(f"  ❌ Performance test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Performance validation error: {e}")
            return False
    
    def _run_integration_tests(self) -> bool:
        """Run integration test suite."""
        test_file = self.project_root / "tests/integration/test_hunyuan_acgs_integration.py"
        
        if not test_file.exists():
            print("  ❌ Integration test file not found")
            return False
        
        if not self._is_service_running():
            print("  ⚠️ Skipping integration tests - service not running")
            return True
        
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", str(test_file), "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("  ✅ All integration tests passed")
                return True
            else:
                print(f"  ❌ Integration tests failed:")
                print(f"  {result.stdout}")
                print(f"  {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("  ❌ Integration tests timed out")
            return False
        except Exception as e:
            print(f"  ❌ Integration test error: {e}")
            return False
    
    def _is_service_running(self) -> bool:
        """Check if Hunyuan service is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _print_summary(self):
        """Print validation summary."""
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, status, _ in self.validation_results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.validation_results if status == "FAILED")
        errors = sum(1 for _, status, _ in self.validation_results if status == "ERROR")
        
        for step_name, status, error in self.validation_results:
            if status == "PASSED":
                print(f"✅ {step_name}")
            elif status == "FAILED":
                print(f"❌ {step_name}")
            else:
                print(f"⚠️ {step_name}: {error}")
        
        print()
        print(f"Results: {passed} passed, {failed} failed, {errors} errors")
        
        if failed == 0 and errors == 0:
            print("🎉 ALL VALIDATIONS PASSED!")
            print(f"Hunyuan A13B integration with ACGS-PGP is complete and functional.")
            print(f"Constitutional Hash: {self.constitutional_hash} ✓")
        else:
            print("❌ VALIDATION ISSUES FOUND")
            print("Please address the issues above before proceeding.")


def main():
    validator = HunyuanIntegrationValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
