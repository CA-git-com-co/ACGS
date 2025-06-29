# CI/CD Performance Validation Implementation Prompt

## Context
You are implementing automated performance validation in the CI/CD pipeline for ACGS-1 Lite. The system must catch performance regressions before they reach production, validate SLOs (sub-5ms latency, >95% compliance), and maintain historical performance trends.

## Requirements

### Performance Testing Framework

1. **Pytest-Benchmark Integration**:
   ```python
   # tests/performance/test_policy_engine_perf.py
   import pytest
   from pytest_benchmark.fixture import BenchmarkFixture
   import asyncio
   import numpy as np
   from policy_engine.client import PolicyEngineClient
   
   class TestPolicyEnginePerformance:
       @pytest.fixture
       def policy_client(self):
           return PolicyEngineClient(base_url="http://localhost:8001")
       
       def test_evaluation_latency(self, benchmark: BenchmarkFixture, policy_client):
           """Test that policy evaluation meets latency SLO"""
           
           # Test data
           test_action = "data.read"
           test_context = {
               "agent": {"id": "test-agent", "trust_level": 0.9},
               "environment": {"sandbox_enabled": True}
           }
           
           # Benchmark the evaluation
           result = benchmark(
               policy_client.evaluate_sync,
               test_action,
               test_context
           )
           
           # Validate result
           assert result["allow"] is not None
           
           # Check latency SLOs
           stats = benchmark.stats
           assert stats["mean"] < 0.005  # 5ms mean
           assert stats["stddev"] < 0.002  # Low variance
           
           # Calculate percentiles
           latencies = [t * 1000 for t in benchmark._raw_values]  # Convert to ms
           p99 = np.percentile(latencies, 99)
           assert p99 < 5.0, f"P99 latency {p99:.2f}ms exceeds 5ms SLO"
       
       @pytest.mark.parametrize("concurrent_requests", [10, 50, 100])
       def test_concurrent_performance(self, benchmark, policy_client, concurrent_requests):
           """Test performance under concurrent load"""
           
           async def run_concurrent_requests():
               tasks = []
               for _ in range(concurrent_requests):
                   task = policy_client.evaluate(
                       "compute.analyze",
                       {"agent": {"id": f"agent-{_}"}}
                   )
                   tasks.append(task)
               
               start = time.perf_counter()
               results = await asyncio.gather(*tasks)
               duration = time.perf_counter() - start
               
               return results, duration
           
           results, duration = benchmark(
               lambda: asyncio.run(run_concurrent_requests())
           )
           
           # All requests should succeed
           assert all(r["allow"] is not None for r in results[0])
           
           # Throughput should scale
           throughput = concurrent_requests / duration
           assert throughput > concurrent_requests * 0.8  # 80% efficiency
   ```

