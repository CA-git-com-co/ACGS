FROM vllm/vllm-openai:latest

# Set working directory
WORKDIR /app

# Install additional dependencies if needed
RUN pip install --no-cache-dir requests pillow

# Copy startup script
COPY ./start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Default model to use
ENV MODEL_NAME="nanonets/Nanonets-OCR-s"
ENV PORT=8666

# Expose API port
EXPOSE ${PORT}

# Run the vLLM service
ENTRYPOINT ["/app/start.sh"]