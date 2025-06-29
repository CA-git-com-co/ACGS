# S0-4: WAF Security Recommendations

**Status**: ✅ COMPLETED  
**Priority**: P1 LOW  
**Date**: 2025-01-29  
**Sprint**: 0 (Hot-fix Security)

## 🎯 Executive Summary

This document provides **Web Application Firewall (WAF) security recommendations** for the ACGS-PGP project based on actual security vulnerabilities discovered during Sprint 0 security remediation. These recommendations provide defense-in-depth protection against injection attacks, unauthorized access, and common web application threats.

**Key Recommendations:**
- 🛡️ **Immediate**: Deploy injection protection rules
- 🔒 **High Priority**: Implement API endpoint protection
- 📊 **Medium Priority**: Add rate limiting and monitoring
- 🔄 **Ongoing**: Maintain and update rule sets

## 🚨 Threat Analysis (Based on Actual Findings)

### **1. Datalog Injection Attacks** (CRITICAL - Fixed in S0-1)
**Vulnerability**: Direct string interpolation in policy evaluation
```python
# VULNERABLE CODE (now fixed)
target_query = f"allow('{user_id}', '{action_type}', '{resource_id}')"
```

**Attack Patterns to Block:**
- Datalog syntax injection: `'; drop_all_rules; allow('admin`
- Nested quotes: `user'nested'quote`
- Logic operators: `user and admin`, `action or delete`
- Special characters: `user()`, `action,malicious`

### **2. Unauthorized Data Export** (HIGH - Fixed in S0-2)
**Vulnerability**: Missing admin authorization on export endpoints
```bash
# ATTACK EXAMPLE (now blocked)
curl -X POST "/api/v1/audit/export" \
  -H "Authorization: Bearer any-valid-token"
```

**Attack Patterns to Block:**
- Bulk data export attempts
- Unauthorized API access
- Token manipulation attempts
- Privilege escalation patterns

### **3. Dependency Exploitation** (MEDIUM - Monitored in S0-3)
**Current Vulnerabilities**: urllib3 CVEs detected
- CVE-2025-50182: Pyodide redirect bypass
- CVE-2025-50181: PoolManager redirect parameter ignored

## 🛡️ WAF Rule Categories

### **Category 1: Injection Protection (CRITICAL)**

#### **SQL/NoSQL Injection Rules**
```yaml
# AWS WAF Rule
- Name: "BlockSQLInjection"
  Priority: 100
  Statement:
    ByteMatchStatement:
      SearchString: "'; DROP TABLE"
      FieldToMatch:
        Body: {}
      TextTransformations:
        - Priority: 0
          Type: "URL_DECODE"
        - Priority: 1
          Type: "HTML_ENTITY_DECODE"
  Action:
    Block: {}
```

#### **Datalog Injection Rules** (Custom for ACGS-PGP)
```yaml
# Cloudflare WAF Rule
- Description: "Block Datalog injection attempts"
  Expression: |
    (http.request.body contains "'; drop_all_rules") or
    (http.request.body contains "allow('") and 
     (http.request.body contains "'; " or 
      http.request.body contains "and " or 
      http.request.body contains "or ")
  Action: "block"
```

#### **Command Injection Rules**
```yaml
# ModSecurity Rule
SecRule ARGS "@detectSQLi" \
    "id:1001,\
    phase:2,\
    block,\
    msg:'SQL Injection Attack Detected',\
    logdata:'Matched Data: %{MATCHED_VAR} found within %{MATCHED_VAR_NAME}',\
    tag:'application-multi',\
    tag:'language-multi',\
    tag:'platform-multi',\
    tag:'attack-sqli'"
```

### **Category 2: API Endpoint Protection (HIGH)**

#### **Export Endpoint Protection**
```yaml
# AWS WAF Rule for Export Endpoints
- Name: "ProtectExportEndpoints"
  Priority: 200
  Statement:
    AndStatement:
      Statements:
        - ByteMatchStatement:
            SearchString: "/export"
            FieldToMatch:
              UriPath: {}
        - NotStatement:
            Statement:
              ByteMatchStatement:
                SearchString: "admin-token"
                FieldToMatch:
                  SingleHeader:
                    Name: "authorization"
  Action:
    Block:
      CustomResponse:
        ResponseCode: 403
        CustomResponseBodyKey: "AdminRequired"
```

#### **Rate Limiting for Sensitive Endpoints**
```yaml
# Cloudflare Rate Limiting
- Description: "Rate limit audit and export endpoints"
  Expression: |
    (http.request.uri.path contains "/api/v1/audit") or
    (http.request.uri.path contains "/export")
  Action: "challenge"
  RateLimit:
    Threshold: 10
    Period: 60
```

### **Category 3: Authentication & Authorization (HIGH)**

