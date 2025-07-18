# 🏛️ ACGS-2 Expert System with Phase 2 Production Enhancements
**Constitutional Hash: cdd01ef066bc6cf2**


A high-performance AI governance expert system built in Rust with ultra-fast LLM API integration, comprehensive production features, and sub-200ms decision latency.

## 🚀 Features

### **🔧 Environment-Driven Configuration**
- **Complete config/environments/development.env support** - All configuration via environment variables
- **Multi-provider LLM switching** - Mock/Groq/OpenAI with single flag
- **Blockchain integration toggle** - Enable/disable Solana with USE_BLOCKCHAIN
- **Port configuration** - Flexible port assignment for services
- **Production-ready** - Secure API key management and deployment patterns

### **🆕 Phase 2 Production Enhancements**
- **🚦 Rate Limiting** - Token bucket rate limiting with configurable limits per endpoint
- **🔄 Circuit Breaker** - Resilient LLM API calls with fallback to cached responses
- **📖 OpenAPI Documentation** - Complete Swagger UI with interactive API docs
- **💾 Redis Distributed Caching** - High-performance caching with fallback support
- **🏥 Enhanced Health Checks** - Comprehensive health and readiness endpoints
- **🐳 Docker Support** - Multi-stage builds with distroless base images
- **📊 Advanced Metrics** - Prometheus integration with detailed performance metrics

### **Ultra-Fast LLM Integration**
- **Groq API**: 10x faster than OpenAI (50-200ms vs 500-2000ms)
- **OpenAI Compatibility**: Drop-in replacement with same API format
- **Mock LLM**: Cost-free testing and development
- **Automatic Fallback**: Graceful degradation between providers

### **Enterprise-Grade Architecture**
- **Multi-Tree Inference**: Parallel policy evaluation with confidence scoring
- **Constitutional Compliance**: Hash validation (cdd01ef066bc6cf2)
- **Performance Monitoring**: Prometheus metrics and health checks
- **Production Ready**: Async/await, connection pooling, circuit breakers
- **Rate Limiting**: Token bucket algorithm with per-endpoint configuration
- **Circuit Breaker**: Automatic failover with exponential backoff and jitter
- **Distributed Caching**: Redis-based caching with in-memory fallback
- **API Documentation**: OpenAPI 3.0 specification with Swagger UI

### **Governance Rules Engine**
- **HIPAA Privacy**: Patient data protection compliance
- **Fairness**: Algorithmic bias prevention
- **Integrity**: Data quality and authenticity validation
- **Extensible**: Easy to add new governance principles

## 📊 Performance Benchmarks

| Provider | RPS | Avg Latency | P99 Latency | Cost/1M tokens |
|----------|-----|-------------|-------------|-------------

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---|
| **Mock LLM** | 485 | 103ms | 105ms | $0 |
| **Groq API** | ~200 | ~150ms | ~300ms | $0.59 |
| **OpenAI** | ~50 | ~1000ms | ~2000ms | $15+ |

## 🔧 Configuration

### Environment Variables (config/environments/development.env)

The system uses a comprehensive config/environments/development.env configuration system for maximum flexibility:

```bash
# Copy the example configuration
cp config/environments/developmentconfig/environments/example.env config/environments/development.env

# Edit with your settings
nano config/environments/development.env
```

#### Core Configuration Options

```bash
# Constitutional Hash (DO NOT CHANGE)
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Server Configuration
EXPERT_SYSTEM_PORT=3000
EXPERT_SYSTEM_METRICS_PORT=9090

# LLM Configuration
LLM_MODEL=llama-3.1-8b-instant
LLM_CONFIDENCE_THRESHOLD=0.66

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Feature Flags
USE_FAKE_LLM=false          # Enable mock LLM for testing
USE_GROQ=true               # Enable ultra-fast Groq API
USE_BLOCKCHAIN=true         # Enable Solana blockchain integration

# Solana Blockchain
SOLANA_CLUSTER=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
GOVERNANCE_PROGRAM_ID=CNru2EYbLnaYMSHydaLzeFJMcBxkJah73oQGh4AYsveE
```

#### Phase 2 Production Features Configuration

