#!/bin/bash

# ACGS-1 vLLM Reasoning Models Deployment Script
# Deploys NVIDIA AceReason-Nemotron-1.1-7B and Microsoft Phi-4-mini-reasoning

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="/tmp/acgs-vllm-deployment.log"

# Set up environment variables for CUDA libraries
export LD_LIBRARY_PATH="/usr/local/lib/python3.10/dist-packages/cusparselt/lib:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
export PATH="/home/ubuntu/.local/bin:$PATH"

# Model configurations
NVIDIA_MODEL="nvidia/AceReason-Nemotron-1.1-7B"
MICROSOFT_MODEL="microsoft/Phi-4-mini-reasoning"
MULTIMODAL_MODEL="nvidia/Llama-3.1-Nemotron-Nano-VL-8B-V1"
NVIDIA_PORT=8000
MICROSOFT_PORT=8001
MULTIMODAL_PORT=8002

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements for vLLM deployment..."
    
    # Check Python version
    if ! command_exists python3; then
        error "Python 3 is not installed"
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    info "Python version: $PYTHON_VERSION"
    
    # Check for CUDA (optional but recommended)
    if command_exists nvidia-smi; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1)
        info "GPU detected: $GPU_INFO"
        
        # Check VRAM requirements
        VRAM=$(echo "$GPU_INFO" | cut -d',' -f2 | tr -d ' ')
        if [ "$VRAM" -lt 16000 ]; then
            warn "GPU VRAM is less than 16GB. Models may run slowly or fail to load."
        fi
    else
        warn "No NVIDIA GPU detected. Models will run on CPU (slower performance)."
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df "$HOME" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 50000000 ]; then  # 50GB in KB
        warn "Less than 50GB disk space available. Model downloads may fail."
    fi
    
    # Check memory
    TOTAL_RAM=$(free -m | awk 'NR==2{print $2}')
    if [ "$TOTAL_RAM" -lt 16000 ]; then
        warn "Less than 16GB RAM available. Models may run slowly."
    fi
    
    log "✅ System requirements check completed"
}

# Function to install vLLM and multimodal dependencies
install_vllm() {
    log "Installing vLLM and multimodal dependencies..."

    # Upgrade pip first
    python3 -m pip install --upgrade pip

    # Install multimodal model dependencies first
    log "Installing multimodal model dependencies..."
    python3 -m pip install transformers accelerate timm einops open-clip-torch

    # Install vLLM with CUDA support if available
    if command_exists nvidia-smi; then
        log "Installing vLLM with CUDA support..."
        python3 -m pip install vllm
    else
        log "Installing vLLM for CPU..."
        python3 -m pip install vllm
    fi

    # Verify installations
    log "Verifying installations..."

    # Check vLLM
    if python3 -c "import vllm; print('vLLM version:', vllm.__version__)" 2>/dev/null; then
        log "✅ vLLM installed successfully"
    else
        error "vLLM installation failed"
    fi

    # Check multimodal dependencies
    for package in transformers accelerate timm einops; do
        if python3 -c "import $package" 2>/dev/null; then
            log "✅ $package installed successfully"
        else
            warn "$package installation may have issues"
        fi
    done

    # Check open-clip-torch separately (different import name)
    if python3 -c "import open_clip" 2>/dev/null; then
        log "✅ open-clip-torch installed successfully"
    else
        warn "open-clip-torch installation may have issues"
    fi
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while ! check_port $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            error "No available ports found in range $start_port-$((start_port + 100))"
        fi
    done
    
    echo $port
}

