# ACGS-1 Post-Cleanup Quick Reference Guide

## 📁 New File Locations

### Configuration Files
| File | Old Location | New Location |
|------|-------------|--------------|
| `pytest.ini` | `/` | `config/pytest.ini` |
| `requirements*.txt` | `/` | `config/requirements*.txt` |
| `.env.example` | `/` | `config/.env.example` |
| `uv.lock` | `/` | `config/uv.lock` |
| `.pre-commit-config.yaml` | `/` | `config/.pre-commit-config.yaml` |
| `.gitleaks.toml` | `/` | `config/.gitleaks.toml` |

### Docker & Infrastructure
| File | Old Location | New Location |
|------|-------------|--------------|
| `docker-compose.*.yml` | `/` | `infrastructure/docker/` |
| `Dockerfile.acgs` | `/` | `infrastructure/docker/` |

### Application Configs
| File | Old Location | New Location |
|------|-------------|--------------|
| `jest.config.js` | `/` | `applications/jest.config.js` |
| `tsconfig.json` | `/` | `applications/tsconfig.json` |
| `package*.json` | `/` | `applications/package*.json` |

### Test Configuration
| File | Old Location | New Location |
|------|-------------|--------------|
| `conftest.py` | `/` | `tests/conftest.py` |

### Reports & Documentation
| File | Old Location | New Location |
|------|-------------|--------------|
| `cleanup_report_*.json` | `/` | `reports/cleanup/` |
| `*SUMMARY.md` | `/` | `docs/` |
| `comprehensive_duplicate_cleanup.py` | `/` | `scripts/` |

## 🔧 Updated Commands

### Running Tests
```bash
# Old command
pytest

# New command (from project root)
python -m pytest -c config/pytest.ini

# Or from config directory
cd config && pytest
```

### Docker Commands
```bash
# Old command
docker-compose up

# New command
docker-compose -f infrastructure/docker/docker-compose.yml up
```

### Installing Dependencies
```bash
# Python dependencies
pip install -r config/requirements.txt

# Node.js dependencies (from applications directory)
cd applications && npm install
```

## 🏗️ Directory Structure Overview

```
ACGS-1/
├── analysis/                  # Cleanup analysis and reports
├── applications/              # Frontend and client applications
├── archive/                   # Historical data and backups
├── blockchain/                # Solana/Anchor smart contracts
├── config/                    # Centralized configuration files
├── docs/                      # Technical documentation
├── infrastructure/            # Docker, K8s, Terraform configs
├── services/                  # Core and platform services
├── scripts/                   # Automation and utility scripts
├── tests/                     # Test suites and coverage
└── [10 essential root files]  # Core project files only
```

## ⚡ Quick Actions

### Restore Service
```bash
# Check service status
curl http://localhost:8000/health

# Restart specific service
bash scripts/manage_pgc_service.sh start
```

### Run Cleanup Validation
```bash
# Validate cleanup completion
python scripts/validate_cleanup_completion.py

# Check system health
bash scripts/comprehensive_health_check.sh
```

### Fix Import Issues
```bash
# Fix Python import paths
python root_scripts/fix_python_imports.py

# Fix test imports
python root_scripts/fix_test_imports.py
```

## 🎯 Success Metrics Achieved

- ✅ **73.7% root directory reduction** (38 → 10 files)
- ✅ **1,559 files cleaned** from repository
- ✅ **Auth service operational** (port 8000)
- ✅ **Configuration centralized** in config/
- ✅ **Docker files organized** in infrastructure/
- ✅ **Comprehensive .gitignore** updated

## 🔍 Next Steps

1. **Service Restoration**: Restore remaining core services
2. **Import Path Fixes**: Run import correction scripts
3. **Test Validation**: Execute full test suite
4. **Performance Validation**: Verify response times
5. **Blockchain Validation**: Test Quantumagi deployment

For detailed information, see: `analysis/ACGS-1_CLEANUP_COMPLETION_REPORT.md`
