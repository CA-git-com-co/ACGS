# 🔒 SECURE DUPLICATION CLEANUP PLAN

## Executive Summary

**SAFE OPERATION**: Underscore service directories are symbolic links, not duplicates.
**RISK LEVEL**: LOW - Only 2 Python imports need updating.
**BACKUP REQUIRED**: Minimal - just symlink recreation script.

## Phase 1: Analysis Results ✅

### Service Quality Ranking

| Rank | Service                  | Lines of Code | Status           | Action   |
| ---- | ------------------------ | ------------- | ---------------- | -------- |
| 🥇   | governance-synthesis     | 52,783        | Production Ready | **KEEP** |
| 🥈   | constitutional-ai        | 28,538        | Production Ready | **KEEP** |
| 🥉   | policy-governance        | 22,422        | Feature Rich     | **KEEP** |
| 4    | formal-verification      | 10,032        | Functional       | **KEEP** |
| 5    | self-evolving-ai         | 7,311         | Basic            | **KEEP** |
| 6    | evolutionary-computation | 6,343         | Minimal          | **KEEP** |

### Symlink Status

```bash
constitutional_ai -> constitutional-ai ✅
formal_verification -> formal-verification ✅
governance_synthesis -> governance-synthesis ✅
policy_governance -> policy-governance ✅
evolutionary_computation -> evolutionary-computation ✅
self_evolving_ai -> self-evolving-ai ✅
```

## Phase 2: Reference Audit Results ✅

### Infrastructure References (SAFE)

- Docker Compose: Uses hyphenated names ✅
- Kubernetes: Uses hyphenated names ✅
- Scripts: Uses hyphenated names ✅

### Python Import Issues (NEED FIXING)

```python
# File: scripts/test_wina_svd_integration.py
from services.core.governance_synthesis.app.core.wina_llm_integration import (
from services.core.governance_synthesis.app.schemas import (

# File: scripts/reorganization/fix_imports.py
'src.backend.gs_service': 'services.core.governance_synthesis'
'src.backend.pgc_service': 'services.core.policy_governance'
'src.backend.fv_service': 'services.core.formal_verification'
```

## Phase 3: Backup Strategy 🔒

### Pre-Cleanup Backup

```bash
# 1. Create backup directory
mkdir -p /home/ubuntu/ACGS_CLEANUP_BACKUP/$(date +%Y%m%d_%H%M%S)

# 2. Backup symlinks (for recreation)
cd /home/ubuntu/ACGS/services/core
ls -la *_* > /home/ubuntu/ACGS_CLEANUP_BACKUP/symlinks_backup.txt

# 3. Backup affected Python files
cp scripts/test_wina_svd_integration.py /home/ubuntu/ACGS_CLEANUP_BACKUP/
cp scripts/reorganization/fix_imports.py /home/ubuntu/ACGS_CLEANUP_BACKUP/
```

### Rollback Script

```bash
#!/bin/bash
# rollback_cleanup.sh
cd /home/ubuntu/ACGS/services/core
ln -sf constitutional-ai constitutional_ai
ln -sf formal-verification formal_verification
ln -sf governance-synthesis governance_synthesis
ln -sf policy-governance policy_governance
ln -sf evolutionary-computation evolutionary_computation
ln -sf self-evolving-ai self_evolving_ai
echo "✅ Symlinks restored"
```

## Phase 4: Cleanup Decision Matrix

### OPTION A: Keep Symlinks (RECOMMENDED)

**Pros:**

- Zero risk of breaking anything
- Both naming conventions continue to work
- No code changes needed
- Maintains backward compatibility

**Cons:**

- Slight directory clutter (6 symlinks)
- Potential confusion for new developers

### OPTION B: Remove Symlinks + Update Imports

**Pros:**

- Cleaner directory structure
- Forces standardization on hyphenated names
- Eliminates naming confusion

**Cons:**

- Requires updating 2 Python files
- Risk of breaking undiscovered imports
- Need to update documentation

### OPTION C: Hybrid Approach

**Pros:**

- Remove unused symlinks only
- Keep symlinks for actively imported services
- Gradual migration path

**Cons:**

- Inconsistent approach
- Still some directory clutter

## Recommendation: OPTION A (Keep Symlinks)

### Rationale:

1. **Symlinks are intentional** - created by dedicated script
2. **Both conventions are used** - infrastructure vs Python imports
3. **Risk vs Benefit** - minimal benefit for cleanup risk
4. **Developer Experience** - both naming styles work seamlessly

## Alternative: Minimal Cleanup

If cleanup is desired, focus on **actual unused files**:

### Safe Cleanup Targets:

```bash
# Remove backup/temp files
find . -name "*.bak" -o -name "*.tmp" -o -name "*~" -o -name "*.orig"

# Remove empty directories
find . -type d -empty

# Remove large log files
find . -name "*.log" -size +10M

# Remove Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Final Recommendation

**DO NOT REMOVE SYMLINKS** - they serve a legitimate purpose for naming convention compatibility.

**FOCUS ON FRONTEND RECREATION** instead - this will provide much greater value with zero risk.