# Function to deploy NVIDIA AceReason model
deploy_nvidia_model() {
    log "Deploying NVIDIA AceReason-Nemotron-1.1-7B model..."
    
    # Find available port
    NVIDIA_PORT=$(find_available_port $NVIDIA_PORT)
    info "Using port $NVIDIA_PORT for NVIDIA model"
    
    # Create deployment script
    cat > "$PROJECT_ROOT/scripts/reasoning-models/run-nvidia-model.sh" << EOF
#!/bin/bash
# NVIDIA AceReason-Nemotron-1.1-7B Deployment Script

export CUDA_VISIBLE_DEVICES=0
export VLLM_WORKER_MULTIPROC_METHOD=spawn

echo "Starting NVIDIA AceReason-Nemotron-1.1-7B on port $NVIDIA_PORT..."

vllm serve "$NVIDIA_MODEL" \\
    --host 0.0.0.0 \\
    --port $NVIDIA_PORT \\
    --tensor-parallel-size 1 \\
    --max-model-len 32768 \\
    --gpu-memory-utilization 0.8 \\
    --swap-space 4 \\
    --disable-log-requests \\
    --trust-remote-code \\
    2>&1 | tee "$PROJECT_ROOT/logs/nvidia-model.log"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/reasoning-models/run-nvidia-model.sh"
    
    # Start model in background
    log "Starting NVIDIA model server..."
    nohup "$PROJECT_ROOT/scripts/reasoning-models/run-nvidia-model.sh" > "$PROJECT_ROOT/logs/nvidia-model-startup.log" 2>&1 &
    NVIDIA_PID=$!
    
    # Wait for model to start
    log "Waiting for NVIDIA model to start (this may take several minutes)..."
    for i in {1..60}; do
        if curl -s "http://localhost:$NVIDIA_PORT/health" >/dev/null 2>&1; then
            log "✅ NVIDIA AceReason model started successfully on port $NVIDIA_PORT"
            echo "$NVIDIA_PID" > "$PROJECT_ROOT/pids/nvidia-model.pid"
            return 0
        fi
        sleep 10
        echo -n "."
    done
    
    error "NVIDIA model failed to start within 10 minutes"
}

# Function to deploy Microsoft Phi-4 model
deploy_microsoft_model() {
    log "Deploying Microsoft Phi-4-mini-reasoning model..."
    
    # Find available port
    MICROSOFT_PORT=$(find_available_port $MICROSOFT_PORT)
    info "Using port $MICROSOFT_PORT for Microsoft model"
    
    # Create deployment script
    cat > "$PROJECT_ROOT/scripts/reasoning-models/run-microsoft-model.sh" << EOF
#!/bin/bash
# Microsoft Phi-4-mini-reasoning Deployment Script

export CUDA_VISIBLE_DEVICES=1
export VLLM_WORKER_MULTIPROC_METHOD=spawn

echo "Starting Microsoft Phi-4-mini-reasoning on port $MICROSOFT_PORT..."

vllm serve "$MICROSOFT_MODEL" \\
    --host 0.0.0.0 \\
    --port $MICROSOFT_PORT \\
    --tensor-parallel-size 1 \\
    --max-model-len 16384 \\
    --gpu-memory-utilization 0.7 \\
    --swap-space 2 \\
    --disable-log-requests \\
    --trust-remote-code \\
    2>&1 | tee "$PROJECT_ROOT/logs/microsoft-model.log"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/reasoning-models/run-microsoft-model.sh"
    
    # Start model in background
    log "Starting Microsoft model server..."
    nohup "$PROJECT_ROOT/scripts/reasoning-models/run-microsoft-model.sh" > "$PROJECT_ROOT/logs/microsoft-model-startup.log" 2>&1 &
    MICROSOFT_PID=$!
    
    # Wait for model to start
    log "Waiting for Microsoft model to start (this may take several minutes)..."
    for i in {1..60}; do
        if curl -s "http://localhost:$MICROSOFT_PORT/health" >/dev/null 2>&1; then
            log "✅ Microsoft Phi-4 model started successfully on port $MICROSOFT_PORT"
            echo "$MICROSOFT_PID" > "$PROJECT_ROOT/pids/microsoft-model.pid"
            return 0
        fi
        sleep 10
        echo -n "."
    done
    
    error "Microsoft model failed to start within 10 minutes"
}

# Function to deploy NVIDIA Multimodal VL model
deploy_multimodal_model() {
    log "Deploying NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 model..."

    # Find available port
    MULTIMODAL_PORT=$(find_available_port $MULTIMODAL_PORT)
    info "Using port $MULTIMODAL_PORT for Multimodal VL model"

    # Check for GPU compatibility issues
    GPU_COMPATIBLE=true
    if command_exists nvidia-smi; then
        # Check for NVIDIA B200 GPU compatibility issue
        GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)
        if echo "$GPU_INFO" | grep -q "B200"; then
            warn "NVIDIA B200 GPU detected - may have PyTorch compatibility issues"
            warn "Will attempt GPU deployment but may fall back to CPU mode"
            GPU_COMPATIBLE=false
        fi
    fi

    # Create deployment script with CPU fallback
    cat > "$PROJECT_ROOT/scripts/reasoning-models/run-multimodal-model.sh" << EOF
#!/bin/bash
# NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 Deployment Script

