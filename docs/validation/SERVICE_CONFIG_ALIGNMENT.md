# Service Configuration Alignment Guide

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

The Service Configuration Alignment Validator ensures consistency and reliability of service configurations across various environments and deployment models. This comprehensive validation framework cross-references Docker Compose files, Kubernetes manifests, service configuration files, and Python code constants to identify misalignments that could cause deployment issues.

**Performance Targets:**
- P99 Latency: ≤5ms for validation operations
- Throughput: ≥100 RPS for validation requests  
- Cache Hit Rate: ≥85% for configuration data
- Constitutional Compliance: 100%

## Capabilities

### Core Validation Features

- **Multi-Source Port Validation**: Cross-checks ports across Docker Compose files, Kubernetes manifests, service configs, and Python code constants
- **Image Tag Consistency**: Validates uniformity of image tags between different configuration sources
- **Environment Variable Alignment**: Ensures environment variables are consistently defined across services
- **API Documentation URL Patterns**: Verifies that FastAPI docs_url follows standard patterns (/docs, /api, /swagger)
- **Constitutional Compliance**: Validates presence of required constitutional hash `cdd01ef066bc6cf2` in all configuration files

### Configuration Sources Analyzed

1. **Docker Compose Files**: `**/docker-compose*.yml`, `**/docker-compose*.yaml`
2. **Kubernetes Manifests**: `**/*.k8s.yml`, `**/k8s/**/*.yml`, `**/kubernetes/**/*.yml`
3. **Service Configuration Files**: `**/config/*.yml`, `**/config/*.yaml`
4. **Python Code Files**: `**/services/**/*.py`, `**/apps/**/*.py`, `**/src/**/*.py`

### Advanced Pattern Detection

- **FastAPI Configuration**: Extracts `app = FastAPI(docs_url=...)` and `uvicorn.run(port=...)` patterns
- **Port Constants**: Detects `*PORT*` variables, `port = number` assignments, and dictionary port definitions
- **Image References**: Identifies image names in various configuration contexts
- **Environment Variables**: Comprehensive extraction from all configuration sources

## How to Run

Run the Service Configuration Alignment Validator using the following command:

```bash
python tools/validation/service_config_alignment_validator.py [--repo-root PATH] [--output REPORT] [--json]
```

- `--repo-root PATH`: Specify the repository root path if different from the current directory.
- `--output REPORT`: Specify the output report file path.
- `--json`: Get the output in JSON format.

## Validation Results and Reporting

### Success Metrics

```
📊 Service Configuration Alignment Summary:
  Total Checks: 5
  Passed: 4
  Failed: 1
  Success Rate: 80.0%
  Duration: 1.23s
  Performance Score: 89.2/100
```

### Issue Severity Levels

- **CRITICAL**: Constitutional compliance failures, security issues
- **ERROR**: Configuration parsing failures, broken references
- **HIGH**: Port conflicts, major inconsistencies
- **MEDIUM**: Minor inconsistencies, image tag mismatches
- **LOW**: Documentation pattern violations, style issues

## Common Validation Findings and Fixes

### 1. Port Conflicts (HIGH Severity)

**Symptom**: Multiple services configured to use the same port

**Example Finding**:
```json
{
  "severity": "HIGH",
  "category": "port_conflict",
  "component": "registry vs constitutional_core",
  "message": "Port conflict detected: [8001]",
  "details": {
    "conflict_details": {
      "services": ["registry", "constitutional_core"],
      "conflicting_ports": [8001]
    }
  }
}
```

**Root Causes**:
- Copy-paste errors in Docker Compose files
- Hardcoded port numbers in multiple services
- Inconsistent port mapping between external and internal ports

**Fixes**:

1. **Update Docker Compose configuration**:
   ```yaml
   # Before (problematic)
   services:
     service1:
       ports:
         - "8001:8001"
     service2:
       ports:
         - "8001:8001"  # CONFLICT!
   
   # After (fixed)
   services:
     service1:
       ports:
         - "8001:8001"
     service2:
       ports:
         - "8002:8001"  # Unique external port
   ```