```bash
# Rate Limiting Configuration
RATE_LIMIT_GOVERNANCE_REQUESTS_PER_MINUTE=100    # Governance endpoints limit
RATE_LIMIT_HEALTH_REQUESTS_PER_MINUTE=1000       # Health endpoints limit
RATE_LIMIT_BURST=10                              # Burst capacity

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5              # Failures before opening
CIRCUIT_BREAKER_TIMEOUT_SECONDS=30               # Timeout before half-open
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=3            # Max calls in half-open state

# Redis Distributed Caching Configuration
REDIS_URL=redis://localhost:6379                 # Redis connection URL
REDIS_CACHE_KEY_PREFIX=acgs:expert_system        # Cache key prefix
REDIS_CACHE_TTL_SECONDS=3600                     # Cache TTL (1 hour)
REDIS_MAX_CONNECTIONS=10                         # Connection pool size
```

#### Configuration Scenarios

**Development Mode (Fast Testing)**
```bash
USE_FAKE_LLM=true
USE_BLOCKCHAIN=false
```

**Blockchain Testing (No API Costs)**
```bash
USE_FAKE_LLM=true
USE_BLOCKCHAIN=true
```

**Production Mode (Ultra-Fast + Immutable)**
```bash
USE_GROQ=true
USE_BLOCKCHAIN=true
GROQ_API_KEY=your_real_key
```

## 🛠️ Quick Start

### Prerequisites
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install oha for benchmarking
cargo install oha
```

### Build and Run
```bash
# Clone and build
git clone <repository>
cd expert_system
cargo build --release

# Run with mock LLM (free)
USE_FAKE_LLM=1 cargo run --release -p governance_app

# Run with Groq API (ultra-fast)
export GROQ_API_KEY="your_groq_api_key"
USE_GROQ=1 cargo run --release -p governance_app

# Run with OpenAI (standard)
export OPENAI_API_KEY="your_openai_api_key"
cargo run --release -p governance_app
```

### Test the API
```bash
# Compliant query
curl -X POST http://127.0.0.1:3000/govern \
  -H "Content-Type: application/json" \
  -d '{"query": {"actor_role": "Researcher", "data_sensitivity": "AnonymizedAggregate"}}'

# Response: {"decision":"comply","confidence":1.0}

# Violating query  
curl -X POST http://127.0.0.1:3000/govern \
  -H "Content-Type: application/json" \
  -d '{"query": {"actor_role": "Clinician", "data_sensitivity": "IdentifiedPatientRecords"}}'

# Response: {"decision":"violate","confidence":0.67}
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone <repository>
cd expert_system

# Set your API keys in config/environments/development.env file
cp config/environments/developmentconfig/environments/example.env config/environments/development.env
# Edit config/environments/development.env with your GROQ_API_KEY or OPENAI_API_KEY

# Start all services (Expert System + Redis + Monitoring)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f expert_system

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build the Docker image
docker build -t acgs-expert-system .

# Run with Redis
docker run -d --name redis redis:7.2-alpine
docker run -d --name expert-system \
  --link redis:redis \
  -p 3000:3000 -p 9090:9090 \
  -e REDIS_URL=redis://redis:6379 \
  -e GROQ_API_KEY=your_groq_api_key \
  acgs-expert-system
```

### Production Deployment

```bash
# Production docker-compose with monitoring
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:3000/health

# API documentation
open http://localhost:3000/docs

