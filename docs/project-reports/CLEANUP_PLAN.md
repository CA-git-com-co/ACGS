# ACGS-2 Project Cleanup Plan

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Date**: 2025-01-08  
**Status**: In Progress

## Executive Summary

This cleanup plan addresses the reorganization of the ACGS-2 root directory, which contains 200+ files that should be better organized into logical directories.

## Current Root Directory Analysis

### File Categories Identified

#### 1. Reports and Documentation (60+ files)
- `ACGS_*_REPORT.md` - Various completion and validation reports
- `*_SUMMARY.md` - Implementation summaries
- Coverage reports (`coverage_*.json`)
- Performance reports (`performance_*.json`)
- Validation reports (`*_validation_report.*`)

#### 2. Configuration Files (20+ files)
- `docker-compose*.yml` - Docker configurations
- `*.toml`, `*.ini` - Project configurations
- Environment and config files

#### 3. Scripts and Tools (30+ files)  
- `*.py` - Standalone Python scripts
- `*.sh` - Shell scripts
- Utility and maintenance scripts

#### 4. Test and Analysis Files (15+ files)
- `test_*.py` - Test files
- `*_test_*.py` - Test scripts
- Analysis and debugging files

#### 5. Temporary/Generated Files (10+ files)
- JSON output files with timestamps
- Temporary validation files
- Cache and backup files

## Proposed Directory Structure

```
ACGS-2/
├── README.md                    # Keep - Primary documentation
├── CLAUDE.md                    # Keep - Claude integration guide  
├── LICENSE                      # Keep - Legal requirement
├── pyproject.toml              # Keep - Project configuration
├── Makefile                    # Keep - Build automation
├── docker-compose.yml          # Keep - Primary compose file
├── CHANGELOG.md                # Keep - Version history
├── CONTRIBUTING.md             # Keep - Development guide
├── 
├── docs/                       # ✅ Already organized
├── services/                   # ✅ Already organized
├── infrastructure/             # ✅ Already organized
├── tests/                      # ✅ Already organized
├── tools/                      # ✅ Already organized
├── scripts/                    # ✅ Already organized
├── 
├── reports/                    # ⭐ NEW - Consolidate all reports
│   ├── completion/            # Completion reports
│   ├── performance/           # Performance analysis
│   ├── validation/            # Validation reports
│   ├── security/              # Security assessments
│   └── archive/               # Historical reports
├── 
├── config/                     # ⭐ ENHANCE - Additional configs
│   ├── docker/                # Docker compose variants
│   ├── deployment/            # Deployment configurations
│   └── environment/           # Environment settings
├── 
├── temp/                       # ⭐ NEW - Temporary files
│   ├── analysis/              # Analysis outputs
│   ├── backups/               # Backup files
│   └── generated/             # Generated files
└── 
└── archive/                    # ⭐ NEW - Historical items
    ├── legacy/                # Legacy files
    ├── migrations/            # Migration artifacts
    └── deprecated/            # Deprecated components
```

## Cleanup Actions

### Phase 1: Immediate Cleanup (High Priority)
1. **Remove build artifacts and cache files**
   - ✅ Python cache directories (__pycache__)
   - ✅ Python bytecode files (*.pyc)
   - ✅ MyPy cache (.mypy_cache)
   - Remove coverage files and test artifacts
   - Clean temporary analysis files

### Phase 2: Organize Reports (High Priority)
2. **Consolidate report files**
   - Move `ACGS_*_REPORT.md` to `reports/completion/`
   - Move `*_SUMMARY.md` to `reports/completion/`
   - Move `coverage_*.json` to `reports/performance/`
   - Move `performance_*.json` to `reports/performance/`
   - Move validation reports to `reports/validation/`

### Phase 3: Organize Configuration (Medium Priority)
3. **Consolidate configuration files**
   - Move `docker-compose.*.yml` to `config/docker/`
   - Move environment files to `config/environment/`
   - Keep core configs in root (pyproject.toml, etc.)

### Phase 4: Clean Scripts and Tools (Medium Priority)
4. **Organize standalone scripts**
   - Move root-level `*.py` scripts to `scripts/` or `tools/`
   - Move test files to appropriate test directories
   - Clean up duplicate or obsolete scripts

### Phase 5: Archive Historical Items (Low Priority)
5. **Archive legacy components**
   - Move old backup directories to `archive/`
   - Archive superseded implementation files
   - Clean up deprecated documentation

## Space Savings Estimate

### Current Cleanup Results
- **Python cache files**: 369 files removed
- **Cache directories**: 62 directories removed  
- **MyPy cache**: 9.3MB freed
- **Build artifacts**: Cleaned

### Expected Additional Savings
- **Log files**: ~200KB of logs can be archived
- **JSON reports**: ~50+ timestamp files can be organized
- **Duplicate configs**: Consolidation will reduce redundancy
- **Total estimated savings**: 15-20MB + improved organization

## Risk Assessment

### Low Risk Items
- Cache files and build artifacts (safe to remove)
- Duplicate configuration files
- Timestamp-based report files

### Medium Risk Items  
- Legacy script files (need validation)
- Old backup directories
- Deprecated components

### High Risk Items (Review Required)
- Core configuration files
- Active script dependencies
- Current development artifacts

## Implementation Timeline

### Week 1: Core Cleanup
- ✅ Remove cache and build artifacts
- ✅ Analyze root directory structure
- Create new directory structure
- Move report files

### Week 2: Configuration Cleanup
- Consolidate Docker configurations
- Organize environment files
- Update documentation references

### Week 3: Final Organization
- Move remaining scripts and tools
- Archive historical components
- Update CI/CD paths if needed
- Validate all moves

## Validation Steps

1. **Pre-cleanup testing**
   - Run test suite to ensure baseline functionality
   - Document current file locations
   - Create backup of critical configs

2. **Post-cleanup validation**
   - Verify all services still start correctly
   - Test Docker compose configurations
   - Validate CI/CD pipeline functionality
   - Ensure documentation links are updated

3. **Performance validation**
   - Measure cleanup impact on build times
   - Verify reduced disk usage
   - Test development workflow efficiency

## Success Metrics

- **File count reduction**: Reduce root directory files by 80%
- **Organization improvement**: Logical grouping of related files
- **Disk space optimization**: 15-20MB space savings
- **Developer experience**: Improved navigation and discoverability
- **Maintenance reduction**: Easier to maintain organized structure

---

**Next Steps**: Execute Phase 1 cleanup and begin Phase 2 organization