2. **Update Kubernetes Service manifests**:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: service2
   spec:
     ports:
     - port: 8002  # Changed from 8001
       targetPort: 8001
   ```

3. **Update service configuration**:
   ```yaml
   # config/service2.yml
   server:
     port: 8002  # Update to match Docker/K8s config
   ```

4. **Verify with validation**:
   ```bash
   python tools/validation/service_config_alignment_validator.py --json
   ```

### 2. Image Tag Inconsistencies (MEDIUM Severity)

**Symptom**: Same service using different image tags across configurations

**Example Finding**:
```json
{
  "severity": "MEDIUM",
  "category": "image_tag_inconsistency",
  "component": "constitutional-ai",
  "message": "Multiple image tags found: ['acgs/constitutional-ai:latest', 'acgs/constitutional-ai:v1.0.0']",
  "details": {
    "inconsistency_details": {
      "service": "constitutional-ai",
      "image_tags": ["acgs/constitutional-ai:latest", "acgs/constitutional-ai:v1.0.0"],
      "sources": ["docker-compose.yml", "k8s/constitutional-ai.yaml"]
    }
  }
}
```

**Fixes**:

1. **Standardize image tags across all configurations**:
   ```bash
   # Find all occurrences
   grep -r "acgs/constitutional-ai" .
   
   # Update to consistent version
   sed -i 's/acgs\/constitutional-ai:latest/acgs\/constitutional-ai:v1.0.0/g' docker-compose.yml
   sed -i 's/acgs\/constitutional-ai:latest/acgs\/constitutional-ai:v1.0.0/g' k8s/*.yaml
   ```

2. **Use environment variables for version management**:
   ```yaml
   # docker-compose.yml
   services:
     constitutional-ai:
       image: acgs/constitutional-ai:${CONSTITUTIONAL_AI_VERSION:-v1.0.0}
   ```

3. **Update config/environments/development.env file**:
   ```bash
   echo "CONSTITUTIONAL_AI_VERSION=v1.0.0" >> config/environments/development.env
   ```

### 3. Environment Variable Discrepancies (MEDIUM Severity)

**Symptom**: Common environment variables with different values across services

**Example Finding**:
```json
{
  "severity": "MEDIUM",
  "category": "environment_inconsistency",
  "component": "Environment variable: DEBUG",
  "message": "Inconsistent values across services",
  "details": {
    "inconsistency_details": {
      "variable_pattern": "DEBUG",
      "services": {
        "service1": [{"key": "DEBUG", "value": "true"}],
        "service2": [{"key": "DEBUG", "value": "false"}]
      }
    }
  }
}
```

**Fixes**:

1. **Standardize environment variables**:
   ```yaml
   # docker-compose.yml
   x-common-env: &common-env
     DEBUG: "false"
     LOG_LEVEL: "info"
     CONSTITUTIONAL_HASH: "cdd01ef066bc6cf2"
   
   services:
     service1:
       environment:
         <<: *common-env
         SERVICE_NAME: "service1"
     
     service2:
       environment:
         <<: *common-env
         SERVICE_NAME: "service2"
   ```

2. **Use shared environment file**:
   ```bash
   # Create sharedconfig/environments/development.env
   cat > sharedconfig/environments/development.env << EOF
   DEBUG=false
   LOG_LEVEL=info
   CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
   EOF
   
   # Reference in docker-compose.yml
   services:
     service1:
       env_file:
         - sharedconfig/environments/development.env
   ```

### 4. Missing Constitutional Hash (CRITICAL Severity)

**Symptom**: Configuration files missing required constitutional hash `cdd01ef066bc6cf2`

**Example Finding**:
```json
{
  "severity": "CRITICAL",
  "category": "constitutional_compliance",
  "component": "Configuration files",
  "message": "Missing constitutional hash in 3 files",
  "details": {
    "missing_hash_files": [
      "docker-compose.yml",
      "k8s/service.yaml",
      "config/app.yml"
    ]
  }
}
```

**Fixes**:

1. **Add constitutional hash to YAML files**:
   ```bash
   # For YAML files
   for file in docker-compose.yml k8s/*.yaml config/*.yml; do
     if [ -f "$file" ]; then
       sed -i '1i# Constitutional Hash: cdd01ef066bc6cf2' "$file"
     fi
   done
   ```

2. **Add constitutional hash to Python files**:
   ```bash
   # For Python files
   for file in services/**/*.py; do
     if [ -f "$file" ] && ! grep -q "cdd01ef066bc6cf2" "$file"; then
       sed -i '1i# Constitutional Hash: cdd01ef066bc6cf2' "$file"
     fi
   done
   ```

3. **Add constitutional hash to Markdown files**:
   ```bash
   # For Markdown files
   for file in docs/**/*.md; do
     if [ -f "$file" ] && ! grep -q "cdd01ef066bc6cf2" "$file"; then
       sed -i '1i<!-- Constitutional Hash: cdd01ef066bc6cf2 -->' "$file"
     fi
   done
   ```

4. **Verify compliance**:
   ```bash
   python tools/validation/service_config_alignment_validator.py
   ./tools/validation/quick_validation.sh
   ```

### 5. Documentation URL Pattern Issues (LOW Severity)

**Symptom**: FastAPI docs URLs not following standard patterns

**Example Finding**:
```json
{
  "severity": "LOW",
  "category": "docs_url_pattern",
  "component": "custom-service",
  "message": "Unusual docs URL pattern: /documentation",
  "details": {
    "pattern_details": {
      "service": "custom-service",
      "docs_url": "/documentation"
    }
  }
}
```

**Fixes**:

1. **Update FastAPI app configuration**:
   ```python
   # Before
   app = FastAPI(docs_url="/documentation")
   
   # After (standard pattern)
   app = FastAPI(docs_url="/docs")
   ```

2. **Alternative standard patterns**:
   ```python
   # Other acceptable patterns
   app = FastAPI(docs_url="/api/docs")
   app = FastAPI(docs_url="/swagger")
   ```

## Adding New Rules with PATTERN_REGISTRY

### Understanding the Pattern Registry

The PATTERN_REGISTRY system allows you to extend validation capabilities by defining custom patterns in `tools/validation/cross_reference_patterns.yaml`. This YAML-based configuration supports multiple pattern categories and confidence scoring.

### Pattern Registry Structure

```yaml
# Constitutional Hash: cdd01ef066bc6cf2
version: "1.0"
constitutional_hash: "cdd01ef066bc6cf2"

