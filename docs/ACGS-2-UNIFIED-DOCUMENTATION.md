# ACGS-2 Unified Documentation
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This unified documentation consolidates 1141 CLAUDE.md files from across the ACGS-2 system into a single-source documentation system with automated generation and cross-reference validation.

**Generated**: 2025-07-18T16:02:35.639020  
**Constitutional Hash**: cdd01ef066bc6cf2  
**Constitutional Compliance**: 100.0%

## Documentation Structure

### By Service Type
- **Unknown**: 691 files
- **Configuration**: 36 files
- **Infrastructure**: 175 files
- **Core**: 151 files
- **Platform**: 88 files

### By Priority
- **Unknown**: 1086 files
- **Critical**: 8 files
- **Low**: 41 files
- **High**: 4 files
- **Medium**: 2 files

### By Implementation Status
- **In Progress**: 660 files
- **Implemented**: 477 files
- **Planned**: 4 files

## Documentation Categories

### Deployments

**Files**: 2


### .Hypothesis

**Files**: 4


### Web

**Files**: 2


### .Cursor

**Files**: 1


### Services

**Files**: 451

#### Core Services

- **services/core** ✅ ⚪ ✅
  - Sections: ACGS-2 Core Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__pycache__/`** - ACGS-2 __pycache__ component, **`a2a-policy-integration/`** - ACGS-2 a2a-policy-integration component, **`agent-hitl/`** - ACGS-2 agent-hitl component
- **services/core/multi_agent_coordinator** ✅ ⚪ ✅
  - Sections: ACGS-2 Multi_Agent_Coordinator Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__pycache__/`** - ACGS-2 __pycache__ component, **`app/`** - ACGS-2 app component, Constitutional AI validation service
- **services/core/audit-service** ✅ ⚪ ✅
  - Sections: ACGS-2 Audit-Service Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/core/consensus-engine** ✅ ⚪ ✅
  - Sections: ACGS-2 Consensus-Engine Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`service, **`requirements.txt`** - ACGS-2 component, Constitutional AI validation service
- **services/core/auth-service** ✅ ⚪ ✅
  - Sections: ACGS-2 Auth-Service Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/core/evolutionary-computation** ✅ ⚪ ✅
  - Sections: ACGS-2 Evolutionary-Computation Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, **`__pycache__/`** - ACGS-2 __pycache__ component, **`app/`** - ACGS-2 app component
- **services/core/seal-adaptation** 🔄 ⚪ ✅
  - Sections: ACGS-2 Seal-Adaptation Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`seal_service/`** - ACGS-2 seal_service component, Constitutional AI validation service, Cross-service
- **services/core/policy-governance** ✅ ⚪ ✅
  - Sections: ACGS-2 Policy-Governance Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__pycache__/`** - ACGS-2 __pycache__ component, **`app/`** - ACGS-2 app component, **`chaos-testing/`** - ACGS-2 chaos-testing component
- **services/core/security-validation** ✅ ⚪ ✅
  - Sections: ACGS-2 Security-Validation Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/core/a2a-policy-integration** ✅ ⚪ ✅
  - Sections: ACGS-2 A2A-Policy-Integration Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, Constitutional AI validation service, Cross-service
  - ... and 133 more files

#### Platform Services

