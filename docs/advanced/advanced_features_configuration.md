# Advanced Features Configuration Guide

This guide covers the configuration and optimization of advanced ACGS-1 features including WINA optimization, constitutional cache system, multi-model consensus engine, and other enterprise-grade capabilities.

## 🧬 WINA Optimization System

### Overview
The WINA (Weighted Intelligence Network Architecture) optimization system provides evolutionary computation capabilities for governance optimization with constitutional compliance monitoring.

### Configuration

#### Basic WINA Configuration
```yaml
# config/services/wina_optimization_config.yaml
wina_optimization:
  enabled: true
  optimization_level: "high"  # low, medium, high, adaptive
  constitutional_weight: 0.8
  performance_weight: 0.2
  max_iterations: 100
  convergence_threshold: 0.01
  
  # Evolutionary parameters
  population_size: 50
  mutation_rate: 0.1
  crossover_rate: 0.8
  selection_method: "tournament"  # tournament, roulette, rank
  
  # Performance monitoring
  performance_monitoring:
    enabled: true
    metrics_collection_interval: 30  # seconds
    optimization_history_retention: 7  # days
    alert_thresholds:
      performance_degradation: 0.1
      constitutional_compliance_drop: 0.05
```

#### Advanced WINA Configuration
```yaml
# Advanced optimization strategies
optimization_strategies:
  adaptive_learning:
    enabled: true
    learning_rate: 0.01
    momentum: 0.9
    decay_rate: 0.95
    
  multi_objective:
    enabled: true
    objectives:
      - name: "constitutional_compliance"
        weight: 0.4
        target: 0.95
      - name: "performance_efficiency"
        weight: 0.3
        target: 0.90
      - name: "stakeholder_satisfaction"
        weight: 0.3
        target: 0.85
        
  constraint_handling:
    constitutional_constraints:
      min_compliance_score: 0.8
      required_principles: ["transparency", "accountability", "fairness"]
    performance_constraints:
      max_response_time_ms: 500
      min_throughput_rps: 100
      max_resource_usage: 0.8
```

### API Configuration
```python
# Configure WINA optimization via API
import httpx

async def configure_wina_optimization():
    config = {
        "optimization_level": "high",
        "constitutional_weight": 0.8,
        "performance_weight": 0.2,
        "max_iterations": 100,
        "convergence_threshold": 0.01,
        "adaptive_learning": {
            "enabled": True,
            "learning_rate": 0.01
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8006/api/v1/wina/configure",
            json=config
        )
        return response.json()

# Monitor WINA performance
async def monitor_wina_performance():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8006/api/v1/wina/performance"
        )
        metrics = response.json()
        
        print(f"Optimization Score: {metrics['wina_metrics']['optimization_score']:.3f}")
        print(f"Performance Improvement: {metrics['wina_metrics']['performance_improvement']:.3f}")
        print(f"Constitutional Compliance: {metrics['wina_metrics']['constitutional_compliance']:.3f}")
```

### Performance Tuning
```bash
# Environment variables for WINA optimization
export WINA_OPTIMIZATION_LEVEL="high"
export WINA_MAX_CONCURRENT_OPTIMIZATIONS=5
export WINA_CACHE_SIZE_MB=512
export WINA_LEARNING_RATE=0.01
export WINA_CONVERGENCE_THRESHOLD=0.001

# Resource allocation
export WINA_CPU_CORES=4
export WINA_MEMORY_LIMIT_GB=8
export WINA_GPU_ENABLED=true
export WINA_GPU_MEMORY_FRACTION=0.5
```

## 🏛️ Constitutional Cache System

### Overview
The Constitutional Cache System provides multi-layer caching with automatic constitutional compliance validation and ultra-low latency performance.

### Configuration

#### Redis Configuration
```yaml
# config/cache/constitutional_cache_config.yaml
constitutional_cache:
  redis:
    url: "redis://localhost:6379"
    db: 0
    max_connections: 100
    socket_keepalive: true
    health_check_interval: 30
    
  # Cache strategies
  strategies:
    constitutional_validations:
      ttl_seconds: 3600
      max_size_mb: 50
      compression: false
      preload_enabled: true
      
    policy_fragments:
      ttl_seconds: 300
      max_size_mb: 100
      compression: true
      
    llm_responses:
      ttl_seconds: 1800
      max_size_mb: 200
      compression: true
      
    governance_decisions:
      ttl_seconds: 600
      max_size_mb: 75
      compression: true
      
  # Performance settings
  performance:
    l1_cache_size: 1000
    batch_window_ms: 100
    max_batch_size: 50
    timeout_ms: 1000
    
  # Constitutional compliance
  constitutional:
    hash: "cdd01ef066bc6cf2"
    validation_strict: true
    performance_target_ms: 5
    circuit_breaker:
      failure_threshold: 5
      recovery_timeout: 30
```

