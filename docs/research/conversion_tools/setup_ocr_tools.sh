#!/bin/bash
# ACGS OCR Tools Setup Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "=========================================="
echo "ACGS Research Paper OCR Tools Setup"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in virtual environment
check_virtual_env() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Not running in a virtual environment"
        print_status "Creating virtual environment for OCR tools..."
        python3 -m venv ocr_env
        source ocr_env/bin/activate
        print_success "Virtual environment created and activated"
    else
        print_success "Running in virtual environment: $VIRTUAL_ENV"
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            tesseract-ocr \
            tesseract-ocr-eng \
            libtesseract-dev \
            poppler-utils \
            python3-dev \
            python3-pip \
            build-essential \
            libffi-dev \
            libssl-dev
        print_success "System dependencies installed (Ubuntu/Debian)"
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y \
            tesseract \
            tesseract-langpack-eng \
            tesseract-devel \
            poppler-utils \
            python3-devel \
            python3-pip \
            gcc \
            gcc-c++ \
            make \
            libffi-devel \
            openssl-devel
        print_success "System dependencies installed (CentOS/RHEL)"
        
    elif command -v brew &> /dev/null; then
        # macOS
        brew install tesseract poppler python3
        print_success "System dependencies installed (macOS)"
        
    else
        print_warning "Could not detect package manager. Please install manually:"
        echo "  - tesseract-ocr"
        echo "  - poppler-utils"
        echo "  - python3-dev"
        echo "  - build-essential"
    fi
}

# Install Python packages
install_python_packages() {
    print_status "Installing Python packages..."

    # Upgrade pip first
    pip install --upgrade pip setuptools wheel

    # Install basic requirements (excluding OCRFlux)
    pip install -r requirements.txt

    print_success "Basic Python packages installed"

    # Try to install OCRFlux (state-of-the-art)
    print_status "Installing OCRFlux (state-of-the-art academic PDF converter)..."
    if install_ocrflux; then
        print_success "OCRFlux installed successfully"
    else
        print_warning "OCRFlux installation failed, will use fallback methods"
    fi

    # Try to install Marker (fallback advanced OCR tool)
    print_status "Installing Marker (fallback academic PDF converter)..."
    if pip install marker-pdf; then
        print_success "Marker installed successfully"
    else
        print_warning "Marker installation failed, will use basic fallback methods"
    fi

    # Install additional OCR models
    print_status "Installing additional language models..."
    python -c "
import nltk
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    print('NLTK models downloaded')
except:
    print('NLTK download failed')
"
}

# Install OCRFlux (GPU-based state-of-the-art)
install_ocrflux() {
    print_status "Setting up OCRFlux..."

    # Check GPU availability
    if ! command -v nvidia-smi &> /dev/null; then
        print_warning "NVIDIA GPU not detected. OCRFlux requires GPU for optimal performance."
        return 1
    fi

    # Check GPU memory
    gpu_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    if [ "$gpu_memory" -lt 12000 ]; then
        print_warning "GPU has less than 12GB memory. OCRFlux may not work optimally."
    fi

    # Clone OCRFlux repository
    if [ ! -d "OCRFlux" ]; then
        print_status "Cloning OCRFlux repository..."
        git clone https://github.com/chatdoc-com/OCRFlux.git
    fi

    # Install OCRFlux
    cd OCRFlux
    pip install -e . --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer/
    cd ..

    # Test OCRFlux installation
    python -c "
try:
    import ocrflux
    from vllm import LLM
    print('OCRFlux installation successful')
except ImportError as e:
    print(f'OCRFlux installation failed: {e}')
    exit(1)
"

    return $?
}

# Test OCR installation
test_installation() {
    print_status "Testing OCR installation..."
    
    python3 -c "
import sys
import importlib

# Test required packages
packages = [
    'fitz',  # PyMuPDF
    'pdfplumber',
    'PIL',  # Pillow
    'pytesseract',
    'tqdm',
    'click',
    'pandas',
    'numpy'
]

failed = []
for package in packages:
    try:
        importlib.import_module(package)
        print(f'✓ {package}')
    except ImportError:
        print(f'✗ {package}')
        failed.append(package)

# Test OCRFlux (state-of-the-art)
try:
    import ocrflux
    from vllm import LLM
    print('✓ OCRFlux (state-of-the-art)')
except ImportError:
    print('✗ OCRFlux (will use fallback methods)')

# Test Marker (fallback)
try:
    import marker
    print('✓ marker (fallback advanced)')
except ImportError:
    print('✗ marker (will use basic fallback methods)')

if failed:
    print(f'\\nFailed to import: {failed}')
    sys.exit(1)
else:
    print('\\nAll core packages imported successfully!')
"
    
    if [ $? -eq 0 ]; then
        print_success "OCR tools installation test passed"
    else
        print_error "OCR tools installation test failed"
        exit 1
    fi
}

# Create directory structure
setup_directories() {
    print_status "Setting up directory structure..."
    
    mkdir -p ../papers_markdown
    mkdir -p ../papers_metadata
    mkdir -p ../papers_archive
    
    print_success "Directory structure created"
}

# Create configuration file
create_config() {
    print_status "Creating configuration file..."
    
    cat > config.json << EOF
{
    "constitutional_hash": "cdd01ef066bc6cf2",
    "conversion_settings": {
        "max_workers": 4,
        "preferred_method": "marker",
        "fallback_methods": ["pymupdf"],
        "quality_threshold": 0.5,
        "max_pages_per_pdf": null,
        "languages": ["English"]
    },
    "output_settings": {
        "markdown_dir": "../papers_markdown",
        "metadata_dir": "../papers_metadata",
        "archive_dir": "../papers_archive"
    },
    "logging": {
        "level": "INFO",
        "file": "conversion.log"
    }
}
EOF
    
    print_success "Configuration file created"
}

# Main installation process
main() {
    print_status "Starting OCR tools setup..."
    
    # Check virtual environment
    check_virtual_env
    
    # Install system dependencies
    install_system_deps
    
    # Install Python packages
    install_python_packages
    
    # Test installation
    test_installation
    
    # Setup directories
    setup_directories
    
    # Create configuration
    create_config
    
    print_success "OCR tools setup completed successfully!"
    echo ""
    echo "=========================================="
    echo "NEXT STEPS:"
    echo "=========================================="
    echo "1. Run the conversion script:"
    echo "   python pdf_to_markdown_converter.py"
    echo ""
    echo "2. Or use with custom options:"
    echo "   python pdf_to_markdown_converter.py -i ../papers -o ../papers_markdown -w 4"
    echo ""
    echo "3. Check conversion results in:"
    echo "   - Markdown files: ../papers_markdown/"
    echo "   - Metadata: ../papers_metadata/"
    echo "   - Conversion report: ../papers_metadata/conversion_report.json"
    echo "=========================================="
}

# Run main function
main
