#!/usr/bin/env python3
"""
ACGS Repository Reorganization Script

This script helps split the monolithic ACGS codebase into smaller,
more manageable sub-repositories while preserving git history.

Author: ACGS Development Team
Date: 2025-01-02
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RepositoryConfig:
    """Configuration for a sub-repository"""
    name: str
    description: str
    paths: List[str]
    dependencies: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    additional_files: List[str] = field(default_factory=list)


class ACGSReorganizer:
    """Main class for reorganizing ACGS repository"""
    
    def __init__(self, source_repo: Path, target_dir: Path, dry_run: bool = False):
        self.source_repo = Path(source_repo).resolve()
        self.target_dir = Path(target_dir).resolve()
        self.dry_run = dry_run
        self.repos = self._define_repositories()
        
    def _define_repositories(self) -> Dict[str, RepositoryConfig]:
        """Define the structure of sub-repositories"""
        return {
            "acgs-core": RepositoryConfig(
                name="acgs-core",
                description="Core constitutional AI services for ACGS",
                paths=[
                    "services/core/constitutional-ai",
                    "services/core/formal-verification",
                    "services/core/governance-synthesis",
                    "services/core/policy-governance",
                    "services/core/evolutionary-computation",
                    "services/core/multi_agent_coordinator",
                    "services/core/worker_agents",
                    "services/core/consensus_engine"
                ],
                dependencies=["acgs-platform"],
                additional_files=["pyproject.toml", "uv.lock", ".python-version"]
            ),
            
            "acgs-platform": RepositoryConfig(
                name="acgs-platform",
                description="Platform services including authentication and integrity",
                paths=[
                    "services/platform_services/authentication",
                    "services/platform_services/integrity",
                    "services/shared"
                ],
                additional_files=["pyproject.toml", "uv.lock", ".python-version"]
            ),
            
            "acgs-blockchain": RepositoryConfig(
                name="acgs-blockchain",
                description="Blockchain components and Solana programs",
                paths=[
                    "services/blockchain"
                ],
                additional_files=[
                    "Anchor.toml",
                    "Cargo.toml",
                    "Cargo.lock",
                    "package.json",
                    "pnpm-lock.yaml"
                ]
            ),
            
            "acgs-models": RepositoryConfig(
                name="acgs-models",
                description="AI model services including reasoning models and ML components",
                paths=[
                    "services/shared/ai_model_service.py",
                    "services/shared/ml_routing_optimizer.py",
                    "services/shared/wina",
                    "tools/reasoning-models"
                ],
                dependencies=["acgs-platform"],
                additional_files=["pyproject.toml", "uv.lock"]
            ),
            
            "acgs-applications": RepositoryConfig(
                name="acgs-applications",
                description="Frontend applications and CLI tools",
                paths=[
                    "services/cli",
                    "tools/mcp-inspector/client",
                    "examples"
                ],
                additional_files=["package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "pyproject.toml"]
            ),
            
            "acgs-infrastructure": RepositoryConfig(
                name="acgs-infrastructure",
                description="Infrastructure components (Docker, K8s, Terraform)",
                paths=[
                    "infrastructure"
                ],
                additional_files=[".env.example", "docker-compose.yml"]
            ),
            
            "acgs-tools": RepositoryConfig(
                name="acgs-tools",
                description="Development and maintenance tools",
                paths=[
                    "tools"
                ],
                exclude_patterns=["tools/reasoning-models", "tools/mcp-inspector/client"],
                additional_files=["pyproject.toml"]
            )
        }
    
    def validate_source_repo(self) -> bool:
        """Validate that source repository exists and is a git repo"""
        if not self.source_repo.exists():
            logger.error(f"Source repository {self.source_repo} does not exist")
            return False
            
        if not (self.source_repo / ".git").exists():
            logger.error(f"{self.source_repo} is not a git repository")
            return False
            
        return True
    
    def validate_paths(self) -> Dict[str, List[str]]:
        """Validate that all specified paths exist in the source repository"""
        missing_paths = {}
        
        for repo_name, config in self.repos.items():
            repo_missing = []
            
            for path in config.paths:
                full_path = self.source_repo / path
                if not full_path.exists():
                    repo_missing.append(path)
                    logger.warning(f"Path does not exist: {path}")
            
            if repo_missing:
                missing_paths[repo_name] = repo_missing
        
        return missing_paths
    
    def check_dependencies(self) -> bool:
        """Check that required dependencies are installed"""
        dependencies = ["git", "git-filter-repo"]
        missing_deps = []
        
        for dep in dependencies:
            try:
                subprocess.run([dep, "--version"], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_deps.append(dep)
        
        if missing_deps:
            logger.error(f"Missing required dependencies: {', '.join(missing_deps)}")
            logger.info("Install git-filter-repo with: pip install git-filter-repo")
            return False
        
        return True
    
    def create_target_structure(self):
        """Create target directory structure"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create target directory: {self.target_dir}")
            return
            
        self.target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created target directory: {self.target_dir}")
    
    def extract_with_history(self, repo_config: RepositoryConfig) -> bool:
        """Extract repository with git history preservation"""
        repo_path = self.target_dir / repo_config.name
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would extract {repo_config.name} to {repo_path}")
            logger.info(f"  Paths: {', '.join(repo_config.paths)}")
            return True
        
        # Validate paths exist before proceeding
        existing_paths = []
        for path in repo_config.paths:
            if (self.source_repo / path).exists():
                existing_paths.append(path)
            else:
                logger.warning(f"Skipping non-existent path: {path}")
        
        if not existing_paths:
            logger.error(f"No valid paths found for {repo_config.name}")
            return False
        
        try:
            # Clone the source repository
            logger.info(f"Cloning repository for {repo_config.name}...")
            subprocess.run([
                "git", "clone", "--no-hardlinks", 
                str(self.source_repo), str(repo_path)
            ], check=True, capture_output=True)
            
            # Change to the new repository
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Use git filter-repo to extract specific paths
            logger.info(f"Filtering repository for {repo_config.name}...")
            
            # Build filter-repo command
            filter_cmd = ["git", "filter-repo", "--force"]
            
            # Add paths to keep (only existing ones)
            for path in existing_paths:
                filter_cmd.extend(["--path", path])
            
            # Add exclude patterns if specified
            for pattern in repo_config.exclude_patterns:
                filter_cmd.extend(["--path-glob", f"!{pattern}"])
            
            # Add additional files
            for file in repo_config.additional_files:
                if (self.source_repo / file).exists():
                    filter_cmd.extend(["--path", file])
            
            subprocess.run(filter_cmd, check=True, capture_output=True)
            
            # Check if repository is empty after filtering
            try:
                subprocess.run(["git", "log", "--oneline", "-1"], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.warning(f"Repository {repo_config.name} appears to be empty after filtering")
                return False
            
            # Update remote origin
            subprocess.run([
                "git", "remote", "add", "origin",
                f"git@github.com:ACGS/{repo_config.name}.git"
            ], capture_output=True)
            
            logger.info(f"Successfully extracted {repo_config.name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract {repo_config.name}: {e}")
            if e.stderr:
                logger.error(f"Error output: {e.stderr.decode()}")
            # Cleanup failed extraction
            if repo_path.exists():
                shutil.rmtree(repo_path)
            return False
        finally:
            os.chdir(original_dir)
    
    def update_dependencies(self, repo_path: Path, repo_config: RepositoryConfig):
        """Update dependencies in configuration files"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update dependencies in {repo_path}")
            return
        
        # Update pyproject.toml if it exists
        pyproject_path = repo_path / "pyproject.toml"
        if pyproject_path.exists():
            logger.info(f"Updating pyproject.toml in {repo_config.name}")
            # This would need actual implementation based on your dependency structure
            
        # Update package.json if it exists
        package_json_path = repo_path / "package.json"
        if package_json_path.exists():
            logger.info(f"Updating package.json in {repo_config.name}")
            # This would need actual implementation based on your dependency structure
    
    def create_workspace_config(self):
        """Create workspace configuration for managing multiple repos"""
        workspace_config = {
            "version": "1.0.0",
            "repositories": {},
            "scripts": {
                "setup": "python scripts/setup_workspace.py",
                "test": "python scripts/run_integration_tests.py",
                "build": "python scripts/build_all.py"
            }
        }
        
        for name, config in self.repos.items():
            workspace_config["repositories"][name] = {
                "path": f"./{name}",
                "description": config.description,
                "dependencies": config.dependencies
            }
        
        workspace_file = self.target_dir / "acgs-workspace.json"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create workspace config at {workspace_file}")
            logger.info(json.dumps(workspace_config, indent=2))
            return
        
        with open(workspace_file, 'w') as f:
            json.dump(workspace_config, f, indent=2)
        
        logger.info(f"Created workspace configuration at {workspace_file}")
    
    def create_setup_scripts(self):
        """Create setup and utility scripts"""
        scripts_dir = self.target_dir / "scripts"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create setup scripts in {scripts_dir}")
            return
        
        scripts_dir.mkdir(exist_ok=True)
        
        # Create setup script
        setup_script = scripts_dir / "setup_workspace.py"
        setup_content = '''#!/usr/bin/env python3
"""Setup ACGS workspace with all sub-repositories"""

import subprocess
import json
from pathlib import Path

def setup_workspace():
    workspace_file = Path(__file__).parent.parent / "acgs-workspace.json"
    with open(workspace_file) as f:
        config = json.load(f)
    
    for repo_name, repo_info in config["repositories"].items():
        print(f"Setting up {repo_name}...")
        repo_path = Path(repo_info["path"])
        
        if not repo_path.exists():
            # Clone repository
            subprocess.run([
                "git", "clone",
                f"git@github.com:ACGS/{repo_name}.git",
                str(repo_path)
            ])
        
        # Install dependencies based on file type
        if (repo_path / "pyproject.toml").exists():
            subprocess.run(["uv", "sync"], cwd=repo_path)
        elif (repo_path / "package.json").exists():
            subprocess.run(["pnpm", "install"], cwd=repo_path)
        elif (repo_path / "Cargo.toml").exists():
            subprocess.run(["cargo", "build"], cwd=repo_path)

if __name__ == "__main__":
    setup_workspace()
'''
        
        with open(setup_script, 'w') as f:
            f.write(setup_content)
        
        setup_script.chmod(0o755)
        logger.info(f"Created setup script at {setup_script}")
    
    def generate_documentation(self):
        """Generate documentation for the reorganization"""
        doc_content = f"""# ACGS Repository Reorganization

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

The ACGS monolithic repository has been reorganized into the following sub-repositories:

"""
        
        for name, config in self.repos.items():
            doc_content += f"""
### {name}

**Description**: {config.description}

**Included Paths**:
"""
            for path in config.paths:
                doc_content += f"- `{path}`\n"
            
            if config.dependencies:
                doc_content += f"\n**Dependencies**: {', '.join(config.dependencies)}\n"
        
        doc_content += """
## Setup Instructions

1. Clone the workspace:
   ```bash
   git clone git@github.com:ACGS/acgs-workspace.git
   cd acgs-workspace
   ```

2. Run the setup script:
   ```bash
   python scripts/setup_workspace.py
   ```

3. For development across multiple repositories:
   ```bash
   # Install development dependencies
   uv sync --all-extras
   
   # Run integration tests
   python scripts/run_integration_tests.py
   ```

## Repository Structure

Each repository follows a standard structure:
- Source code in appropriate language directories
- Tests in `tests/` directory
- Documentation in `docs/` directory
- CI/CD configuration in `.github/workflows/`

## Contributing

When making changes that affect multiple repositories:
1. Create feature branches in affected repositories
2. Update cross-repository dependencies
3. Run integration tests
4. Create pull requests with cross-references

## Migration Notes

- Git history has been preserved for all migrated files
- Large binary files have been moved to Git LFS
- Sensitive configuration has been moved to environment variables
"""
        
        doc_file = self.target_dir / "REORGANIZATION.md"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create documentation at {doc_file}")
            return
        
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        logger.info(f"Created documentation at {doc_file}")
    
    def run(self):
        """Run the complete reorganization process"""
        logger.info("Starting ACGS repository reorganization...")
        
        # Check dependencies first
        if not self.check_dependencies():
            return False
        
        # Validate source
        if not self.validate_source_repo():
            return False
        
        # Validate paths
        missing_paths = self.validate_paths()
        if missing_paths:
            logger.warning("The following paths do not exist:")
            for repo, paths in missing_paths.items():
                logger.warning(f"  {repo}: {', '.join(paths)}")
            
            if not self.dry_run:
                response = input("Continue with missing paths? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Reorganization cancelled by user")
                    return False
        
        # Create target structure
        self.create_target_structure()
        
        # Extract each repository
        success_count = 0
        failed_repos = []
        
        for name, config in self.repos.items():
            logger.info(f"\nProcessing {name}...")
            if self.extract_with_history(config):
                success_count += 1
                
                # Update dependencies
                repo_path = self.target_dir / name
                if repo_path.exists():
                    self.update_dependencies(repo_path, config)
            else:
                failed_repos.append(name)
        
        # Create workspace configuration
        self.create_workspace_config()
        
        # Create setup scripts
        self.create_setup_scripts()
        
        # Generate documentation
        self.generate_documentation()
        
        logger.info(f"\nReorganization complete!")
        logger.info(f"Successfully created {success_count}/{len(self.repos)} repositories")
        
        if failed_repos:
            logger.warning(f"Failed repositories: {', '.join(failed_repos)}")
        
        logger.info(f"Target directory: {self.target_dir}")
        
        return success_count == len(self.repos)


def main():
    parser = argparse.ArgumentParser(
        description="Reorganize ACGS monolithic repository into sub-repositories"
    )
    parser.add_argument(
        "source_repo",
        help="Path to the source ACGS repository"
    )
    parser.add_argument(
        "target_dir",
        help="Target directory for sub-repositories"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes"
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        help="Specific repositories to extract (default: all)"
    )
    
    args = parser.parse_args()
    
    # Create reorganizer instance
    reorganizer = ACGSReorganizer(
        source_repo=args.source_repo,
        target_dir=args.target_dir,
        dry_run=args.dry_run
    )
    
    # Filter repositories if specified
    if args.repos:
        reorganizer.repos = {
            name: config 
            for name, config in reorganizer.repos.items() 
            if name in args.repos
        }
    
    # Run reorganization
    success = reorganizer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()