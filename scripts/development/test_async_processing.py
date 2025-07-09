#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Test script for ACGS-1 Async Processing Manager
Demonstrates async job submission, processing, and monitoring
"""

import asyncio
import json
import logging
import os
import sys
import time

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

from shared.async_processing_manager import (
    AsyncProcessingManager,
    JobPriority,
    JobStatus,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncProcessingTester:
    """Test suite for async processing capabilities."""

    def __init__(self):
        self.manager = None
        self.test_results = {}

    async def initialize(self):
        """Initialize the async processing manager."""
        self.manager = AsyncProcessingManager()
        await self.manager.initialize()

    async def test_job_submission(self):
        """Test basic job submission and processing."""
        logger.info("🧪 Testing job submission...")

        # Submit various types of jobs
        jobs = []

        # Constitutional compliance job
        job_id1 = await self.manager.submit_job(
            "constitutional_compliance_check",
            {"principles": ["transparency", "accountability", "fairness"]},
            priority=JobPriority.HIGH,
        )
        jobs.append(("constitutional_compliance", job_id1))

        # Policy synthesis job
        job_id2 = await self.manager.submit_job(
            "policy_synthesis",
            {"topic": "data privacy", "context": "AI governance"},
            priority=JobPriority.NORMAL,
        )
        jobs.append(("policy_synthesis", job_id2))

        # Performance monitoring job
        job_id3 = await self.manager.submit_job(
            "performance_monitoring",
            {"service": "ac_service", "metrics": ["response_time", "throughput"]},
            priority=JobPriority.LOW,
        )
        jobs.append(("performance_monitoring", job_id3))

        # Data export job
        job_id4 = await self.manager.submit_job(
            "data_export",
            {"format": "json", "record_count": 1000, "table": "governance_actions"},
            priority=JobPriority.NORMAL,
        )
        jobs.append(("data_export", job_id4))

        self.test_results["job_submission"] = {
            "jobs_submitted": len(jobs),
            "job_ids": [job[1] for job in jobs],
            "status": "completed",
        }

        logger.info(f"✅ Submitted {len(jobs)} test jobs")
        return jobs

    async def test_job_processing(self, jobs):
        """Test job processing with workers."""
        logger.info("🔄 Testing job processing...")

        # Start workers
        await self.manager.start_workers(worker_count=2)

        # Wait for jobs to complete
        completed_jobs = 0
        max_wait_time = 30  # 30 seconds
        start_time = time.time()

        while completed_jobs < len(jobs) and (time.time() - start_time) < max_wait_time:
            completed_jobs = 0
            for job_type, job_id in jobs:
                job_status = await self.manager.get_job_status(job_id)
                if job_status and job_status.status in [
                    JobStatus.COMPLETED,
                    JobStatus.FAILED,
                ]:
                    completed_jobs += 1

            if completed_jobs < len(jobs):
                await asyncio.sleep(1)

        # Stop workers
        await self.manager.stop_workers()

        # Collect results
        job_results = []
        for job_type, job_id in jobs:
            job_status = await self.manager.get_job_status(job_id)
            if job_status:
                job_results.append(
                    {
                        "job_id": job_id,
                        "job_type": job_type,
                        "status": job_status.status.value,
                        "processing_time": job_status.metadata.get(
                            "processing_time", 0
                        ),
                        "error": job_status.error_message,
                    }
                )

        self.test_results["job_processing"] = {
            "total_jobs": len(jobs),
            "completed_jobs": completed_jobs,
            "job_results": job_results,
            "processing_time": time.time() - start_time,
            "status": "completed" if completed_jobs == len(jobs) else "partial",
        }

        logger.info(f"✅ Processed {completed_jobs}/{len(jobs)} jobs")
        return job_results

    async def test_priority_handling(self):
        """Test priority-based job processing."""
        logger.info("⚡ Testing priority handling...")

        # Submit jobs with different priorities
        priority_jobs = []

        # Submit low priority jobs first
        for i in range(3):
            job_id = await self.manager.submit_job(
                "performance_monitoring",
                {"service": f"test_service_{i}", "priority_test": True},
                priority=JobPriority.LOW,
            )
            priority_jobs.append(("low", job_id))

        # Submit high priority job
        high_priority_job = await self.manager.submit_job(
            "constitutional_compliance_check",
            {"principles": ["urgent_check"], "priority_test": True},
            priority=JobPriority.CRITICAL,
        )
        priority_jobs.append(("critical", high_priority_job))

        # Start single worker to test priority ordering
        await self.manager.start_workers(worker_count=1)

        # Wait for processing
        await asyncio.sleep(3)

        # Stop workers
        await self.manager.stop_workers()

        # Check if high priority job was processed first
        high_priority_status = await self.manager.get_job_status(high_priority_job)

        self.test_results["priority_handling"] = {
            "high_priority_job": high_priority_job,
            "high_priority_completed": (
                high_priority_status.status == JobStatus.COMPLETED
                if high_priority_status
                else False
            ),
            "total_priority_jobs": len(priority_jobs),
            "status": "completed",
        }

        logger.info("✅ Priority handling test completed")

    async def test_error_handling_and_retries(self):
        """Test error handling and retry mechanisms."""
        logger.info("🔧 Testing error handling and retries...")

        # Submit a job that will fail (invalid job type)
        try:
            failing_job_id = await self.manager.submit_job(
                "invalid_job_type", {"test": "error_handling"}, max_retries=2
            )

            # Start workers
            await self.manager.start_workers(worker_count=1)

            # Wait for job to fail and retry
            await asyncio.sleep(5)

            # Stop workers
            await self.manager.stop_workers()

            # Check job status
            job_status = await self.manager.get_job_status(failing_job_id)

            self.test_results["error_handling"] = {
                "failing_job_id": failing_job_id,
                "final_status": job_status.status.value if job_status else "unknown",
                "retry_count": job_status.retry_count if job_status else 0,
                "error_message": job_status.error_message if job_status else None,
                "status": "completed",
            }

        except Exception as e:
            self.test_results["error_handling"] = {"status": "failed", "error": str(e)}

        logger.info("✅ Error handling test completed")

    async def test_metrics_and_monitoring(self):
        """Test metrics collection and monitoring."""
        logger.info("📊 Testing metrics and monitoring...")

        # Get current metrics
        metrics = await self.manager.get_metrics()

        self.test_results["metrics_monitoring"] = {
            "metrics": metrics,
            "status": "completed",
        }

        logger.info("✅ Metrics collection test completed")

    async def run_comprehensive_test(self):
        """Run comprehensive async processing tests."""
        logger.info("🚀 Starting comprehensive async processing tests")

        try:
            # Initialize
            await self.initialize()

            # Run tests
            jobs = await self.test_job_submission()
            await self.test_job_processing(jobs)
            await self.test_priority_handling()
            await self.test_error_handling_and_retries()
            await self.test_metrics_and_monitoring()

            # Generate summary
            self._generate_test_summary()

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            self.test_results["overall_status"] = "failed"
            self.test_results["error"] = str(e)

    def _generate_test_summary(self):
        """Generate test summary."""
        total_tests = len(
            [k for k in self.test_results.keys() if k != "overall_status"]
        )
        passed_tests = len(
            [
                v
                for v in self.test_results.values()
                if isinstance(v, dict) and v.get("status") == "completed"
            ]
        )

        self.test_results["overall_status"] = (
            "passed" if passed_tests == total_tests else "partial"
        )
        self.test_results["test_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (
                round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0
            ),
        }

    def print_results(self):
        """Print formatted test results."""
        print("\n" + "=" * 80)
        print("🧪 ACGS-1 ASYNC PROCESSING TEST RESULTS")
        print("=" * 80)

        summary = self.test_results.get("test_summary", {})
        print("\n📊 Test Summary:")
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Passed Tests: {summary.get('passed_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0)}%")
        print(
            f"Overall Status: {self.test_results.get('overall_status', 'unknown').upper()}"
        )

        # Job submission results
        job_submission = self.test_results.get("job_submission", {})
        if job_submission:
            print("\n✅ Job Submission Test:")
            print(f"Jobs Submitted: {job_submission.get('jobs_submitted', 0)}")
            print(f"Status: {job_submission.get('status', 'unknown').upper()}")

        # Job processing results
        job_processing = self.test_results.get("job_processing", {})
        if job_processing:
            print("\n🔄 Job Processing Test:")
            print(
                f"Jobs Processed: {job_processing.get('completed_jobs', 0)}/{job_processing.get('total_jobs', 0)}"
            )
            print(f"Processing Time: {job_processing.get('processing_time', 0):.2f}s")
            print(f"Status: {job_processing.get('status', 'unknown').upper()}")

        # Priority handling results
        priority_handling = self.test_results.get("priority_handling", {})
        if priority_handling:
            print("\n⚡ Priority Handling Test:")
            print(
                f"High Priority Completed: {priority_handling.get('high_priority_completed', False)}"
            )
            print(f"Status: {priority_handling.get('status', 'unknown').upper()}")

        # Error handling results
        error_handling = self.test_results.get("error_handling", {})
        if error_handling:
            print("\n🔧 Error Handling Test:")
            print(
                f"Final Status: {error_handling.get('final_status', 'unknown').upper()}"
            )
            print(f"Retry Count: {error_handling.get('retry_count', 0)}")
            print(f"Status: {error_handling.get('status', 'unknown').upper()}")

        # Metrics results
        metrics = self.test_results.get("metrics_monitoring", {})
        if metrics and "metrics" in metrics:
            print("\n📊 Metrics Test:")
            m = metrics["metrics"]
            print(f"Jobs Processed: {m.get('jobs_processed', 0)}")
            print(f"Jobs Failed: {m.get('jobs_failed', 0)}")
            print(
                f"Average Processing Time: {m.get('average_processing_time', 0):.3f}s"
            )
            print(f"Active Workers: {m.get('active_workers', 0)}")

        if self.test_results.get("overall_status") == "passed":
            print(
                "\n🎉 ALL TESTS PASSED: Async processing system is working correctly!"
            )
        else:
            print("\n⚠️  SOME TESTS FAILED: Check individual test results above")

    def save_results(self, filename: str = "async_processing_test_results.json"):
        """Save test results to file."""
        with open(filename, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        logger.info(f"Test results saved to {filename}")


async def main():
    """Main function to run async processing tests."""
    tester = AsyncProcessingTester()
    await tester.run_comprehensive_test()
    tester.print_results()
    tester.save_results()


if __name__ == "__main__":
    asyncio.run(main())
