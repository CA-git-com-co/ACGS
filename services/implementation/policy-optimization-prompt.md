# Policy Engine Performance Optimization Prompt

## Context

The Policy Engine currently achieves 2.1ms P99 latency using OPA as an external service. You need to optimize it to reach <1ms P99 latency by embedding OPA, improving caching, and implementing partial evaluation. The service must maintain the same API while significantly improving performance.

## Requirements

### Core Optimizations

1. **Embed OPA In-Process**:

   ```python
   # Option A: Use OPA Python SDK with Wasm
   from opa_wasm import OPAModule
   import wasmtime

   class EmbeddedOPAEvaluator:
       def __init__(self, policy_bundle_path: str):
           # Load compiled Wasm policy
           with open(policy_bundle_path, 'rb') as f:
               self.policy_wasm = f.read()

           # Initialize Wasmtime engine
           self.engine = wasmtime.Engine()
           self.module = wasmtime.Module(self.engine, self.policy_wasm)
           self.store = wasmtime.Store(self.engine)

           # Create OPA instance
           self.opa = OPAModule(self.store, self.module)
           self.opa.initialize()

       async def evaluate(self, input_data: dict) -> dict:
           # Direct in-memory evaluation
           start = time.perf_counter_ns()

           # Convert input to JSON bytes
           input_json = json.dumps(input_data).encode()

           # Evaluate policy
           result_ptr = self.opa.evaluate(input_json)
           result = self.opa.get_result(result_ptr)

           # Track metrics
           latency_ns = time.perf_counter_ns() - start
           self.metrics.record_evaluation(latency_ns)

           return json.loads(result)
   ```

   ```python
   # Option B: Rewrite critical path in Go
   # services/core/policy-engine-go/evaluator.go
   package main

   import (
       "context"
       "github.com/open-policy-agent/opa/rego"
       "github.com/open-policy-agent/opa/storage/inmem"
   )

   type Evaluator struct {
       queries map[string]*rego.PreparedEvalQuery
       store   storage.Store
   }

   func NewEvaluator(policies map[string]string) (*Evaluator, error) {
       store := inmem.New()
       queries := make(map[string]*rego.PreparedEvalQuery)

       // Pre-compile all queries
       for name, policy := range policies {
           query, err := rego.New(
               rego.Query("data.acgs.constitutional.evaluate"),
               rego.Module(name, policy),
               rego.Store(store),
           ).PrepareForEval(context.Background())

           if err != nil {
               return nil, err
           }
           queries[name] = &query
       }

       return &Evaluator{queries: queries, store: store}, nil
   }
   ```

2. **Advanced Caching Strategy**:

   ```python
   class OptimizedCache:
       def __init__(self, redis_client):
           self.redis = redis_client
           self.local_cache = {}  # L1 cache
           self.cache_stats = {
               "hits": 0,
               "misses": 0,
               "l1_hits": 0,
               "l2_hits": 0
           }

       def generate_key(self, action: str, context: dict) -> str:
           # Create minimal cache key
           # Only include fields that affect the decision
           relevant_fields = {
               "action": action,
               "agent_id": context.get("agent", {}).get("id"),
               "sandbox": context.get("environment", {}).get("sandbox_enabled"),
               "trust_level": context.get("agent", {}).get("trust_level")
           }

           # Use xxhash for fast hashing
           import xxhash
           key_str = json.dumps(relevant_fields, sort_keys=True)
           return f"pe:v1:{xxhash.xxh64(key_str).hexdigest()}"

       async def get_cached_decision(self, key: str) -> Optional[dict]:
           # Check L1 cache first
           if key in self.local_cache:
               self.cache_stats["l1_hits"] += 1
               return self.local_cache[key]

           # Check L2 cache (Redis)
           cached = await self.redis.get(key)
           if cached:
               self.cache_stats["l2_hits"] += 1
               result = json.loads(cached)
               # Promote to L1
               self.local_cache[key] = result
               return result

           self.cache_stats["misses"] += 1
           return None

       async def cache_decision(self, key: str, decision: dict, ttl: int = 300):
           # Store in both L1 and L2
           self.local_cache[key] = decision

           # Use pipeline for Redis operations
           pipe = self.redis.pipeline()
           pipe.setex(key, ttl, json.dumps(decision))
           pipe.hincrby("cache:stats", "total_cached", 1)
           await pipe.execute()
   ```

