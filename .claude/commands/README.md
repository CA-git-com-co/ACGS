<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# Claude Commands for ACGS-2 Project Organization

This directory contains Claude-specific commands and specifications for optimizing the ACGS-2 project structure.

## Available Commands

### 1. Project Structure Organization

#### `organize-project-structure.md`
**Purpose**: Comprehensive design specification for reorganizing the ACGS-2 project structure.

**What it addresses**:
- Root directory cleanup (200+ files → <20)
- Service architecture standardization
- Duplicate code consolidation (16 duplicate scripts)
- Dependency management (22 requirements files → 6 shared)
- Documentation organization

**Key Features**:
- ✅ Complete analysis of current issues
- ✅ Detailed reorganization plan with phases
- ✅ Success criteria and metrics
- ✅ Risk mitigation strategies
- ✅ Implementation timeline

#### `execute-reorganization.sh`
**Purpose**: Automated implementation script based on the design specification.

**Usage**:
```bash
# Preview changes (recommended first)
./.claude/commands/execute-reorganization.sh --dry-run

# Execute reorganization
./.claude/commands/execute-reorganization.sh

# Get help
./.claude/commands/execute-reorganization.sh --help
```

**What it does**:
- ✅ Creates standardized directory structure
- ✅ Moves misplaced files to appropriate locations
- ✅ Consolidates duplicate scripts and tools
- ✅ Creates shared dependency structure
- ✅ Updates .gitignore for new organization
- ✅ Generates comprehensive report
- ✅ Creates backup before changes

## Implementation Workflow

### Phase 1: Analysis & Planning
1. Read the design specification: `organize-project-structure.md`
2. Review current project structure issues
3. Understand the proposed solutions

### Phase 2: Preview Changes
```bash
# See what would change without making modifications
./.claude/commands/execute-reorganization.sh --dry-run
```

### Phase 3: Create Backup
The script automatically creates timestamped backups, but you can also:
```bash
# Manual backup
cp -r . ../ACGS-2-backup-$(date +%Y%m%d)
```

### Phase 4: Execute Reorganization
```bash
# Run the full reorganization
./.claude/commands/execute-reorganization.sh
```

### Phase 5: Validation
1. Check that all services still function
2. Verify documentation links work
3. Test dependency resolution
4. Run CI/CD pipelines

## Expected Results

### Before Reorganization
- **Root directory**: 200+ scattered files
- **Duplicate scripts**: 16 copies across directories
- **Requirements files**: 22 with version conflicts
- **Documentation**: Fragmented across locations
- **Project size**: 6.3GB with unnecessary files

### After Reorganization
- **Root directory**: <20 essential files
- **Duplicate scripts**: 0 (consolidated and categorized)
- **Requirements files**: 6 shared, standardized files
- **Documentation**: Organized hierarchical structure
- **Project structure**: Clear architectural boundaries

## Directory Structure (Post-Reorganization)

```
/home/dislove/ACGS-2/
├── README.md                    # Primary project overview
├── CHANGELOG.md                 # Version history
├── pyproject.toml              # Main Python config
├── docker-compose.yml          # Primary compose
├── Makefile                    # Build automation
├── 
├── docs/                       # All documentation
│   ├── getting-started/        # Quick start guides
│   ├── architecture/           # System design docs
│   ├── api/                    # API documentation
│   ├── deployment/             # Infrastructure guides
│   ├── development/            # Developer guides
│   ├── security/               # Security docs
│   └── troubleshooting/        # Common issues
├── 
├── services/                   # Microservices
│   ├── shared/                 # Shared libraries
│   │   └── requirements/       # Consolidated dependencies
│   ├── core/                   # Core business services
│   ├── platform/               # Platform services
│   └── integration/            # External integrations
├── 
├── scripts/                    # Organized automation
│   ├── setup/                  # Installation scripts
│   ├── deployment/             # Deploy automation
│   ├── monitoring/             # Health checks
│   ├── testing/                # Test automation
│   ├── maintenance/            # Cleanup utilities
│   └── development/            # Dev tools
├── 
├── infrastructure/             # Infrastructure as code
├── tests/                      # Test suites
├── config/                     # Configuration templates
├── data/                       # Data files & schemas
├── reports/                    # Generated reports (gitignored)
├── temp/                       # Temporary files (gitignored)
└── .claude/                    # Claude commands
```

## Rollback Instructions

If you need to revert the reorganization:

1. **Using the backup**:
   ```bash
   # Find your backup directory
   ls -la backup-*
   
   # Restore from backup
   cp -r backup-YYYYMMDD-HHMMSS/* .
   ```

2. **Using git**:
   ```bash
   # Reset to pre-reorganization state
   git reset --hard HEAD~1  # If changes were committed
   git clean -fdx           # Remove untracked files
   ```

## Troubleshooting

### Common Issues

1. **Services fail to start after reorganization**
   - Check that shared requirements are accessible
   - Verify import paths are updated
   - Review service-specific requirements

2. **Documentation links broken**
   - Update relative paths in documentation
   - Check cross-references between docs
   - Verify README links

3. **CI/CD pipeline failures**
   - Update build scripts for new structure
   - Modify Docker file paths
   - Update test discovery patterns

### Getting Help

1. Review the design specification for detailed explanations
2. Check the reorganization report for specific changes made
3. Use `--dry-run` mode to preview changes before applying
4. Restore from backup if needed

## Benefits of Reorganization

✅ **Improved Maintainability**: Clear structure with consistent patterns
✅ **Reduced Duplication**: Consolidated scripts and dependencies  
✅ **Better Documentation**: Organized, discoverable information
✅ **Enhanced Developer Experience**: Faster onboarding and navigation
✅ **Cleaner CI/CD**: Simplified build and deployment processes
✅ **Reduced Technical Debt**: Eliminated scattered files and configs


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

---

**Created**: $(date)  
**Based on**: Post-cleanup analysis of ACGS-2 project structure  
**Scope**: Complete project reorganization and optimization


## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

**Constitutional Compliance**: All operations maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets (P99 <5ms, >100 RPS, >85% cache hit rates).

**Last Updated**: 2025-07-17 - Constitutional compliance enhancement
