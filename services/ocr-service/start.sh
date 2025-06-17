#!/bin/bash
set -e

echo "Starting OCR service with model: ${MODEL_NAME}"
echo "Serving on port: ${PORT}"

# Start the vLLM server with the specified model
exec vllm serve ${MODEL_NAME} --port ${PORT} --host 0.0.0.0