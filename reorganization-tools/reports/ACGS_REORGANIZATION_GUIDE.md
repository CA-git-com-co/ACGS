<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS Repository Reorganization Guide

## Overview

This guide provides comprehensive instructions for reorganizing the monolithic ACGS (Adaptive Constitutional Governance System) repository into 7 smaller, more manageable sub-repositories. The reorganization preserves git history, maintains integration capabilities, and improves maintainability.

## Repository Structure

The ACGS codebase will be split into the following repositories:

### 1. acgs-core
**Purpose**: Core constitutional AI services  
**Components**:
- Constitutional AI Service (AC)
- Formal Verification Service (FV)
- Governance Synthesis Service (GS)
- Policy Governance Compliance (PGC)
- Evolutionary Computation Service (EC)
- Multi-agent coordination
- Worker agents (Ethics, Legal, Operational)
- Consensus mechanisms

### 2. acgs-platform
**Purpose**: Platform services and shared utilities  
**Components**:
- Authentication service (JWT, MFA, OAuth)
- Integrity verification service
- Shared utilities (blackboard, service mesh, database, Redis, WINA)

### 3. acgs-blockchain
**Purpose**: Blockchain integration and Solana programs  
**Components**:
- Anchor programs (quantumagi-core, appeals, logging)
- Client libraries (Python, Rust)
- Scripts and tests
- Blockchain configuration

### 4. acgs-models
**Purpose**: AI model services  
**Components**:
- Model service
- Reasoning models
- vLLM service

### 5. acgs-applications
**Purpose**: Frontend applications  
**Components**:
- Web dashboards
- Admin panels
- User interfaces

### 6. acgs-infrastructure
**Purpose**: Infrastructure as Code  
**Components**:
- Docker configurations (30+ compose files)
- Kubernetes manifests
- Terraform definitions
- Monitoring (Prometheus, Grafana)
- Security policies
- Load balancer configurations

### 7. acgs-tools
**Purpose**: Development and maintenance tools  
**Components**:
- 400+ utility scripts
- Security scanners
- Performance testing tools
- Deployment scripts
- Migration tools
- SWE agent implementation

## Prerequisites

Before starting the reorganization:

1. **Install Required Tools**:
   ```bash
   # Git filter-repo (for preserving history)
   pip install git-filter-repo
   
   # Python dependencies
   pip install toml pyyaml
   
   # Ensure you have git, uv, pnpm, and cargo installed
   ```

2. **Backup Your Repository**:
   ```bash
   # Create a full backup
   cp -r /path/to/acgs /path/to/acgs-backup
   
   # Or create a git bundle
   cd /path/to/acgs
   git bundle create acgs-backup.bundle --all
   ```

3. **Check Repository Size**:
   ```bash
   # The current repository is ~5.6GB with 90K+ files
   # Ensure you have sufficient disk space (at least 20GB recommended)
   du -sh /path/to/acgs
   find /path/to/acgs -type f | wc -l
   ```

## Usage Instructions

### Step 1: Basic Reorganization

Run the reorganization script with a dry run first:

```bash
# Dry run to see what will happen
python acgs_reorganize.py /path/to/acgs /path/to/workspace --dry-run

# Actual reorganization
python acgs_reorganize.py /path/to/acgs /path/to/workspace
```

### Step 2: Extract Specific Repositories

To extract only specific repositories:

```bash
# Extract only core and platform services
python acgs_reorganize.py /path/to/acgs /path/to/workspace --repos acgs-core acgs-platform
```

### Step 3: Verify Migration

After reorganization, verify the results:

```bash
cd /path/to/workspace

# Check repository structure
ls -la

# Verify git history is preserved
cd acgs-core
git log --oneline | head -20

# Check file count
find . -type f | wc -l
```

### Step 4: Update Dependencies

The script automatically updates dependencies, but you may need to manually verify:

1. **Python Projects** (pyproject.toml):
   ```toml
   [project.dependencies]
   acgs-platform = {path = "../acgs-platform", develop = true}
   ```

2. **Node.js Projects** (package.json):
   ```json
   {
     "dependencies": {
       "@acgs/platform": "workspace:*"
     }
   }
   ```

3. **Rust Projects** (Cargo.toml):
   ```toml
   [dependencies]
   acgs-platform = { path = "../acgs-platform" }
   ```

### Step 5: Set Up Workspace

After reorganization, set up the development workspace:

```bash
cd /path/to/workspace

# Run the automated setup
python scripts/setup_workspace.py

# This will:
# - Clone any missing repositories
# - Install dependencies for each repo
# - Set up cross-repository links
```

### Step 6: Run Integration Tests

Verify everything works together:

```bash
# Run integration tests across all repositories
python scripts/run_integration_tests.py

# Run specific repository tests
cd acgs-core
uv run pytest tests/

cd ../acgs-blockchain
pnpm test
```

## Post-Migration Tasks

### 1. Update CI/CD Pipelines

Each repository now has its own `.github/workflows/ci.yml`. Update as needed:

