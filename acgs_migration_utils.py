#!/usr/bin/env python3
"""
ACGS Migration Utilities

Helper utilities for migrating different file types and updating dependencies
during the repository reorganization process.

Author: ACGS Development Team
Date: 2025-01-02
"""

import os
import re
import json
import toml
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class DependencyMapper:
    """Maps and updates dependencies between repositories"""
    
    def __init__(self, repo_mapping: Dict[str, List[str]]):
        self.repo_mapping = repo_mapping
        self.import_mapping = self._build_import_mapping()
    
    def _build_import_mapping(self) -> Dict[str, str]:
        """Build mapping of import paths to repository names"""
        mapping = {}
        
        # Map service paths to repositories
        mapping.update({
            "services.core.constitutional_ai": "acgs-core",
            "services.core.formal_verification": "acgs-core", 
            "services.core.governance_synthesis": "acgs-core",
            "services.core.policy_governance": "acgs-core",
            "services.core.evolutionary_computation": "acgs-core",
            "services.core.multi_agent_coordinator": "acgs-core",
            "services.core.worker_agents": "acgs-core",
            "services.core.consensus_engine": "acgs-core",
            "services.platform_services.authentication": "acgs-platform",
            "services.platform_services.integrity": "acgs-platform",
            "services.shared": "acgs-platform",
            "services.blockchain": "acgs-blockchain",
            "services.shared.ai_model_service": "acgs-models",
            "services.shared.ml_routing_optimizer": "acgs-models",
            "services.shared.wina": "acgs-models",
            "tools.reasoning_models": "acgs-models",
            "services.cli": "acgs-applications",
            "tools.mcp_inspector.client": "acgs-applications",
            "examples": "acgs-applications",
            "tools": "acgs-tools",
        })
        
        return mapping
    
    def find_cross_repo_imports(self, file_path: Path, current_repo: str) -> List[Tuple[str, str]]:
        """Find imports that cross repository boundaries"""
        cross_imports = []
        
        if file_path.suffix == '.py':
            content = file_path.read_text()
            
            # Find all import statements
            import_pattern = r'(?:from\s+(\S+)\s+import|import\s+(\S+))'
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                import_path = match[0] or match[1]
                
                # Check if this import crosses repository boundaries
                for prefix, repo in self.import_mapping.items():
                    if import_path.startswith(prefix) and repo != current_repo:
                        cross_imports.append((import_path, repo))
                        break
        
        return cross_imports


class ConfigurationUpdater:
    """Updates various configuration files during migration"""
    
    @staticmethod
    def update_pyproject_toml(file_path: Path, repo_name: str, dependencies: List[str]):
        """Update pyproject.toml with new dependencies"""
        try:
            with open(file_path, 'r') as f:
                data = toml.load(f)
            
            # Update project name
            if 'project' in data:
                data['project']['name'] = repo_name
                
                # Add workspace dependencies
                if 'dependencies' not in data['project']:
                    data['project']['dependencies'] = []
                
                for dep in dependencies:
                    dep_entry = f"{dep} = {{path = '../{dep}', develop = true}}"
                    if dep_entry not in data['project']['dependencies']:
                        data['project']['dependencies'].append(dep_entry)
            
            # Update build system if needed
            if 'build-system' in data:
                data['build-system']['requires'] = ["hatchling", "hatch-vcs"]
            
            with open(file_path, 'w') as f:
                toml.dump(data, f)
            
            logger.info(f"Updated pyproject.toml for {repo_name}")
            
        except Exception as e:
            logger.error(f"Failed to update pyproject.toml: {e}")
    
    @staticmethod
    def update_package_json(file_path: Path, repo_name: str, dependencies: List[str]):
        """Update package.json with new dependencies"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Update package name
            data['name'] = f"@acgs/{repo_name}"
            
            # Add workspace dependencies
            if 'dependencies' not in data:
                data['dependencies'] = {}
            
            for dep in dependencies:
                data['dependencies'][f"@acgs/{dep}"] = "workspace:*"
            
            # Update scripts if needed
            if 'scripts' not in data:
                data['scripts'] = {}
            
            data['scripts'].update({
                "build": "tsc",
                "test": "jest",
                "lint": "eslint src --ext .ts,.tsx"
            })
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Updated package.json for {repo_name}")
            
        except Exception as e:
            logger.error(f"Failed to update package.json: {e}")
    
    @staticmethod
    def create_dockerfile(repo_path: Path, repo_name: str, base_image: str = "python:3.11-slim"):
        """Create a Dockerfile for the repository"""
        dockerfile_content = f"""# Dockerfile for {repo_name}

