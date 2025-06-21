# ACGS-1 Repository Cleanup Analysis Report

## Current State Analysis

### Baseline Metrics

- **Total files**: 1,571,722 files
- **Root directory files**: 38 files
- **Target reduction**: >70% of root directory files (target: <12 files)

### Directory Size Analysis

- **Largest directories**:
  - backups: 11GB (cleanup candidate)
  - applications: 5.9GB (reorganize)
  - venv: 4.0GB (exclude from git)
  - tools: 35MB (reorganize)
  - blockchain: 561MB (already organized)
  - services: 259MB (already organized)

### Service Health Status

- Auth service (8000): ✅ OPERATIONAL
- PGC service (8005): ❌ DOWN
- Other services: Need verification

## Cleanup Strategy

### Phase 1: Immediate Cleanup Targets

1. **Root directory files** (38 → <12 files):

   - Move cleanup reports to reports/
   - Move comprehensive summaries to docs/
   - Archive old backups (11GB)
   - Remove duplicate files

2. **Generated artifacts**:

   - **pycache** directories
   - node_modules (applications/)
   - target/ directories (Rust)
   - .pyc files
   - Temporary logs

3. **Archive management**:
   - Compress old backups (11GB → <1GB)
   - Move timestamped reports to archive/
   - Implement 30-day retention policy

### Phase 2: Reorganization Targets

1. **Applications directory** (5.9GB):

   - Consolidate frontend components
   - Remove duplicate node_modules
   - Optimize build artifacts

2. **Scripts consolidation**:

   - Merge root_scripts/ into scripts/
   - Categorize by function
   - Remove duplicates

3. **Documentation restructuring**:
   - Consolidate scattered docs
   - Remove outdated files
   - Standardize naming

### Phase 3: Quality Enforcement

1. **Code formatting**:

   - rustfmt for Rust files
   - Black for Python files
   - Prettier for JS/TS files

2. **Configuration consolidation**:
   - Centralize in config/
   - Remove duplicates
   - Update paths

### Risk Mitigation

- Preserve Quantumagi deployment functionality
- Maintain service configurations
- Keep git history intact
- Create rollback points

## Success Criteria

- [ ] Root directory files: 38 → <12 (>70% reduction)
- [ ] Total repository size reduction: >30%
- [ ] All 7 core services operational
- [ ] Quantumagi Solana devnet preserved
- [ ] > 80% test coverage maintained
- [ ] <500ms response times maintained
