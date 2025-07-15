#!/bin/bash

# ACGS Kimi-Dev SWE-bench Environment Setup
# Automated setup for SWE-bench repository structure and dependencies

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SWE_DATA_DIR="$PROJECT_ROOT/data/swe_repos"
KIMI_DEV_DIR="$PROJECT_ROOT/integrations/kimi-dev"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create conda environment for Kimi-Dev
setup_conda_environment() {
    log_info "Setting up Kimi-Dev conda environment..."
    
    # Check if conda is available
    if ! command -v conda &> /dev/null; then
        log_error "Conda is not installed. Please install Miniconda or Anaconda first."
        exit 1
    fi
    
    # Create environment if it doesn't exist
    if ! conda env list | grep -q "kimidev"; then
        log_info "Creating kimidev conda environment..."
        conda create -n kimidev python=3.12 -y
        log_success "Created kimidev environment"
    else
        log_info "kimidev environment already exists"
    fi
    
    # Activate environment and install dependencies
    log_info "Installing Kimi-Dev dependencies..."
    eval "$(conda shell.bash hook)"
    conda activate kimidev
    
    # Install vLLM with CUDA support
    pip install vllm --extra-index-url https://download.pytorch.org/whl/cu128
    
    # Install other dependencies
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    pip install transformers datasets accelerate
    pip install requests aiohttp fastapi uvicorn
    pip install pytest pytest-asyncio
    
    log_success "Dependencies installed"
}

# Clone Kimi-Dev repository
clone_kimi_dev() {
    log_info "Setting up Kimi-Dev repository..."
    
    if [[ ! -d "$KIMI_DEV_DIR" ]]; then
        log_info "Cloning Kimi-Dev repository..."
        git clone https://github.com/MoonshotAI/Kimi-Dev.git "$KIMI_DEV_DIR"
        log_success "Kimi-Dev repository cloned"
    else
        log_info "Kimi-Dev repository already exists, updating..."
        cd "$KIMI_DEV_DIR"
        git pull origin main
        log_success "Kimi-Dev repository updated"
    fi
    
    # Install Kimi-Dev in development mode
    cd "$KIMI_DEV_DIR"
    eval "$(conda shell.bash hook)"
    conda activate kimidev
    pip install -e .
    
    log_success "Kimi-Dev installed in development mode"
}

# Download SWE-bench repository structure
download_swe_data() {
    log_info "Setting up SWE-bench repository structure..."
    
    mkdir -p "$SWE_DATA_DIR"
    
    # Check if data already exists
    if [[ -d "$SWE_DATA_DIR/repos" ]] && [[ $(find "$SWE_DATA_DIR/repos" -type d | wc -l) -gt 10 ]]; then
        log_info "SWE-bench data already exists"
        return 0
    fi
    
    log_info "Downloading SWE-bench repository structure..."
    log_warning "This is a large download (~10GB). Please be patient..."
    
    # Download the preprocessed data
    cd "$SWE_DATA_DIR"
    
    # Use wget or curl to download
    if command -v wget &> /dev/null; then
        wget -O swebench_repo_structure.zip "https://drive.google.com/uc?export=download&id=15-4XjTmY48ystrsc_xcvtOkMs3Fx8RoW"
    elif command -v curl &> /dev/null; then
        curl -L -o swebench_repo_structure.zip "https://drive.google.com/uc?export=download&id=15-4XjTmY48ystrsc_xcvtOkMs3Fx8RoW"
    else
        log_error "Neither wget nor curl is available. Please download manually:"
        log_error "URL: https://drive.google.com/file/d/15-4XjTmY48ystrsc_xcvtOkMs3Fx8RoW/view"
        log_error "Extract to: $SWE_DATA_DIR"
        exit 1
    fi
    
    # Extract the data
    if [[ -f "swebench_repo_structure.zip" ]]; then
        log_info "Extracting SWE-bench data..."
        unzip -q swebench_repo_structure.zip
        rm swebench_repo_structure.zip
        log_success "SWE-bench data extracted"
    else
        log_error "Failed to download SWE-bench data"
        log_info "Please download manually from: https://drive.google.com/file/d/15-4XjTmY48ystrsc_xcvtOkMs3Fx8RoW/view"
        exit 1
    fi
}

# Set up environment variables
setup_environment_variables() {
    log_info "Setting up environment variables..."
    
    # Add to config/environments/development.env file
    cd "$PROJECT_ROOT"
    
    # Check if PROJECT_FILE_LOC is already set
    if ! grep -q "PROJECT_FILE_LOC=" config/environments/development.env; then
        echo "" >> config/environments/development.env
        echo "# SWE-bench Configuration" >> config/environments/development.env
        echo "PROJECT_FILE_LOC=$SWE_DATA_DIR" >> config/environments/development.env
        log_success "Added PROJECT_FILE_LOC to config/environments/development.env"
    else
        log_info "PROJECT_FILE_LOC already configured"
    fi
    
    # Add other SWE-bench related variables
    if ! grep -q "ENABLE_SWE_BENCH=" config/environments/development.env; then
        echo "ENABLE_SWE_BENCH=true" >> config/environments/development.env
        echo "SWE_BENCH_DATASET=swe-bench-verified" >> config/environments/development.env
        echo "TENSOR_PARALLEL_SIZE=1" >> config/environments/development.env
        log_success "Added SWE-bench configuration to config/environments/development.env"
    fi
}