FROM {base_image}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["uv", "run", "python", "-m", "{repo_name}"]
"""
        
        dockerfile_path = repo_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        logger.info(f"Created Dockerfile for {repo_name}")
    
    @staticmethod
    def create_github_workflows(repo_path: Path, repo_name: str):
        """Create GitHub Actions workflows"""
        workflows_dir = repo_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # CI workflow
        ci_workflow = f"""name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests
      run: uv run pytest tests/
    
    - name: Run linting
      run: |
        uv run ruff check .
        uv run mypy .

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
"""
        
        ci_file = workflows_dir / "ci.yml"
        with open(ci_file, 'w') as f:
            f.write(ci_workflow)
        
        logger.info(f"Created GitHub workflows for {repo_name}")


class FileOrganizer:
    """Organizes files within repositories"""
    
    @staticmethod
    def organize_python_files(repo_path: Path):
        """Organize Python files according to best practices"""
        # Create standard directories
        dirs_to_create = ["tests", "docs", "examples", "scripts"]
        for dir_name in dirs_to_create:
            (repo_path / dir_name).mkdir(exist_ok=True)
        
        # Move test files to tests directory
        for test_file in repo_path.rglob("test_*.py"):
            if test_file.parent.name != "tests":
                new_path = repo_path / "tests" / test_file.relative_to(repo_path)
                new_path.parent.mkdir(parents=True, exist_ok=True)
                test_file.rename(new_path)
                logger.info(f"Moved {test_file} to tests directory")
    
    @staticmethod
    def create_init_files(repo_path: Path):
        """Create __init__.py files for Python packages"""
        for dir_path in repo_path.rglob("*"):
            if dir_path.is_dir() and not dir_path.name.startswith('.'):
                # Check if directory contains Python files
                py_files = list(dir_path.glob("*.py"))
                if py_files and not (dir_path / "__init__.py").exists():
                    init_file = dir_path / "__init__.py"
                    init_file.write_text('"""Package initialization"""')
                    logger.info(f"Created {init_file}")


class MigrationValidator:
    """Validates the migration results"""
    
    def __init__(self, source_repo: Path, target_repos: Dict[str, Path]):
        self.source_repo = source_repo
        self.target_repos = target_repos
    
    def validate_file_count(self) -> Dict[str, Dict[str, int]]:
        """Compare file counts between source and target"""
        results = {}
        
        for repo_name, repo_path in self.target_repos.items():
            source_count = 0
            target_count = len(list(repo_path.rglob("*")))
            
            results[repo_name] = {
                "source_files": source_count,
                "target_files": target_count
            }
        
        return results
    
    def validate_imports(self) -> Dict[str, List[str]]:
        """Check for broken imports"""
        broken_imports = {}
        
        for repo_name, repo_path in self.target_repos.items():
            repo_broken = []
            
            for py_file in repo_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    # Simple check for imports that might be broken
                    import_lines = [
                        line for line in content.split('\n') 
                        if line.strip().startswith(('import ', 'from '))
                    ]
                    
                    for line in import_lines:
                        # Check if import references old structure
                        if 'services.' in line and '../' not in line:
                            repo_broken.append(f"{py_file}: {line.strip()}")
                
                except Exception as e:
                    logger.error(f"Error checking {py_file}: {e}")
            
            if repo_broken:
                broken_imports[repo_name] = repo_broken
        
        return broken_imports
    
    def generate_validation_report(self) -> str:
        """Generate a validation report"""
        report = "# Migration Validation Report\n\n"
        
        # File count validation
        file_counts = self.validate_file_count()
        report += "## File Count Summary\n\n"
        for repo, counts in file_counts.items():
            report += f"- **{repo}**: {counts['target_files']} files\n"
        
        # Import validation
        broken_imports = self.validate_imports()
        if broken_imports:
            report += "\n## Broken Imports Found\n\n"
            for repo, imports in broken_imports.items():
                report += f"### {repo}\n"
                for imp in imports[:5]:  # Show first 5
                    report += f"- {imp}\n"
                if len(imports) > 5:
                    report += f"- ... and {len(imports) - 5} more\n"
        else:
            report += "\n## Import Validation\n\nNo broken imports found.\n"
        
        return report


def create_integration_test_setup(workspace_dir: Path):
    """Create integration testing setup for the workspace"""
    test_dir = workspace_dir / "integration_tests"
    test_dir.mkdir(exist_ok=True)
    
    # Create test runner script
    test_runner = test_dir / "run_tests.py"
    test_content = '''#!/usr/bin/env python3
"""
Integration Test Runner for ACGS Workspace

Runs tests across all repositories to ensure proper integration.
"""

import subprocess
import json
from pathlib import Path
import sys

def run_integration_tests():
    workspace_file = Path(__file__).parent.parent / "acgs-workspace.json"
    with open(workspace_file) as f:
        config = json.load(f)
    
    failed_tests = []
    
    for repo_name, repo_info in config["repositories"].items():
        print(f"\\nRunning tests for {repo_name}...")
        repo_path = Path(repo_info["path"])
        
        if (repo_path / "pyproject.toml").exists():
            result = subprocess.run(
                ["uv", "run", "pytest", "tests/"],
                cwd=repo_path,
                capture_output=True
            )
            if result.returncode != 0:
                failed_tests.append(repo_name)
                print(f"  FAILED: {result.stderr.decode()}")
            else:
                print("  PASSED")
        
        elif (repo_path / "package.json").exists():
            result = subprocess.run(
                ["pnpm", "test"],
                cwd=repo_path,
                capture_output=True
            )
            if result.returncode != 0:
                failed_tests.append(repo_name)
    
    if failed_tests:
        print(f"\\n❌ Failed repositories: {', '.join(failed_tests)}")
        return 1
    else:
        print("\\n✅ All integration tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(run_integration_tests())
'''
    
    with open(test_runner, 'w') as f:
        f.write(test_content)
    
    test_runner.chmod(0o755)
    logger.info(f"Created integration test setup at {test_dir}")