- **services/platform_services** ✅ ⚪ ✅
  - Sections: ACGS-2 Platform_Services Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__pycache__/`** - ACGS-2 __pycache__ component, **`adaptive-learning/`** - ACGS-2 adaptive-learning component, **`api_gateway/`** - ACGS-2 api_gateway component
- **services/platform_services/blackboard** ✅ ⚪ ✅
  - Sections: ACGS-2 Blackboard Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../services/CLAUDE.md)** - Core service
- **services/platform_services/api_gateway** 🔄 ⚪ ✅
  - Sections: ACGS-2 Api_Gateway Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`AUTHENTICATION_CONSOLIDATION.md.backup`** - ACGS-2 component, **`gateway_service/`** - ACGS-2 gateway_service component, **`gateway_service_standardized/`** - ACGS-2 gateway_service_standardized component
- **services/platform_services/integrity** ✅ ⚪ ✅
  - Sections: ACGS-2 Integrity Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`app/`** - ACGS-2 app component, **`integrity_service/`** - ACGS-2 integrity_service component, **`integrity_service_standardized/`** - ACGS-2 integrity_service_standardized component
- **services/platform_services/adaptive-learning** 🔄 ⚪ ✅
  - Sections: ACGS-2 Adaptive-Learning Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, **`app/`** - ACGS-2 app component, **`config/`** - ACGS-2 config component
- **services/platform_services/image-compliance** 🔄 ⚪ ✅
  - Sections: ACGS-2 Image-Compliance Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`Dockerfile`** - ACGS-2 component, **`requirements.txt`** - ACGS-2 component, **`app/`** - ACGS-2 app component
- **services/platform_services/coordinator** ✅ ⚪ ✅
  - Sections: ACGS-2 Coordinator Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../services/CLAUDE.md)** - Core service
- **services/platform_services/authentication** 🔄 ⚪ ✅
  - Sections: ACGS-2 Authentication Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`app/`** - ACGS-2 app component, **`auth_service/`** - ACGS-2 auth_service component, **`auth_service_standardized/`** - ACGS-2 auth_service_standardized component
- **services/platform_services/formal_verification** ✅ ⚪ ✅
  - Sections: ACGS-2 Formal_Verification Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`requirements.txt`** - ACGS-2 component, **`service, **`__pycache__/`** - ACGS-2 __pycache__ component
- **services/platform_services/audit_aggregator** ✅ ⚪ ✅
  - Sections: ACGS-2 Audit_Aggregator Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`Dockerfile`** - ACGS-2 component, **`requirements.txt`** - ACGS-2 component, Constitutional AI validation service
  - ... and 73 more files

#### Configuration Services

- **services/cli/opencode/src/config** ✅ ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`hooks.ts`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/cli/tui/sdk/internal/requestconfig** 🔄 ⚪ ✅
  - Sections: ACGS-2 Requestconfig Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../../../../services/CLAUDE.md)** - Core service
- **services/cli/tui/internal/config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../../../services/CLAUDE.md)** - Core service
- **services/blockchain/config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`deployment/`** - ACGS-2 deployment component, **`docker/`** - ACGS-2 docker component, **`environment/`** - ACGS-2 environment component
- **services/blockchain/artifacts/configuration** 🔄 ⚪ ✅
  - Sections: ACGS-2 Configuration Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`FINAL_REMEDIATION_REPORT.json`** - ACGS-2 component, **`blockchain_improvement_report.json`** - ACGS-2 component, **`constitution_data.json`** - ACGS-2 component
- **services/blockchain/expert-service/config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`Dockerfile`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/blockchain/config/docker** 🔄 ⚪ ✅
  - Sections: ACGS-2 Docker Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../../services/CLAUDE.md)** - Core service
- **services/blockchain/config/deployment** 🔄 ⚪ ✅
  - Sections: ACGS-2 Deployment Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../../services/CLAUDE.md)** - Core service
- **services/shared/configuration** ✅ ⚪ ✅
  - Sections: ACGS-2 Configuration Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../services/CLAUDE.md)** - Core service
- **services/shared/config** ✅ ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`ac_service_cache_optimization.json`** - ACGS-2 component, **`auth_service_cache_optimization.json`** - ACGS-2 component, **`blackboard_cache_optimization.json`** - ACGS-2 component

#### Infrastructure Services