# Metrics dashboard
open http://localhost:3001  # Grafana (admin/admin)
```

## 🎯 API Reference

### Governance Endpoints

#### POST /govern
Evaluate a governance query against configured policy trees.

**Request Body:**
```json
{
  "query": {
    "actorRole": "Researcher" | "Clinician",
    "dataSensitivity": "AnonymizedAggregate" | "IdentifiedPatientRecords"
  }
}
```

**Response:**
```json
{
  "decision": "Comply" | "Violate" | {"Uncertain": {"explanation": "..."}},
  "confidence": 0.85,
  "blockchain_tx": null,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### POST /govern/blockchain
Evaluate governance query and record decision on blockchain.

**Request Body:** Same as `/govern`

**Response:**
```json
{
  "decision": "Comply",
  "confidence": 0.85,
  "policy_id": 1234567890,
  "blockchain_tx": "5J7X8K9L2M3N4P5Q6R7S8T9U0V1W2X3Y4Z5A6B7C8D9E0F1G2H3I4J5K6L7M8N9P0Q",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Health & Monitoring Endpoints

#### GET /health
Basic health check for load balancers.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "version": "1.0.0"
}
```

#### GET /ready
Comprehensive readiness check with dependency status.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00Z",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "llm_provider": "groq",
  "blockchain_enabled": true,
  "circuit_breaker_states": [
    {
      "provider": "groq",
      "state": "Closed",
      "failure_threshold": 5,
      "timeout_duration_seconds": 30
    }
  ]
}
```

#### GET /metrics
Prometheus metrics endpoint for monitoring.

#### GET /docs
Interactive OpenAPI documentation (Swagger UI).

### Rate Limiting

All endpoints include rate limiting headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets

**Rate Limits:**
- Governance endpoints: 100 requests/minute per IP
- Health endpoints: 1000 requests/minute per IP

## 🔧 Configuration

### Environment Variables
- `USE_FAKE_LLM=1`: Use mock LLM for testing
- `USE_GROQ=1`: Use Groq API for ultra-fast inference
- `GROQ_API_KEY`: Your Groq API key
- `OPENAI_API_KEY`: Your OpenAI API key

### config.yaml
```yaml
llm_model: "llama3-8b-8192"  # Groq model for fast inference
forest:
  - [ hipaa-privacy, integrity ]
  - [ fairness, integrity ]  
  - [ hipaa-privacy, fairness ]
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Client   │───▶│  Axum Web Server │───▶│ Inference Engine│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐             ▼
                       │ Prometheus       │    ┌─────────────────┐
                       │ Metrics          │◀───│ Policy Forest   │
                       └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Groq API         │◀───│ LLM Judge       │
                       │ (Ultra-Fast)     │    │ (Pluggable)     │
                       └──────────────────┘    └─────────────────┘
```

## 🚀 Deployment

### Docker
```dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates
COPY --from=builder /app/target/release/governance_app /usr/local/bin/
EXPOSE 3000 9090
CMD ["governance_app"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-expert-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: acgs-expert-system
  template:
    metadata:
      labels:
        app: acgs-expert-system
    spec:
      containers:
      - name: expert-system
        image: acgs/expert-system:latest
        ports:
        - containerPort: 3000
        - containerPort: 9090
        env:
        - name: USE_GROQ
          value: "1"
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: groq-secret
              key: api-key
```

## 🧪 Testing & Benchmarking

### Run Demo
```bash
./demo_groq_integration.sh
```

### Benchmark Suite
```bash
./run_benchmarks.sh
```

### Unit Tests
```bash
cargo test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🎬 Demo Scripts

Comprehensive demonstration scripts are included to showcase all features:

### Available Demos

```bash
# Complete config/environments/development.env configuration demo
./demo_env_configuration.sh
# Shows: Environment variable loading, multi-provider switching, blockchain toggle

# Groq integration performance demo
./demo_groq_integration.sh
# Shows: Ultra-fast inference, performance comparison, cost analysis

# Blockchain integration demo
./demo_blockchain_integration.sh
# Shows: Solana integration, immutable governance records, audit trails

# Performance benchmarks
./run_benchmarks.sh
# Shows: RPS testing, latency analysis, provider comparison
```

### Demo Features

- **🔧 Configuration Testing** - All config/environments/development.env scenarios (Mock/Groq/Blockchain)
- **⚡ Performance Analysis** - Real-time latency and throughput metrics
- **🔗 Blockchain Integration** - Solana governance contract interaction
- **📊 Comparative Benchmarks** - Mock vs Groq vs OpenAI performance
- **🎯 Production Readiness** - End-to-end deployment validation

## 🔗 Links

- [Groq Console](https://console.groq.com/keys) - Get your API key
- [ACGS-2 Documentation](README.md.backup) - Main project docs
- [Rust Performance Guide](https://nnethercote.github.io/perf-book/) - Optimization tips
- [Solana Devnet](https://explorer.solana.com/?cluster=devnet) - Blockchain explorer
