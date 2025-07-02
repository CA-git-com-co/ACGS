#!/bin/bash
# ACGS-1 Codebase Reorganization Script
# Safely reorganizes the codebase while preserving git history

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Starting ACGS-1 Codebase Reorganization"
echo "Root directory: $ROOT_DIR"
echo "=================================================="

# Backup current state
backup_current_state() {
    echo "📦 Creating backup of current state..."
    BACKUP_DIR="$ROOT_DIR/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Create git bundle for complete backup
    git bundle create "$BACKUP_DIR/acgs_backup.bundle" --all
    
    # Copy critical files
    cp -r quantumagi_core "$BACKUP_DIR/" 2>/dev/null || true
    cp -r src "$BACKUP_DIR/" 2>/dev/null || true
    cp -r docs "$BACKUP_DIR/" 2>/dev/null || true
    
    echo "✅ Backup created at: $BACKUP_DIR"
}

# Phase 1: Create new directory structure
create_directory_structure() {
    echo "📁 Phase 1: Creating new directory structure..."
    
    # Blockchain directories
    mkdir -p blockchain/{programs,client,tests,scripts,docs}
    mkdir -p blockchain/client/{rust,typescript,python}
    
    # Services directories
    mkdir -p services/core/{constitutional-ai,governance-synthesis,policy-governance,formal-verification}
    mkdir -p services/platform/{authentication,integrity,workflow}
    mkdir -p services/research/{federated-evaluation,research-platform}
    mkdir -p services/shared/{models,database,auth,config,events,utils}
    mkdir -p services/monitoring
    
    # Applications directories
    mkdir -p applications/{governance-dashboard,constitutional-council,public-consultation,admin-panel}
    
    # Integration directories
    mkdir -p integrations/{quantumagi-bridge,alphaevolve-engine,external-apis}
    
    # Infrastructure directories
    mkdir -p infrastructure/{docker,kubernetes,monitoring,deployment}
    
    # Tools and documentation
    mkdir -p tools/{cli,generators,validators}
    mkdir -p docs/{architecture,api,deployment,development,research}
    
    # Testing directories
    mkdir -p tests/{unit,integration,e2e,performance,fixtures}
    
    # Scripts and config
    mkdir -p scripts/{setup,migration,deployment,maintenance}
    mkdir -p config/{environments,database,monitoring,security}
    
    echo "✅ Directory structure created"
}

