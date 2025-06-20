# ACGS-1 Rust Setup Guide for Blockchain Development

## 🎯 Quick Start

For experienced developers who want to get started immediately:

```bash
# Install Rust 1.81.0 for Solana compatibility
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustup install 1.81.0 && rustup default 1.81.0
rustup target add wasm32-unknown-unknown bpf-unknown-unknown

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"

# Install Anchor CLI
npm install -g @coral-xyz/anchor-cli@0.29.0

# Verify setup
rustc --version && solana --version && anchor --version
```

## 🔧 Detailed Installation Guide

### Step 1: System Prerequisites

#### Ubuntu/Debian
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl build-essential pkg-config libudev-dev git
```

#### macOS
```bash
# Install Xcode command line tools
xcode-select --install

# Optional: Install via Homebrew
brew install curl git
```

#### Windows
```powershell
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install Git for Windows
# Download from: https://git-scm.com/download/win
```

### Step 2: Install Rust

#### Method 1: rustup (Recommended)
```bash
# Download and install rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow the prompts, choose option 1 (default installation)
# Restart your shell or run:
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

#### Method 2: Package Manager
```bash
# Ubuntu/Debian (not recommended for Solana development)
sudo apt install rustc cargo

# macOS
brew install rust

# Note: Package manager versions may be outdated
# Always verify version compatibility with Solana
```

### Step 3: Configure Rust for Solana

```bash
# Install specific Rust version for Solana compatibility
rustup install 1.81.0
rustup default 1.81.0

# Add required compilation targets
rustup target add wasm32-unknown-unknown
rustup target add bpf-unknown-unknown

# Verify targets are installed
rustup target list --installed
```

### Step 4: Install Solana CLI

```bash
# Install Solana CLI v1.18.22
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Reload shell or source the file
source ~/.bashrc

# Verify installation
solana --version
```

### Step 5: Install Anchor Framework

```bash
# Install Anchor CLI v0.29.0 (requires Node.js)
npm install -g @coral-xyz/anchor-cli@0.29.0

# Verify installation
anchor --version
```

### Step 6: Configure Development Environment

#### Create Cargo Configuration
```bash
# Create cargo config directory
mkdir -p ~/.cargo

# Create config file for optimization
cat > ~/.cargo/config.toml << 'EOF'
[build]
jobs = 4

[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[net]
retry = 10
git-fetch-with-cli = true
EOF
```

#### Set Environment Variables
```bash
# Add to ~/.bashrc or ~/.zshrc
cat >> ~/.bashrc << 'EOF'
# Rust environment
export RUST_LOG=info
export RUST_BACKTRACE=1
export CARGO_INCREMENTAL=1
export CARGO_BUILD_JOBS=4

# Solana environment
export SOLANA_CLI_VERSION=1.18.22
export ANCHOR_CLI_VERSION=0.29.0
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
EOF

# Reload environment
source ~/.bashrc
```

## 🛠️ Development Tools

### Essential Cargo Tools
```bash
# Security and quality tools
cargo install cargo-audit      # Security vulnerability scanning
cargo install cargo-deny       # Dependency policy enforcement
cargo install cargo-outdated   # Check for outdated dependencies

# Development productivity tools
cargo install cargo-watch      # Auto-rebuild on file changes
cargo install cargo-expand     # Macro expansion debugging
cargo install cargo-flamegraph # Performance profiling

# Solana-specific tools
cargo install spl-token-cli     # SPL token management
```

### IDE Setup (VS Code)

#### Install Extensions
```bash
code --install-extension rust-lang.rust-analyzer
code --install-extension vadimcn.vscode-lldb
code --install-extension serayuzgur.crates
code --install-extension tamasfe.even-better-toml
```

#### VS Code Configuration
Create `.vscode/settings.json` in your project:
```json
{
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.checkOnSave.command": "clippy",
    "rust-analyzer.completion.addCallArgumentSnippets": true,
    "rust-analyzer.completion.addCallParenthesis": true,
    "rust-analyzer.inlayHints.enable": true,
    "rust-analyzer.inlayHints.chainingHints": true,
    "rust-analyzer.inlayHints.parameterHints": true
}
```

## ✅ Verification

