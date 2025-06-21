# ACGS-1 Development Container

This directory contains the VS Code development container configuration for the ACGS-1 Constitutional Governance System. The dev container provides a consistent, fully-configured development environment that works across different platforms.

## 🚀 Quick Start

### Prerequisites

- [VS Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Getting Started

1. **Open in VS Code**: Open the ACGS repository in VS Code
2. **Reopen in Container**: When prompted, click "Reopen in Container" or use `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"
3. **Wait for Setup**: The container will build and configure automatically (first time takes 5-10 minutes)
4. **Start Coding**: Your development environment is ready!

## 🏗️ What's Included

### Development Tools

- **Python 3.11+** with virtual environment
- **Node.js 18+** with npm
- **Rust** with Cargo and Anchor CLI
- **Solana CLI** for blockchain development
- **UV** for fast Python package management

### VS Code Extensions

- Python development (Black, Flake8, MyPy, isort)
- Rust development (rust-analyzer, LLDB debugger)
- TypeScript/JavaScript development
- Docker and Kubernetes tools
- GitHub Copilot (if available)
- Playwright for testing

### Infrastructure Services

- **PostgreSQL 15** database (localhost:5432)
- **Redis 7** cache (localhost:6379)
- **Docker-in-Docker** for containerized services

### Pre-configured Ports

- `3000`: Frontend applications
- `8000-8012`: Backend services
- `5432`: PostgreSQL database
- `6379`: Redis cache

## 📁 Container Structure

```
.devcontainer/
├── devcontainer.json    # Main configuration
├── docker-compose.yml   # Multi-service setup
├── Dockerfile          # Container image definition
├── setup.sh            # Post-creation setup script
└── README.md           # This file
```

## 🔧 Configuration Details

### Environment Variables

- `PYTHONPATH`: Configured for ACGS service imports
- `NODE_ENV`: Set to development
- `RUST_LOG`: Set to debug level

### Volume Mounts

- Workspace: `../..:/workspace:cached`
- Docker socket: For Docker-in-Docker functionality

### Network

- Custom bridge network `acgs-dev`
- All services can communicate by service name

## 🚀 Development Workflow

### Starting Services

```bash
# Start all development services
./scripts/setup/start_development.sh

# Or start individual services
cd services/core/constitutional-ai
python -m uvicorn app.main:app --reload --port 8001
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/e2e/test_multimodal_vl_integration.py -v

# Run with coverage
pytest tests/ --cov=services --cov-report=html
```

### Database Operations

```bash
# Connect to PostgreSQL
psql -h postgres -U acgs_user -d acgs_db

# Run migrations
python scripts/database/migrate.py

# Check database status
pg_isready -h postgres -p 5432 -U acgs_user
```

### Frontend Development

```bash
# Start governance dashboard
cd applications/governance-dashboard
npm start

# Build for production
npm run build
```

## 🐛 Troubleshooting

### Container Won't Start

1. **Check Docker**: Ensure Docker Desktop is running
2. **Free Space**: Ensure sufficient disk space (>10GB)
3. **Rebuild**: Use "Dev Containers: Rebuild Container"

### Services Not Accessible

1. **Check Ports**: Verify port forwarding in VS Code
2. **Service Status**: Check if services are running with `docker ps`
3. **Logs**: Check service logs in the `logs/` directory

### Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose -f .devcontainer/docker-compose.yml ps postgres

# View PostgreSQL logs
docker-compose -f .devcontainer/docker-compose.yml logs postgres

# Restart database
docker-compose -f .devcontainer/docker-compose.yml restart postgres
```

### Python Import Errors

```bash
# Fix Python imports
python root_scripts/fix_python_imports.py

# Verify PYTHONPATH
echo $PYTHONPATH

# Reinstall dependencies
pip install -r requirements.txt
```

## 🔄 Updating the Container

### Rebuild Container

When you modify the container configuration:

1. `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
2. Or delete the container and reopen

### Update Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node.js packages
npm update

# Update Rust toolchain
rustup update
```

## 🌐 External Access

The dev container forwards ports to your local machine:

- Access services at `http://localhost:<port>`
- Database: `postgresql://acgs_user:acgs_password@localhost:5432/acgs_db`
- Redis: `redis://localhost:6379/0`

## 📚 Additional Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/remote/containers)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [ACGS Development Guide](../docs/development/REORGANIZED_DEVELOPER_GUIDE.md)
- [ACGS API Documentation](../docs/api/README.md)

## 🤝 Contributing

When modifying the dev container:

1. Test changes thoroughly
2. Update this README if needed
3. Consider backward compatibility
4. Document any new requirements

---

**Happy coding in your containerized ACGS development environment! 🏛️✨**