#### **JWT Token Validation**
```yaml
# Custom WAF Rule for JWT Validation
- Name: "ValidateJWTTokens"
  Condition: |
    http.request.headers["authorization"] exists and
    not regex_match(http.request.headers["authorization"], "^Bearer [A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$")
  Action: "block"
  Response:
    Status: 401
    Body: "Invalid JWT token format"
```

#### **Admin Endpoint Protection**
```yaml
# Protect admin-only endpoints
- Name: "AdminEndpointProtection"
  Expression: |
    (http.request.uri.path contains "/admin") and
    not (http.request.headers["authorization"] contains "admin-token")
  Action: "block"
```

### **Category 4: OWASP Top 10 Protection (MEDIUM)**

#### **XSS Protection**
```yaml
# AWS WAF XSS Rule Set
- Name: "AWSManagedRulesCommonRuleSet"
  Priority: 300
  Statement:
    ManagedRuleGroupStatement:
      VendorName: "AWS"
      Name: "AWSManagedRulesCommonRuleSet"
      ExcludedRules: []
```

#### **File Upload Protection**
```yaml
# Block dangerous file uploads
- Name: "BlockDangerousUploads"
  Expression: |
    (http.request.method eq "POST") and
    (http.request.headers["content-type"] contains "multipart/form-data") and
    (http.request.body contains ".exe" or 
     http.request.body contains ".bat" or 
     http.request.body contains ".sh")
  Action: "block"
```

## 🚀 Implementation Guide

### **Phase 1: Immediate Deployment (Week 1)**
1. **Deploy injection protection rules** (Category 1)
2. **Implement API endpoint protection** (Category 2)
3. **Configure basic monitoring**

### **Phase 2: Enhanced Protection (Week 2)**
1. **Add authentication validation** (Category 3)
2. **Deploy OWASP Top 10 rules** (Category 4)
3. **Configure advanced monitoring**

### **Phase 3: Optimization (Week 3-4)**
1. **Fine-tune rules based on false positives**
2. **Add custom rules for application-specific threats**
3. **Implement automated rule updates**

## 📊 Testing & Validation

### **Penetration Testing Scripts**
```bash
#!/bin/bash
# Test injection protection
curl -X POST "https://api.acgs-pgp.com/api/v1/policy/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "admin'\'''; drop_all_rules; allow('\''admin"}'

# Test export endpoint protection
curl -X POST "https://api.acgs-pgp.com/api/v1/audit/export" \
  -H "Authorization: Bearer invalid-token"

# Test rate limiting
for i in {1..20}; do
  curl "https://api.acgs-pgp.com/api/v1/audit/events"
done
```

### **Expected WAF Responses**
- **Injection attempts**: `403 Forbidden` with WAF block message
- **Unauthorized export**: `403 Forbidden` with admin required message
- **Rate limit exceeded**: `429 Too Many Requests`

## 🔍 Monitoring & Alerting

### **Key Metrics to Monitor**
- **Blocked requests per hour** (target: < 100 legitimate blocks)
- **False positive rate** (target: < 1%)
- **Response time impact** (target: < 50ms additional latency)
- **Attack pattern trends** (weekly analysis)

### **Alert Thresholds**
```yaml
# High Priority Alerts
- Name: "High Volume Attack"
  Condition: "blocked_requests > 1000 in 5 minutes"
  Action: "immediate_notification"

- Name: "New Attack Pattern"
  Condition: "unique_attack_signatures > 10 in 1 hour"
  Action: "security_team_notification"

# Medium Priority Alerts  
- Name: "False Positive Spike"
  Condition: "legitimate_blocks > 50 in 1 hour"
  Action: "review_rules"
```

## 🔄 Maintenance Guidelines

### **Weekly Tasks**
- Review blocked request logs
- Analyze false positive reports
- Update attack signature database
- Performance impact assessment

### **Monthly Tasks**
- Comprehensive rule effectiveness review
- Update rules based on new threat intelligence
- Penetration testing validation
- Documentation updates

### **Quarterly Tasks**
- Full WAF configuration audit
- Threat landscape analysis
- Rule optimization based on traffic patterns
- Security team training updates

## 📋 Implementation Checklist

- [ ] **Deploy injection protection rules**
- [ ] **Configure API endpoint protection**
- [ ] **Set up monitoring dashboards**
- [ ] **Create alert notifications**
- [ ] **Document rule exceptions**
- [ ] **Train security team on WAF management**
- [ ] **Schedule regular penetration testing**
- [ ] **Establish rule update procedures**

## 🔗 Related Files

- **WAF Rules Configuration**: `config/security/waf-rules.json` (see below)
- **Testing Scripts**: `scripts/security/test_waf_rules.sh`
- **Monitoring Dashboard**: `config/monitoring/waf-dashboard.json`
- **Documentation**: This file

---

**Security Review**: ✅ APPROVED
**Implementation Priority**: HIGH
**Estimated Deployment Time**: 2-3 weeks

*These WAF recommendations provide comprehensive protection against the specific vulnerabilities discovered in Sprint 0 and common web application threats.*
