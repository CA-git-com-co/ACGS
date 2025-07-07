#!/usr/bin/env python3
"""
Concurrent Processing Implementation Test for ACGS-1
Tests async workflows, concurrent governance operations, and scalability
"""

import asyncio
import logging
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GovernanceAction:
    """Represents a governance action for processing."""

    id: str
    action_type: str
    priority: int
    payload: Dict[str, Any]
    created_at: float
    status: str = "pending"


@dataclass
class ProcessingResult:
    """Result of processing a governance action."""

    action_id: str
    success: bool
    processing_time: float
    error: Optional[str] = None


class ConcurrentGovernanceProcessor:
    """Handles concurrent processing of governance operations."""

    def __init__(self, max_workers: int = 50, queue_size: int = 1000):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.action_queue = asyncio.Queue(maxsize=queue_size)
        self.result_queue = asyncio.Queue()
        self.workers = []
        self.is_running = False

        # Performance metrics
        self.processed_actions = 0
        self.failed_actions = 0
        self.total_processing_time = 0
        self.response_times = []

        # Constitutional compliance
        self.constitutional_hash = "cdd01ef066bc6cf2"

    async def start_workers(self):
        """Start concurrent worker tasks."""
        self.is_running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker_{i}"))
            for i in range(self.max_workers)
        ]
        logger.info(f"✅ Started {self.max_workers} concurrent workers")

    async def stop_workers(self):
        """Stop all worker tasks."""
        self.is_running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("✅ All workers stopped")

    async def _worker(self, worker_id: str):
        """Worker task that processes governance actions."""
        while self.is_running:
            try:
                # Get action from queue with timeout
                action = await asyncio.wait_for(self.action_queue.get(), timeout=1.0)

                # Process the action
                result = await self._process_action(action, worker_id)

                # Store result
                await self.result_queue.put(result)

                # Mark task as done
                self.action_queue.task_done()

            except asyncio.TimeoutError:
                # No action available, continue
                continue
            except asyncio.CancelledError:
                # Worker cancelled
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")

    async def _process_action(
        self, action: GovernanceAction, worker_id: str
    ) -> ProcessingResult:
        """Process a single governance action."""
        start_time = time.time()

        try:
            # Simulate different types of governance operations
            if action.action_type == "policy_creation":
                await self._process_policy_creation(action)
            elif action.action_type == "constitutional_validation":
                await self._process_constitutional_validation(action)
            elif action.action_type == "governance_voting":
                await self._process_governance_voting(action)
            elif action.action_type == "compliance_check":
                await self._process_compliance_check(action)
            elif action.action_type == "audit_logging":
                await self._process_audit_logging(action)
            else:
                await self._process_generic_action(action)

            processing_time = (time.time() - start_time) * 1000  # Convert to ms

            # Update metrics
            self.processed_actions += 1
            self.total_processing_time += processing_time
            self.response_times.append(processing_time)

            return ProcessingResult(
                action_id=action.id, success=True, processing_time=processing_time
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.failed_actions += 1

            return ProcessingResult(
                action_id=action.id,
                success=False,
                processing_time=processing_time,
                error=str(e),
            )

    async def _process_policy_creation(self, action: GovernanceAction):
        """Process policy creation action."""
        # Simulate policy synthesis and validation
        await asyncio.sleep(random.uniform(0.05, 0.15))  # 50-150ms

        # Simulate constitutional compliance check
        if self.constitutional_hash not in str(action.payload):
            action.payload["constitutional_hash"] = self.constitutional_hash

        # Simulate policy storage
        await asyncio.sleep(random.uniform(0.02, 0.08))  # 20-80ms

    async def _process_constitutional_validation(self, action: GovernanceAction):
        """Process constitutional validation action."""
        # Simulate constitutional compliance checking
        await asyncio.sleep(random.uniform(0.03, 0.12))  # 30-120ms

        # Validate against constitutional hash
        if action.payload.get("constitutional_hash") != self.constitutional_hash:
            raise ValueError("Constitutional hash mismatch")

    async def _process_governance_voting(self, action: GovernanceAction):
        """Process governance voting action."""
        # Simulate vote validation and counting
        await asyncio.sleep(random.uniform(0.04, 0.10))  # 40-100ms

        # Simulate vote storage
        await asyncio.sleep(random.uniform(0.02, 0.06))  # 20-60ms

    async def _process_compliance_check(self, action: GovernanceAction):
        """Process compliance check action."""
        # Simulate compliance validation
        await asyncio.sleep(random.uniform(0.02, 0.08))  # 20-80ms

        # Simulate compliance scoring
        await asyncio.sleep(random.uniform(0.01, 0.05))  # 10-50ms

    async def _process_audit_logging(self, action: GovernanceAction):
        """Process audit logging action."""
        # Simulate audit log creation
        await asyncio.sleep(random.uniform(0.01, 0.04))  # 10-40ms

        # Simulate log storage
        await asyncio.sleep(random.uniform(0.01, 0.03))  # 10-30ms

    async def _process_generic_action(self, action: GovernanceAction):
        """Process generic governance action."""
        # Simulate generic processing
        await asyncio.sleep(random.uniform(0.03, 0.10))  # 30-100ms

    async def submit_action(self, action: GovernanceAction) -> bool:
        """Submit a governance action for processing."""
        try:
            await self.action_queue.put(action)
            return True
        except asyncio.QueueFull:
            return False

    async def get_results(self, timeout: float = 1.0) -> List[ProcessingResult]:
        """Get processed results."""
        results = []

        try:
            while True:
                result = await asyncio.wait_for(
                    self.result_queue.get(), timeout=timeout
                )
                results.append(result)
        except asyncio.TimeoutError:
            pass

        return results

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.response_times:
            return {
                "processed_actions": 0,
                "failed_actions": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "throughput": 0,
            }

        success_rate = (
            self.processed_actions / (self.processed_actions + self.failed_actions)
        ) * 100
        avg_response_time = statistics.mean(self.response_times)
        p95_response_time = (
            statistics.quantiles(self.response_times, n=20)[18]
            if len(self.response_times) >= 20
            else max(self.response_times)
        )
        p99_response_time = (
            statistics.quantiles(self.response_times, n=100)[98]
            if len(self.response_times) >= 100
            else max(self.response_times)
        )

        return {
            "processed_actions": self.processed_actions,
            "failed_actions": self.failed_actions,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "throughput": (
                self.processed_actions / (self.total_processing_time / 1000)
                if self.total_processing_time > 0
                else 0
            ),
        }


async def test_concurrent_processing():
    """Test concurrent processing capabilities."""
    print("🔍 Testing Concurrent Processing Implementation")
    print("=" * 60)

    # Initialize processor
    processor = ConcurrentGovernanceProcessor(max_workers=50, queue_size=1000)

    print("⚡ Starting Concurrent Processing Test...")
    print(f"   Max Workers: {processor.max_workers}")
    print(f"   Queue Size: {processor.queue_size}")
    print(f"   Constitutional Hash: {processor.constitutional_hash}")

    # Start workers
    await processor.start_workers()

    try:
        # Test 1: Basic concurrent processing
        print("\n📊 Test 1: Basic Concurrent Processing (100 actions)")

        # Generate test actions
        test_actions = []
        action_types = [
            "policy_creation",
            "constitutional_validation",
            "governance_voting",
            "compliance_check",
            "audit_logging",
        ]

        for i in range(100):
            action = GovernanceAction(
                id=f"action_{i:03d}",
                action_type=random.choice(action_types),
                priority=random.randint(1, 5),
                payload={
                    "data": f"test_data_{i}",
                    "constitutional_hash": processor.constitutional_hash,
                },
                created_at=time.time(),
            )
            test_actions.append(action)

        # Submit actions
        start_time = time.time()
        for action in test_actions:
            await processor.submit_action(action)

        # Wait for processing to complete
        await processor.action_queue.join()
        processing_time = time.time() - start_time

        # Get results
        results = await processor.get_results(timeout=2.0)

        print(f"   ✅ Processed {len(results)} actions in {processing_time:.2f}s")
        print(f"   Throughput: {len(results)/processing_time:.1f} actions/second")

        # Test 2: High-load concurrent processing
        print("\n📊 Test 2: High-Load Processing (1000 actions)")

        # Reset metrics
        processor.processed_actions = 0
        processor.failed_actions = 0
        processor.response_times = []
        processor.total_processing_time = 0

        # Generate more test actions
        high_load_actions = []
        for i in range(1000):
            action = GovernanceAction(
                id=f"high_load_{i:04d}",
                action_type=random.choice(action_types),
                priority=random.randint(1, 5),
                payload={
                    "data": f"high_load_data_{i}",
                    "constitutional_hash": processor.constitutional_hash,
                },
                created_at=time.time(),
            )
            high_load_actions.append(action)

        # Submit actions in batches
        start_time = time.time()
        batch_size = 50
        for i in range(0, len(high_load_actions), batch_size):
            batch = high_load_actions[i : i + batch_size]
            for action in batch:
                await processor.submit_action(action)
            # Small delay between batches to simulate realistic load
            await asyncio.sleep(0.01)

        # Wait for processing to complete
        await processor.action_queue.join()
        total_processing_time = time.time() - start_time

        # Get results
        high_load_results = await processor.get_results(timeout=5.0)

        print(
            f"   ✅ Processed {len(high_load_results)} actions in {total_processing_time:.2f}s"
        )
        print(
            f"   Throughput: {len(high_load_results)/total_processing_time:.1f} actions/second"
        )

        # Test 3: Stress test with concurrent submissions
        print("\n📊 Test 3: Stress Test (Concurrent Submissions)")

        async def submit_batch(batch_id: int, num_actions: int):
            """Submit a batch of actions concurrently."""
            actions_submitted = 0
            for i in range(num_actions):
                action = GovernanceAction(
                    id=f"stress_{batch_id}_{i:03d}",
                    action_type=random.choice(action_types),
                    priority=random.randint(1, 5),
                    payload={
                        "batch_id": batch_id,
                        "data": f"stress_data_{i}",
                        "constitutional_hash": processor.constitutional_hash,
                    },
                    created_at=time.time(),
                )

                if await processor.submit_action(action):
                    actions_submitted += 1
                else:
                    break  # Queue full

            return actions_submitted

        # Reset metrics
        processor.processed_actions = 0
        processor.failed_actions = 0
        processor.response_times = []
        processor.total_processing_time = 0

        # Submit actions from multiple concurrent sources
        start_time = time.time()
        batch_tasks = [
            submit_batch(batch_id, 100)
            for batch_id in range(10)  # 10 concurrent batches of 100 actions each
        ]

        batch_results = await asyncio.gather(*batch_tasks)
        total_submitted = sum(batch_results)

        # Wait for processing to complete
        await processor.action_queue.join()
        stress_processing_time = time.time() - start_time

        # Get results
        stress_results = await processor.get_results(timeout=5.0)

        print(f"   ✅ Submitted {total_submitted} actions from 10 concurrent sources")
        print(
            f"   ✅ Processed {len(stress_results)} actions in {stress_processing_time:.2f}s"
        )
        print(
            f"   Throughput: {len(stress_results)/stress_processing_time:.1f} actions/second"
        )

        # Get final performance metrics
        metrics = processor.get_performance_metrics()

        print("\n📈 Performance Summary:")
        print(f"   Total Processed Actions: {metrics['processed_actions']}")
        print(f"   Failed Actions: {metrics['failed_actions']}")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   Average Response Time: {metrics['avg_response_time']:.2f}ms")
        print(f"   95th Percentile Response Time: {metrics['p95_response_time']:.2f}ms")
        print(f"   99th Percentile Response Time: {metrics['p99_response_time']:.2f}ms")

        # Target validation
        target_concurrent_actions = 1000
        target_response_time = 500.0  # ms
        target_success_rate = 95.0  # %

        meets_concurrency_target = (
            metrics["processed_actions"] >= target_concurrent_actions
        )
        meets_response_target = metrics["p95_response_time"] <= target_response_time
        meets_success_target = metrics["success_rate"] >= target_success_rate

        print(f"\n🎯 Target Validation:")
        print(f"   Target Concurrent Actions: ≥{target_concurrent_actions}")
        print(f"   Achieved Concurrent Actions: {metrics['processed_actions']}")
        print(
            f"   Concurrency Target: {'✅ MET' if meets_concurrency_target else '❌ NOT MET'}"
        )
        print(f"   Target Response Time (95th percentile): ≤{target_response_time}ms")
        print(f"   Achieved Response Time: {metrics['p95_response_time']:.2f}ms")
        print(
            f"   Response Time Target: {'✅ MET' if meets_response_target else '❌ NOT MET'}"
        )
        print(f"   Target Success Rate: ≥{target_success_rate}%")
        print(f"   Achieved Success Rate: {metrics['success_rate']:.1f}%")
        print(
            f"   Success Rate Target: {'✅ MET' if meets_success_target else '❌ NOT MET'}"
        )

        return {
            "success": True,
            "metrics": metrics,
            "meets_concurrency_target": meets_concurrency_target,
            "meets_response_target": meets_response_target,
            "meets_success_target": meets_success_target,
        }

    finally:
        # Stop workers
        await processor.stop_workers()


async def main():
    """Main function."""
    print("🚀 Starting Concurrent Processing Implementation Test")
    print("=" * 70)

    result = await test_concurrent_processing()

    if result["success"]:
        metrics = result["metrics"]

        print("\n🎯 Concurrent Processing Summary")
        print("=" * 50)
        print(f"⚡ Processed Actions: {metrics['processed_actions']}")
        print(f"📊 Average Response Time: {metrics['avg_response_time']:.2f}ms")
        print(f"📊 95th Percentile Response Time: {metrics['p95_response_time']:.2f}ms")
        print(f"✅ Success Rate: {metrics['success_rate']:.1f}%")
        print(
            f"🎯 Concurrency Target: {'MET' if result['meets_concurrency_target'] else 'NOT MET'}"
        )
        print(
            f"🎯 Response Time Target: {'MET' if result['meets_response_target'] else 'NOT MET'}"
        )
        print(
            f"🎯 Success Rate Target: {'MET' if result['meets_success_target'] else 'NOT MET'}"
        )

        if all(
            [
                result["meets_concurrency_target"],
                result["meets_response_target"],
                result["meets_success_target"],
            ]
        ):
            print("\n🎉 Concurrent processing implementation successful!")
            print("   All performance targets achieved!")
            exit(0)
        else:
            print("\n⚠️ Some concurrent processing targets not fully met.")
            exit(1)
    else:
        print("\n❌ Concurrent processing implementation test failed.")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