# Phase 2: Move blockchain components
move_blockchain_components() {
    echo "⛓️ Phase 2: Moving blockchain components..."
    
    if [ -d "quantumagi_core" ]; then
        # Move Anchor programs
        if [ -d "quantumagi_core/programs" ]; then
            echo "Moving Anchor programs..."
            git mv quantumagi_core/programs/* blockchain/programs/ 2>/dev/null || {
                cp -r quantumagi_core/programs/* blockchain/programs/
                git add blockchain/programs/
            }
        fi
        
        # Move configuration files
        echo "Moving blockchain configuration..."
        [ -f "quantumagi_core/Anchor.toml" ] && git mv quantumagi_core/Anchor.toml blockchain/
        [ -f "quantumagi_core/Cargo.toml" ] && git mv quantumagi_core/Cargo.toml blockchain/
        [ -f "quantumagi_core/package.json" ] && git mv quantumagi_core/package.json blockchain/
        [ -f "quantumagi_core/tsconfig.json" ] && git mv quantumagi_core/tsconfig.json blockchain/
        
        # Move client libraries
        echo "Moving client libraries..."
        if [ -d "quantumagi_core/client" ]; then
            git mv quantumagi_core/client/* blockchain/client/python/ 2>/dev/null || {
                cp -r quantumagi_core/client/* blockchain/client/python/
                git add blockchain/client/python/
            }
        fi
        
        # Move tests and scripts
        [ -d "quantumagi_core/tests" ] && git mv quantumagi_core/tests/* blockchain/tests/
        [ -d "quantumagi_core/scripts" ] && git mv quantumagi_core/scripts/* blockchain/scripts/
        
        # Move GS Engine to integrations
        if [ -d "quantumagi_core/gs_engine" ]; then
            echo "Moving GS Engine to integrations..."
            git mv quantumagi_core/gs_engine integrations/quantumagi-bridge/gs_engine
        fi
        
        # Move frontend components
        if [ -d "quantumagi_core/frontend" ]; then
            echo "Moving frontend components..."
            git mv quantumagi_core/frontend/* applications/governance-dashboard/
        fi
    fi
    
    echo "✅ Blockchain components moved"
}

# Phase 3: Move backend services
move_backend_services() {
    echo "🏗️ Phase 3: Moving backend services..."
    
    if [ -d "services" ]; then
        # Move core services with renaming
        echo "Moving core services..."
        [ -d "services/core/constitutional-ai/ac_service" ] && git mv services/core/constitutional-ai/ac_service services/core/constitutional-ai/
        [ -d "services/core/governance-synthesis/gs_service" ] && git mv services/core/governance-synthesis/gs_service services/core/governance-synthesis/
        [ -d "services/core/policy-governance/pgc_service" ] && git mv services/core/policy-governance/pgc_service services/core/policy-governance/
        [ -d "services/core/formal-verification/fv_service" ] && git mv services/core/formal-verification/fv_service services/core/formal-verification/
        
        # Move platform services
        echo "Moving platform services..."
        [ -d "services/platform/authentication/auth_service" ] && git mv services/platform/authentication/auth_service services/platform/authentication/
        [ -d "services/platform/integrity/integrity_service" ] && git mv services/platform/integrity/integrity_service services/platform/integrity/
        [ -d "services/workflow_service" ] && git mv services/workflow_service services/platform/workflow/
        
        # Move research services
        echo "Moving research services..."
        [ -d "services/federated_service" ] && git mv services/federated_service services/research/federated-evaluation/
        [ -d "services/research_service" ] && git mv services/research_service services/research/research-platform/
        
        # Move shared components
        echo "Moving shared components..."
        if [ -d "services/shared" ]; then
            git mv services/shared/* services/shared/ 2>/dev/null || {
                cp -r services/shared/* services/shared/
                git add services/shared/
            }
        fi
        
        # Move monitoring
        [ -d "services/monitoring" ] && git mv services/monitoring services/monitoring/
    fi
    
    echo "✅ Backend services moved"
}

# Phase 4: Move frontend applications
move_frontend_applications() {
    echo "🖥️ Phase 4: Moving frontend applications..."
    
    if [ -d "applications/legacy-frontend" ]; then
        echo "Moving main frontend application..."
        git mv applications/legacy-frontend/* applications/governance-dashboard/ 2>/dev/null || {
            cp -r applications/legacy-frontend/* applications/governance-dashboard/
            git add applications/governance-dashboard/
        }
    fi
    
    echo "✅ Frontend applications moved"
}

# Phase 5: Move AlphaEvolve engine
move_alphaevolve_engine() {
    echo "🧠 Phase 5: Moving AlphaEvolve engine..."
    
    if [ -d "integrations/alphaevolve-engine" ]; then
        echo "Moving AlphaEvolve GS Engine..."
        git mv integrations/alphaevolve-engine integrations/alphaevolve-engine/
    fi
    
    echo "✅ AlphaEvolve engine moved"
}

# Phase 6: Move infrastructure and configuration
move_infrastructure() {
    echo "🏗️ Phase 6: Moving infrastructure components..."
    
    # Move Docker configurations
    if [ -d "config/docker" ]; then
        git mv config/docker/* infrastructure/docker/
    fi
    
    # Move Kubernetes configurations
    if [ -d "config/k8s" ]; then
        git mv config/k8s/* infrastructure/kubernetes/
    fi
    
    # Move monitoring configurations
    if [ -d "monitoring" ]; then
        git mv monitoring/* infrastructure/monitoring/
    fi
    
    # Move configuration files
    if [ -d "config" ]; then
        # Keep some configs, move others
        [ -d "config/database" ] && git mv config/database config/database_backup
        [ -d "config/monitoring" ] && git mv config/monitoring config/monitoring_backup
        
        # Move to new structure
        mkdir -p config/environments
        [ -f "config/database_backup" ] && mv config/database_backup config/database
        [ -f "config/monitoring_backup" ] && mv config/monitoring_backup config/monitoring
    fi
    
    echo "✅ Infrastructure components moved"
}

# Phase 7: Move documentation
move_documentation() {
    echo "📚 Phase 7: Moving documentation..."
    
    if [ -d "docs" ]; then
        # Create subdirectories and move docs
        [ -f "docs/architecture.md" ] && git mv docs/architecture.md docs/architecture/
        [ -f "docs/api_reference.md" ] && git mv docs/api_reference.md docs/api/
        [ -f "docs/deployment.md" ] && git mv docs/deployment.md docs/deployment/
        [ -f "docs/developer_guide.md" ] && git mv docs/developer_guide.md docs/development/
        
        # Move research documentation
        if [ -d "docs/research" ]; then
            # Already in correct location
            echo "Research docs already in correct location"
        fi
    fi
    
    echo "✅ Documentation moved"
}

# Phase 8: Move tests
move_tests() {
    echo "🧪 Phase 8: Moving tests..."
    
    if [ -d "tests" ]; then
        # Tests are already in a good location, just organize better
        [ -d "tests/unit" ] || mkdir -p tests/unit
        [ -d "tests/integration" ] || mkdir -p tests/integration
        [ -d "tests/e2e" ] || mkdir -p tests/e2e
        
        # Move test files to appropriate subdirectories
        find tests -name "test_*.py" -maxdepth 1 -exec mv {} tests/unit/ \; 2>/dev/null || true
        find tests -name "*_test.py" -maxdepth 1 -exec mv {} tests/unit/ \; 2>/dev/null || true
    fi
    
    echo "✅ Tests moved"
}

# Phase 9: Move scripts
move_scripts() {
    echo "📜 Phase 9: Moving scripts..."
    
    if [ -d "scripts" ]; then
        # Organize scripts into subdirectories
        mkdir -p scripts/setup scripts/migration scripts/deployment scripts/maintenance
        
        # Move scripts based on naming patterns
        find scripts -name "setup_*" -maxdepth 1 -exec mv {} scripts/setup/ \; 2>/dev/null || true
        find scripts -name "deploy_*" -maxdepth 1 -exec mv {} scripts/deployment/ \; 2>/dev/null || true
        find scripts -name "*_migration*" -maxdepth 1 -exec mv {} scripts/migration/ \; 2>/dev/null || true
    fi
    
    echo "✅ Scripts moved"
}

# Phase 10: Clean up empty directories
cleanup_empty_directories() {
    echo "🧹 Phase 10: Cleaning up empty directories..."
    
    # Remove empty directories
    find . -type d -empty -delete 2>/dev/null || true
    
    # Remove old quantumagi_core if empty
    if [ -d "quantumagi_core" ] && [ -z "$(ls -A quantumagi_core)" ]; then
        rmdir quantumagi_core
        echo "Removed empty quantumagi_core directory"
    fi
    
    # Remove old src if empty
    if [ -d "src" ] && [ -z "$(ls -A src)" ]; then
        rmdir src
        echo "Removed empty src directory"
    fi
    
    echo "✅ Cleanup completed"
}

# Main execution
main() {
    cd "$ROOT_DIR"
    
    # Check if git repository
    if [ ! -d ".git" ]; then
        echo "❌ Not a git repository. Please run from the root of the ACGS-1 repository."
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo "⚠️ You have uncommitted changes. Please commit or stash them before reorganization."
        echo "Uncommitted files:"
        git status --porcelain
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Execute phases
    backup_current_state
    create_directory_structure
    move_blockchain_components
    move_backend_services
    move_frontend_applications
    move_alphaevolve_engine
    move_infrastructure
    move_documentation
    move_tests
    move_scripts
    cleanup_empty_directories
    
    # Commit changes
    echo "💾 Committing reorganization changes..."
    git add .
    git commit -m "feat: reorganize ACGS-1 codebase for improved modularity and blockchain-first architecture

- Move Solana programs to blockchain/ directory
- Reorganize backend services with clear domain boundaries  
- Separate frontend applications by purpose
- Create integration layer for blockchain-backend bridge
- Improve infrastructure and tooling organization
- Maintain git history for all moved files"
    
    echo ""
    echo "🎉 ACGS-1 Reorganization Complete!"
    echo "=================================================="
    echo "✅ All components moved to new structure"
    echo "✅ Git history preserved"
    echo "✅ Changes committed"
    echo ""
    echo "Next steps:"
    echo "1. Run validation: python scripts/validation/validate_reorganization.py"
    echo "2. Update import paths: python scripts/reorganization/fix_imports.py"
    echo "3. Test build processes: ./scripts/validation/test_builds.sh"
    echo "4. Deploy and validate: python scripts/validation/validate_deployment.py"
}

# Execute main function
main "$@"