2. **Locust Load Testing**:
   ```python
   # tests/load/locustfile.py
   from locust import HttpUser, task, between, events
   import json
   import time
   
   class PolicyEngineUser(HttpUser):
       wait_time = between(0.1, 0.5)
       
       def on_start(self):
           self.request_count = 0
           self.latencies = []
       
       @task(weight=70)
       def evaluate_safe_action(self):
           """Test common safe actions (70% of traffic)"""
           response = self.client.post(
               "/api/v1/evaluate",
               json={
                   "action": "data.read",
                   "context": {
                       "agent": {"id": f"agent-{self.request_count}"},
                       "environment": {"sandbox_enabled": True}
                   }
               },
               catch_response=True
           )
           
           if response.elapsed.total_seconds() > 0.005:
               response.failure(f"Latency {response.elapsed.total_seconds():.3f}s exceeds SLO")
           else:
               response.success()
           
           self.latencies.append(response.elapsed.total_seconds() * 1000)
           self.request_count += 1
       
       @task(weight=20)
       def evaluate_complex_action(self):
           """Test complex evaluation (20% of traffic)"""
           response = self.client.post(
               "/api/v1/evaluate",
               json={
                   "action": "model.train",
                   "context": {
                       "agent": {"id": f"ml-agent-{self.request_count}"},
                       "resources": {"gpu": 2, "memory_gb": 16}
                   }
               }
           )
       
       @task(weight=10)
       def evaluate_denied_action(self):
           """Test denied actions (10% of traffic)"""
           response = self.client.post(
               "/api/v1/evaluate",
               json={
                   "action": "system.execute_shell",
                   "context": {"agent": {"id": "malicious"}}
               }
           )
           
           result = response.json()
           assert result["allow"] == False
   
   @events.test_stop.add_listener
   def on_test_stop(environment, **kwargs):
       """Calculate and report percentiles at end of test"""
       all_latencies = []
       for user in environment.runner.user_instances:
           all_latencies.extend(user.latencies)
       
       if all_latencies:
           p50 = np.percentile(all_latencies, 50)
           p95 = np.percentile(all_latencies, 95)
           p99 = np.percentile(all_latencies, 99)
           
           print(f"\nLatency Percentiles:")
           print(f"P50: {p50:.2f}ms")
           print(f"P95: {p95:.2f}ms")
           print(f"P99: {p99:.2f}ms")
           
           # Fail if P99 exceeds SLO
           if p99 > 5.0:
               environment.runner.quit()
               raise Exception(f"P99 latency {p99:.2f}ms exceeds 5ms SLO")
   ```

3. **Prometheus Metrics Validation**:
   ```python
   # tests/performance/test_metrics_validation.py
   import requests
   from prometheus_client.parser import text_string_to_metric_families
   
   class TestMetricsValidation:
       def test_policy_engine_metrics(self):
           """Validate Prometheus metrics meet SLOs"""
           
           # Get metrics from Policy Engine
           response = requests.get("http://localhost:8001/metrics")
           metrics = {}
           
           for family in text_string_to_metric_families(response.text):
               for sample in family.samples:
                   metrics[sample.name] = sample.value
           
           # Check evaluation latency histogram
           latency_sum = metrics.get("policy_evaluation_duration_seconds_sum", 0)
           latency_count = metrics.get("policy_evaluation_duration_seconds_count", 1)
           avg_latency = latency_sum / latency_count if latency_count > 0 else 0
           
           assert avg_latency < 0.002, f"Average latency {avg_latency:.3f}s exceeds target"
           
           # Check compliance rate
           compliance_rate = metrics.get("constitutional_compliance_rate", 0)
           assert compliance_rate > 0.95, f"Compliance rate {compliance_rate:.2%} below 95%"
           
           # Check cache hit rate
           cache_hits = metrics.get("cache_hits_total", 0)
           cache_total = metrics.get("cache_requests_total", 1)
           cache_hit_rate = cache_hits / cache_total if cache_total > 0 else 0
           
           assert cache_hit_rate > 0.90, f"Cache hit rate {cache_hit_rate:.2%} below 90%"
   ```

