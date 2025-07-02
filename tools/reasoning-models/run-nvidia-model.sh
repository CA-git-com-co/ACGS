#!/bin/bash
# NVIDIA AceReason-Nemotron-1.1-7B Deployment Script

export CUDA_VISIBLE_DEVICES=0
export VLLM_WORKER_MULTIPROC_METHOD=spawn

echo "Starting NVIDIA AceReason-Nemotron-1.1-7B on port 8000..."

nano-vllm-service.py "nvidia/AceReason-Nemotron-1.1-7B" \
    --host 0.0.0.0 \
    --port 8000 \
    # --tensor-parallel-size (handled by Nano-vLLM) 1 \
    --max-model-len 32768 \
    # --gpu-memory-utilization (handled by Nano-vLLM) 0.8 \
    --swap-space 4 \
    --disable-log-requests \
    --trust-remote-code \
    2>&1 | tee "/home/ubuntu/ACGS/logs/nvidia-model.log"
