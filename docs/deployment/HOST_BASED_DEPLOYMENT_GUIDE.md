# ACGS-1 Host-Based Deployment Guide

This guide covers deploying ACGS-1 constitutional AI governance system using host-based architecture (non-Docker deployment).

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **RAM**: 16GB minimum, 32GB recommended
- **CPU**: 8 cores minimum, 16 cores recommended
- **Storage**: 100GB SSD minimum
- **Network**: Stable internet connection for Solana devnet

### Software Dependencies

- **Python**: 3.9+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **Solana CLI**: 1.18.22+
- **Anchor Framework**: 0.29.0+

## Installation Steps

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y build-essential curl git postgresql postgresql-contrib redis-server

# Install Python 3.9+
sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE acgs_db;
CREATE USER acgs_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE acgs_db TO acgs_user;
\q
EOF

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 3. Solana & Anchor Setup

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install Anchor
npm install -g @coral-xyz/anchor-cli@0.29.0

# Configure Solana for devnet
solana config set --url devnet
solana-keygen new --outfile ~/.config/solana/id.json
```

### 4. ACGS-1 Application Setup

```bash
# Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-1

# Create Python virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Build Rust blockchain tools
cd blockchain/scripts
cargo build --release
cd ../..
```

### 5. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Configure the following variables in `.env`:

```bash
# Database Configuration
DATABASE_URL=postgresql://acgs_user:secure_password@localhost:5432/acgs_db
REDIS_URL=redis://localhost:6379

# API Keys (obtain from respective providers)
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Service Configuration
AUTH_SERVICE_PORT=8000
AC_SERVICE_PORT=8001
INTEGRITY_SERVICE_PORT=8002
FV_SERVICE_PORT=8003
GS_SERVICE_PORT=8004
PGC_SERVICE_PORT=8005
EC_SERVICE_PORT=8006

# Solana Configuration
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
```

## Service Deployment

### 1. Build Blockchain Programs

```bash
cd blockchain
anchor build
anchor test
anchor deploy --provider.cluster devnet
cd ..
```

### 2. Initialize Database

```bash
# Run database migrations
python scripts/database/init_database.py

# Initialize constitutional principles
python scripts/initialize_constitution.py
```

### 3. Start Services

Create systemd service files for each service:

#### Authentication Service (Port 8000)

```bash
sudo tee /etc/systemd/system/acgs-auth.service > /dev/null << EOF
[Unit]
Description=ACGS Authentication Service
After=network.target postgresql.service

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/platform/authentication/auth_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Constitutional AI Service (Port 8001)

```bash
sudo tee /etc/systemd/system/acgs-constitutional-ai.service > /dev/null << EOF
[Unit]
Description=ACGS Constitutional AI Service
After=network.target postgresql.service

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/core/constitutional-ai/ac_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Integrity Service (Port 8002)

```bash
sudo tee /etc/systemd/system/acgs-integrity.service > /dev/null << EOF
[Unit]
Description=ACGS Integrity Service
After=network.target postgresql.service

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/platform/integrity/integrity_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Formal Verification Service (Port 8003)

```bash
sudo tee /etc/systemd/system/acgs-formal-verification.service > /dev/null << EOF
[Unit]
Description=ACGS Formal Verification Service
After=network.target

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/core/formal-verification/fv_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8003
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Governance Synthesis Service (Port 8004)

```bash
sudo tee /etc/systemd/system/acgs-governance-synthesis.service > /dev/null << EOF
[Unit]
Description=ACGS Governance Synthesis Service
After=network.target postgresql.service

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/core/governance-synthesis/gs_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8004
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Policy Governance Service (Port 8005)

```bash
sudo tee /etc/systemd/system/acgs-policy-governance.service > /dev/null << EOF
[Unit]
Description=ACGS Policy Governance Service
After=network.target postgresql.service

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/core/policy-governance/pgc_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

#### Evolutionary Computation Service (Port 8006)

```bash
sudo tee /etc/systemd/system/acgs-evolutionary-computation.service > /dev/null << EOF
[Unit]
Description=ACGS Evolutionary Computation Service
After=network.target

[Service]
Type=simple
User=acgs
WorkingDirectory=/path/to/ACGS-1/services/core/evolutionary-computation/ec_service
Environment=PATH=/path/to/ACGS-1/venv/bin
ExecStart=/path/to/ACGS-1/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8006
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### 4. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable acgs-auth acgs-constitutional-ai acgs-integrity acgs-formal-verification acgs-governance-synthesis acgs-policy-governance acgs-evolutionary-computation

# Start services
sudo systemctl start acgs-auth acgs-constitutional-ai acgs-integrity acgs-formal-verification acgs-governance-synthesis acgs-policy-governance acgs-evolutionary-computation
```

## Validation & Testing

### 1. Service Health Checks

```bash
# Check all services are running
python scripts/comprehensive_health_check.py

# Validate service stack
./scripts/validate_service_stack.py

# Test individual services
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
```

### 2. Integration Testing

```bash
# Run comprehensive integration tests
python scripts/comprehensive_integration_test_runner.py

# Validate Solana devnet deployment
python scripts/validate_devnet_deployment.py

# Performance validation
python scripts/phase2_performance_validation.py
```

## Monitoring & Maintenance

### 1. Log Management

```bash
# View service logs
sudo journalctl -u acgs-auth -f
sudo journalctl -u acgs-constitutional-ai -f

# Centralized logging
tail -f /var/log/acgs/*.log
```

### 2. Performance Monitoring

```bash
# Monitor system resources
htop
iostat -x 1

# Monitor service performance
python scripts/priority3_monitoring_infrastructure.py
```

### 3. Backup & Recovery

```bash
# Database backup
pg_dump acgs_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz .env blockchain/target/deploy/
```

## Troubleshooting

### Common Issues

1. **Service won't start**: Check logs with `journalctl -u service-name`
2. **Database connection errors**: Verify PostgreSQL is running and credentials are correct
3. **Solana deployment fails**: Check network connectivity and wallet balance
4. **API key errors**: Verify environment variables are set correctly

### Performance Optimization

1. **Database tuning**: Optimize PostgreSQL configuration for workload
2. **Redis caching**: Configure Redis for session and data caching
3. **Load balancing**: Use nginx for load balancing multiple instances
4. **Resource monitoring**: Set up monitoring for CPU, memory, and disk usage

## Security Considerations

1. **Firewall configuration**: Only expose necessary ports (8000-8006)
2. **SSL/TLS**: Configure HTTPS for production deployments
3. **API key rotation**: Regularly rotate API keys and secrets
4. **Database security**: Use strong passwords and restrict database access
5. **System updates**: Keep system packages and dependencies updated