4. **CI/CD Pipeline Configuration**:
   ```yaml
   # .github/workflows/performance-tests.yml
   name: Performance Validation
   
   on:
     pull_request:
       paths:
         - 'services/core/**'
         - 'tests/performance/**'
   
   jobs:
     performance-tests:
       runs-on: ubuntu-latest
       
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         
         - name: Install dependencies
           run: |
             pip install -r requirements-test.txt
             pip install pytest-benchmark locust prometheus-client
         
         - name: Start services
           run: |
             docker-compose -f docker-compose.test.yml up -d
             ./scripts/wait-for-services.sh
         
         - name: Run benchmark tests
           run: |
             pytest tests/performance/test_policy_engine_perf.py \
               --benchmark-only \
               --benchmark-json=benchmark-results.json \
               --benchmark-min-rounds=100
         
         - name: Run load tests
           run: |
             locust -f tests/load/locustfile.py \
               --headless \
               --users 100 \
               --spawn-rate 10 \
               --run-time 60s \
               --host http://localhost:8001 \
               --html performance-report.html
         
         - name: Validate metrics
           run: |
             python tests/performance/test_metrics_validation.py
         
         - name: Compare with baseline
           run: |
             python scripts/compare-performance.py \
               --current benchmark-results.json \
               --baseline .performance-baseline.json \
               --threshold 10  # Allow 10% regression
         
         - name: Upload results
           uses: actions/upload-artifact@v3
           with:
             name: performance-results
             path: |
               benchmark-results.json
               performance-report.html
         
         - name: Comment on PR
           if: always()
           uses: actions/github-script@v6
           with:
             script: |
               const fs = require('fs');
               const results = JSON.parse(fs.readFileSync('benchmark-results.json'));
               
               // Extract key metrics
               const p99Latency = results.benchmarks[0].stats.percentiles['99'];
               
               const comment = `## Performance Test Results
               
               **P99 Latency**: ${(p99Latency * 1000).toFixed(2)}ms
               **Throughput**: ${results.benchmarks[0].stats.ops.toFixed(0)} ops/sec
               
               [Full Report](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})`;
               
               github.rest.issues.createComment({
                 issue_number: context.issue.number,
                 owner: context.repo.owner,
                 repo: context.repo.repo,
                 body: comment
               });
   ```

5. **Historical Tracking**:
   ```python
   # scripts/track-performance.py
   import json
   import boto3
   from datetime import datetime
   
   class PerformanceTracker:
       def __init__(self, s3_bucket: str):
           self.s3 = boto3.client('s3')
           self.bucket = s3_bucket
       
       def store_results(self, results: dict, commit_sha: str):
           """Store performance results in S3 for historical tracking"""
           
           key = f"performance/{datetime.utcnow().strftime('%Y/%m/%d')}/{commit_sha}.json"
           
           # Add metadata
           results["metadata"] = {
               "commit_sha": commit_sha,
               "timestamp": datetime.utcnow().isoformat(),
               "branch": os.environ.get("GITHUB_REF_NAME", "unknown")
           }
           
           self.s3.put_object(
               Bucket=self.bucket,
               Key=key,
               Body=json.dumps(results),
               ContentType="application/json"
           )
       
       def generate_trend_report(self, days: int = 30):
           """Generate performance trend report"""
           
           # Fetch historical data
           data = self.fetch_historical_data(days)
           
           # Calculate trends
           latencies = [d["p99_latency"] for d in data]
           throughputs = [d["throughput"] for d in data]
           
           trend = {
               "latency_trend": np.polyfit(range(len(latencies)), latencies, 1)[0],
               "throughput_trend": np.polyfit(range(len(throughputs)), throughputs, 1)[0],
               "current_p99": latencies[-1],
               "avg_p99_30d": np.mean(latencies),
               "latency_improving": latencies[-1] < np.mean(latencies[:5])
           }
           
           return trend
   ```

## Implementation Steps

1. **Set Up Test Infrastructure**:
   - Create isolated test environment
   - Configure test databases and services
   - Set up metrics collection

2. **Implement Test Suite**:
   - Write pytest-benchmark tests
   - Create Locust scenarios
   - Add metrics validation

3. **Configure CI Pipeline**:
   - Add performance job to GitHub Actions
   - Configure artifact storage
   - Set up PR commenting

4. **Establish Baselines**:
   - Run tests on current version
   - Store baseline metrics
   - Document acceptable ranges

5. **Monitor and Iterate**:
   - Review daily performance trends
   - Adjust thresholds based on data
   - Add new test scenarios

## Success Criteria
- [ ] All PRs run performance tests automatically
- [ ] P99 latency regression >10% blocks merge
- [ ] Historical data stored for 90+ days
- [ ] Performance trends visible in dashboard
- [ ] <5% false positive rate on failures