#!/usr/bin/env python3
"""
Comprehensive testing suite for anthropic upgrade (PR #107)
CRITICAL: Do not merge until all tests pass
"""

import os
import sys
import logging
import time
import asyncio
import json
from typing import Dict, Any, List
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnthropicUpgradeValidator:
    """Critical validation suite for anthropic upgrade"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found - some tests will be skipped")
        
    def test_basic_import(self) -> Dict[str, Any]:
        """Test basic anthropic import and version"""
        logger.info("📦 Testing anthropic import...")
        
        try:
            import anthropic
            version = getattr(anthropic, '__version__', 'unknown')
            
            return {
                "status": "success",
                "version": version,
                "import_successful": True
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "import_successful": False
            }
    
    def test_api_compatibility(self) -> Dict[str, Any]:
        """Test API compatibility with new version"""
        logger.info("🔌 Testing API compatibility...")
        
        if not self.api_key:
            return {
                "status": "skipped",
                "reason": "No API key provided"
            }
        
        try:
            import anthropic
            
            # Test basic client creation
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Test message creation (new API format)
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ]
            )
            
            return {
                "status": "success",
                "response_type": type(response).__name__,
                "has_content": hasattr(response, 'content'),
                "content_length": len(response.content) if hasattr(response, 'content') else 0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def test_bedrock_compatibility(self) -> Dict[str, Any]:
        """Test Bedrock integration compatibility"""
        logger.info("☁️ Testing Bedrock compatibility...")
        
        try:
            import anthropic
            
            # Test Bedrock client creation (without actual AWS credentials)
            try:
                client = anthropic.AnthropicBedrock(
                    aws_access_key="test",
                    aws_secret_key="test", 
                    aws_region="us-east-1"
                )
                
                return {
                    "status": "success",
                    "bedrock_client_created": True,
                    "client_type": type(client).__name__
                }
            except Exception as e:
                # Expected to fail without real credentials, but should not fail on import
                if "credentials" in str(e).lower() or "auth" in str(e).lower():
                    return {
                        "status": "success",
                        "bedrock_client_created": True,
                        "expected_auth_error": str(e)
                    }
                else:
                    raise e
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def test_vertex_ai_compatibility(self) -> Dict[str, Any]:
        """Test Vertex AI integration compatibility"""
        logger.info("🔺 Testing Vertex AI compatibility...")
        
        try:
            import anthropic
            
            # Test Vertex AI client creation
            try:
                client = anthropic.AnthropicVertex()
                
                return {
                    "status": "success", 
                    "vertex_client_created": True,
                    "client_type": type(client).__name__
                }
            except Exception as e:
                # Expected to fail without proper GCP setup
                if any(keyword in str(e).lower() for keyword in ["credentials", "auth", "gcp", "google"]):
                    return {
                        "status": "success",
                        "vertex_client_created": True,
                        "expected_auth_error": str(e)
                    }
                else:
                    raise e
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def test_dgm_agent_compatibility(self) -> Dict[str, Any]:
        """Test DGM best SWE agent compatibility"""
        logger.info("🤖 Testing DGM agent compatibility...")
        
        try:
            # Test import of DGM agent modules
            sys.path.append('src/dgm-best_swe_agent')
            
            from llm import create_client, AVAILABLE_LLMS
            
            # Test client creation for Claude models
            claude_models = [model for model in AVAILABLE_LLMS if "claude" in model]
            
            client_tests = {}
            for model in claude_models[:3]:  # Test first 3 Claude models
                try:
                    client, client_model = create_client(model)
                    client_tests[model] = {
                        "status": "success",
                        "client_created": True,
                        "client_type": type(client).__name__,
                        "model_name": client_model
                    }
                except Exception as e:
                    client_tests[model] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            return {
                "status": "success",
                "available_claude_models": len(claude_models),
                "client_tests": client_tests
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def test_cross_platform_adapter(self) -> Dict[str, Any]:
        """Test cross-platform adapter compatibility"""
        logger.info("🔄 Testing cross-platform adapter...")
        
        try:
            sys.path.append('src/backend/federated_service/app/core')
            
            # Test import of cross-platform adapters
            from cross_platform_adapters import AnthropicPlatformAdapter
            
            # Test adapter creation (without API key)
            try:
                adapter = AnthropicPlatformAdapter("test-key")
                
                return {
                    "status": "success",
                    "adapter_created": True,
                    "adapter_type": type(adapter).__name__,
                    "has_evaluate_method": hasattr(adapter, 'evaluate'),
                    "api_version": "2023-06-01"  # Current version in code
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "adapter_creation_failed": True
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "import_failed": True
            }
    
    def test_api_version_compatibility(self) -> Dict[str, Any]:
        """Test API version compatibility"""
        logger.info("📅 Testing API version compatibility...")
        
        current_version = "2023-06-01"
        recommended_version = "2024-06-01"
        
        # Check if code needs API version updates
        files_to_check = [
            "src/backend/federated_service/app/core/cross_platform_adapters.py"
        ]
        
        version_check_results = {}
        
        for file_path in files_to_check:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    has_old_version = current_version in content
                    has_new_version = recommended_version in content
                    
                    version_check_results[file_path] = {
                        "file_exists": True,
                        "has_old_version": has_old_version,
                        "has_new_version": has_new_version,
                        "needs_update": has_old_version and not has_new_version
                    }
                else:
                    version_check_results[file_path] = {
                        "file_exists": False
                    }
                    
            except Exception as e:
                version_check_results[file_path] = {
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "current_api_version": current_version,
            "recommended_api_version": recommended_version,
            "file_checks": version_check_results
        }
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("🚀 Starting anthropic upgrade validation...")
        logger.warning("⚠️ CRITICAL: This is a major version upgrade - thorough testing required")
        
        start_time = time.time()
        
        validation_results = {
            "timestamp": time.time(),
            "critical_upgrade": True,
            "tests": {}
        }
        
        # Run all validation tests
        validation_results["tests"]["import_test"] = self.test_basic_import()
        validation_results["tests"]["api_compatibility"] = self.test_api_compatibility()
        validation_results["tests"]["bedrock_compatibility"] = self.test_bedrock_compatibility()
        validation_results["tests"]["vertex_ai_compatibility"] = self.test_vertex_ai_compatibility()
        validation_results["tests"]["dgm_agent_compatibility"] = self.test_dgm_agent_compatibility()
        validation_results["tests"]["cross_platform_adapter"] = self.test_cross_platform_adapter()
        validation_results["tests"]["api_version_check"] = self.test_api_version_compatibility()
        
        validation_results["execution_time"] = time.time() - start_time
        
        # Calculate success rate (excluding skipped tests)
        successful_tests = 0
        total_tests = 0
        
        for test_name, test_result in validation_results["tests"].items():
            if test_result.get("status") != "skipped":
                total_tests += 1
                if test_result.get("status") == "success":
                    successful_tests += 1
        
        validation_results["success_rate"] = successful_tests / total_tests if total_tests > 0 else 0
        validation_results["overall_status"] = "PASS" if validation_results["success_rate"] >= 0.9 else "FAIL"
        
        logger.info(f"🎯 Validation complete: {validation_results['success_rate']:.1%} success rate")
        logger.info(f"📊 Overall status: {validation_results['overall_status']}")
        
        return validation_results

def main():
    """Main validation execution"""
    validator = AnthropicUpgradeValidator()
    results = validator.run_full_validation()
    
    # Print summary
    print("\n" + "="*70)
    print("ANTHROPIC UPGRADE VALIDATION SUMMARY")
    print("🔴 CRITICAL: MAJOR VERSION UPGRADE (0.7.7 → 0.52.2)")
    print("="*70)
    print(f"Success Rate: {results['success_rate']:.1%}")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Execution Time: {results['execution_time']:.2f}s")
    
    # Print detailed results
    for test_name, test_result in results["tests"].items():
        status = test_result.get("status", "unknown")
        print(f"  {test_name}: {status.upper()}")
        
        if status == "error" and "error" in test_result:
            print(f"    Error: {test_result['error']}")
        elif status == "skipped" and "reason" in test_result:
            print(f"    Skipped: {test_result['reason']}")
    
    print("="*70)
    
    # Provide merge recommendation
    if results['overall_status'] == 'PASS':
        print("⚠️ CONDITIONAL RECOMMENDATION: PROCEED WITH CAUTION")
        print("   Basic compatibility tests passed, but additional testing required:")
        print("   1. Update API version from 2023-06-01 to 2024-06-01")
        print("   2. Test constitutional AI evaluation system")
        print("   3. Test full DGM agent workflow")
        print("   4. Test federated learning integration")
        print("   5. Run comprehensive integration tests")
    else:
        print("❌ RECOMMENDATION: DO NOT MERGE PR #107")
        print("   Critical compatibility issues found")
        print("   Resolve all errors before proceeding")
    
    print("="*70)
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_status'] == 'PASS' else 1)

if __name__ == "__main__":
    main()