- **services/contexts/constitutional_governance/infrastructure** ✅ ⚪ ✅
  - Sections: ACGS-2 Infrastructure Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`external_service, Constitutional AI validation service, Cross-service
- **services/blockchain/infrastructure** 🔄 ⚪ ✅
  - Sections: ACGS-2 Infrastructure Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`cache/`** - ACGS-2 cache component, **`connection_pool/`** - ACGS-2 connection_pool component, **`cost_optimization/`** - ACGS-2 cost_optimization component
- **services/blockchain/infrastructure/cost_optimization** ✅ ⚪ ✅
  - Sections: ACGS-2 Cost_Optimization Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`compute_optimizer.rs`** - ACGS-2 component, **`cost_analyzer.rs`** - ACGS-2 component, **`storage_optimizer.rs`** - ACGS-2 component
- **services/blockchain/infrastructure/security** 🔄 ⚪ ✅
  - Sections: ACGS-2 Security Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`formal_verification/`** - ACGS-2 formal_verification component, Constitutional AI validation service, Cross-service
- **services/blockchain/infrastructure/governance** ✅ ⚪ ✅
  - Sections: ACGS-2 Governance Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`advanced_features.rs`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/blockchain/infrastructure/cross_chain** ✅ ⚪ ✅
  - Sections: ACGS-2 Cross_Chain Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`interoperability.rs`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **services/blockchain/infrastructure/cache** ✅ ⚪ ✅
  - Sections: ACGS-2 Cache Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`cache_compression.rs`** - ACGS-2 component, **`intelligent_cache_warmer.rs`** - ACGS-2 component, **`mod.rs`** - ACGS-2 component
- **services/blockchain/infrastructure/monitoring** ✅ ⚪ ✅
  - Sections: ACGS-2 Monitoring Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`lib.rs`** - ACGS-2 component, **`observability.rs`** - ACGS-2 component, **`Cargo.toml`** - ACGS-2 component
- **services/blockchain/infrastructure/connection_pool** ✅ ⚪ ✅
  - Sections: ACGS-2 Connection_Pool Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`dynamic_sizing.rs`** - ACGS-2 component, **`mod.rs`** - ACGS-2 component, **`unified_connection_pool.rs`** - ACGS-2 component
- **services/blockchain/infrastructure/security/formal_verification** ✅ ⚪ ✅
  - Sections: ACGS-2 Formal_Verification Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`governance_proofs.rs`** - ACGS-2 component, Constitutional AI validation service, Cross-service
  - ... and 1 more files


### Docs

**Files**: 38

#### Configuration Services

- **docs/configuration** 🔄 ⚪ ✅
  - Sections: ACGS-2 Configuration Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`groqcloud-integration.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service


### Pipeline_Results

**Files**: 1


### .Ruff_Cache

**Files**: 2


### Generated_Tests

**Files**: 1


### Security

**Files**: 1


### Validation_Reports

**Files**: 1


### .Roo

**Files**: 9

#### Core Services

- **.roo/engine/core** ✅ ⚪ ✅
  - Sections: ACGS-2 Core Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../services/CLAUDE.md)** - Core service


### Demo_Training_Data

**Files**: 1


### Claude-Code-Hooks-Mastery

**Files**: 10


### Release

**Files**: 3


### .Mypy_Cache

**Files**: 124

#### Configuration Services

- **.mypy_cache/3.10/iniconfig** 🔄 ⚪ ✅
  - Sections: ACGS-2 Iniconfig Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__init__.data.json`** - ACGS-2 component, **`__init__.meta.json`** - ACGS-2 component, **`_parse.data.json`** - ACGS-2 component
- **.mypy_cache/3.10/_pytest/config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__init__.data.json`** - ACGS-2 component, **`__init__.meta.json`** - ACGS-2 component, **`argparsing.data.json`** - ACGS-2 component

#### Platform Services

- **.mypy_cache/3.10/platformdirs** 🔄 ⚪ ✅
  - Sections: ACGS-2 Platformdirs Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__init__.data.json`** - ACGS-2 component, **`__init__.meta.json`** - ACGS-2 component, **`api.data.json`** - ACGS-2 component

#### Core Services

- **.mypy_cache/3.10/app/core** 🔄 ⚪ ✅
  - Sections: ACGS-2 Core Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__init__.meta.json.backup`** - ACGS-2 component, **`__init__.data.json`** - ACGS-2 component, **`__init__.meta.json`** - ACGS-2 component
- **.mypy_cache/3.10/numpy/_core** 🔄 ⚪ ✅
  - Sections: ACGS-2 _Core Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`__init__.data.json`** - ACGS-2 component, **`__init__.meta.json`** - ACGS-2 component, **`_asarray.data.json`** - ACGS-2 component


### Training_Outputs

**Files**: 6


### Frontend

**Files**: 19

#### Configuration Services