categories:
  your_category:
    description: "Custom validation category"
    base_confidence: 0.8

patterns:
  - name: "custom_rule_name"
    category: "your_category"
    regex: "your_regex_pattern"
    capture_groups:
      text: 1
      url: 2
    reference_type: "custom"
    confidence_modifiers:
      descriptive_text: 0.2
      generic_text: -0.3
    exclusions:
      - "^https?://"
      - "^mailto:"
```

### Steps to Add Custom Validation Rules

#### 1. Define Pattern Category

First, add a new category if it doesn't exist:

```yaml
categories:
  service_endpoints:
    description: "Service endpoint validation patterns"
    base_confidence: 0.9
```

#### 2. Create Validation Pattern

Add your custom pattern to the patterns section:

```yaml
patterns:
  - name: "service_health_endpoint"
    category: "service_endpoints"
    regex: "(?:health|healthz|ready|readiness)\\s*=\\s*[\"']([^\"']+)[\"']"
    capture_groups:
      endpoint: 1
    reference_type: "health_endpoint"
    confidence_modifiers:
      standard_names: 0.2  # /health, /healthz, /ready
      custom_names: -0.1   # non-standard endpoint names
    exclusions:
      - "^#"  # commented lines
```

#### 3. Test New Pattern

Test your pattern before deploying:

```bash
# Test pattern matching
echo "health = '/api/v1/health'" | grep -E "(?:health|healthz|ready|readiness)\\s*=\\s*[\"']([^\"']+)[\"']"

# Run validator with debug output
python tools/validation/advanced_cross_reference_analyzer.py --debug --pattern "service_health_endpoint"
```

#### 4. Validate Pattern Integration

Run the full validation suite:

```bash
# Run service config alignment
python tools/validation/service_config_alignment_validator.py --output reports/config_alignment.md

# Run cross-reference analysis
python tools/validation/advanced_cross_reference_analyzer.py --output-dir reports/

# Quick validation check
./tools/validation/quick_validation.sh
```

### Advanced Pattern Examples

#### Service Port Detection

```yaml
- name: "service_port_mapping"
  category: "configuration_references"
  regex: "(?:targetPort|containerPort|port)\\s*:\\s*(\\d+)"
  capture_groups:
    port: 1
  reference_type: "port_mapping"
  confidence_modifiers:
    kubernetes_context: 0.2
    docker_context: 0.1
```

#### Database Connection Strings

```yaml
- name: "database_connection"
  category: "configuration_references"
  regex: "(?:DATABASE_URL|DB_URL|db_url)\\s*[=:]\\s*[\"']([^\"']+)[\"']"
  capture_groups:
    connection_string: 1
  reference_type: "database_config"
  confidence_modifiers:
    postgres_protocol: 0.2
    localhost_connection: -0.1
  exclusions:
    - "password"
    - "secret"
```

#### Custom Configuration Validation

```yaml
- name: "feature_flag_definition"
  category: "configuration_references"
  regex: "(?:feature_flags?|features?)\\s*[=:]\\s*\\{([^}]+)\\}"
  capture_groups:
    feature_config: 1
  reference_type: "feature_flag"
  confidence_modifiers:
    boolean_values: 0.1
    string_values: -0.1
