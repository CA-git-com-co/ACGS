#!/usr/bin/env python3
"""
ACGS Nano-vLLM Constitutional AI Load Testing Suite

This script performs comprehensive load testing of the Nano-vLLM system
with realistic constitutional AI workloads to validate performance,
stability, and compliance scoring under sustained load.
"""

import argparse
import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for load testing."""

    base_url: str = "http://localhost:8100"
    concurrent_users: int = 20
    test_duration_minutes: int = 30
    ramp_up_minutes: int = 5
    constitutional_reasoning_weight: float = 0.6  # 60% constitutional reasoning
    chat_completion_weight: float = 0.4  # 40% chat completions
    target_response_time_seconds: float = 2.0
    max_response_time_seconds: float = 5.0
    min_compliance_score: float = 0.75


@dataclass
class TestResult:
    """Individual test result."""

    endpoint: str
    request_time: float
    response_time: float
    status_code: int
    success: bool
    compliance_score: float | None = None
    error_message: str | None = None


@dataclass
class LoadTestResults:
    """Aggregated load test results."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list[float] = field(default_factory=list)
    compliance_scores: list[float] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None


class ConstitutionalAILoadTester:
    """Load tester for Constitutional AI workloads."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = LoadTestResults()
        self.session: aiohttp.ClientSession | None = None

        # Constitutional reasoning test scenarios
        self.constitutional_scenarios = [
            {
                "content": "Should we implement a policy that restricts user access based on geographic location?",
                "domain": "governance",
                "context": "Privacy and accessibility considerations",
                "reasoning_depth": "standard",
            },
            {
                "content": "Is it ethical to use AI for automated decision-making in hiring processes?",
                "domain": "ethics",
                "context": "Employment fairness and bias prevention",
                "reasoning_depth": "deep",
            },
            {
                "content": "How should we handle user data when implementing new features?",
                "domain": "privacy",
                "context": "GDPR compliance and user consent",
                "reasoning_depth": "standard",
            },
            {
                "content": "What are the implications of implementing real-time content moderation?",
                "domain": "governance",
                "context": "Free speech vs. harmful content",
                "reasoning_depth": "deep",
            },
            {
                "content": "Should AI systems be required to explain their decision-making processes?",
                "domain": "transparency",
                "context": "Explainable AI and accountability",
                "reasoning_depth": "standard",
            },
        ]

        # Chat completion test scenarios
        self.chat_scenarios = [
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant focused on constitutional governance.",
                    },
                    {
                        "role": "user",
                        "content": "Explain the importance of transparency in AI governance.",
                    },
                ]
            },
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the key principles of ethical AI development?",
                    }
                ]
            },
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert in constitutional law and AI ethics.",
                    },
                    {
                        "role": "user",
                        "content": "How can we ensure AI systems respect human rights?",
                    },
                ]
            },
        ]

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def test_constitutional_reasoning(
        self, scenario: dict[str, Any]
    ) -> TestResult:
        """Test constitutional reasoning endpoint."""
        start_time = time.time()

        try:
            async with self.session.post(
                f"{self.config.base_url}/v1/constitutional-reasoning",
                json=scenario,
                headers={"Content-Type": "application/json"},
            ) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    compliance_score = data.get("constitutional_compliance", 0.0)

                    return TestResult(
                        endpoint="constitutional-reasoning",
                        request_time=start_time,
                        response_time=response_time,
                        status_code=response.status,
                        success=True,
                        compliance_score=compliance_score,
                    )
                error_text = await response.text()
                return TestResult(
                    endpoint="constitutional-reasoning",
                    request_time=start_time,
                    response_time=response_time,
                    status_code=response.status,
                    success=False,
                    error_message=f"HTTP {response.status}: {error_text}",
                )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="constitutional-reasoning",
                request_time=start_time,
                response_time=response_time,
                status_code=0,
                success=False,
                error_message=str(e),
            )

    async def test_chat_completion(self, scenario: dict[str, Any]) -> TestResult:
        """Test chat completion endpoint."""
        start_time = time.time()

        payload = {
            "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            "messages": scenario["messages"],
            "max_tokens": 150,
            "temperature": 0.7,
        }

        try:
            async with self.session.post(
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    data = await response.json()

                    return TestResult(
                        endpoint="chat-completions",
                        request_time=start_time,
                        response_time=response_time,
                        status_code=response.status,
                        success=True,
                    )
                error_text = await response.text()
                return TestResult(
                    endpoint="chat-completions",
                    request_time=start_time,
                    response_time=response_time,
                    status_code=response.status,
                    success=False,
                    error_message=f"HTTP {response.status}: {error_text}",
                )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="chat-completions",
                request_time=start_time,
                response_time=response_time,
                status_code=0,
                success=False,
                error_message=str(e),
            )

    async def worker(self, worker_id: int, duration_seconds: int):
        """Individual worker that generates load."""
        logger.info(f"Worker {worker_id} starting for {duration_seconds} seconds")

        end_time = time.time() + duration_seconds
        request_count = 0

        while time.time() < end_time:
            # Choose endpoint based on weights
            if (
                asyncio.get_event_loop().time() % 1
                < self.config.constitutional_reasoning_weight
            ):
                # Constitutional reasoning request
                scenario = self.constitutional_scenarios[
                    request_count % len(self.constitutional_scenarios)
                ]
                result = await self.test_constitutional_reasoning(scenario)
            else:
                # Chat completion request
                scenario = self.chat_scenarios[request_count % len(self.chat_scenarios)]
                result = await self.test_chat_completion(scenario)

            # Record result
            self.results.total_requests += 1
            if result.success:
                self.results.successful_requests += 1
                self.results.response_times.append(result.response_time)
                if result.compliance_score is not None:
                    self.results.compliance_scores.append(result.compliance_score)
            else:
                self.results.failed_requests += 1
                if result.error_message:
                    self.results.errors.append(result.error_message)

            request_count += 1

            # Brief pause between requests
            await asyncio.sleep(0.1)

        logger.info(f"Worker {worker_id} completed {request_count} requests")

    async def run_load_test(self) -> LoadTestResults:
        """Run the complete load test."""
        logger.info(
            f"Starting load test with {self.config.concurrent_users} concurrent users"
        )
        logger.info(f"Test duration: {self.config.test_duration_minutes} minutes")
        logger.info(f"Ramp-up period: {self.config.ramp_up_minutes} minutes")

        self.results.start_time = datetime.now()

        # Calculate timing
        total_duration = self.config.test_duration_minutes * 60
        ramp_up_duration = self.config.ramp_up_minutes * 60

        # Start workers with ramp-up
        workers = []
        for i in range(self.config.concurrent_users):
            # Stagger worker starts during ramp-up period
            start_delay = (i / self.config.concurrent_users) * ramp_up_duration
            worker_duration = total_duration - start_delay

            worker_task = asyncio.create_task(
                self._delayed_worker(i, start_delay, worker_duration)
            )
            workers.append(worker_task)

        # Wait for all workers to complete
        await asyncio.gather(*workers)

        self.results.end_time = datetime.now()
        return self.results

    async def _delayed_worker(self, worker_id: int, delay: float, duration: float):
        """Worker with delayed start for ramp-up."""
        await asyncio.sleep(delay)
        await self.worker(worker_id, int(duration))

    def analyze_results(self) -> dict[str, Any]:
        """Analyze and summarize test results."""
        if not self.results.response_times:
            return {"error": "No successful requests recorded"}

        # Calculate statistics
        response_times = self.results.response_times
        compliance_scores = self.results.compliance_scores

        analysis = {
            "summary": {
                "total_requests": self.results.total_requests,
                "successful_requests": self.results.successful_requests,
                "failed_requests": self.results.failed_requests,
                "success_rate": self.results.successful_requests
                / max(1, self.results.total_requests),
                "test_duration": (
                    self.results.end_time - self.results.start_time
                ).total_seconds(),
            },
            "performance": {
                "avg_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "p95_response_time": self._percentile(response_times, 95),
                "p99_response_time": self._percentile(response_times, 99),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
            },
            "constitutional_compliance": {
                "avg_compliance_score": (
                    statistics.mean(compliance_scores) if compliance_scores else 0
                ),
                "min_compliance_score": (
                    min(compliance_scores) if compliance_scores else 0
                ),
                "compliance_violations": len(
                    [
                        s
                        for s in compliance_scores
                        if s < self.config.min_compliance_score
                    ]
                ),
            },
            "quality_metrics": {
                "target_response_time_met": len(
                    [
                        t
                        for t in response_times
                        if t <= self.config.target_response_time_seconds
                    ]
                )
                / len(response_times),
                "max_response_time_exceeded": len(
                    [
                        t
                        for t in response_times
                        if t > self.config.max_response_time_seconds
                    ]
                ),
                "requests_per_second": self.results.total_requests
                / (self.results.end_time - self.results.start_time).total_seconds(),
            },
        }

        return analysis

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


async def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(
        description="ACGS Nano-vLLM Constitutional AI Load Test"
    )
    parser.add_argument(
        "--url", default="http://localhost:8100", help="Base URL for Nano-vLLM service"
    )
    parser.add_argument(
        "--users", type=int, default=20, help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Test duration in minutes"
    )
    parser.add_argument(
        "--ramp-up", type=int, default=5, help="Ramp-up period in minutes"
    )
    parser.add_argument("--output", help="Output file for results (JSON)")

    args = parser.parse_args()

    config = LoadTestConfig(
        base_url=args.url,
        concurrent_users=args.users,
        test_duration_minutes=args.duration,
        ramp_up_minutes=args.ramp_up,
    )

    async with ConstitutionalAILoadTester(config) as tester:
        # Run the load test
        results = await tester.run_load_test()

        # Analyze results
        analysis = tester.analyze_results()

        # Print summary
        print("\n" + "=" * 60)
        print("ACGS Nano-vLLM Load Test Results")
        print("=" * 60)
        print(f"Total Requests: {analysis['summary']['total_requests']}")
        print(f"Success Rate: {analysis['summary']['success_rate']:.2%}")
        print(
            f"Average Response Time: {analysis['performance']['avg_response_time']:.3f}s"
        )
        print(
            f"95th Percentile Response Time: {analysis['performance']['p95_response_time']:.3f}s"
        )
        print(
            f"Average Compliance Score: {analysis['constitutional_compliance']['avg_compliance_score']:.3f}"
        )
        print(
            f"Requests/Second: {analysis['quality_metrics']['requests_per_second']:.2f}"
        )

        # Check success criteria
        print("\n" + "=" * 60)
        print("Success Criteria Validation")
        print("=" * 60)

        criteria_met = True

        if (
            analysis["performance"]["p95_response_time"]
            <= config.target_response_time_seconds
        ):
            print(
                f"✅ Response time target met (≤{config.target_response_time_seconds}s)"
            )
        else:
            print(
                f"❌ Response time target missed (>{config.target_response_time_seconds}s)"
            )
            criteria_met = False

        if (
            analysis["constitutional_compliance"]["avg_compliance_score"]
            >= config.min_compliance_score
        ):
            print(f"✅ Compliance score target met (≥{config.min_compliance_score})")
        else:
            print(f"❌ Compliance score target missed (<{config.min_compliance_score})")
            criteria_met = False

        if analysis["summary"]["success_rate"] >= 0.95:
            print("✅ Success rate target met (≥95%)")
        else:
            print("❌ Success rate target missed (<95%)")
            criteria_met = False

        if criteria_met:
            print("\n🎉 All success criteria met!")
        else:
            print("\n⚠️  Some success criteria not met")

        # Save results if output file specified
        if args.output:
            with open(args.output, "w") as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
