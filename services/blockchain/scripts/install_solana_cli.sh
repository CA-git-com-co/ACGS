# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Quantumagi Solana CLI Installation Script
# Multiple fallback methods for Solana CLI installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Quantumagi Solana CLI Installation${NC}"
echo "======================================"

# Function to check if Solana CLI is working
check_solana_cli() {
    if command -v solana &> /dev/null; then
        echo -e "${GREEN}✅ Solana CLI found: $(solana --version)${NC}"
        return 0
    else
        echo -e "${RED}❌ Solana CLI not found${NC}"
        return 1
    fi
}

# Method 1: Standard installation
install_method_1() {
    echo -e "${BLUE}Method 1: Standard Solana installation${NC}"
    sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)" || return 1
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> ~/.bashrc
}

# Method 2: Package manager installation
install_method_2() {
    echo -e "${BLUE}Method 2: Package manager installation${NC}"
    
    # Try different package managers
    if command -v apt &> /dev/null; then
        echo "Using apt package manager..."
        sudo apt update
        sudo apt install -y curl
        curl -sSfL https://release.solana.com/v1.18.22/install | sh
    elif command -v yum &> /dev/null; then
        echo "Using yum package manager..."
        sudo yum install -y curl
        curl -sSfL https://release.solana.com/v1.18.22/install | sh
    elif command -v brew &> /dev/null; then
        echo "Using Homebrew..."
        brew install solana
    else
        echo "No supported package manager found"
        return 1
    fi
}

# Method 3: Manual binary download
install_method_3() {
    echo -e "${BLUE}Method 3: Manual binary download${NC}"
    
    SOLANA_VERSION="v1.18.22"
    ARCH=$(uname -m)
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    
    # Determine the correct binary
    if [[ "$OS" == "linux" ]]; then
        if [[ "$ARCH" == "x86_64" ]]; then
            BINARY_URL="https://github.com/solana-labs/solana/releases/download/${SOLANA_VERSION}/solana-release-x86_64-unknown-linux-gnu.tar.bz2"
        else
            echo "Unsupported architecture: $ARCH"
            return 1
        fi
    elif [[ "$OS" == "darwin" ]]; then
        BINARY_URL="https://github.com/solana-labs/solana/releases/download/${SOLANA_VERSION}/solana-release-x86_64-apple-darwin.tar.bz2"
    else
        echo "Unsupported OS: $OS"
        return 1
    fi
    
    # Download and install
    mkdir -p ~/.local/share/solana
    cd ~/.local/share/solana
    curl -L "$BINARY_URL" | tar -xj
    
    # Create symlinks
    mkdir -p ~/.local/bin
    ln -sf ~/.local/share/solana/solana-release/bin/* ~/.local/bin/
    
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
}

# Method 4: Use Anchor's embedded Solana
install_method_4() {
    echo -e "${BLUE}Method 4: Using Anchor's embedded Solana${NC}"
    
    # Check if Anchor has Solana embedded
    if command -v anchor &> /dev/null; then
        echo "Anchor CLI found, checking for embedded Solana..."
        
        # Try to use Anchor's Solana
        ANCHOR_PATH=$(which anchor)
        ANCHOR_DIR=$(dirname "$ANCHOR_PATH")
        
        if [ -f "$ANCHOR_DIR/solana" ]; then
            echo "Found Anchor's Solana binary"
            ln -sf "$ANCHOR_DIR/solana" ~/.local/bin/solana
            export PATH="$HOME/.local/bin:$PATH"
            return 0
        fi
    fi
    
    return 1
}

# Method 5: Docker-based Solana CLI
install_method_5() {
    echo -e "${BLUE}Method 5: Docker-based Solana CLI${NC}"
    
    if command -v docker &> /dev/null; then
        echo "Creating Docker-based Solana CLI wrapper..."
        
        mkdir -p ~/.local/bin
        cat > ~/.local/bin/solana << 'EOF'
#!/bin/bash
docker run --rm -v "$HOME/.config/solana:/root/.config/solana" \
    -v "$(pwd):/workspace" -w /workspace \
    solanalabs/solana:v1.18.22 solana "$@"
EOF
        chmod +x ~/.local/bin/solana
        
        export PATH="$HOME/.local/bin:$PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        
        # Pull the Docker image
        docker pull solanalabs/solana:v1.18.22
        return 0
    fi
    
    return 1
}

# Main installation logic
main() {
    echo "Checking current Solana CLI status..."
    if check_solana_cli; then
        echo -e "${GREEN}Solana CLI already installed and working!${NC}"
        exit 0
    fi
    
    echo "Solana CLI not found. Trying installation methods..."
    
    # Try each method in order
    methods=(
        "install_method_1"
        "install_method_2" 
        "install_method_3"
        "install_method_4"
        "install_method_5"
    )
    
    for method in "${methods[@]}"; do
        echo -e "\n${YELLOW}Trying $method...${NC}"
        if $method; then
            # Reload PATH
            source ~/.bashrc 2>/dev/null || true
            export PATH="$HOME/.local/share/solana/install/active_release/bin:$HOME/.local/bin:$PATH"
            
            if check_solana_cli; then
                echo -e "${GREEN}✅ Successfully installed Solana CLI using $method${NC}"
                
                # Setup Solana configuration
                echo "Setting up Solana configuration..."
                solana config set --url https://api.devnet.solana.com
                
                # Generate keypair if it doesn't exist
                if [ ! -f ~/.config/solana/id.json ]; then
                    echo "Generating new keypair..."
                    solana-keygen new --outfile ~/.config/solana/id.json --no-bip39-passphrase
                fi
                
                echo -e "${GREEN}🎉 Solana CLI setup complete!${NC}"
                echo "Wallet address: $(solana address)"
                echo "Current cluster: $(solana config get | grep 'RPC URL')"
                exit 0
            fi
        fi
        echo -e "${RED}$method failed, trying next method...${NC}"
    done
    
    echo -e "${RED}❌ All installation methods failed${NC}"
    echo "Please install Solana CLI manually or contact support"
    exit 1
}

main "$@"