# Set up environment for CUDA libraries
export LD_LIBRARY_PATH="/usr/local/lib/python3.10/dist-packages/cusparselt/lib:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH"
export PATH="/home/ubuntu/.local/bin:\$PATH"

echo "Starting NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 on port $MULTIMODAL_PORT..."

# Try GPU deployment first, fall back to CPU if needed
if command -v nvidia-smi >/dev/null 2>&1 && [ "$GPU_COMPATIBLE" = "true" ]; then
    echo "Attempting GPU deployment..."
    export CUDA_VISIBLE_DEVICES=2
    export VLLM_WORKER_MULTIPROC_METHOD=spawn

    vllm serve "$MULTIMODAL_MODEL" \\
        --host 0.0.0.0 \\
        --port $MULTIMODAL_PORT \\
        --tensor-parallel-size 1 \\
        --max-model-len 16384 \\
        --gpu-memory-utilization 0.6 \\
        --swap-space 4 \\
        --disable-log-requests \\
        --trust-remote-code \\
        --enable-multimodal \\
        2>&1 | tee "$PROJECT_ROOT/logs/multimodal-model.log"
else
    echo "Using CPU-only deployment due to GPU compatibility issues..."
    export CUDA_VISIBLE_DEVICES=""

    vllm serve "$MULTIMODAL_MODEL" \\
        --host 0.0.0.0 \\
        --port $MULTIMODAL_PORT \\
        --tensor-parallel-size 1 \\
        --max-model-len 8192 \\
        --disable-log-requests \\
        --trust-remote-code \\
        --enable-multimodal \\
        --device cpu \\
        2>&1 | tee "$PROJECT_ROOT/logs/multimodal-model.log"
fi
EOF

    chmod +x "$PROJECT_ROOT/scripts/reasoning-models/run-multimodal-model.sh"

    # Start model in background
    log "Starting Multimodal VL model server..."
    nohup "$PROJECT_ROOT/scripts/reasoning-models/run-multimodal-model.sh" > "$PROJECT_ROOT/logs/multimodal-model-startup.log" 2>&1 &
    MULTIMODAL_PID=$!

    # Wait for model to start
    log "Waiting for Multimodal VL model to start (this may take several minutes)..."
    for i in {1..60}; do
        if curl -s "http://localhost:$MULTIMODAL_PORT/health" >/dev/null 2>&1; then
            log "✅ NVIDIA Multimodal VL model started successfully on port $MULTIMODAL_PORT"
            echo "$MULTIMODAL_PID" > "$PROJECT_ROOT/pids/multimodal-model.pid"
            return 0
        fi
        sleep 10
        echo -n "."
    done

    error "Multimodal VL model failed to start within 10 minutes"
}

# Function to test model deployments
test_model_deployments() {
    log "Testing model deployments..."
    
    # Test NVIDIA model
    log "Testing NVIDIA AceReason model..."
    NVIDIA_RESPONSE=$(curl -s -X POST "http://localhost:$NVIDIA_PORT/v1/chat/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "'"$NVIDIA_MODEL"'",
            "messages": [
                {
                    "role": "user",
                    "content": "What is constitutional governance?"
                }
            ],
            "max_tokens": 100
        }' | jq -r '.choices[0].message.content' 2>/dev/null)
    
    if [ -n "$NVIDIA_RESPONSE" ] && [ "$NVIDIA_RESPONSE" != "null" ]; then
        log "✅ NVIDIA model test successful"
        info "Response preview: ${NVIDIA_RESPONSE:0:100}..."
    else
        warn "NVIDIA model test failed or returned empty response"
    fi
    
    # Test Microsoft model
    log "Testing Microsoft Phi-4 model..."
    MICROSOFT_RESPONSE=$(curl -s -X POST "http://localhost:$MICROSOFT_PORT/v1/chat/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "'"$MICROSOFT_MODEL"'",
            "messages": [
                {
                    "role": "user",
                    "content": "What is ethical AI reasoning?"
                }
            ],
            "max_tokens": 100
        }' | jq -r '.choices[0].message.content' 2>/dev/null)
    
    if [ -n "$MICROSOFT_RESPONSE" ] && [ "$MICROSOFT_RESPONSE" != "null" ]; then
        log "✅ Microsoft model test successful"
        info "Response preview: ${MICROSOFT_RESPONSE:0:100}..."
    else
        warn "Microsoft model test failed or returned empty response"
    fi

    # Test Multimodal VL model
    log "Testing NVIDIA Multimodal VL model..."
    MULTIMODAL_RESPONSE=$(curl -s -X POST "http://localhost:$MULTIMODAL_PORT/v1/completions" \
        -H "Content-Type: application/json" \
        --data '{
            "model": "'"$MULTIMODAL_MODEL"'",
            "prompt": "Analyze this governance document for constitutional compliance:",
            "max_tokens": 100,
            "temperature": 0.1
        }' | jq -r '.choices[0].text' 2>/dev/null)

    if [ -n "$MULTIMODAL_RESPONSE" ] && [ "$MULTIMODAL_RESPONSE" != "null" ]; then
        log "✅ Multimodal VL model test successful"
        info "Response preview: ${MULTIMODAL_RESPONSE:0:100}..."
    else
        warn "Multimodal VL model test failed or returned empty response"
    fi
}