```

### Confidence Scoring Configuration

Customize confidence scoring for your patterns:

```yaml
confidence_scoring:
  base_confidence: 1.0
  max_confidence: 1.0
  min_confidence: 0.1
  
  context_modifiers:
    yaml_context:
      pattern: ".*\\.ya?ml$"
      modifier: 0.2
    
    production_context:
      pattern: "(?:prod|production)"
      modifier: 0.3
    
    test_context:
      pattern: "(?:test|spec|mock)"
      modifier: -0.2
```

### Performance Optimization

Optimize pattern performance:

```yaml
performance:
  parallel_processing: true
  max_workers: 4
  cache_compiled_patterns: true
  batch_size: 100
  timeout_seconds: 30
```

### Error Handling

Configure error handling for robust validation:

```yaml
error_handling:
  skip_binary_files: true
  handle_encoding_errors: true
  continue_on_pattern_errors: true
  log_pattern_failures: true
  
  fallback_patterns:
    basic_config_reference: "[a-zA-Z_][a-zA-Z0-9_]*\\s*[=:]\\s*.+"
```

### Validation and Testing

#### Pattern Validation Checklist

- [ ] Pattern compiles without regex errors
- [ ] Capture groups are correctly numbered
- [ ] Exclusions prevent false positives
- [ ] Confidence modifiers make sense
- [ ] Pattern doesn't conflict with existing patterns
- [ ] Performance impact is acceptable

#### Integration Testing

```bash
# Test with sample files
echo "Sample config content" > test_config.yml
python tools/validation/service_config_alignment_validator.py --repo-root . --output test_report.md

# Verify pattern detection
grep -n "custom_rule_name" test_report.md

# Check performance
time python tools/validation/service_config_alignment_validator.py > /dev/null
```

### Troubleshooting Pattern Issues

#### Common Problems

1. **Pattern doesn't match**: Use regex testing tools to validate your pattern
2. **Too many false positives**: Add exclusions or refine the regex
3. **Performance issues**: Optimize regex or add early filtering
4. **Confidence scoring issues**: Adjust base confidence and modifiers

#### Debug Commands

```bash
# Test regex pattern
python -c "import re; print(re.findall(r'your_pattern', 'test_string'))"

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('tools/validation/cross_reference_patterns.yaml'))"

# Check pattern compilation
python tools/validation/advanced_cross_reference_analyzer.py --validate-patterns
```

## Best Practices

### Configuration Management

1. **Use consistent naming conventions** across all configuration files
2. **Centralize common configurations** using YAML anchors or environment files
3. **Version your configurations** alongside your application code
4. **Document configuration changes** in your commit messages
5. **Test configuration changes** in staging before production

### Validation Integration

1. **Run validation in CI/CD pipelines** to catch issues early
2. **Set up automated alerts** for configuration drift
3. **Regular scheduled validation** (daily/weekly) for large projects
4. **Include validation in code review process**
5. **Maintain up-to-date pattern registry** as your system evolves

### Performance Optimization

1. **Cache validation results** for frequently accessed configurations
2. **Use incremental validation** for large repositories
3. **Optimize regex patterns** for better performance
4. **Monitor validation execution time** and set reasonable timeouts

## Related Tools and Integration

### ACGS Validation Ecosystem

- **Quick Validation**: `./tools/validation/quick_validation.sh` - Fast constitutional compliance checks
- **Cross-Reference Analysis**: `advanced_cross_reference_analyzer.py` - Link validation and relationship analysis
- **Constitutional Compliance**: Built-in hash validation across all tools
- **Performance Monitoring**: Real-time validation metrics and alerting

### CI/CD Integration

```bash
# Add to your CI pipeline
#!/bin/bash
set -e

# Run validation
python tools/validation/service_config_alignment_validator.py --json > validation_results.json

# Check for critical issues
if grep -q '"severity": "CRITICAL"' validation_results.json; then
  echo "Critical configuration issues found!"
  exit 1
fi

# Generate report
python tools/validation/service_config_alignment_validator.py --output deployment_validation_report.md
```

### Monitoring and Alerting

```bash
# Set up monitoring
crontab -e
# Add: 0 2 * * * /path/to/tools/validation/quick_validation.sh

# Alert on failures
if [ $? -ne 0 ]; then
  echo "Configuration validation failed" | mail -s "ACGS Validation Alert" devops@company.com
fi
```


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

---

**Constitutional Hash**: `cdd01ef066bc6cf2` ✅

For additional information, see:
- [ACGS Validation Tools Cheat Sheet](../training/validation_tools_cheatsheet.md)
- [ACGS Documentation Index](../ACGS_docs/DOCUMENTATION_INDEX.md)
