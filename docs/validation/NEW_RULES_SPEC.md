# New Validation Rules Specification

## Overview

This document outlines the specifications for new validation rules related to link/regex patterns, service-port reconciliation, and constitutional hash checks.

## Rules

### 1. Link/Regex Patterns

- **Pattern:** `import ... from './path'`
  - Enforce consistent use of relative paths in import statements across all `.ts`, `.js` files.

- **Pattern:** Image tags in `values.yaml`
  - Ensure image tags are correctly defined in `values.yaml` files.
  
- **Pattern:** Helm chart `service.port`
  - Validate service ports are explicitly defined within Helm charts.

### 2. Service-Port Reconciliation

- **Description:** 
  - Check consistency of service port numbers across code constants, Docker Compose files, and Kubernetes YAML configurations.

### 3. Constitutional Hash Check

- **Files:** `.py`, `.ts`, `.js`, `.yaml`, `.yml`, `.toml`, `.json`, `.md`
  - Perform a constitutional hash check using `cdd01ef066bc6cf2` for all text-like files ensuring compliance.

## Implementation
Each rule must be integrated into the existing validation framework, allowing automated checks during the development lifecycle.

# New Validation Rules Specification

## Overview

This document outlines the specifications for new validation rules related to link/regex patterns, service-port reconciliation, and constitutional hash checks.

## Rules

### 1. Link/Regex Patterns

- **Pattern:** `import ... from './path'`
  - Validate that all import statements follow this pattern.
  
- **Pattern:** `values.yaml` image tags
  - Ensure all image tags in `values.yaml` are specified correctly.
  
- **Pattern:** Helm chart `service.port`
  - Validate that service ports in Helm charts are correctly specified.
  

### 2. Service-Port Reconciliation

- **Description:**
  - Ensure consistency between service ports in code constants, Docker compose files, and Kubernetes YAML files.
  - Validate that the port numbers are consistently defined across these files.


### 3. Constitutional Hash Check

- **Files:** `.py`, `.ts`, `.js`, `.yaml`, `.yml`, `.toml`, `.json`, `.md`
  - Compute and verify the constitutional hash for all text-like files.
  - Use the hash `cdd01ef066bc6cf2` for verification to ensure constitutional compliance.

## Implementation
Each rule must be integrated into the existing validation framework, ensuring automated checks during the development lifecycle.