- **frontend/src/config** ✅ ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`index.ts`** - ACGS-2 component, **`__tests__/`** - ACGS-2 __tests__ component, Constitutional AI validation service
- **frontend/src/config/__tests__** ✅ ⚪ ✅
  - Sections: ACGS-2 __Tests__ Directory Documentation, Directory Overview, File Inventory
  - Dependencies: Constitutional AI validation service, Cross-service, **[Services](../../../../services/CLAUDE.md)** - Core service


### Reorganization-Tools

**Files**: 4


### Config

**Files**: 19

#### Configuration Services

- **config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`.keep`** - ACGS-2 component, **`mapping_table.yml.backup`** - ACGS-2 component, **`nginx.production.conf`** - ACGS-2 component
- **config/services** 🔄 ⚪ ✅
  - Sections: ACGS-2 Services Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`api-gateway/`** - ACGS-2 api-gateway component, **`constitutional-ai/`** - ACGS-2 constitutional-ai component
- **config/security** 🔄 ⚪ ✅
  - Sections: ACGS-2 Security Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`.env.example`** - ACGS-2 component, **`production.yml.backup`** - ACGS-2 component, Constitutional AI validation service
- **config/docker** 🔄 ⚪ ✅
  - Sections: ACGS-2 Docker Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **config/opa** 🔄 ⚪ ✅
  - Sections: ACGS-2 Opa Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`policies/`** - ACGS-2 policies component, Constitutional AI validation service
- **config/validation** 🔄 🔵 ✅
  - Sections: ACGS-2 Validation Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **config/environments** 🔄 ⚪ ✅
  - Sections: ACGS-2 Environments Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`.env`** - ACGS-2 component, **`.env.development`** - ACGS-2 component, **`.env.template`** - ACGS-2 component
- **config/nginx** 🔄 ⚪ ✅
  - Sections: ACGS-2 Nginx Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`ssl/`** - ACGS-2 ssl component, Constitutional AI validation service
- **config/logging** ✅ ⚪ ✅
  - Sections: ACGS-2 Logging Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`fluent-bit-constitutional.conf`** - ACGS-2 component, Constitutional AI validation service
- **config/documentation** ✅ ⚪ ✅
  - Sections: ACGS-2 Documentation Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`constitutional_openapi.py.backup`** - ACGS-2 component, Constitutional AI validation service
  - ... and 9 more files


### Observability

**Files**: 2


### .Github

**Files**: 3


### Disaster-Recovery

**Files**: 4


### .Augment

**Files**: 2


### Backup_Duplicates_20250718_062051

**Files**: 3


### Prps

**Files**: 3


### Testing

**Files**: 2


### Tests

**Files**: 28


### Validation_Results

**Files**: 1


### Test_Reports

**Files**: 1


### Compose-Stacks

**Files**: 1


### Procedures

**Files**: 1


### Reports

**Files**: 12


### Infrastructure

**Files**: 173

#### Infrastructure Services

- **infrastructure** 🔄 🟡 ✅
  - Sections: ACGS-2 Infrastructure Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`composite-resource-definition.yaml.backup`** - ACGS-2 component, **`composition.yaml.backup`** - ACGS-2 component, **`file_structure_log.txt`** - ACGS-2 component
- **infrastructure/scaling** ✅ ⚪ ✅
  - Sections: ACGS-2 Scaling Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **infrastructure/messaging** ✅ ⚪ ✅
  - Sections: ACGS-2 Messaging Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **infrastructure/linkerd** 🔄 ⚪ ✅
  - Sections: ACGS-2 Linkerd Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **infrastructure/scripts** 🔄 ⚪ ✅
  - Sections: ACGS-2 Scripts Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`docker/`** - ACGS-2 docker component, Constitutional AI validation service
- **infrastructure/high_availability** ✅ 🟡 ✅
  - Sections: ACGS-2 High_Availability Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **infrastructure/alerting** 🔄 ⚪ ✅
  - Sections: ACGS-2 Alerting Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **infrastructure/phase3** 🔄 ⚪ ✅
  - Sections: ACGS-2 Phase3 Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`.env`** - ACGS-2 component, **`CLAUDE.md.backup`** - ACGS-2 component, **`phase3a-database-ha.yml.backup`** - ACGS-2 component