# Function to create service configuration
create_service_config() {
    log "Creating service configuration..."
    
    # Create configuration file
    cat > "$PROJECT_ROOT/config/reasoning-models.json" << EOF
{
    "reasoning_models": {
        "nvidia_acerreason": {
            "model_name": "$NVIDIA_MODEL",
            "endpoint": "http://localhost:$NVIDIA_PORT",
            "specialties": ["governance", "accountability"],
            "max_context_length": 32768,
            "reasoning_strength": 0.95,
            "status": "active"
        },
        "microsoft_phi4": {
            "model_name": "$MICROSOFT_MODEL",
            "endpoint": "http://localhost:$MICROSOFT_PORT",
            "specialties": ["ethics", "fairness"],
            "max_context_length": 16384,
            "reasoning_strength": 0.90,
            "status": "active"
        },
        "nvidia_multimodal_vl": {
            "model_name": "$MULTIMODAL_MODEL",
            "endpoint": "http://localhost:$MULTIMODAL_PORT",
            "specialties": ["document_analysis", "visual_reasoning", "multimodal_compliance", "ocr", "constitutional_document_analysis"],
            "max_context_length": 16384,
            "reasoning_strength": 0.88,
            "vision_capabilities": true,
            "supported_formats": ["image", "text"],
            "max_image_resolution": "3072x1024",
            "tile_layout": "12_tiles_max",
            "use_cases": ["image_summarization", "text_image_analysis", "ocr", "interactive_qa", "chain_of_thought_reasoning"],
            "dependencies": ["transformers", "accelerate", "timm", "einops", "open-clip-torch"],
            "status": "active"
        }
    },
    "deployment_info": {
        "deployed_at": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")",
        "deployed_by": "$(whoami)",
        "version": "1.0",
        "log_directory": "$PROJECT_ROOT/logs",
        "pid_directory": "$PROJECT_ROOT/pids"
    }
}
EOF
    
    log "✅ Service configuration created"
}

# Function to create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > "$PROJECT_ROOT/scripts/reasoning-models/monitor-models.sh" << EOF
#!/bin/bash
# ACGS-1 Reasoning Models Monitoring Script

check_model_health() {
    local model_name=\$1
    local port=\$2
    
    if curl -s "http://localhost:\$port/health" >/dev/null 2>&1; then
        echo "✅ \$model_name: Healthy (port \$port)"
        return 0
    else
        echo "❌ \$model_name: Unhealthy (port \$port)"
        return 1
    fi
}

echo "🔍 ACGS-1 Reasoning Models Health Check"
echo "======================================"
echo "Timestamp: \$(date)"
echo ""

# Check NVIDIA model
check_model_health "NVIDIA AceReason" "$NVIDIA_PORT"

# Check Microsoft model
check_model_health "Microsoft Phi-4" "$MICROSOFT_PORT"

# Check Multimodal VL model
check_model_health "NVIDIA Multimodal VL" "$MULTIMODAL_PORT"

echo ""
echo "📊 Resource Usage:"
echo "CPU: \$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | cut -d'%' -f1)%"
echo "Memory: \$(free | grep Mem | awk '{printf("%.1f%%", \$3/\$2 * 100.0)}')"

if command -v nvidia-smi >/dev/null 2>&1; then
    echo "GPU Memory: \$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf("%.1f%%", \$1/\$2 * 100.0)}')"
fi
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/reasoning-models/monitor-models.sh"
    
    log "✅ Monitoring script created"
}

# Function to setup directories
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/pids"
    mkdir -p "$PROJECT_ROOT/config"
    mkdir -p "$PROJECT_ROOT/scripts/reasoning-models"
    
    log "✅ Directories created"
}

