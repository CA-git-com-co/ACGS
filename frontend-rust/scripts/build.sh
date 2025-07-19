#!/bin/bash
# ACGS-2 Rust Frontend Build Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constitutional compliance
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

echo -e "${BLUE}🏛️  ACGS-2 Rust Frontend Build${NC}"
echo -e "${BLUE}Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Rust
if ! command -v rustc &> /dev/null; then
    echo -e "${RED}❌ Rust is not installed. Please install Rust from https://rustup.rs/${NC}"
    exit 1
fi

# Check wasm-pack
if ! command -v wasm-pack &> /dev/null; then
    echo -e "${YELLOW}⚠️  wasm-pack not found. Installing...${NC}"
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Check trunk
if ! command -v trunk &> /dev/null; then
    echo -e "${YELLOW}⚠️  trunk not found. Installing...${NC}"
    cargo install trunk
fi

# Add wasm target if not present
if ! rustup target list --installed | grep -q "wasm32-unknown-unknown"; then
    echo -e "${YELLOW}⚠️  Adding wasm32-unknown-unknown target...${NC}"
    rustup target add wasm32-unknown-unknown
fi

echo -e "${GREEN}✅ Prerequisites check complete${NC}"
echo ""

# Parse command line arguments
BUILD_MODE="release"
SERVE_MODE=false
WATCH_MODE=false
CLEAN_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            BUILD_MODE="dev"
            shift
            ;;
        --serve)
            SERVE_MODE=true
            shift
            ;;
        --watch)
            WATCH_MODE=true
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        --help|-h)
            echo "ACGS-2 Rust Frontend Build Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev, --development    Build in development mode"
            echo "  --serve                 Start development server after build"
            echo "  --watch                 Watch for changes and rebuild"
            echo "  --clean                 Clean build artifacts before building"
            echo "  --help, -h              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                      # Production build"
            echo "  $0 --dev --serve        # Development build with server"
            echo "  $0 --watch              # Watch mode for development"
            echo "  $0 --clean              # Clean and rebuild"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Clean if requested
if [ "$CLEAN_MODE" = true ]; then
    echo -e "${YELLOW}🧹 Cleaning build artifacts...${NC}"
    cargo clean
    rm -rf dist/
    rm -rf pkg/
    echo -e "${GREEN}✅ Clean complete${NC}"
    echo ""
fi

# Validate constitutional compliance
echo -e "${YELLOW}🏛️  Validating constitutional compliance...${NC}"

# Check that constitutional hash is present in source files
if ! grep -r "$CONSTITUTIONAL_HASH" src/ > /dev/null; then
    echo -e "${RED}❌ Constitutional hash not found in source files${NC}"
    exit 1
fi

# Check Cargo.toml metadata
if ! grep -q "constitutional_hash.*$CONSTITUTIONAL_HASH" Cargo.toml; then
    echo -e "${RED}❌ Constitutional hash not found in Cargo.toml metadata${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Constitutional compliance validated${NC}"
echo ""

# Performance targets
echo -e "${YELLOW}🎯 Performance Targets:${NC}"
echo -e "  • P99 Latency: <5ms"
echo -e "  • Throughput: >100 RPS"
echo -e "  • Cache Hit Rate: >85%"
echo ""

# Build configuration
if [ "$BUILD_MODE" = "dev" ]; then
    echo -e "${YELLOW}🔨 Building in development mode...${NC}"
    RUST_LOG=info
    TRUNK_BUILD_MODE="--dev"
else
    echo -e "${YELLOW}🔨 Building in production mode...${NC}"
    RUST_LOG=warn
    TRUNK_BUILD_MODE="--release"
fi

# Set environment variables
export RUST_LOG
export CONSTITUTIONAL_HASH

# Start build
echo -e "${BLUE}🚀 Starting build process...${NC}"
start_time=$(date +%s)

if [ "$WATCH_MODE" = true ]; then
    echo -e "${YELLOW}👀 Starting watch mode...${NC}"
    trunk watch $TRUNK_BUILD_MODE
elif [ "$SERVE_MODE" = true ]; then
    echo -e "${YELLOW}🌐 Starting development server...${NC}"
    trunk serve $TRUNK_BUILD_MODE --open
else
    # Regular build
    if trunk build $TRUNK_BUILD_MODE; then
        end_time=$(date +%s)
        build_time=$((end_time - start_time))
        
        echo ""
        echo -e "${GREEN}✅ Build completed successfully!${NC}"
        echo -e "${GREEN}⏱️  Build time: ${build_time}s${NC}"
        echo ""
        
        # Check build artifacts
        if [ -d "dist" ]; then
            echo -e "${BLUE}📦 Build artifacts:${NC}"
            ls -la dist/
            echo ""
            
            # Calculate bundle size
            if [ -f "dist/acgs_frontend_bg.wasm" ]; then
                wasm_size=$(stat -f%z "dist/acgs_frontend_bg.wasm" 2>/dev/null || stat -c%s "dist/acgs_frontend_bg.wasm" 2>/dev/null || echo "unknown")
                echo -e "${BLUE}📊 WASM bundle size: ${wasm_size} bytes${NC}"
                
                # Check if size is reasonable (< 2MB for initial load)
                if [ "$wasm_size" != "unknown" ] && [ "$wasm_size" -gt 2097152 ]; then
                    echo -e "${YELLOW}⚠️  WASM bundle size is large (>2MB). Consider optimization.${NC}"
                fi
            fi
            
            # Validate constitutional hash in built files
            if grep -r "$CONSTITUTIONAL_HASH" dist/ > /dev/null; then
                echo -e "${GREEN}✅ Constitutional hash validated in build artifacts${NC}"
            else
                echo -e "${RED}❌ Constitutional hash not found in build artifacts${NC}"
                exit 1
            fi
        fi
        
        echo ""
        echo -e "${GREEN}🎉 ACGS-2 Rust Frontend build complete!${NC}"
        echo -e "${BLUE}Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo -e "  • Test the application: trunk serve --open"
        echo -e "  • Deploy to production: copy dist/ to your web server"
        echo -e "  • Monitor performance: ensure P99 latency <5ms"
        echo ""
        
    else
        echo -e "${RED}❌ Build failed!${NC}"
        exit 1
    fi
fi