#### Advanced Cache Configuration
```python
# Advanced cache configuration
from shared.constitutional_cache import ConstitutionalCache

async def setup_advanced_cache():
    cache = ConstitutionalCache(
        redis_url="redis://localhost:6379",
        constitutional_hash="cdd01ef066bc6cf2",
        cache_ttl=300
    )
    
    # Configure cache strategies
    await cache.configure_strategy(
        "high_frequency_validations",
        {
            "ttl": 60,
            "max_size": 1000,
            "compression": False,
            "preload": True
        }
    )
    
    # Set up cache warming
    await cache.warm_cache([
        "constitutional_principles",
        "common_policies",
        "stakeholder_data"
    ])
    
    # Configure monitoring
    await cache.setup_monitoring({
        "metrics_interval": 30,
        "alert_thresholds": {
            "hit_rate_min": 0.8,
            "response_time_max": 5
        }
    })
```

### Cache Optimization
```bash
# Redis optimization for constitutional cache
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# Monitor cache performance
redis-cli INFO memory
redis-cli INFO stats
redis-cli MONITOR | grep "acgs:constitutional"
```

## 🤖 Multi-Model Consensus Engine

### Overview
The Multi-Model Consensus Engine orchestrates multiple AI models to achieve robust policy generation with high accuracy and constitutional compliance.

### Configuration

#### Model Configuration
```yaml
# config/ai/multi_model_consensus_config.yaml
multi_model_consensus:
  enabled: true
  consensus_threshold: 0.8
  timeout_seconds: 60
  
  # Primary models
  models:
    primary:
      - name: "qwen3-32b"
        weight: 0.4
        endpoint: "http://localhost:8080/v1/chat/completions"
        api_key: "${QWEN_API_KEY}"
        max_tokens: 4096
        temperature: 0.7
        
    secondary:
      - name: "deepseek-chat"
        weight: 0.3
        endpoint: "http://localhost:8081/v1/chat/completions"
        api_key: "${DEEPSEEK_API_KEY}"
        max_tokens: 4096
        temperature: 0.7
        
      - name: "qwen3-235b"
        weight: 0.3
        endpoint: "http://localhost:8082/v1/chat/completions"
        api_key: "${QWEN_235B_API_KEY}"
        max_tokens: 4096
        temperature: 0.7
        
  # Fallback models
  fallback_models:
    - name: "deepseek-r1"
      endpoint: "http://localhost:8083/v1/chat/completions"
      api_key: "${DEEPSEEK_R1_API_KEY}"
      
  # Consensus algorithms
  consensus_algorithms:
    weighted_average:
      enabled: true
      weight_by_confidence: true
      
    voting_based:
      enabled: true
      voting_threshold: 0.6
      
    ensemble_learning:
      enabled: true
      meta_model: "consensus_meta_v1"
      
  # Quality assurance
  quality_assurance:
    constitutional_validation: true
    stakeholder_alignment_check: true
    coherence_scoring: true
    bias_detection: true
```

#### Advanced Consensus Configuration
```python
# Configure multi-model consensus
async def configure_consensus_engine():
    config = {
        "consensus_threshold": 0.8,
        "models": [
            {
                "name": "qwen3-32b",
                "weight": 0.4,
                "temperature": 0.7,
                "max_tokens": 4096
            },
            {
                "name": "deepseek-chat", 
                "weight": 0.3,
                "temperature": 0.7,
                "max_tokens": 4096
            },
            {
                "name": "qwen3-235b",
                "weight": 0.3,
                "temperature": 0.7,
                "max_tokens": 4096
            }
        ],
        "consensus_algorithms": {
            "weighted_average": True,
            "voting_based": True,
            "ensemble_learning": True
        },
        "quality_assurance": {
            "constitutional_validation": True,
            "stakeholder_alignment_check": True,
            "coherence_scoring": True
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8004/api/v1/consensus/configure",
            json=config
        )
        return response.json()
```

### Model Performance Optimization
```bash
# Environment variables for model optimization
export MODEL_PARALLEL_REQUESTS=3
export MODEL_TIMEOUT_SECONDS=60
export MODEL_RETRY_ATTEMPTS=3
export MODEL_CACHE_ENABLED=true
export MODEL_CACHE_TTL=1800

# GPU optimization (if available)
export CUDA_VISIBLE_DEVICES=0,1
export MODEL_GPU_MEMORY_FRACTION=0.8
export MODEL_MIXED_PRECISION=true
```