### Automated Verification Script
```bash
#!/bin/bash
# Save as verify_setup.sh and run: chmod +x verify_setup.sh && ./verify_setup.sh

echo "🦀 Verifying ACGS-1 Rust blockchain development setup..."

# Check Rust version
if rustc --version | grep -q "1.81.0"; then
    echo "✅ Rust 1.81.0 installed"
else
    echo "❌ Rust 1.81.0 not found. Current version: $(rustc --version)"
    exit 1
fi

# Check Cargo
if cargo --version > /dev/null 2>&1; then
    echo "✅ Cargo available: $(cargo --version)"
else
    echo "❌ Cargo not found"
    exit 1
fi

# Check Solana targets
if rustup target list --installed | grep -q "wasm32-unknown-unknown"; then
    echo "✅ wasm32-unknown-unknown target installed"
else
    echo "❌ wasm32-unknown-unknown target missing"
    exit 1
fi

if rustup target list --installed | grep -q "bpf-unknown-unknown"; then
    echo "✅ bpf-unknown-unknown target installed"
else
    echo "❌ bpf-unknown-unknown target missing"
    exit 1
fi

# Check Solana CLI
if solana --version > /dev/null 2>&1; then
    echo "✅ Solana CLI available: $(solana --version)"
else
    echo "❌ Solana CLI not found"
    exit 1
fi

# Check Anchor CLI
if anchor --version > /dev/null 2>&1; then
    echo "✅ Anchor CLI available: $(anchor --version)"
else
    echo "❌ Anchor CLI not found"
    exit 1
fi

# Test compilation
echo "Testing Rust compilation..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
cargo new test_project --bin > /dev/null 2>&1
cd test_project
if cargo build > /dev/null 2>&1; then
    echo "✅ Rust compilation test passed"
else
    echo "❌ Rust compilation test failed"
    exit 1
fi
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo "🎉 All checks passed! Your Rust blockchain development environment is ready."
```

### Manual Verification
```bash
# Check versions
rustc --version    # Should show 1.81.0
cargo --version    # Should show 1.81.0
solana --version   # Should show 1.18.22
anchor --version   # Should show 0.29.0

# Check targets
rustup target list --installed | grep -E "(wasm32|bpf)"

# Test ACGS-1 blockchain tools
cd blockchain/scripts
cargo build --release
cargo run --bin deploy_quantumagi -- --help
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "rustc: command not found"
```bash
# Solution: Source the cargo environment
source ~/.cargo/env

# Or add to shell profile permanently
echo 'source ~/.cargo/env' >> ~/.bashrc
```

#### Issue: Linker errors on Linux
```bash
# Solution: Install build essentials and linker
sudo apt install build-essential pkg-config libudev-dev lld
```

#### Issue: Permission denied errors
```bash
# Solution: Fix cargo directory permissions
sudo chown -R $USER:$USER ~/.cargo
```

#### Issue: Slow compilation
```bash
# Solution: Enable parallel compilation and faster linker
export CARGO_BUILD_JOBS=$(nproc)
sudo apt install lld  # Linux
```

#### Issue: "target not found" errors
```bash
# Solution: Add missing targets
rustup target add wasm32-unknown-unknown
rustup target add bpf-unknown-unknown
```

#### Issue: Anchor CLI installation fails
```bash
# Solution: Ensure Node.js is installed
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g @coral-xyz/anchor-cli@0.29.0
```

## 🚀 Next Steps

After completing the setup:

1. **Clone ACGS-1 Repository**
   ```bash
   git clone https://github.com/CA-git-com-co/ACGS.git
   cd ACGS/blockchain
   ```

2. **Build Rust Tools**
   ```bash
   cd scripts
   cargo build --release
   ```

3. **Test Blockchain Programs**
   ```bash
   anchor build
   anchor test
   ```

4. **Deploy to Devnet**
   ```bash
   cargo run --bin deploy_quantumagi -- deploy --cluster devnet
   ```

## 📚 Additional Resources

- [Rust Programming Language](https://www.rust-lang.org/)
- [Solana Documentation](https://docs.solana.com/)
- [Anchor Framework](https://www.anchor-lang.com/)
- [ACGS-1 Rust-First Workflow](./RUST_FIRST_BLOCKCHAIN_WORKFLOW.md)
- [Three-Tier Dependency Strategy](./THREE_TIER_DEPENDENCY_STRATEGY.md)
