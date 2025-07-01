#!/usr/bin/env python3
"""
Hunyuan A13B Integration Tests for ACGS-PGP System

Tests the integration of Tencent Hunyuan A13B model with ACGS-PGP
constitutional governance framework, ensuring compliance with
constitutional hash cdd01ef066bc6cf2 and performance targets.
"""

import unittest
import time
import requests
import json
import subprocess
from typing import Dict, Any, List
from pathlib import Path


class TestHunyuanACGSIntegration(unittest.TestCase):
    """Test Hunyuan A13B integration with ACGS-PGP system."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.base_url = "http://localhost:8000"
        cls.constitutional_hash = "cdd01ef066bc6cf2"
        cls.performance_targets = {
            "response_time_ms": 2000,  # Sub-2s response times
            "constitutional_compliance": 0.95,  # >95% compliance
            "availability": 0.999,  # 99.9% availability
        }

        # Check if Hunyuan service is running
        cls._wait_for_service()

    @classmethod
    def _wait_for_service(cls, max_wait=300):
        """Wait for Hunyuan service to be ready."""
        print("🔍 Waiting for Hunyuan service to be ready...")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Hunyuan service is ready")
                    return
            except requests.RequestException:
                pass

            time.sleep(5)

        raise RuntimeError("Hunyuan service not available within timeout")

    def test_service_health(self):
        """Test basic service health and availability."""
        print("\n=== Testing Service Health ===")

        response = requests.get(f"{self.base_url}/health", timeout=30)
        self.assertEqual(response.status_code, 200)

        health_data = response.json()
        print(f"✓ Health check passed: {health_data}")

        # Check for constitutional hash if available
        if "constitutional_hash" in health_data:
            self.assertEqual(
                health_data["constitutional_hash"],
                self.constitutional_hash,
                "Constitutional hash mismatch",
            )
            print(f"✓ Constitutional hash verified: {self.constitutional_hash}")

    def test_chinese_governance_analysis(self):
        """Test Chinese governance analysis capabilities."""
        print("\n=== Testing Chinese Governance Analysis ===")

        test_prompt = """
        请分析以下政策建议的合规性：
        建议实施更严格的数据保护法规，确保公民隐私权得到充分保护。
        请从宪法合规性角度进行评估。
        """

        payload = {
            "model": "hunyuan-a13b",
            "messages": [
                {
                    "role": "system",
                    "content": f"你是中国治理专家。Constitutional Hash: {self.constitutional_hash}",
                },
                {"role": "user", "content": test_prompt},
            ],
            "max_tokens": 500,
            "temperature": 0.7,
        }

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/v1/chat/completions", json=payload, timeout=30
        )
        response_time = (time.time() - start_time) * 1000

        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIn("choices", result)
        self.assertGreater(len(result["choices"]), 0)

        content = result["choices"][0]["message"]["content"]
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 50)

        # Check response time target
        self.assertLess(
            response_time,
            self.performance_targets["response_time_ms"],
            f"Response time {response_time:.1f}ms exceeds target",
        )

        print(f"✓ Chinese governance analysis completed in {response_time:.1f}ms")
        print(f"✓ Response length: {len(content)} characters")

    def test_multilingual_translation(self):
        """Test multilingual translation capabilities."""
        print("\n=== Testing Multilingual Translation ===")

        test_cases = [
            {
                "source": "Constitutional governance requires transparency and accountability.",
                "target_lang": "Chinese",
                "expected_keywords": ["宪法", "治理", "透明", "问责"],
            },
            {
                "source": "宪法合规性是民主治理的基础。",
                "target_lang": "English",
                "expected_keywords": [
                    "constitutional",
                    "compliance",
                    "democratic",
                    "governance",
                ],
            },
        ]

        for i, test_case in enumerate(test_cases):
            with self.subTest(case=i):
                payload = {
                    "model": "hunyuan-a13b",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a multilingual translator. Constitutional Hash: {self.constitutional_hash}",
                        },
                        {
                            "role": "user",
                            "content": f"Translate to {test_case['target_lang']}: {test_case['source']}",
                        },
                    ],
                    "max_tokens": 200,
                    "temperature": 0.3,
                }

                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions", json=payload, timeout=30
                )
                response_time = (time.time() - start_time) * 1000

                self.assertEqual(response.status_code, 200)

                result = response.json()
                translation = result["choices"][0]["message"]["content"]

                # Check if translation contains expected keywords
                translation_lower = translation.lower()
                found_keywords = [
                    kw
                    for kw in test_case["expected_keywords"]
                    if kw.lower() in translation_lower
                ]

                self.assertGreater(
                    len(found_keywords),
                    0,
                    f"Translation missing expected keywords: {test_case['expected_keywords']}",
                )

                print(f"✓ Translation {i+1} completed in {response_time:.1f}ms")
                print(f"  Found keywords: {found_keywords}")

    def test_cross_cultural_analysis(self):
        """Test cross-cultural analysis capabilities."""
        print("\n=== Testing Cross-Cultural Analysis ===")

        test_prompt = """
        Analyze the cultural differences in governance approaches between 
        Western democratic systems and East Asian consensus-building models.
        Focus on constitutional frameworks and decision-making processes.
        """

        payload = {
            "model": "hunyuan-a13b",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a cross-cultural analyst. Constitutional Hash: {self.constitutional_hash}",
                },
                {"role": "user", "content": test_prompt},
            ],
            "max_tokens": 600,
            "temperature": 0.7,
        }

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/v1/chat/completions", json=payload, timeout=30
        )
        response_time = (time.time() - start_time) * 1000

        self.assertEqual(response.status_code, 200)

        result = response.json()
        analysis = result["choices"][0]["message"]["content"]

        # Check for balanced analysis keywords
        expected_concepts = [
            "democratic",
            "consensus",
            "constitutional",
            "cultural",
            "governance",
            "decision",
            "framework",
        ]

        analysis_lower = analysis.lower()
        found_concepts = [
            concept for concept in expected_concepts if concept in analysis_lower
        ]

        self.assertGreaterEqual(
            len(found_concepts),
            4,
            f"Analysis should cover key concepts: {expected_concepts}",
        )

        print(f"✓ Cross-cultural analysis completed in {response_time:.1f}ms")
        print(f"✓ Covered concepts: {found_concepts}")

    def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""
        print("\n=== Testing Constitutional Compliance Validation ===")

        # Test with compliant content
        compliant_prompt = (
            "Explain the importance of constitutional rights in democratic governance."
        )

        payload = {
            "model": "hunyuan-a13b",
            "messages": [
                {
                    "role": "system",
                    "content": f"Ensure constitutional compliance. Hash: {self.constitutional_hash}",
                },
                {"role": "user", "content": compliant_prompt},
            ],
            "max_tokens": 300,
            "temperature": 0.5,
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions", json=payload, timeout=30
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # Check for constitutional compliance indicators
        compliance_indicators = [
            "constitutional",
            "rights",
            "democratic",
            "governance",
            "law",
            "legal",
            "framework",
            "protection",
        ]

        content_lower = content.lower()
        found_indicators = [
            indicator
            for indicator in compliance_indicators
            if indicator in content_lower
        ]

        compliance_score = len(found_indicators) / len(compliance_indicators)

        self.assertGreaterEqual(
            compliance_score,
            self.performance_targets["constitutional_compliance"],
            f"Constitutional compliance score {compliance_score:.2f} below target",
        )

        print(f"✓ Constitutional compliance score: {compliance_score:.2f}")
        print(f"✓ Found indicators: {found_indicators}")

    def test_performance_under_load(self):
        """Test performance under concurrent load."""
        print("\n=== Testing Performance Under Load ===")

        import concurrent.futures
        import threading

        def make_request():
            payload = {
                "model": "hunyuan-a13b",
                "messages": [
                    {
                        "role": "user",
                        "content": "Briefly explain constitutional governance principles.",
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.5,
            }

            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions", json=payload, timeout=30
                )
                response_time = (time.time() - start_time) * 1000
                return {
                    "success": response.status_code == 200,
                    "response_time": response_time,
                    "status_code": response.status_code,
                }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": (time.time() - start_time) * 1000,
                    "error": str(e),
                }

        # Run 10 concurrent requests
        num_requests = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / num_requests

        if successful_requests:
            avg_response_time = sum(
                r["response_time"] for r in successful_requests
            ) / len(successful_requests)
            max_response_time = max(r["response_time"] for r in successful_requests)
        else:
            avg_response_time = float("inf")
            max_response_time = float("inf")

        # Validate performance targets
        self.assertGreaterEqual(
            success_rate, 0.9, f"Success rate {success_rate:.2f} below 90%"
        )

        self.assertLess(
            avg_response_time,
            self.performance_targets["response_time_ms"],
            f"Average response time {avg_response_time:.1f}ms exceeds target",
        )

        print(
            f"✓ Load test completed: {len(successful_requests)}/{num_requests} successful"
        )
        print(f"✓ Success rate: {success_rate:.2f}")
        print(f"✓ Average response time: {avg_response_time:.1f}ms")
        print(f"✓ Max response time: {max_response_time:.1f}ms")


if __name__ == "__main__":
    unittest.main(verbosity=2)