# Function to create shutdown script
create_shutdown_script() {
    log "Creating shutdown script..."
    
    cat > "$PROJECT_ROOT/scripts/reasoning-models/shutdown-models.sh" << EOF
#!/bin/bash
# ACGS-1 Reasoning Models Shutdown Script

echo "🛑 Shutting down ACGS-1 reasoning models..."

# Shutdown NVIDIA model
if [ -f "$PROJECT_ROOT/pids/nvidia-model.pid" ]; then
    NVIDIA_PID=\$(cat "$PROJECT_ROOT/pids/nvidia-model.pid")
    if kill -0 "\$NVIDIA_PID" 2>/dev/null; then
        echo "Stopping NVIDIA model (PID: \$NVIDIA_PID)..."
        kill "\$NVIDIA_PID"
        rm -f "$PROJECT_ROOT/pids/nvidia-model.pid"
    fi
fi

# Shutdown Microsoft model
if [ -f "$PROJECT_ROOT/pids/microsoft-model.pid" ]; then
    MICROSOFT_PID=\$(cat "$PROJECT_ROOT/pids/microsoft-model.pid")
    if kill -0 "\$MICROSOFT_PID" 2>/dev/null; then
        echo "Stopping Microsoft model (PID: \$MICROSOFT_PID)..."
        kill "\$MICROSOFT_PID"
        rm -f "$PROJECT_ROOT/pids/microsoft-model.pid"
    fi
fi

# Shutdown Multimodal VL model
if [ -f "$PROJECT_ROOT/pids/multimodal-model.pid" ]; then
    MULTIMODAL_PID=\$(cat "$PROJECT_ROOT/pids/multimodal-model.pid")
    if kill -0 "\$MULTIMODAL_PID" 2>/dev/null; then
        echo "Stopping Multimodal VL model (PID: \$MULTIMODAL_PID)..."
        kill "\$MULTIMODAL_PID"
        rm -f "$PROJECT_ROOT/pids/multimodal-model.pid"
    fi
fi

echo "✅ All reasoning models stopped"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/reasoning-models/shutdown-models.sh"
    
    log "✅ Shutdown script created"
}

# Main deployment function
main() {
    log "🚀 Starting ACGS-1 vLLM Reasoning Models Deployment"
    log "=================================================="
    
    # Setup
    setup_directories
    check_system_requirements
    install_vllm
    
    # Deploy models
    deploy_nvidia_model
    deploy_microsoft_model
    deploy_multimodal_model
    
    # Test and configure
    test_model_deployments
    create_service_config
    create_monitoring_script
    create_shutdown_script
    
    log "🎉 ACGS-1 vLLM Reasoning Models Deployment Complete!"
    log "=================================================="
    log "NVIDIA AceReason: http://localhost:$NVIDIA_PORT"
    log "Microsoft Phi-4: http://localhost:$MICROSOFT_PORT"
    log "NVIDIA Multimodal VL: http://localhost:$MULTIMODAL_PORT"
    log ""
    log "Management Commands:"
    log "  Monitor: $PROJECT_ROOT/scripts/reasoning-models/monitor-models.sh"
    log "  Shutdown: $PROJECT_ROOT/scripts/reasoning-models/shutdown-models.sh"
    log ""
    log "Log files:"
    log "  NVIDIA: $PROJECT_ROOT/logs/nvidia-model.log"
    log "  Microsoft: $PROJECT_ROOT/logs/microsoft-model.log"
    log "  Deployment: $LOG_FILE"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "test")
        test_model_deployments
        ;;
    "monitor")
        if [ -f "$PROJECT_ROOT/scripts/reasoning-models/monitor-models.sh" ]; then
            "$PROJECT_ROOT/scripts/reasoning-models/monitor-models.sh"
        else
            error "Monitoring script not found. Run deployment first."
        fi
        ;;
    "shutdown")
        if [ -f "$PROJECT_ROOT/scripts/reasoning-models/shutdown-models.sh" ]; then
            "$PROJECT_ROOT/scripts/reasoning-models/shutdown-models.sh"
        else
            error "Shutdown script not found. Run deployment first."
        fi
        ;;
    "help")
        echo "ACGS-1 vLLM Reasoning Models Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  test      - Test model endpoints"
        echo "  monitor   - Check model health"
        echo "  shutdown  - Stop all models"
        echo "  help      - Show this help message"
        ;;
    *)
        error "Unknown command: $1. Use 'help' for usage information."
        ;;
esac
