# ACGS Blockchain Service Makefile
# Constitutional Hash: cdd01ef066bc6cf2

.PHONY: help clean build test deploy dev ci lint format

# Default target
help:
	@echo "ACGS Blockchain Service Build Commands"
	@echo "====================================="
	@echo "clean        - Clean all build artifacts"
	@echo "build        - Build all components"
	@echo "build-fast   - Fast development build"
	@echo "test         - Run all tests"
	@echo "test-rust    - Run only Rust tests"
	@echo "test-anchor  - Run only Anchor tests"
	@echo "deploy       - Deploy to devnet"
	@echo "deploy-main  - Deploy to mainnet"
	@echo "dev          - Development workflow (build + test)"
	@echo "ci           - CI/CD pipeline"
	@echo "lint         - Run linting"
	@echo "format       - Format code"
	@echo "validate     - Validate deployment"
	@echo "init         - Initialize constitution"

# Clean targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	@./build.sh clean

# Build targets
build:
	@echo "🔨 Building all components..."
	@./build.sh all

build-fast:
	@echo "⚡ Fast development build..."
	@./build.sh dev devnet true

build-rust:
	@echo "🦀 Building Rust tools..."
	@./build.sh rust-tools

build-programs:
	@echo "⚓ Building Anchor programs..."
	@./build.sh programs

# Test targets
test:
	@echo "🧪 Running all tests..."
	@./build.sh test

test-rust:
	@echo "🦀 Running Rust tests..."
	@npm run test:rust

test-anchor:
	@echo "⚓ Running Anchor tests..."
	@npm run test

# Deploy targets
deploy:
	@echo "🚀 Deploying to devnet..."
	@./build.sh deploy devnet

deploy-main:
	@echo "🌟 Deploying to mainnet..."
	@./build.sh deploy mainnet

# Development workflow
dev:
	@echo "🛠️  Development workflow..."
	@./build.sh dev

# CI/CD pipeline
ci:
	@echo "🔄 Running CI/CD pipeline..."
	@./build.sh ci

# Code quality
lint:
	@echo "🔍 Running linter..."
	@npm run lint

format:
	@echo "💅 Formatting code..."
	@npm run lint:fix
	@cd scripts && cargo fmt

# Deployment helpers
validate:
	@echo "✅ Validating deployment..."
	@./build.sh validate

init:
	@echo "📜 Initializing constitution..."
	@./build.sh init

# Quick shortcuts
quick: build-fast test-rust
	@echo "⚡ Quick development cycle completed"

full: clean build test validate
	@echo "🎯 Full build and validation completed"

# Watch mode for development (requires entr)
watch:
	@echo "👀 Watching for changes..."
	@find . -name "*.rs" -o -name "*.ts" -o -name "*.js" | entr -r make quick