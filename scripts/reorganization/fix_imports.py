#!/usr/bin/env python3
"""
Import Path Fix Script
Automatically fixes import paths after codebase reorganization
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImportPathFixer:
    """Fixes import paths after reorganization"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.import_mappings = self._create_import_mappings()
        self.files_modified = 0
        self.imports_fixed = 0
    
    def _create_import_mappings(self) -> Dict[str, str]:
        """Create mapping of old import paths to new paths"""
        return {
            # Backend service mappings
            'src.backend.ac_service': 'services.core.constitutional_ai',
            'src.backend.gs_service': 'services.core.governance_synthesis', 
            'src.backend.pgc_service': 'services.core.policy_governance',
            'src.backend.fv_service': 'services.core.formal_verification',
            'src.backend.auth_service': 'services.platform.authentication',
            'src.backend.integrity_service': 'services.platform.integrity',
            'src.backend.workflow_service': 'services.platform.workflow',
            'src.backend.federated_service': 'services.research.federated_evaluation',
            'src.backend.research_service': 'services.research.research_platform',
            'src.backend.shared': 'services.shared',
            'src.backend.monitoring': 'services.monitoring',
            
            # AlphaEvolve engine mappings
            'src.alphaevolve_gs_engine': 'integrations.alphaevolve_engine',
            'alphaevolve_gs_engine': 'integrations.alphaevolve_engine',
            
            # Quantumagi mappings
            'quantumagi_core.gs_engine': 'integrations.quantumagi_bridge.gs_engine',
            'quantumagi_core.client': 'blockchain.client.python',
            'quantumagi_core.frontend': 'applications.governance_dashboard',
            
            # Shared component mappings
            'shared.models': 'services.shared.models',
            'shared.database': 'services.shared.database',
            'shared.auth': 'services.shared.auth',
            'shared.utils': 'services.shared.utils',
            'shared.config': 'services.shared.config',
            'shared.events': 'services.shared.events',
        }
    
    def fix_all_imports(self) -> bool:
        """Fix imports in all Python files"""
        logger.info("🔧 Starting import path fixes...")
        
        python_files = list(self.root_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to process")
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                self._fix_file_imports(py_file)
            except Exception as e:
                logger.error(f"Error processing {py_file}: {e}")
        
        logger.info(f"✅ Import fixes complete: {self.files_modified} files modified, {self.imports_fixed} imports fixed")
        return True
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            'venv/', 'node_modules/', '__pycache__/', '.git/',
            'target/', '.pytest_cache/', 'backup_'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _fix_file_imports(self, file_path: Path):
        """Fix imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            modified_content = self._process_file_content(original_content, file_path)
            
            if modified_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.files_modified += 1
                logger.info(f"Fixed imports in: {file_path.relative_to(self.root_path)}")
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    def _process_file_content(self, content: str, file_path: Path) -> str:
        """Process file content to fix imports"""
        lines = content.split('\n')
        modified_lines = []
        file_imports_fixed = 0
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            modified_line = self._fix_import_line(line, file_path)
            
            if modified_line != original_line:
                file_imports_fixed += 1
                self.imports_fixed += 1
                logger.debug(f"  Line {line_num}: {original_line.strip()} -> {modified_line.strip()}")
            
            modified_lines.append(modified_line)
        
        if file_imports_fixed > 0:
            logger.debug(f"Fixed {file_imports_fixed} imports in {file_path.name}")
        
        return '\n'.join(modified_lines)
    
    def _fix_import_line(self, line: str, file_path: Path) -> str:
        """Fix a single import line"""
        stripped = line.strip()
        
        # Skip comments and non-import lines
        if not stripped or stripped.startswith('#'):
            return line
        
        # Handle different import patterns
        if stripped.startswith('from ') and ' import ' in stripped:
            return self._fix_from_import(line, file_path)
        elif stripped.startswith('import '):
            return self._fix_direct_import(line, file_path)
        # elif 'sys.path.append' in stripped:  # Removed during reorganization
            return self._fix_sys_path_append(line, file_path)
        
        return line
    
    def _fix_from_import(self, line: str, file_path: Path) -> str:
        """Fix 'from ... import ...' statements"""
        # Pattern: from module import items
        match = re.match(r'^(\s*from\s+)([^\s]+)(\s+import\s+.+)$', line)
        if not match:
            return line
        
        prefix, module_path, suffix = match.groups()
        
        # Check for mappings
        for old_path, new_path in self.import_mappings.items():
            if module_path == old_path:
                return f"{prefix}{new_path}{suffix}"
            elif module_path.startswith(old_path + '.'):
                # Handle submodule imports
                submodule = module_path[len(old_path):]
                return f"{prefix}{new_path}{submodule}{suffix}"
        
        return line
    
    def _fix_direct_import(self, line: str, file_path: Path) -> str:
        """Fix 'import ...' statements"""
        # Pattern: import module
        match = re.match(r'^(\s*import\s+)([^\s]+)(.*)$', line)
        if not match:
            return line
        
        prefix, module_path, suffix = match.groups()
        
        # Check for mappings
        for old_path, new_path in self.import_mappings.items():
            if module_path == old_path:
                return f"{prefix}{new_path}{suffix}"
            elif module_path.startswith(old_path + '.'):
                # Handle submodule imports
                submodule = module_path[len(old_path):]
                return f"{prefix}{new_path}{submodule}{suffix}"
        
        return line
    
    def _fix_sys_path_append(self, line: str, file_path: Path) -> str:
        # """Fix or remove sys.path.append statements"""  # Removed during reorganization
        # These should generally be removed in the new structure
        # if 'sys.path.append' in line:  # Removed during reorganization
            # Comment out the line instead of removing it
            if not line.strip().startswith('#'):
                indentation = len(line) - len(line.lstrip())
                return ' ' * indentation + '# ' + line.strip() + '  # Removed during reorganization'
        
        return line
    
    def fix_configuration_files(self) -> bool:
        """Fix configuration files with updated paths"""
        logger.info("⚙️ Fixing configuration files...")
        
        config_fixes = [
            self._fix_anchor_toml,
            self._fix_package_json,
            self._fix_docker_compose,
            self._fix_env_files
        ]
        
        for fix_func in config_fixes:
            try:
                fix_func()
            except Exception as e:
                logger.error(f"Error in {fix_func.__name__}: {e}")
        
        logger.info("✅ Configuration files fixed")
        return True
    
    def _fix_anchor_toml(self):
        """Fix Anchor.toml workspace members"""
        anchor_toml = self.root_path / "blockchain" / "Anchor.toml"
        if not anchor_toml.exists():
            return
        
        with open(anchor_toml, 'r') as f:
            content = f.read()
        
        # Update workspace members to use new program names
        content = re.sub(
            r'members = \[\s*"programs/quantumagi_core",\s*"programs/appeals",\s*"programs/logging"\s*\]',
            'members = [\n    "programs/quantumagi-core",\n    "programs/appeals",\n    "programs/logging"\n]',
            content
        )
        
        with open(anchor_toml, 'w') as f:
            f.write(content)
        
        logger.info("Fixed Anchor.toml workspace members")
    
    def _fix_package_json(self):
        """Fix package.json scripts and paths"""
        package_json = self.root_path / "blockchain" / "package.json"
        if not package_json.exists():
            return
        
        import json
        
        with open(package_json, 'r') as f:
            data = json.load(f)
        
        # Update scripts if needed
        if 'scripts' in data:
            # Update test script path if it references old structure
            if 'test' in data['scripts']:
                data['scripts']['test'] = data['scripts']['test'].replace(
                    'tests/**/*.ts', 'tests/**/*.ts'
                )
        
        with open(package_json, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("Fixed package.json")
    
    def _fix_docker_compose(self):
        """Fix Docker Compose files with new service paths"""
        docker_compose_files = [
            self.root_path / "infrastructure" / "docker" / "docker-compose.yml",
            self.root_path / "docker-compose.yml"  # Root level if exists
        ]
        
        for compose_file in docker_compose_files:
            if not compose_file.exists():
                continue
            
            with open(compose_file, 'r') as f:
                content = f.read()
            
            # Update build contexts to new service locations
            service_mappings = {
                './src/backend/ac_service': './services/core/constitutional-ai',
                './src/backend/gs_service': './services/core/governance-synthesis',
                './src/backend/pgc_service': './services/core/policy-governance',
                './src/backend/fv_service': './services/core/formal-verification',
                './src/backend/auth_service': './services/platform/authentication',
                './src/backend/integrity_service': './services/platform/integrity',
            }
            
            for old_path, new_path in service_mappings.items():
                content = content.replace(old_path, new_path)
            
            with open(compose_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Fixed {compose_file.name}")
    
    def _fix_env_files(self):
        """Fix environment files with updated service URLs"""
        env_files = list(self.root_path.rglob("*.env"))
        env_files.extend(list(self.root_path.rglob(".env*")))
        
        for env_file in env_files:
            if self._should_skip_file(env_file):
                continue
            
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Update any hardcoded paths in environment variables
                original_content = content
                
                # Example: update service URLs if they reference old structure
                content = re.sub(
                    r'(.*_SERVICE_URL=.*)/src/backend/([^/]+)',
                    r'\1/services/core/\2',
                    content
                )
                
                if content != original_content:
                    with open(env_file, 'w') as f:
                        f.write(content)
                    logger.info(f"Fixed {env_file.name}")
                    
            except Exception as e:
                logger.warning(f"Could not process {env_file}: {e}")
    
    def generate_import_report(self) -> Dict:
        """Generate report of import fixes"""
        return {
            'files_modified': self.files_modified,
            'imports_fixed': self.imports_fixed,
            'mappings_used': len(self.import_mappings),
            'import_mappings': self.import_mappings
        }

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.getcwd()
    
    fixer = ImportPathFixer(root_path)
    
    # Fix Python imports
    success = fixer.fix_all_imports()
    
    # Fix configuration files
    config_success = fixer.fix_configuration_files()
    
    # Generate report
    report = fixer.generate_import_report()
    
    logger.info("\n" + "=" * 50)
    logger.info("📊 Import Fix Report")
    logger.info("=" * 50)
    logger.info(f"Files modified: {report['files_modified']}")
    logger.info(f"Imports fixed: {report['imports_fixed']}")
    logger.info(f"Mappings available: {report['mappings_used']}")
    
    if success and config_success:
        logger.info("🎉 All import fixes completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some import fixes failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