- **infrastructure/opa** 🔄 ⚪ ✅
  - Sections: ACGS-2 Opa Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service
- **infrastructure/gitops** 🔄 ⚪ ✅
  - Sections: ACGS-2 Gitops Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, **`applications/`** - ACGS-2 applications component, Constitutional AI validation service
  - ... and 154 more files

#### Core Services

- **infrastructure/docker/services/core** 🔄 ⚪ ✅
  - Sections: ACGS-2 Core Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`agent-hitl/`** - ACGS-2 agent-hitl component, **`constitutional-ai/`** - ACGS-2 constitutional-ai component, **`formal-verification/`** - ACGS-2 formal-verification component
- **infrastructure/docker/services/core/constitutional-ai** 🔄 ⚪ ✅
  - Sections: ACGS-2 Constitutional-Ai Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`ac_service/`** - ACGS-2 ac_service component, Constitutional AI validation service, Cross-service
- **infrastructure/docker/services/core/governance-synthesis** 🔄 ⚪ ✅
  - Sections: ACGS-2 Governance-Synthesis Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`gs_service/`** - ACGS-2 gs_service component, Constitutional AI validation service, Cross-service
- **infrastructure/docker/services/core/formal-verification** 🔄 ⚪ ✅
  - Sections: ACGS-2 Formal-Verification Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`fv_service/`** - ACGS-2 fv_service component, Constitutional AI validation service, Cross-service
- **infrastructure/docker/services/core/policy-governance** 🔄 ⚪ ✅
  - Sections: ACGS-2 Policy-Governance Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`pgc_service/`** - ACGS-2 pgc_service component, Constitutional AI validation service, Cross-service

#### Platform Services

- **infrastructure/docker/services/platform** 🔄 ⚪ ✅
  - Sections: ACGS-2 Platform Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`authentication/`** - ACGS-2 authentication component, **`integrity/`** - ACGS-2 integrity component, Constitutional AI validation service
- **infrastructure/docker/services/platform/authentication** 🔄 ⚪ ✅
  - Sections: ACGS-2 Authentication Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`auth_service/`** - ACGS-2 auth_service component, Constitutional AI validation service, Cross-service
- **infrastructure/docker/services/platform/integrity** 🔄 ⚪ ✅
  - Sections: ACGS-2 Integrity Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`integrity_service/`** - ACGS-2 integrity_service component, Constitutional AI validation service, Cross-service
- **infrastructure/terraform/modules/acgs-platform** 🔄 ⚪ ✅
  - Sections: ACGS-2 Acgs-Platform Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`main.tf`** - ACGS-2 component, Constitutional AI validation service, Cross-service


### Tools

**Files**: 62

#### Configuration Services

- **tools/config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`CLAUDE.md.backup`** - ACGS-2 component, Constitutional AI validation service, Cross-service


### .Claudedocs

**Files**: 2


### Monitoring

**Files**: 3


### Scripts

**Files**: 108

#### Configuration Services

- **scripts/development/config** 🔄 ⚪ ✅
  - Sections: ACGS-2 Config Directory Documentation, Directory Overview, File Inventory
  - Dependencies: **`authentication_hardening.json`** - ACGS-2 component, **`encryption_hardening.json`** - ACGS-2 component, **`input_validation.json`** - ACGS-2 component


### Test_Generated_Tests

**Files**: 1


### Performance

**Files**: 1


### Training_Data

**Files**: 1


### Deployment

**Files**: 8


### Examples

**Files**: 1


### .Claude

**Files**: 4


### Operations

**Files**: 2


### Demo_Trained_Models

**Files**: 7


### Database

**Files**: 5


## Constitutional Compliance

**Hash**: cdd01ef066bc6cf2  
**Compliance Rate**: 100.0%

