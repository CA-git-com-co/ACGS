# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Expert Service Unified Dockerfile
# Multi-stage build for optimized production deployment

# Build stage
FROM rust:1.75-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy workspace configuration
COPY Cargo.toml Cargo.lock ./

# Copy shared libraries
COPY shared/ ./shared/

# Copy expert service source
COPY expert-service/ ./expert-service/

# Build the expert service
RUN cargo build --release --bin governance_app

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -r -s /bin/false -m -d /app acgs

# Set working directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/target/release/governance_app ./governance_app

# Copy configuration files
COPY expert-service/config/ ./config/

# Set ownership
RUN chown -R acgs:acgs /app

# Switch to app user
USER acgs

# Expose ports
EXPOSE 8002 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Environment variables with defaults
ENV RUST_LOG=info
ENV BIND_ADDRESS=0.0.0.0:8002
ENV METRICS_ADDRESS=0.0.0.0:8003
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Start the application
CMD ["./governance_app"]
