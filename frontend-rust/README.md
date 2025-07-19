# ACGS-2 Rust Frontend

A high-performance, memory-safe frontend for the ACGS-2 Constitutional AI Governance System built with Rust and WebAssembly.

## Constitutional Hash: `cdd01ef066bc6cf2`

## Features

- **🏛️ Constitutional Compliance**: Built-in constitutional AI governance validation
- **⚡ High Performance**: WebAssembly-powered with P99 <5ms latency targets
- **🔒 Memory Safety**: Rust's memory safety guarantees prevent common web vulnerabilities
- **🔄 Real-time Updates**: WebSocket integration with ACGS-2 backend services
- **📊 Performance Monitoring**: Built-in performance metrics and monitoring
- **🎨 Modern UI**: Clean, accessible design system inspired by modern web standards
- **🌐 Service Integration**: Seamless integration with all ACGS-2 backend services

## Architecture

### Technology Stack

- **Framework**: Yew (Rust web framework)
- **Build Tool**: Trunk (Rust WASM application bundler)
- **State Management**: Yewdux (Redux-like state management)
- **Routing**: Yew Router
- **Styling**: CSS with custom properties and modern design system
- **HTTP Client**: reqwasm
- **WebSocket**: Native WebSocket API with Rust wrappers

### Service Integration

The frontend integrates with the following ACGS-2 services:

- **Constitutional AI Service** (Port 8001): Constitutional compliance validation
- **Integrity Service** (Port 8002): Data integrity and validation
- **Formal Verification Service** (Port 8003): Formal verification of policies
- **Governance Synthesis Service** (Port 8004): AI-powered governance synthesis
- **Policy Governance Service** (Port 8005): Policy evaluation and compliance
- **Evolutionary Computation Service** (Port 8006): Evolutionary optimization
- **Auth Service** (Port 8016): Authentication and authorization

## Prerequisites

- **Rust** (latest stable): Install from [rustup.rs](https://rustup.rs/)
- **wasm-pack**: WebAssembly build tool
- **trunk**: Rust WASM application bundler

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install wasm-pack
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Install trunk
cargo install trunk

# Add WebAssembly target
rustup target add wasm32-unknown-unknown
```

## Quick Start

### Development

```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS/frontend-rust

# Start development server
./scripts/build.sh --dev --serve

# Or use trunk directly
trunk serve --dev --open
```

### Production Build

```bash
# Build for production
./scripts/build.sh

# Or use trunk directly
trunk build --release
```

### Watch Mode

```bash
# Watch for changes and rebuild
./scripts/build.sh --watch
```

## Project Structure

```
frontend-rust/
├── src/
│   ├── app.rs              # Main application component
│   ├── lib.rs              # Library entry point and WASM bindings
│   ├── router.rs           # Application routing
│   ├── types.rs            # Type definitions
│   ├── utils.rs            # Utility functions
│   ├── hooks.rs            # Custom Yew hooks
│   ├── components/         # UI components
│   │   ├── mod.rs
│   │   ├── layout.rs       # Layout components
│   │   ├── navigation.rs   # Navigation components
│   │   ├── dashboard.rs    # Dashboard components
│   │   ├── constitutional.rs # Constitutional compliance components
│   │   ├── error_boundary.rs # Error handling components
│   │   └── ui.rs           # Common UI components
│   ├── services/           # Service integration
│   │   ├── mod.rs
│   │   ├── api_client.rs   # HTTP API client
│   │   ├── websocket.rs    # WebSocket client
│   │   ├── constitutional_ai.rs # Constitutional AI service
│   │   ├── governance_synthesis.rs # Governance synthesis service
│   │   ├── policy_governance.rs # Policy governance service
│   │   └── auth.rs         # Authentication service
│   └── store/              # State management
│       ├── mod.rs
│       └── ...
├── styles/
│   └── main.css            # Application styles
├── scripts/
│   └── build.sh            # Build script
├── assets/                 # Static assets
├── Cargo.toml              # Rust dependencies
├── Trunk.toml              # Trunk configuration
├── index.html              # HTML template
└── README.md               # This file
```

## Configuration

### Environment Variables

- `CONSTITUTIONAL_HASH`: Constitutional compliance hash (default: `cdd01ef066bc6cf2`)
- `RUST_LOG`: Logging level (default: `info`)

### Performance Targets

- **P99 Latency**: <5ms
- **Throughput**: >100 RPS
- **Cache Hit Rate**: >85%

## Development

### Adding New Components

1. Create component file in `src/components/`
2. Add module declaration to `src/components/mod.rs`
3. Export component if needed
4. Add routing if it's a page component

### Adding New Services

1. Create service file in `src/services/`
2. Add module declaration to `src/services/mod.rs`
3. Implement service client with constitutional compliance validation
4. Add WebSocket support if needed

### State Management

The application uses Yewdux for state management with the following stores:

- `AppStore`: Global application state
- `ConstitutionalStore`: Constitutional compliance state
- `DashboardStore`: Dashboard-specific state
- `NotificationStore`: Notification management

## Testing

```bash
# Run tests
cargo test

# Run tests with WASM target
wasm-pack test --headless --firefox
```

## Performance Monitoring

The application includes built-in performance monitoring:

- Render time tracking
- API response time monitoring
- Constitutional compliance validation timing
- Memory usage tracking (in development)

## Constitutional Compliance

All components and services must maintain constitutional compliance:

- Include constitutional hash in all API requests
- Validate constitutional hash in all responses
- Log constitutional compliance events
- Monitor compliance scores

## Deployment

### Static Hosting

The built application can be deployed to any static hosting service:

```bash
# Build for production
trunk build --release

# Deploy dist/ directory to your hosting service
```

### Docker

```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Contributing

1. Follow Rust coding standards
2. Ensure constitutional compliance in all code
3. Add tests for new functionality
4. Update documentation
5. Verify performance targets are met

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:

- Check the documentation in `docs/`
- Review the ACGS-2 service documentation
- Contact the development team

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Performance Targets**: P99 <5ms, >100 RPS, >85% cache hit rate  
**Implementation Status**: 🔄 IN PROGRESS