# Create processor Dockerfile
create_processor_dockerfile() {
    log_info "Creating processor Dockerfile..."
    
    cat > "$KIMI_DEV_DIR/Dockerfile.processor" << 'EOF'
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Kimi-Dev source
COPY . /app/kimi-dev

# Install Python dependencies
RUN pip install -e /app/kimi-dev
RUN pip install requests aiohttp fastapi uvicorn

# Create processor script
RUN mkdir -p /app/kimi-dev/kimidev/processor

# Set environment variables
ENV PYTHONPATH=/app/kimi-dev
ENV PROJECT_FILE_LOC=/app/swe_repos

# Default command
CMD ["python", "-m", "kimidev.processor.main"]
EOF
    
    log_success "Processor Dockerfile created"
}

# Create SWE-bench data manager script
create_data_manager() {
    log_info "Creating SWE-bench data manager..."
    
    cat > "$SCRIPT_DIR/manage_swe_data.py" << 'EOF'
#!/usr/bin/env python3
"""
SWE-bench Data Manager
Manages repository structure and preprocessing for Kimi-Dev
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SWEDataManager:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.repos_dir = self.data_dir / "repos"
        self.metadata_file = self.data_dir / "metadata.json"
        
    def validate_structure(self) -> bool:
        """Validate SWE-bench repository structure"""
        logger.info("Validating SWE-bench repository structure...")
        
        if not self.repos_dir.exists():
            logger.error(f"Repository directory not found: {self.repos_dir}")
            return False
            
        # Count repositories
        repo_count = len([d for d in self.repos_dir.iterdir() if d.is_dir()])
        logger.info(f"Found {repo_count} repositories")
        
        if repo_count < 10:
            logger.warning("Low repository count. Data may be incomplete.")
            
        return True
        
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata for available repositories"""
        logger.info("Generating repository metadata...")
        
        metadata = {
            "repositories": [],
            "total_count": 0,
            "last_updated": None
        }
        
        if not self.repos_dir.exists():
            return metadata
            
        for repo_dir in self.repos_dir.iterdir():
            if repo_dir.is_dir():
                repo_info = {
                    "name": repo_dir.name,
                    "path": str(repo_dir),
                    "size": sum(f.stat().st_size for f in repo_dir.rglob('*') if f.is_file())
                }
                metadata["repositories"].append(repo_info)
                
        metadata["total_count"] = len(metadata["repositories"])
        
        # Save metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Generated metadata for {metadata['total_count']} repositories")
        return metadata
        
    def cleanup_old_data(self, days: int = 30):
        """Clean up old temporary files"""
        logger.info(f"Cleaning up files older than {days} days...")
        
        # Implementation for cleanup
        # This would remove temporary files, logs, etc.
        pass

def main():
    data_dir = os.environ.get('PROJECT_FILE_LOC', '/app/swe_repos')
    manager = SWEDataManager(data_dir)
    
    # Validate and generate metadata
    if manager.validate_structure():
        manager.generate_metadata()
        logger.info("SWE-bench data management completed successfully")
    else:
        logger.error("SWE-bench data validation failed")
        exit(1)

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$SCRIPT_DIR/manage_swe_data.py"
    log_success "SWE-bench data manager created"
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    # Check conda environment
    eval "$(conda shell.bash hook)"
    if conda activate kimidev 2>/dev/null; then
        log_success "✓ Conda environment accessible"
        
        # Check Python packages
        if python -c "import vllm" 2>/dev/null; then
            log_success "✓ vLLM installed"
        else
            log_error "✗ vLLM not installed"
        fi
        
        if python -c "import kimidev" 2>/dev/null; then
            log_success "✓ Kimi-Dev installed"
        else
            log_warning "⚠ Kimi-Dev not installed (may need manual setup)"
        fi
    else
        log_error "✗ Conda environment not accessible"
    fi
    
    # Check data directory
    if [[ -d "$SWE_DATA_DIR" ]]; then
        local repo_count=$(find "$SWE_DATA_DIR" -maxdepth 2 -type d -name "repos" | wc -l)
        if [[ $repo_count -gt 0 ]]; then
            log_success "✓ SWE-bench data directory exists"
        else
            log_warning "⚠ SWE-bench data may be incomplete"
        fi
    else
        log_error "✗ SWE-bench data directory not found"
    fi
    
    # Check environment variables
    if grep -q "PROJECT_FILE_LOC=" "$PROJECT_ROOT/config/environments/development.env"; then
        log_success "✓ Environment variables configured"
    else
        log_error "✗ Environment variables not configured"
    fi
}

# Main execution
main() {
    log_info "Starting SWE-bench environment setup..."
    
    setup_conda_environment
    clone_kimi_dev
    download_swe_data
    setup_environment_variables
    create_processor_dockerfile
    create_data_manager
    validate_installation
    
    log_success "SWE-bench environment setup completed!"
    echo
    echo -e "${GREEN}Next Steps:${NC}"
    echo "1. Activate the environment: conda activate kimidev"
    echo "2. Deploy the service: ./scripts/deploy_kimi_service.sh"
    echo "3. Or deploy SWE-bench version: docker-compose -f infrastructure/docker/docker-compose.kimi-swe.yml up -d"
    echo "4. Test the installation: python scripts/test_kimi_integration.py"
}

# Handle interruption
trap 'echo -e "\n${YELLOW}Setup interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"
