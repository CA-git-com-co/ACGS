# Add AICI runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libwasmtime-dev \
    && rm -rf /var/lib/apt/lists/*

# Install AICI Python bindings
RUN pip install --no-cache-dir \
    aici-python==0.5.0 \
    wasmtime==11.0.0

# Copy AICI controller WASM modules
COPY services/core/aici-integration/wasm/*.wasm /app/wasm/

# Set AICI environment variables
ENV AICI_CONTROLLERS_PATH=/app/wasm
ENV AICI_OPA_SERVICE_URL=http://opa:8181/v1/data
ENV AICI_CONSTITUTIONAL_HASH=cdd01ef066bc6cf2