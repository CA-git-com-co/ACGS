#!/bin/bash
set -e

# Environment variables with defaults
export MODEL_NAME=${MODEL_NAME:-"nanonets/Nanonets-OCR-s"}
export PORT=${PORT:-8666}
export HEALTH_PORT=${HEALTH_PORT:-8667}

echo "Starting OCR service with model: ${MODEL_NAME}"
echo "API serving on port: ${PORT}"
echo "Health check on port: ${HEALTH_PORT}"

# Copy the health server script
cp /app/health_server.py /app/health_server.py

# Start the health check server in the background
echo "Starting health check server..."
python /app/health_server.py --port ${HEALTH_PORT} --vllm-port ${PORT} &
HEALTH_PID=$!

# Give the health server a moment to start
sleep 1

# Add trap to kill health server on exit
trap 'kill ${HEALTH_PID} 2>/dev/null || true' EXIT

# Start the vLLM server with the specified model
echo "Starting vLLM server..."
exec vllm serve ${MODEL_NAME} --port ${PORT} --host 0.0.0.0