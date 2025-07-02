#!/usr/bin/env python3
"""
Setup GitHub Repositories for ACGS Reorganization

This script creates GitHub repositories and pushes the reorganized code.
"""

import subprocess
import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubRepositorySetup:
    def __init__(self, workspace_path: Path, org_name: str = "ACGS"):
        self.workspace_path = Path(workspace_path)
        self.org_name = org_name
        self.repositories = self._load_workspace_config()
    
    def _load_workspace_config(self) -> dict:
        """Load workspace configuration"""
        config_file = self.workspace_path / "acgs-workspace.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config["repositories"]
    
    def check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed and authenticated"""
        try:
            result = subprocess.run(["gh", "auth", "status"], 
                                  capture_output=True, check=True)
            logger.info("GitHub CLI is authenticated")
            return True
        except subprocess.CalledProcessError:
            logger.error("GitHub CLI not authenticated. Run: gh auth login")
            return False
        except FileNotFoundError:
            logger.error("GitHub CLI not installed. Install from: https://cli.github.com/")
            return False
    
    def create_github_repository(self, repo_name: str, description: str) -> bool:
        """Create a GitHub repository"""
        try:
            # Check if repository already exists
            result = subprocess.run([
                "gh", "repo", "view", f"{self.org_name}/{repo_name}"
            ], capture_output=True)
            
            if result.returncode == 0:
                logger.info(f"Repository {repo_name} already exists")
                return True
            
            # Create the repository
            logger.info(f"Creating GitHub repository: {repo_name}")
            subprocess.run([
                "gh", "repo", "create", f"{self.org_name}/{repo_name}",
                "--description", description,
                "--public",  # Change to --private if needed
                "--confirm"
            ], check=True)
            
            logger.info(f"Successfully created repository: {repo_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create repository {repo_name}: {e}")
            return False
    
    def setup_repository_remote(self, repo_path: Path, repo_name: str) -> bool:
        """Setup remote origin for repository"""
        try:
            os.chdir(repo_path)
            
            # Remove existing origin if it exists
            subprocess.run(["git", "remote", "remove", "origin"], 
                         capture_output=True)
            
            # Add new origin
            remote_url = f"git@github.com:{self.org_name}/{repo_name}.git"
            subprocess.run([
                "git", "remote", "add", "origin", remote_url
            ], check=True)
            
            logger.info(f"Set remote origin for {repo_name}: {remote_url}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup remote for {repo_name}: {e}")
            return False
    
    def push_repository(self, repo_path: Path, repo_name: str) -> bool:
        """Push repository to GitHub"""
        try:
            os.chdir(repo_path)
            
            # Get current branch name
            result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            
            # Push to GitHub
            logger.info(f"Pushing {repo_name} to GitHub...")
            subprocess.run([
                "git", "push", "-u", "origin", current_branch
            ], check=True)
            
            logger.info(f"Successfully pushed {repo_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push {repo_name}: {e}")
            return False
    
    def setup_all_repositories(self) -> dict:
        """Setup all repositories on GitHub"""
        results = {}
        
        if not self.check_gh_cli():
            return {"error": "GitHub CLI not available"}
        
        for repo_name, config in self.repositories.items():
            logger.info(f"\n=== Setting up {repo_name} ===")
            
            # Create GitHub repository
            if not self.create_github_repository(repo_name, config["description"]):
                results[repo_name] = "failed_create"
                continue
            
            # Setup local repository
            repo_path = self.workspace_path / repo_name
            if not repo_path.exists():
                logger.error(f"Local repository path does not exist: {repo_path}")
                results[repo_name] = "missing_local"
                continue
            
            # Setup remote
            if not self.setup_repository_remote(repo_path, repo_name):
                results[repo_name] = "failed_remote"
                continue
            
            # Push to GitHub
            if not self.push_repository(repo_path, repo_name):
                results[repo_name] = "failed_push"
                continue
            
            results[repo_name] = "success"
            logger.info(f"✅ {repo_name} setup complete")
        
        return results
    
    def generate_setup_summary(self, results: dict) -> str:
        """Generate summary of setup results"""
        successful = [repo for repo, status in results.items() if status == "success"]
        failed = [repo for repo, status in results.items() if status != "success"]
        
        summary = f"""
# GitHub Repository Setup Summary

## Successful Repositories ({len(successful)})
"""
        for repo in successful:
            summary += f"- ✅ **{repo}**: https://github.com/{self.org_name}/{repo}\n"
        
        if failed:
            summary += f"\n## Failed Repositories ({len(failed)})\n"
            for repo in failed:
                status = results[repo]
                summary += f"- ❌ **{repo}**: {status}\n"
        
        summary += f"\n## Next Steps\n"
        summary += f"1. Review and verify all repositories on GitHub\n"
        summary += f"2. Set up branch protection rules\n"
        summary += f"3. Configure team access permissions\n"
        summary += f"4. Set up CI/CD pipelines\n"
        
        return summary

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup GitHub repositories for ACGS")
    parser.add_argument("workspace_path", help="Path to ACGS workspace")
    parser.add_argument("--org", default="ACGS", help="GitHub organization name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    setup = GitHubRepositorySetup(args.workspace_path, args.org)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - Would setup the following repositories:")
        for repo_name, config in setup.repositories.items():
            logger.info(f"  {repo_name}: {config['description']}")
        return
    
    # Execute setup
    results = setup.setup_all_repositories()
    
    # Generate and save summary
    summary = setup.generate_setup_summary(results)
    summary_file = Path(args.workspace_path) / "GITHUB_SETUP_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    logger.info(f"\nSetup complete! Summary saved to: {summary_file}")
    print(summary)

if __name__ == "__main__":
    main()