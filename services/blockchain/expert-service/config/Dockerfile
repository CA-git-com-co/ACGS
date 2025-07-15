# Multi-stage Dockerfile for ACGS-2 Expert System
# Constitutional Hash: cdd01ef066bc6cf2

# Build stage
FROM rust:1.75-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1001 appuser

# Set working directory
WORKDIR /app

# Copy workspace configuration
COPY Cargo.toml Cargo.lock ./
COPY crates/ ./crates/
COPY bin/ ./bin/

# Build the application in release mode
RUN cargo build --release --bin governance_app

# Runtime stage using distroless
FROM gcr.io/distroless/cc-debian12:latest

# Copy CA certificates for HTTPS requests
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy the binary from builder stage
COPY --from=builder /app/target/release/governance_app /usr/local/bin/governance_app

# Copy configuration files
COPY --from=builder /app/config.yaml /app/config.yaml

# Set working directory
WORKDIR /app

# Expose ports
EXPOSE 3000 9090

# Environment variables with defaults
ENV EXPERT_SYSTEM_PORT=3000
ENV EXPERT_SYSTEM_METRICS_PORT=9090
ENV LLM_MODEL=llama-3.1-8b-instant
ENV LLM_CONFIDENCE_THRESHOLD=0.66
ENV USE_FAKE_LLM=false
ENV USE_GROQ=true
ENV USE_BLOCKCHAIN=false
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENV SOLANA_RPC_URL=https://api.devnet.solana.com
ENV GOVERNANCE_PROGRAM_ID=CNru2EYbLnaYMSHydaLzeFJMcBxkJah73oQGh4AYsveE
ENV REDIS_URL=redis://redis:6379
ENV REDIS_CACHE_KEY_PREFIX=acgs:expert_system
ENV REDIS_CACHE_TTL_SECONDS=3600
ENV RATE_LIMIT_GOVERNANCE_REQUESTS_PER_MINUTE=100
ENV RATE_LIMIT_HEALTH_REQUESTS_PER_MINUTE=1000
ENV RATE_LIMIT_BURST=10
ENV CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
ENV CIRCUIT_BREAKER_TIMEOUT_SECONDS=30
ENV CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=3
ENV RUST_LOG=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["/usr/local/bin/governance_app", "--health-check"] || exit 1

# Run as non-root user (distroless uses nobody by default)
USER nobody

# Start the application
ENTRYPOINT ["/usr/local/bin/governance_app"]
