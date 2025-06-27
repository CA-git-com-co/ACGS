# ACGS Documentation Maintenance Guide

**Version**: 1.0  
**Last Updated**: 2025-06-23  
**Owner**: Development Team

## 🎯 Overview

This guide establishes standards and procedures for maintaining high-quality, accurate documentation across the ACGS project.

## 📋 Documentation Standards

### File Organization

```
docs/
├── README.md                    # Documentation index
├── api/                         # API documentation
├── architecture/                # System design docs
├── deployment/                  # Deployment guides
├── development/                 # Developer guides
├── operations/                  # Operational runbooks
├── security/                    # Security documentation
├── testing/                     # Testing guides
└── troubleshooting/            # Troubleshooting guides
```

### Naming Conventions

- **Files**: Use kebab-case: `deployment-guide.md`
- **Directories**: Use kebab-case: `api-reference/`
- **Headings**: Use sentence case: `Getting started`
- **Code blocks**: Always specify language: `bash`, `python`, `typescript`

### Required Sections

Every major documentation file should include:

1. **Title and metadata**
2. **Table of contents** (for files >100 lines)
3. **Overview/Purpose**
4. **Prerequisites**
5. **Step-by-step instructions**
6. **Examples**
7. **Troubleshooting**
8. **Related documentation**

## ✅ Quality Checklist

### Before Publishing

- [ ] All service paths are correct and current
- [ ] All code examples have been tested
- [ ] All internal links work
- [ ] All external links are valid
- [ ] Screenshots are up-to-date
- [ ] Version numbers are current
- [ ] Prerequisites are clearly stated
- [ ] Troubleshooting section is complete

### Content Review

- [ ] Information is accurate and current
- [ ] Instructions are clear and complete
- [ ] Examples work as documented
- [ ] Terminology is consistent
- [ ] Grammar and spelling are correct
- [ ] Formatting follows standards

## 🔧 Maintenance Procedures

### Weekly Tasks

1. **Link Validation**

   ```bash
   python documentation_audit_analyzer.py
   ```

2. **Service Path Verification**

   - Verify all service directory references
   - Check port number consistency
   - Validate Docker Compose paths

3. **Code Example Testing**
   - Test setup instructions
   - Verify API examples
   - Check deployment scripts

### Monthly Tasks

1. **Comprehensive Review**

   - Review all user-facing documentation
   - Update version numbers
   - Refresh screenshots
   - Update performance metrics

2. **Structure Assessment**
   - Evaluate documentation organization
   - Identify gaps or redundancies
   - Plan improvements

### Quarterly Tasks

1. **Full Audit**

   - Complete documentation inventory
   - Assess quality metrics
   - Plan major improvements

2. **User Feedback Integration**
   - Review user feedback and issues
   - Update based on common questions
   - Improve unclear sections

## 🚨 Critical Paths to Monitor

### Service Documentation

Always verify these paths are current:

```bash
# Core Services
services/core/constitutional-ai/ac_service/
services/core/governance-synthesis/gs_service/
services/core/policy-governance/pgc_service/
services/core/formal-verification/fv_service/
services/core/evolutionary-computation/
services/core/dgm-service/

# Platform Services
services/platform/authentication/auth_service/
services/platform/integrity/integrity_service/

# Frontend
project/  # (consolidated frontend application)
```

### Port Assignments

Maintain consistency across all documentation:

- Authentication Service: 8000
- Constitutional AI Service: 8001
- Integrity Service: 8002
- Formal Verification Service: 8003
- Governance Synthesis Service: 8004
- Policy Governance Service: 8005
- Evolutionary Computation Service: 8006
- Darwin Gödel Machine Service: 8007

## 🛠️ Tools and Automation

### Documentation Audit Tool

```bash
# Run comprehensive audit
python documentation_audit_analyzer.py

# Check specific directory
python documentation_audit_analyzer.py --path docs/api/

# Validate links only
python documentation_audit_analyzer.py --links-only
```

### Automated Checks

Set up pre-commit hooks to:

- Validate markdown syntax
- Check internal links
- Verify service paths
- Test code examples

### CI/CD Integration

Include documentation validation in CI pipeline:

```yaml
- name: Validate Documentation
  run: |
    python documentation_audit_analyzer.py
    # Fail build if critical issues found
```

## 📊 Quality Metrics

Track these metrics monthly:

| Metric                 | Target | Current |
| ---------------------- | ------ | ------- |
| Broken Links           | 0      | Monitor |
| Files with TOC         | 80%    | 26.4%   |
| Accurate Service Paths | 100%   | Monitor |
| Code Example Coverage  | 85%    | 78.1%   |
| User Satisfaction      | >4.5/5 | Survey  |

## 🔄 Update Workflow

### For Service Changes

1. **Before Code Changes**

   - Identify affected documentation
   - Plan documentation updates

2. **During Development**

   - Update documentation alongside code
   - Test all examples and instructions

3. **Before Merge**
   - Run documentation audit
   - Review all changes
   - Test user workflows

### For Documentation-Only Changes

1. **Create branch**: `docs/update-description`
2. **Make changes** following standards
3. **Test thoroughly** using checklist
4. **Submit PR** with documentation review
5. **Merge** after approval

## 🆘 Emergency Procedures

### Critical Documentation Issues

If documentation is blocking users:

1. **Immediate Fix**

   - Create hotfix branch
   - Make minimal necessary changes
   - Test quickly but thoroughly
   - Deploy immediately

2. **Follow-up**
   - Create comprehensive fix
   - Update related documentation
   - Improve processes to prevent recurrence

### Rollback Procedures

If documentation changes cause issues:

1. **Identify problem** scope and impact
2. **Revert changes** to last known good state
3. **Communicate** to affected users
4. **Plan proper fix** with thorough testing

## 📞 Contacts and Escalation

- **Documentation Owner**: Development Team Lead
- **Technical Review**: Senior Engineers
- **User Experience**: Product Team
- **Emergency Contact**: On-call Engineer

---

**Remember**: Good documentation is as important as good code. Keep it current, accurate, and user-focused.
