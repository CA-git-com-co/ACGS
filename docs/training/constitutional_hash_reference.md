# Constitutional Hash Quick Reference

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Purpose**: Security and compliance identifier for all ACGS documentation  
**Requirement**: MANDATORY in all documentation files

## Quick Implementation Guide

### 1. Documentation Files (.md)

**Add to the top of every markdown file:**
```markdown
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
```

**Example:**
```markdown
# Service Documentation

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

This document describes...
```

### 2. API Response Examples

**Include in ALL JSON response examples:**
```json
{
  "data": "response content",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-05T10:30:00Z"
}
```

### 3. Configuration Files

**Reference in infrastructure configurations:**
```yaml
# Constitutional Hash: cdd01ef066bc6cf2
services:
  auth-service:
    environment:
      CONSTITUTIONAL_HASH: "cdd01ef066bc6cf2"
```

## Validation Commands

### Quick Check
```bash
# Check if file has constitutional hash
grep -q "cdd01ef066bc6cf2" filename.md && echo "✅ Found" || echo "❌ Missing"
```

### Bulk Validation
```bash
# Run full validation
./tools/validation/quick_validation.sh
```

### Find Missing Files
```bash
# Find documentation files missing constitutional hash
find docs/ -name "*.md" -exec grep -L "cdd01ef066bc6cf2" {} \;
```

## Common Mistakes

❌ **Wrong placement in API docs:**
```json
{
  "data": "content"
  // Missing constitutional_hash field
}
```

✅ **Correct placement:**
```json
{
  "data": "content",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

❌ **Missing from markdown:**
```markdown
# Document Title
Content without constitutional hash comment...
```

✅ **Correct markdown:**
```markdown
# Document Title

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

Content with constitutional hash comment...
```

## Troubleshooting

**Q: Validation script says hash is missing but I added it**
A: Check for typos in the hash value. It must be exactly `cdd01ef066bc6cf2`

**Q: Where should I place the hash in markdown files?**
A: After the main heading, as an HTML comment

**Q: Do I need the hash in code examples?**
A: Only in API response examples, not in code snippets

**Q: What if I forget to add it?**
A: The validation tools will catch it. Add it before committing.

---

**Constitutional Hash**: `cdd01ef066bc6cf2` ✅