3. **Partial Evaluation Implementation**:

   ```python
   class PartialEvaluator:
       def __init__(self, opa_evaluator):
           self.opa = opa_evaluator
           self.partial_results = {}

       async def prepare_partial_evaluation(self):
           """Pre-compute partial results for common scenarios"""

           # Partial evaluation for known safe actions
           safe_actions = ["data.read", "compute.analyze", "report.generate"]
           for action in safe_actions:
               partial = await self.opa.partial_eval(
                   query="data.acgs.constitutional.evaluate",
                   unknowns=["input.context.agent", "input.context.request_id"],
                   input={"action": action}
               )
               self.partial_results[f"safe:{action}"] = partial

           # Partial evaluation for sandboxed environment
           sandbox_partial = await self.opa.partial_eval(
               query="data.acgs.constitutional.evaluate",
               unknowns=["input.action", "input.context.agent"],
               input={"context": {"environment": {"sandbox_enabled": True}}}
           )
           self.partial_results["env:sandboxed"] = sandbox_partial

       async def evaluate_with_partial(self, action: str, context: dict) -> dict:
           # Try to use partial evaluation
           if action in ["data.read", "compute.analyze", "report.generate"]:
               partial = self.partial_results.get(f"safe:{action}")
               if partial:
                   # Complete the partial evaluation
                   return await partial.eval({"context": context})

           # Fall back to full evaluation
           return await self.opa.evaluate({"action": action, "context": context})
   ```

4. **Request Batching**:

   ```python
   class BatchedEvaluator:
       def __init__(self, evaluator, batch_size: int = 10, batch_window_ms: int = 5):
           self.evaluator = evaluator
           self.batch_size = batch_size
           self.batch_window_ms = batch_window_ms
           self.pending_requests = []
           self.batch_lock = asyncio.Lock()

       async def evaluate(self, action: str, context: dict) -> dict:
           # Create future for this request
           future = asyncio.Future()
           request = {
               "action": action,
               "context": context,
               "future": future
           }

           async with self.batch_lock:
               self.pending_requests.append(request)

               # If batch is full, process immediately
               if len(self.pending_requests) >= self.batch_size:
                   await self._process_batch()
               else:
                   # Schedule batch processing
                   asyncio.create_task(self._schedule_batch())

           # Wait for result
           return await future

       async def _process_batch(self):
           if not self.pending_requests:
               return

           batch = self.pending_requests[:self.batch_size]
           self.pending_requests = self.pending_requests[self.batch_size:]

           # Evaluate all requests in parallel
           tasks = [
               self.evaluator.evaluate(req["action"], req["context"])
               for req in batch
           ]
           results = await asyncio.gather(*tasks, return_exceptions=True)

           # Set results
           for req, result in zip(batch, results):
               if isinstance(result, Exception):
                   req["future"].set_exception(result)
               else:
                   req["future"].set_result(result)
   ```

### Performance Targets

1. **Latency Goals**:

   - P50: <0.5ms
   - P95: <0.8ms
   - P99: <1.0ms

2. **Throughput Goals**:

   - Single instance: 10,000 RPS
   - With 4 workers: 40,000 RPS

3. **Resource Usage**:
   - Memory: <500MB per instance
   - CPU: <2 cores at 10K RPS

## Implementation Steps

1. **Benchmark Current Performance**:

   ```python
   async def benchmark_baseline():
       # Measure current latencies
       latencies = []
       for _ in range(10000):
           start = time.perf_counter_ns()
           await policy_engine.evaluate(test_action, test_context)
           latencies.append(time.perf_counter_ns() - start)

       print(f"P50: {np.percentile(latencies, 50) / 1e6:.2f}ms")
       print(f"P95: {np.percentile(latencies, 95) / 1e6:.2f}ms")
       print(f"P99: {np.percentile(latencies, 99) / 1e6:.2f}ms")
   ```

2. **Implement Embedded OPA**:

   - Choose between Wasm or Go approach
   - Migrate policies to embedded format
   - Update deployment to remove OPA sidecar

3. **Optimize Caching**:

   - Implement two-tier cache
   - Add cache warming on startup
   - Monitor cache hit rates

4. **Deploy and Validate**:
   - A/B test optimized version
   - Monitor latency metrics
   - Ensure no functionality regression

## Success Criteria

- [ ] P99 latency <1ms verified in production
- [ ] Cache hit rate >95%
- [ ] 10,000 RPS per instance achieved
- [ ] Memory usage <500MB
- [ ] All tests pass with optimized version
