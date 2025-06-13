# ACGS-1 Reorganization Migration Guide

This guide helps existing contributors adapt to the new blockchain-focused directory structure.

## 🔄 What Changed

### Directory Structure Changes

| Old Location | New Location | Purpose |
|--------------|--------------|---------|
| `services/core/ac_service/` | `services/core/constitutional-ai/` | Constitutional AI service |
| `services/core/gs_service/` | `services/core/governance-synthesis/` | Governance synthesis service |
| `services/core/pgc_service/` | `services/core/policy-governance/` | Policy governance service |
| `services/core/fv_service/` | `services/core/formal-verification/` | Formal verification service |
| `services/core/auth_service/` | `services/platform/authentication/` | Authentication service |
| `services/core/integrity_service/` | `services/platform/integrity/` | Integrity service |
| `services/core/shared/` | `services/shared/` | Shared libraries |
| `applications/` | `applications/legacy-frontend/` | Legacy frontend |
| `quantumagi_core/` | `blockchain/` | Blockchain programs |
| `src/alphaevolve_gs_engine/` | `integrations/alphaevolve-engine/` | AlphaEvolve integration |

### Import Path Changes

| Old Import | New Import |
|------------|------------|
| `from src.backend.shared` | `from services.shared` |
| `from src.backend.ac_service` | `from services.core.constitutional_ai.ac_service` |
| `from shared.models` | `from services.shared.models` |
| `import src.backend.gs_service` | `import services.core.governance_synthesis.gs_service` |

### Docker & Deployment Changes

| Old Path | New Path |
|----------|----------|
| `./services/core/ac_service` | `./services/core/constitutional-ai/ac_service` |
| `./quantumagi_core/deploy` | `./blockchain/quantumagi-deployment/deploy` |
| `docker-compose.yml` | `infrastructure/docker/docker-compose.yml` |

## 🛠️ Migration Steps

### 1. Update Local Development Environment

```bash
# Pull latest changes
git pull origin master

# Update Python virtual environment
source venv/bin/activate
pip install -r requirements.txt

# Rebuild Anchor programs
cd blockchain
anchor build
cd ..

# Update Node.js dependencies
cd applications/governance-dashboard
npm install
cd ../..
```

### 2. Update Import Statements

**Python Services**:
```python
# Old
from src.backend.shared.models import User
from src.backend.ac_service.app.main import app

# New
from services.shared.models import User
from services.core.constitutional_ai.ac_service.app.main import app
```

**TypeScript/JavaScript**:
```typescript
// Old
import { SolanaService } from '../../../quantumagi_core/client'

// New
import { SolanaService } from '../../../blockchain/client'
```

### 3. Update Docker Configurations

**docker-compose.yml**:
```yaml
# Old
services:
  ac_service:
    build: ./services/core/ac_service

# New
services:
  ac_service:
    build: ./services/core/constitutional-ai/ac_service
```

### 4. Update CI/CD Workflows

**GitHub Actions**:
```yaml
# Old
- name: Build service
  run: docker build ./services/core/ac_service

# New
- name: Build service
  run: docker build ./services/core/constitutional-ai/ac_service
```

### 5. Update Documentation References

- Replace `services/core/` with `services/`
- Replace `quantumagi_core/` with `blockchain/`
- Update API endpoint documentation
- Update deployment guide references

## 🧪 Testing Your Migration

### 1. Verify Service Startup

```bash
# Test core services
cd services/core/constitutional-ai && python -m uvicorn app.main:app --port 8001
cd services/core/governance-synthesis && python -m uvicorn app.main:app --port 8002

# Test platform services
cd services/platform/authentication && python -m uvicorn app.main:app --port 8000
cd services/platform/integrity && python -m uvicorn app.main:app --port 8005
```

### 2. Verify Blockchain Programs

```bash
cd blockchain
anchor test
```

### 3. Verify Frontend Applications

```bash
cd applications/governance-dashboard
npm start
```

### 4. Run Full Test Suite

```bash
./run_tests.sh
```

## 🔧 Common Migration Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src.backend'`

**Solution**: Update import statements to use new paths:
```python
# Change this
from src.backend.shared.models import User

# To this
from services.shared.models import User
```

### Docker Build Failures

**Problem**: `COPY failed: file not found`

**Solution**: Update Dockerfile paths:
```dockerfile
# Change this
COPY services/core/shared /app/shared

# To this
COPY services/shared /app/shared
```

### Test Failures

**Problem**: Tests can't find modules or files

**Solution**: Update test imports and file paths:
```python
# Update test imports
from services.core.constitutional_ai.ac_service.app.main import app

# Update test file paths
test_file = "services/shared/test_data/sample.json"
```

### Anchor Program Issues

**Problem**: `anchor build` fails

**Solution**: Ensure you're in the `blockchain/` directory:
```bash
cd blockchain
anchor build
```

## 📋 Migration Checklist

- [ ] Updated local development environment
- [ ] Fixed all import statements in Python code
- [ ] Fixed all import statements in TypeScript/JavaScript code
- [ ] Updated Docker configurations
- [ ] Updated CI/CD workflow files
- [ ] Updated documentation references
- [ ] Tested service startup
- [ ] Tested blockchain programs
- [ ] Tested frontend applications
- [ ] Ran full test suite
- [ ] Verified deployment scripts work

## 🆘 Getting Help

If you encounter issues during migration:

1. **Check the logs**: Look for specific error messages
2. **Review this guide**: Ensure you've followed all steps
3. **Check GitHub Issues**: Search for similar migration issues
4. **Ask for help**: Create a GitHub issue with:
   - Error message
   - Steps you've tried
   - Your environment details

## 🎯 Benefits of New Structure

- **Clearer separation of concerns**: Blockchain, services, applications
- **Better scalability**: Modular service architecture
- **Improved maintainability**: Logical organization
- **Enhanced development velocity**: Clear development workflows
- **Blockchain-first approach**: Prioritizes on-chain components

The reorganization positions ACGS-1 for better long-term maintainability and development efficiency while following blockchain development best practices.