- Add repository-specific test commands
- Configure deployment triggers
- Set up cross-repository integration tests

### 2. Configure Git Remotes

Set up proper Git remotes for each repository:

```bash
cd acgs-core
git remote remove origin
git remote add origin git@github.com:ACGS/acgs-core.git
git push -u origin main
```

### 3. Update Import Paths

Some imports may need updating to reference the new structure:

```python
# Old import
from services.shared.blackboard import Blackboard

# New import (if in different repo)
from acgs_platform.shared.blackboard import Blackboard
```

### 4. Set Up Git LFS (if needed)

For repositories with large files:

```bash
git lfs track "*.bin"
git lfs track "*.model"
git add .gitattributes
git commit -m "Configure Git LFS"
```

### 5. Update Documentation

Update all documentation to reflect the new structure:

- README files in each repository
- API documentation
- Deployment guides
- Developer setup instructions

## Workspace Management

### Working Across Repositories

The workspace configuration (`acgs-workspace.json`) helps manage multiple repositories:

```bash
# Pull all repositories
for repo in acgs-*; do
  echo "Updating $repo..."
  cd $repo && git pull && cd ..
done

# Run a command across all repos
for repo in acgs-*; do
  echo "Building $repo..."
  cd $repo && make build && cd ..
done
```

### Cross-Repository Development

When developing features that span multiple repositories:

1. Create feature branches in each affected repository
2. Use workspace dependencies for local development
3. Test integration before creating pull requests
4. Reference related PRs in commit messages

### Dependency Management

Keep dependencies synchronized:

```bash
# Update all Python dependencies
for repo in acgs-*; do
  if [ -f "$repo/pyproject.toml" ]; then
    cd $repo && uv sync && cd ..
  fi
done

# Update all Node.js dependencies
for repo in acgs-*; do
  if [ -f "$repo/package.json" ]; then
    cd $repo && pnpm install && cd ..
  fi
done
```

## Troubleshooting

### Common Issues

1. **Git filter-repo not found**:
   ```bash
   pip install --user git-filter-repo
   # Add to PATH if needed
   export PATH=$PATH:~/.local/bin
   ```

2. **Large file warnings**:
   ```bash
   # Find large files
   find . -type f -size +100M
   
   # Add to Git LFS before committing
   git lfs track "path/to/large/file"
   ```

3. **Import errors after migration**:
   - Check that workspace dependencies are properly configured
   - Ensure PYTHONPATH includes workspace root
   - Verify all __init__.py files exist

4. **Missing dependencies**:
   ```bash
   # Reinstall dependencies
   cd affected-repo
   rm -rf .venv uv.lock
   uv sync
   ```

### Validation

Use the migration utilities to validate:

```python
from acgs_migration_utils import MigrationValidator

validator = MigrationValidator(
    source_repo=Path("/path/to/original"),
    target_repos={
        "acgs-core": Path("/path/to/workspace/acgs-core"),
        # ... other repos
    }
)

report = validator.generate_validation_report()
print(report)
```

## Best Practices

1. **Commit Frequently**: Make small, focused commits during migration
2. **Test Early**: Run tests after each major change
3. **Document Changes**: Update documentation as you go
4. **Use Branches**: Create migration branches for safety
5. **Automate**: Use scripts for repetitive tasks

## Next Steps

After successful reorganization:

1. **Set up CI/CD**: Configure GitHub Actions for each repository
2. **Create Release Process**: Define how to coordinate releases across repos
3. **Update Deployment**: Modify deployment scripts for new structure
4. **Train Team**: Ensure all developers understand the new structure
5. **Monitor Performance**: Track build times and development velocity

## Support

For issues or questions:

1. Check the generated `REORGANIZATION.md` in your workspace
2. Review logs in each repository's `.migration` directory
3. Use validation tools to diagnose problems
4. Create issues in the appropriate repository

## Appendix: Script Options

### acgs_reorganize.py Options

```
usage: acgs_reorganize.py [-h] [--dry-run] [--repos REPOS [REPOS ...]]
                          source_repo target_dir

Reorganize ACGS monolithic repository into sub-repositories

positional arguments:
  source_repo           Path to the source ACGS repository
  target_dir            Target directory for sub-repositories

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             Perform a dry run without making changes
  --repos REPOS [REPOS ...]
                        Specific repositories to extract (default: all)
```

### Environment Variables

- `ACGS_WORKSPACE`: Set default workspace directory
- `ACGS_SKIP_VALIDATION`: Skip validation steps
- `ACGS_PRESERVE_TIMESTAMPS`: Preserve file timestamps during migration

## Conclusion

This reorganization improves:

- **Maintainability**: Smaller, focused repositories
- **Performance**: Faster clone/build times
- **Collaboration**: Teams can work on specific components
- **Security**: Granular access control per repository
- **CI/CD**: Parallel builds and targeted deployments

Follow this guide carefully, and don't hesitate to run dry runs before actual migration. The modular structure will significantly improve the development experience while maintaining the integrated nature of the ACGS system.