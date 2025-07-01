#!/usr/bin/env python3
"""
ACGS-PGP AI Model Integration Test Script

Tests the integration of AI models (Google Gemini, DeepSeek-R1, NVIDIA Qwen, Nano-vLLM)
with the ACGS-PGP services and validates constitutional constraints.
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any
import requests


class AIModelIntegrationTester:
    """Test AI model integrations with ACGS-PGP services."""

    def __init__(self):
        self.base_url = "http://localhost"
        self.services = {
            "auth_service": 8000,
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
            "pgc_service": 8005,
            "ec_service": 8006,
            "nano_vllm": 8007,
        }
        self.test_results = {}

    def test_service_health(self, service_name: str, port: int) -> bool:
        """Test if a service is healthy."""
        try:
            response = requests.get(f"{self.base_url}:{port}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ {service_name} health check failed: {e}")
            return False

    def test_ai_model_endpoints(self) -> Dict[str, Any]:
        """Test AI model integration endpoints."""
        results = {}

        # Test AC Service constitutional analysis
        try:
            payload = {
                "content": "AI governance policy for constitutional compliance",
                "analysis_type": "constitutional_compliance",
            }
            response = requests.post(
                f"{self.base_url}:8001/api/v1/constitutional/analyze",
                json=payload,
                timeout=10,
            )
            results["ac_constitutional_analysis"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None,
            }
        except Exception as e:
            results["ac_constitutional_analysis"] = {"status": "error", "error": str(e)}

        # Test GS Service validation
        try:
            payload = {
                "content": "Test AI governance policy with constitutional constraints",
                "validation_type": "constitutional",
            }
            response = requests.post(
                f"{self.base_url}:8004/api/v1/validate", json=payload, timeout=10
            )
            results["gs_validation"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None,
            }
        except Exception as e:
            results["gs_validation"] = {"status": "error", "error": str(e)}

        # Test Nano-vLLM service
        try:
            response = requests.get(f"{self.base_url}:8007/health", timeout=5)
            results["nano_vllm_health"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "data": response.json() if response.status_code == 200 else None,
            }
        except Exception as e:
            results["nano_vllm_health"] = {"status": "error", "error": str(e)}

        return results

    def test_constitutional_constraints(self) -> Dict[str, Any]:
        """Test constitutional constraints and DGM safety patterns."""
        results = {}

        # Test constitutional hash validation
        try:
            response = requests.get(
                f"{self.base_url}:8001/api/v1/constitutional/rules", timeout=5
            )
            results["constitutional_rules"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "data": response.json() if response.status_code == 200 else None,
            }
        except Exception as e:
            results["constitutional_rules"] = {"status": "error", "error": str(e)}

        # Test compliance scoring
        try:
            payload = {
                "content": "AI model decision with constitutional implications",
                "scoring_criteria": ["transparency", "accountability", "fairness"],
            }
            response = requests.post(
                f"{self.base_url}:8001/api/v1/constitutional/compliance-score",
                json=payload,
                timeout=10,
            )
            results["compliance_scoring"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None,
            }
        except Exception as e:
            results["compliance_scoring"] = {"status": "error", "error": str(e)}

        return results

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive AI model integration tests."""
        print("🚀 Starting ACGS-PGP AI Model Integration Tests")
        print("=" * 60)

        # Test service health
        print("\n📊 Testing Service Health:")
        health_results = {}
        for service_name, port in self.services.items():
            is_healthy = self.test_service_health(service_name, port)
            health_results[service_name] = is_healthy
            status = "✅" if is_healthy else "❌"
            print(
                f"{status} {service_name} (port {port}): {'Healthy' if is_healthy else 'Unhealthy'}"
            )

        # Test AI model endpoints
        print("\n🤖 Testing AI Model Endpoints:")
        ai_results = self.test_ai_model_endpoints()
        for test_name, result in ai_results.items():
            status = "✅" if result["status"] == "success" else "❌"
            print(f"{status} {test_name}: {result['status']}")
            if "response_time" in result:
                print(f"   Response time: {result['response_time']:.3f}s")

        # Test constitutional constraints
        print("\n⚖️ Testing Constitutional Constraints:")
        constitutional_results = self.test_constitutional_constraints()
        for test_name, result in constitutional_results.items():
            status = "✅" if result["status"] == "success" else "❌"
            print(f"{status} {test_name}: {result['status']}")
            if "response_time" in result:
                print(f"   Response time: {result['response_time']:.3f}s")

        # Compile final results
        final_results = {
            "timestamp": time.time(),
            "service_health": health_results,
            "ai_model_endpoints": ai_results,
            "constitutional_constraints": constitutional_results,
            "summary": {
                "healthy_services": sum(health_results.values()),
                "total_services": len(health_results),
                "successful_ai_tests": sum(
                    1 for r in ai_results.values() if r["status"] == "success"
                ),
                "total_ai_tests": len(ai_results),
                "successful_constitutional_tests": sum(
                    1
                    for r in constitutional_results.values()
                    if r["status"] == "success"
                ),
                "total_constitutional_tests": len(constitutional_results),
            },
        }

        print("\n📋 Test Summary:")
        summary = final_results["summary"]
        print(
            f"   Services: {summary['healthy_services']}/{summary['total_services']} healthy"
        )
        print(
            f"   AI Model Tests: {summary['successful_ai_tests']}/{summary['total_ai_tests']} passed"
        )
        print(
            f"   Constitutional Tests: {summary['successful_constitutional_tests']}/{summary['total_constitutional_tests']} passed"
        )

        overall_success = (
            summary["healthy_services"] >= 6
            and summary["successful_ai_tests"] >= 2  # At least 6/8 services healthy
            and summary[  # At least 2/3 AI tests passed
                "successful_constitutional_tests"
            ]
            >= 1  # At least 1/2 constitutional tests passed
        )

        print(f"\n🎯 Overall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")

        return final_results


def main():
    """Main function to run AI model integration tests."""
    tester = AIModelIntegrationTester()
    results = tester.run_comprehensive_test()

    # Save results to file
    with open("ai_model_integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: ai_model_integration_test_results.json")

    # Exit with appropriate code
    summary = results["summary"]
    overall_success = (
        summary["healthy_services"] >= 6
        and summary["successful_ai_tests"] >= 2
        and summary["successful_constitutional_tests"] >= 1
    )

    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
