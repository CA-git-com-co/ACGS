FROM vllm/vllm-openai:latest

# Set working directory
WORKDIR /app

# Install additional dependencies
RUN apt-get update && apt-get install -y curl procps && \
    pip install --no-cache-dir requests pillow

# Copy service files
COPY ./health_server.py /app/health_server.py
COPY ./start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Default configuration
ENV MODEL_NAME="nanonets/Nanonets-OCR-s"
ENV PORT=8666
ENV HEALTH_PORT=8667

# Expose ports
EXPOSE ${PORT}
EXPOSE ${HEALTH_PORT}

# Set up healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${HEALTH_PORT}/health || exit 1

# Run the service
ENTRYPOINT ["/app/start.sh"]