### Compliance by Category
- **Deployments**: 100.0% (2/2)
- **.Hypothesis**: 100.0% (4/4)
- **Web**: 100.0% (2/2)
- **.Cursor**: 100.0% (1/1)
- **Services**: 100.0% (451/451)
- **Docs**: 100.0% (38/38)
- **Pipeline_Results**: 100.0% (1/1)
- **.Ruff_Cache**: 100.0% (2/2)
- **Generated_Tests**: 100.0% (1/1)
- **Security**: 100.0% (1/1)
- **Validation_Reports**: 100.0% (1/1)
- **.Roo**: 100.0% (9/9)
- **Demo_Training_Data**: 100.0% (1/1)
- **Claude-Code-Hooks-Mastery**: 100.0% (10/10)
- **Release**: 100.0% (3/3)
- **.Mypy_Cache**: 100.0% (124/124)
- **Training_Outputs**: 100.0% (6/6)
- **Frontend**: 100.0% (19/19)
- **Reorganization-Tools**: 100.0% (4/4)
- **Config**: 100.0% (19/19)
- **Observability**: 100.0% (2/2)
- **.Github**: 100.0% (3/3)
- **Disaster-Recovery**: 100.0% (4/4)
- **.Augment**: 100.0% (2/2)
- **Backup_Duplicates_20250718_062051**: 100.0% (3/3)
- **Prps**: 100.0% (3/3)
- **Testing**: 100.0% (2/2)
- **Tests**: 100.0% (28/28)
- **Validation_Results**: 100.0% (1/1)
- **Test_Reports**: 100.0% (1/1)
- **Compose-Stacks**: 100.0% (1/1)
- **Procedures**: 100.0% (1/1)
- **Reports**: 100.0% (12/12)
- **Infrastructure**: 100.0% (173/173)
- **Tools**: 100.0% (62/62)
- **.Claudedocs**: 100.0% (2/2)
- **Monitoring**: 100.0% (3/3)
- **Scripts**: 100.0% (108/108)
- **Test_Generated_Tests**: 100.0% (1/1)
- **Performance**: 100.0% (1/1)
- **Training_Data**: 100.0% (1/1)
- **Deployment**: 100.0% (8/8)
- **Examples**: 100.0% (1/1)
- **.Claude**: 100.0% (4/4)
- **Operations**: 100.0% (2/2)
- **Demo_Trained_Models**: 100.0% (7/7)
- **Database**: 100.0% (5/5)


## Simplification Recommendations

### High Priority Actions
1. **Constitutional Compliance**: Add constitutional hash to 0 non-compliant files
2. **Status Updates**: Update implementation status for 0 files with unknown status
3. **Priority Classification**: Classify priority for 1086 files with unknown priority

### Consolidation Opportunities
- **Services**: 451 files - Consider consolidating into domain-specific documentation
- **Docs**: 38 files - Consider consolidating into domain-specific documentation
- **.Mypy_Cache**: 124 files - Consider consolidating into domain-specific documentation
- **Tests**: 28 files - Consider consolidating into domain-specific documentation
- **Infrastructure**: 173 files - Consider consolidating into domain-specific documentation
- **Tools**: 62 files - Consider consolidating into domain-specific documentation
- **Scripts**: 108 files - Consider consolidating into domain-specific documentation


## Cross-Reference Validation

Total cross-references found: 5705

### Validation Status
- ✅ **Active Documentation**: 1141 files processed
- 🔄 **Cross-Reference Check**: Automated validation implemented
- ✅ **Constitutional Compliance**: 100.0% compliant

## Implementation Status

### Legend
- ✅ **Implemented**: Feature/component is complete and operational
- 🔄 **In Progress**: Feature/component is under active development
- ❌ **Planned**: Feature/component is planned for future implementation
- ❓ **Unknown**: Implementation status needs to be determined

### Priority Legend
- 🔴 **Critical**: Essential for system operation
- 🟡 **High**: Important for system functionality
- 🟢 **Medium**: Beneficial for system enhancement
- 🔵 **Low**: Nice-to-have features
- ⚪ **Unknown**: Priority needs to be determined

### Compliance Legend
- ✅ **Compliant**: Contains constitutional hash cdd01ef066bc6cf2
- ❌ **Non-Compliant**: Missing constitutional hash

---

**Generated by**: ACGS-2 Documentation Simplification System  
**Constitutional Hash**: cdd01ef066bc6cf2  
**Generation Date**: 2025-07-18T16:02:35.639489