## 🔧 Performance Monitoring and Optimization

### Comprehensive Monitoring Setup
```yaml
# config/monitoring/advanced_monitoring_config.yaml
advanced_monitoring:
  metrics_collection:
    interval_seconds: 30
    retention_days: 30
    
  performance_metrics:
    - name: "wina_optimization_score"
      threshold: 0.8
      alert_on_drop: true
      
    - name: "constitutional_compliance_rate"
      threshold: 0.95
      alert_on_drop: true
      
    - name: "cache_hit_rate"
      threshold: 0.8
      alert_on_drop: true
      
    - name: "consensus_accuracy"
      threshold: 0.85
      alert_on_drop: true
      
  alerting:
    channels:
      - type: "slack"
        webhook_url: "${SLACK_WEBHOOK_URL}"
        
      - type: "email"
        smtp_server: "${SMTP_SERVER}"
        recipients: ["ops@acgs.com"]
        
  dashboards:
    grafana:
      enabled: true
      url: "http://localhost:3001"
      dashboards:
        - "acgs_system_overview"
        - "wina_optimization_metrics"
        - "constitutional_cache_performance"
        - "multi_model_consensus_stats"
```

### Performance Tuning Scripts
```bash
#!/bin/bash
# scripts/optimization/tune_advanced_features.sh

echo "🔧 Tuning ACGS-1 Advanced Features..."

# WINA Optimization Tuning
echo "Optimizing WINA parameters..."
curl -X POST http://localhost:8006/api/v1/wina/optimize \
  -H "Content-Type: application/json" \
  -d '{"auto_tune": true, "target_performance": 0.95}'

# Constitutional Cache Optimization
echo "Optimizing constitutional cache..."
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET maxmemory 2gb

# Multi-Model Consensus Tuning
echo "Tuning consensus parameters..."
curl -X POST http://localhost:8004/api/v1/consensus/tune \
  -H "Content-Type: application/json" \
  -d '{"auto_optimize": true, "target_accuracy": 0.9}'

echo "✅ Advanced features optimization completed!"
```

## 🚀 Production Deployment

### Advanced Production Configuration
```yaml
# config/production/advanced_production_config.yaml
production:
  scaling:
    wina_optimization:
      replicas: 3
      cpu_limit: "2000m"
      memory_limit: "4Gi"
      
    constitutional_cache:
      redis_cluster: true
      nodes: 3
      memory_per_node: "2Gi"
      
    consensus_engine:
      model_replicas: 2
      load_balancing: "round_robin"
      
  security:
    encryption_at_rest: true
    encryption_in_transit: true
    key_rotation_days: 30
    
  monitoring:
    prometheus_retention: "30d"
    log_retention: "90d"
    metrics_resolution: "15s"
    
  backup:
    constitutional_cache_backup: true
    wina_model_backup: true
    consensus_weights_backup: true
    backup_frequency: "daily"
    retention_days: 30
```

### Deployment Commands
```bash
# Deploy advanced features to production
kubectl apply -f infrastructure/kubernetes/advanced-features/

# Verify deployment
kubectl get pods -n acgs-system -l tier=advanced

# Monitor performance
kubectl top pods -n acgs-system
kubectl logs -f deployment/wina-optimization -n acgs-system
```

## 📊 Monitoring and Troubleshooting

### Advanced Monitoring Queries
```bash
# WINA optimization performance
curl "http://localhost:9090/api/v1/query?query=wina_optimization_score"

# Constitutional cache hit rate
curl "http://localhost:9090/api/v1/query?query=constitutional_cache_hit_rate"

# Multi-model consensus accuracy
curl "http://localhost:9090/api/v1/query?query=consensus_accuracy_rate"

# System resource usage
curl "http://localhost:9090/api/v1/query?query=container_memory_usage_bytes"
```

### Troubleshooting Common Issues
```bash
# WINA optimization not converging
curl http://localhost:8006/api/v1/wina/diagnostics
# Check: learning rate, population size, convergence threshold

# Cache performance degradation
redis-cli INFO stats
redis-cli SLOWLOG GET 10
# Check: memory usage, slow queries, connection pool

# Consensus accuracy dropping
curl http://localhost:8004/api/v1/consensus/diagnostics
# Check: model availability, response times, weight distribution
```

---

This guide provides comprehensive configuration options for ACGS-1's advanced features. For specific use cases or custom configurations, refer to the individual service documentation or contact the development team.
