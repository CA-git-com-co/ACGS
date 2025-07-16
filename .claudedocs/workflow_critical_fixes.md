# ACGS-2 GitHub Actions Critical Fixes
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 🚨 Critical Issues Fixed

### 1. **Redis CLI Missing** ✅
**Error**: `redis-cli: command not found`
**Solution**: Already added in testing workflow
```yaml
# Install system dependencies
sudo apt-get update
sudo apt-get install -y postgresql-client redis-tools
```

### 2. **Pytest Plugin Dependencies** ✅
**Error**: `pytest: error: unrecognized arguments: --html --self-contained-html --timeout`
**Solution**: Added pytest plugin installations
```yaml
# Install pytest and required plugins
pip install pytest pytest-asyncio httpx docker psycopg2-binary redis
pip install pytest-html pytest-timeout pytest-json-report
```

### 3. **PostgreSQL Role Configuration** ✅
**Error**: `FATAL: role "root" does not exist`
**Solution**: Fixed PostgreSQL service configuration
```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: postgres  # Explicitly set user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: acgs_test
      POSTGRES_HOST_AUTH_METHOD: trust  # Allow connections
    ports:
      - 5432:5432  # Expose port for connections
```

## 📋 Complete Fixes Applied

### testing-consolidated.yml
1. **PostgreSQL Service**: Added explicit POSTGRES_USER and port mapping
2. **Redis Service**: Added port mapping for external access
3. **Pytest Plugins**: Added pytest-html, pytest-timeout, pytest-json-report
4. **System Dependencies**: Already had redis-tools and postgresql-client

### main-ci-cd.yml
1. **Pytest Plugins**: Added same plugin dependencies with error handling
2. **Graceful Fallback**: Continues if plugins fail to install

## 🔍 Verification Commands

To verify these fixes work:
```bash
# Check redis-cli is available
which redis-cli

# Check PostgreSQL connection
psql -h localhost -U postgres -d acgs_test -c "SELECT 1"

# Check pytest plugins
pytest --version
pytest --help | grep -E "(html|timeout)"
```

## ✅ Results

All three critical issues have been addressed:
- ✅ Redis CLI installed via redis-tools package
- ✅ Pytest plugins installed for HTML reports and timeouts
- ✅ PostgreSQL configured with proper user and authentication

The workflows should now proceed without these specific errors.

---
**Fixes Applied**: 2025-07-16 03:00 UTC  
**Constitutional Hash**: cdd01ef066bc6cf2