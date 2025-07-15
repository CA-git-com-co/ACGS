<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS-2 Project Structure Organization & Optimization Prompt

## Context
The ACGS-2 (Advanced Constitutional Governance System) project requires comprehensive file organization and structure optimization to improve maintainability, reduce duplication, and establish clear architectural boundaries.

## Current Issues Identified

### Root Directory Chaos (Priority 1)
- 200+ files in root directory lacking organization
- Mixed documentation, configuration, and executable files
- No clear separation of concerns
- Reports and temporary files scattered throughout

### Duplicate Code & Files (Priority 1)
- 16 duplicate Python scripts across `/scripts` and `/tools`
- Multiple requirements.txt files (22 total) with overlapping dependencies
- Duplicate configuration files across services
- 610 Python files with print statements (should use logging)
- 54 files with commented-out code blocks

### Service Architecture Issues (Priority 2)
- Inconsistent service structure patterns
- Mixed domain boundaries
- Shared code scattered across services
- No clear dependency management strategy

### Documentation Fragmentation (Priority 2)
- Multiple README files with overlapping content
- Documentation scattered across root and subdirectories
- No clear information architecture
- Inconsistent documentation standards

## Design Objectives

### 1. Root Directory Organization
Create a clean, scannable root directory with clear purpose for each top-level item:

```
/home/dislove/ACGS-2/
├── README.md                    # Primary project overview
├── CHANGELOG.md                 # Version history
├── LICENSE                      # Legal
├── pyproject.toml              # Main Python project config
├── uv.lock                     # Dependency lock file
├── Makefile                    # Build automation
├── docker-compose.yml          # Primary compose file
├── .gitignore                  # VCS ignore rules
├── config/environments/developmentconfig/environments/example.env                # Environment template
├── 
├── docs/                       # All documentation
├── services/                   # Microservices code
├── scripts/                    # Automation & tooling
├── tests/                      # Test suites
├── infrastructure/             # Infrastructure as code
├── config/                     # Configuration templates
├── data/                       # Data files & schemas
├── tools/                      # Development tools
├── reports/                    # Generated reports (gitignored)
├── temp/                       # Temporary files (gitignored)
└── .claude/                    # Claude-specific commands
```

### 2. Service Architecture Standardization
Establish consistent patterns for all services:

```
services/
├── shared/                     # Shared libraries & utilities
│   ├── middleware/             # Common middleware
│   ├── models/                 # Shared data models
│   ├── utils/                  # Utility functions
│   ├── config/                 # Shared configuration
│   └── requirements/           # Consolidated dependencies
│       ├── requirements-base.txt
│       ├── requirements-dev.txt
│       └── requirements-test.txt
│
├── core/                       # Core business services
│   ├── constitutional-ai/      # Constitutional validation
│   ├── governance-synthesis/   # Policy synthesis
│   ├── multi-agent-coordinator/# Agent coordination
│   └── [other-core-services]/
│
├── platform/                  # Platform services
│   ├── api-gateway/           # API routing & auth
│   ├── authentication/       # Identity management
│   ├── integrity/            # Audit & compliance
│   └── [other-platform-services]/
│
└── integration/               # External integrations
    ├── blockchain/           # Blockchain integration
    ├── mcp/                 # Model Context Protocol
    └── [other-integrations]/
```

### 3. Duplicate Code Consolidation Strategy

#### Script Consolidation
```
scripts/
├── setup/                     # Initial setup & installation
├── deployment/               # Deployment automation
├── monitoring/               # Health checks & monitoring
├── testing/                  # Test automation
├── maintenance/              # Cleanup & maintenance
└── development/              # Development utilities

tools/                        # Remove - merge into scripts/
```

#### Dependency Consolidation
```
services/shared/requirements/
├── requirements-base.txt     # Core dependencies (FastAPI, etc)
├── requirements-web.txt      # Web-specific dependencies
├── requirements-data.txt     # Database & storage
├── requirements-security.txt # Security & crypto
├── requirements-dev.txt      # Development tools
└── requirements-test.txt     # Testing frameworks

# Service requirements become minimal:
services/[service]/requirements.txt:
-r ../shared/requirements/requirements-base.txt
-r ../shared/requirements/requirements-web.txt
# Add only service-specific dependencies here
```

### 4. Documentation Architecture
```
docs/
├── README.md                 # Documentation index
├── getting-started/          # Quick start guides
├── architecture/             # System design
├── api/                      # API documentation
├── deployment/               # Infrastructure guides
├── development/              # Developer guides
├── security/                 # Security documentation
├── troubleshooting/          # Common issues
└── research/                 # Research materials
```

## Implementation Plan

### Phase 1: Root Directory Cleanup (Day 1)
1. Create standardized directory structure
2. Move misplaced files to appropriate locations
3. Consolidate scattered documentation
4. Clean up temporary files and reports
5. Update .gitignore for new structure

### Phase 2: Service Standardization (Day 2-3)
1. Establish service template structure
2. Migrate services to new structure
3. Consolidate shared libraries
4. Standardize service interfaces
5. Update inter-service dependencies

### Phase 3: Script & Tool Consolidation (Day 4)
1. Analyze all scripts for functionality overlap
2. Merge duplicate scripts
3. Organize by purpose (setup, deployment, testing, etc)
4. Remove obsolete scripts
5. Create unified tool interfaces

### Phase 4: Dependency Management (Day 5)
1. Analyze all requirements files
2. Create shared dependency base
3. Migrate services to use shared requirements
4. Remove duplicate dependencies
5. Standardize version constraints

### Phase 5: Documentation Consolidation (Day 6)
1. Audit all documentation for overlap
2. Create unified documentation structure
3. Migrate content to new organization
4. Remove redundant documentation
5. Establish documentation standards

## Success Criteria

### Quantitative Metrics
- Root directory files: 200+ → <20
- Duplicate scripts: 16 → 0
- Requirements files: 22 → 6 (shared structure)
- Documentation files: Consolidated 80%
- Project disk usage: Reduced by 1GB+

### Qualitative Improvements
- Clear separation of concerns
- Consistent architecture patterns
- Unified dependency management
- Comprehensive documentation structure
- Improved developer experience
- Easier onboarding for new developers
- Better CI/CD pipeline efficiency

## Implementation Commands

Execute this reorganization through the following sequence:

```bash
# 1. Create new directory structure
mkdir -p docs/{getting-started,architecture,api,deployment,development,security,troubleshooting}
mkdir -p scripts/{setup,deployment,monitoring,testing,maintenance,development}
mkdir -p services/shared/requirements
mkdir -p temp reports

# 2. Move files to appropriate locations
# (Specific moves based on file analysis)

# 3. Consolidate dependencies
# (Create shared requirements files)

# 4. Update service structures
# (Migrate services to new pattern)

# 5. Clean up duplicates
# (Remove duplicate files and merge functionality)
```

## Risk Mitigation

### Backup Strategy
- Create comprehensive backup before changes
- Use git branches for incremental changes
- Test critical services after each phase

### Validation Steps
- Verify all services still function after moves
- Check dependency resolution
- Validate documentation links
- Test CI/CD pipelines

### Rollback Plan
- Maintain original structure in separate branch
- Document all changes for easy reversal
- Test rollback procedures

This reorganization will transform ACGS-2 into a well-structured, maintainable project with clear architectural boundaries and reduced technical debt.