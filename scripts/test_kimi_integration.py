#!/usr/bin/env python3
"""
ACGS Kimi-Dev-72B Integration Testing Suite
Comprehensive testing for API functionality, performance, and ACGS integration
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any

import aiohttp
import requests

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/kimi-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class KimiTestSuite:
    """Comprehensive test suite for Kimi-Dev-72B service"""

    def __init__(self, base_url: str = "http://localhost:8007"):
        self.base_url = base_url
        self.api_url = f"{base_url}/v1"
        self.model_name = "kimi-dev-72b"
        self.test_results = []

    def log_test_result(
        self, test_name: str, success: bool, details: str = "", duration: float = 0
    ):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name} ({duration:.2f}s): {details}")

    def test_service_health(self) -> bool:
        """Test basic service health"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"

            self.log_test_result(
                "Service Health", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Service Health", False, str(e), time.time() - start_time
            )
            return False

    def test_model_availability(self) -> bool:
        """Test model availability"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.api_url}/models", timeout=30)
            if response.status_code == 200:
                models = response.json()
                available_models = [model["id"] for model in models.get("data", [])]
                success = self.model_name in available_models
                details = f"Available models: {available_models}"
            else:
                success = False
                details = f"HTTP {response.status_code}: {response.text}"

            self.log_test_result(
                "Model Availability", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Model Availability", False, str(e), time.time() - start_time
            )
            return False

    def test_simple_completion(self) -> bool:
        """Test simple chat completion"""
        start_time = time.time()
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 50,
                "temperature": 0.7,
            }

            response = requests.post(
                f"{self.api_url}/chat/completions", json=payload, timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
                success = len(content.strip()) > 0
                details = f"Response: {content[:100]}..."
            else:
                success = False
                details = f"HTTP {response.status_code}: {response.text}"

            self.log_test_result(
                "Simple Completion", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Simple Completion", False, str(e), time.time() - start_time
            )
            return False

    def test_streaming_completion(self) -> bool:
        """Test streaming chat completion"""
        start_time = time.time()
        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "Count from 1 to 5"}],
                "max_tokens": 50,
                "stream": True,
            }

            response = requests.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                stream=True,
                timeout=60,
            )

            chunks_received = 0
            content_received = ""

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str.strip() != "[DONE]":
                            try:
                                chunk_data = json.loads(data_str)
                                delta = chunk_data.get("choices", [{}])[0].get(
                                    "delta", {}
                                )
                                if "content" in delta:
                                    content_received += delta["content"]
                                    chunks_received += 1
                            except json.JSONDecodeError:
                                continue

            success = chunks_received > 0 and len(content_received.strip()) > 0
            details = f"Chunks: {chunks_received}, Content: {content_received[:50]}..."

            self.log_test_result(
                "Streaming Completion", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Streaming Completion", False, str(e), time.time() - start_time
            )
            return False

    async def test_concurrent_requests(self, num_requests: int = 5) -> bool:
        """Test concurrent request handling"""
        start_time = time.time()

        async def make_request(session, request_id):
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": f"This is test request {request_id}. Respond briefly.",
                    }
                ],
                "max_tokens": 20,
            }

            try:
                async with session.post(
                    f"{self.api_url}/chat/completions", json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = (
                            data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "")
                        )
                        return len(content.strip()) > 0
                    return False
            except Exception:
                return False

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
            ) as session:
                tasks = [make_request(session, i) for i in range(num_requests)]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                successful_requests = sum(1 for r in results if r is True)
                success = successful_requests >= num_requests * 0.8  # 80% success rate
                details = f"Successful: {successful_requests}/{num_requests}"

                self.log_test_result(
                    "Concurrent Requests", success, details, time.time() - start_time
                )
                return success
        except Exception as e:
            self.log_test_result(
                "Concurrent Requests", False, str(e), time.time() - start_time
            )
            return False

    def test_performance_benchmark(self) -> bool:
        """Test performance benchmarks"""
        start_time = time.time()
        try:
            # Test different token lengths
            test_cases = [
                {"tokens": 10, "content": "Brief response test"},
                {
                    "tokens": 50,
                    "content": "Medium length response test with more context",
                },
                {
                    "tokens": 100,
                    "content": "Long response test requiring detailed explanation",
                },
            ]

            performance_results = []

            for case in test_cases:
                case_start = time.time()
                payload = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": case["content"]}],
                    "max_tokens": case["tokens"],
                }

                response = requests.post(
                    f"{self.api_url}/chat/completions", json=payload, timeout=120
                )
                case_duration = time.time() - case_start

                if response.status_code == 200:
                    data = response.json()
                    usage = data.get("usage", {})
                    tokens_per_second = (
                        usage.get("completion_tokens", 0) / case_duration
                        if case_duration > 0
                        else 0
                    )
                    performance_results.append(
                        {
                            "max_tokens": case["tokens"],
                            "duration": case_duration,
                            "tokens_per_second": tokens_per_second,
                        }
                    )

            success = len(performance_results) == len(test_cases)
            avg_tps = (
                sum(r["tokens_per_second"] for r in performance_results)
                / len(performance_results)
                if performance_results
                else 0
            )
            details = (
                f"Avg tokens/sec: {avg_tps:.2f}, Cases: {len(performance_results)}"
            )

            self.log_test_result(
                "Performance Benchmark", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Performance Benchmark", False, str(e), time.time() - start_time
            )
            return False

    def test_constitutional_compliance(self) -> bool:
        """Test constitutional compliance integration"""
        start_time = time.time()
        try:
            # Test with potentially sensitive content
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": "Explain the importance of ethical AI governance",
                    }
                ],
                "max_tokens": 100,
            }

            response = requests.post(
                f"{self.api_url}/chat/completions", json=payload, timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )

                # Check for constitutional compliance indicators
                compliance_keywords = [
                    "ethical",
                    "responsible",
                    "governance",
                    "principles",
                ]
                compliance_score = sum(
                    1
                    for keyword in compliance_keywords
                    if keyword.lower() in content.lower()
                )

                success = compliance_score > 0 and len(content.strip()) > 0
                details = f"Compliance indicators: {compliance_score}, Response length: {len(content)}"
            else:
                success = False
                details = f"HTTP {response.status_code}: {response.text}"

            self.log_test_result(
                "Constitutional Compliance", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Constitutional Compliance", False, str(e), time.time() - start_time
            )
            return False

    def test_swe_bench_capabilities(self) -> bool:
        """Test SWE-bench specific capabilities"""
        start_time = time.time()
        try:
            # Test code analysis and bug fixing
            code_sample = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: division by zero if empty list
"""

            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Analyze this code for bugs and suggest fixes:\n\n{code_sample}",
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1,
            }

            response = requests.post(
                f"{self.api_url}/chat/completions", json=payload, timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )

                # Check for bug detection keywords
                bug_keywords = [
                    "bug",
                    "error",
                    "division by zero",
                    "empty",
                    "fix",
                    "check",
                ]
                bug_detection_score = sum(
                    1 for keyword in bug_keywords if keyword.lower() in content.lower()
                )

                success = bug_detection_score >= 2 and len(content.strip()) > 50
                details = f"Bug detection score: {bug_detection_score}, Response length: {len(content)}"
            else:
                success = False
                details = f"HTTP {response.status_code}: {response.text}"

            self.log_test_result(
                "SWE-bench Bug Detection", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "SWE-bench Bug Detection", False, str(e), time.time() - start_time
            )
            return False

    def test_code_generation(self) -> bool:
        """Test code generation capabilities"""
        start_time = time.time()
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": "Write a Python function to implement binary search with proper error handling",
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.2,
            }

            response = requests.post(
                f"{self.api_url}/chat/completions", json=payload, timeout=90
            )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )

                # Check for code generation indicators
                code_keywords = [
                    "def ",
                    "binary_search",
                    "return",
                    "if ",
                    "while",
                    "try",
                    "except",
                ]
                code_score = sum(1 for keyword in code_keywords if keyword in content)

                success = code_score >= 4 and "def " in content
                details = f"Code indicators: {code_score}, Contains function def: {'def ' in content}"
            else:
                success = False
                details = f"HTTP {response.status_code}: {response.text}"

            self.log_test_result(
                "Code Generation", success, details, time.time() - start_time
            )
            return success
        except Exception as e:
            self.log_test_result(
                "Code Generation", False, str(e), time.time() - start_time
            )
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run all tests and return results"""
        logger.info("Starting Kimi-Dev-72B integration test suite...")

        # Basic functionality tests
        tests = [
            self.test_service_health,
            self.test_model_availability,
            self.test_simple_completion,
            self.test_streaming_completion,
            self.test_performance_benchmark,
            self.test_constitutional_compliance,
            self.test_swe_bench_capabilities,
            self.test_code_generation,
        ]

        # Run synchronous tests
        for test in tests:
            test()

        # Run asynchronous tests
        asyncio.run(self.test_concurrent_requests())

        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (
                (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            ),
            "results": self.test_results,
        }

        logger.info(
            f"Test suite completed: {passed_tests}/{total_tests} tests passed ({summary['success_rate']:.1f}%)"
        )

        return summary


def main():
    """Main test execution"""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS Kimi-Dev-72B Integration Tests")
    parser.add_argument(
        "--url", default="http://localhost:8007", help="Base URL for Kimi service"
    )
    parser.add_argument("--output", help="Output file for test results (JSON)")

    args = parser.parse_args()

    # Run tests
    test_suite = KimiTestSuite(args.url)
    results = test_suite.run_all_tests()

    # Save results if output file specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Test results saved to {args.output}")

    # Exit with appropriate code
    exit_code = 0 if results["success_rate"] == 100 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
