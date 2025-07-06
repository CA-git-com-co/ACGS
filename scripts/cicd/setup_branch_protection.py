#!/usr/bin/env python3
"""
ACGS Enterprise Branch Protection Setup Script

This script configures GitHub branch protection rules to enforce quality gates
and prevent merges when test coverage falls below 90% threshold.
"""
# Constitutional Hash: cdd01ef066bc6cf2

import os
import sys
import json
import requests
from typing import Dict, Any, List


class BranchProtectionManager:
    """Manages GitHub branch protection rules for ACGS enterprise quality gates."""
    
    def __init__(self, repo_owner: str, repo_name: str, github_token: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def get_branch_protection_config(self) -> Dict[str, Any]:
        """Get enterprise-grade branch protection configuration."""
        return {
            "required_status_checks": {
                "strict": True,
                "contexts": [
                    "Enterprise Quality Gates Validation",
                    "Enterprise Code Quality Gates",
                    "Enterprise Security Scanning (Parallel)",
                    "Rust Quality & Build (Parallel)"
                ]
            },
            "enforce_admins": True,
            "required_pull_request_reviews": {
                "required_approving_review_count": 2,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "require_last_push_approval": True
            },
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True
        }
    
    def setup_branch_protection(self, branch: str) -> bool:
        """Set up branch protection for the specified branch."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/branches/{branch}/protection"
        config = self.get_branch_protection_config()
        
        try:
            response = requests.put(url, headers=self.headers, json=config)
            
            if response.status_code == 200:
                print(f"✅ Branch protection configured for '{branch}'")
                return True
            elif response.status_code == 403:
                print(f"⚠️ Insufficient permissions to configure branch protection for '{branch}'")
                print("   Administrator access required to set up branch protection rules")
                return False
            else:
                print(f"❌ Failed to configure branch protection for '{branch}': {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error configuring branch protection for '{branch}': {e}")
            return False
    
    def verify_branch_protection(self, branch: str) -> bool:
        """Verify that branch protection is properly configured."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/branches/{branch}/protection"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                protection = response.json()
                
                # Verify required status checks
                required_checks = protection.get("required_status_checks", {})
                if not required_checks.get("strict"):
                    print(f"⚠️ Branch '{branch}' does not have strict status checks enabled")
                    return False
                
                contexts = required_checks.get("contexts", [])
                required_contexts = [
                    "Enterprise Quality Gates Validation"
                ]
                
                missing_contexts = [ctx for ctx in required_contexts if ctx not in contexts]
                if missing_contexts:
                    print(f"⚠️ Branch '{branch}' missing required status checks: {missing_contexts}")
                    return False
                
                # Verify PR reviews
                pr_reviews = protection.get("required_pull_request_reviews", {})
                if pr_reviews.get("required_approving_review_count", 0) < 2:
                    print(f"⚠️ Branch '{branch}' requires fewer than 2 approving reviews")
                    return False
                
                print(f"✅ Branch protection verified for '{branch}'")
                return True
                
            elif response.status_code == 404:
                print(f"⚠️ No branch protection configured for '{branch}'")
                return False
            else:
                print(f"❌ Failed to verify branch protection for '{branch}': {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying branch protection for '{branch}': {e}")
            return False
    
    def create_quality_gates_ruleset(self) -> bool:
        """Create a repository ruleset for quality gates enforcement."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/rulesets"
        
        ruleset_config = {
            "name": "ACGS Enterprise Quality Gates",
            "target": "branch",
            "enforcement": "active",
            "conditions": {
                "ref_name": {
                    "include": ["refs/heads/main", "refs/heads/master", "refs/heads/develop"],
                    "exclude": []
                }
            },
            "rules": [
                {
                    "type": "required_status_checks",
                    "parameters": {
                        "strict_required_status_checks_policy": True,
                        "required_status_checks": [
                            {
                                "context": "Enterprise Quality Gates Validation",
                                "integration_id": None
                            }
                        ]
                    }
                },
                {
                    "type": "pull_request",
                    "parameters": {
                        "required_approving_review_count": 2,
                        "dismiss_stale_reviews_on_push": True,
                        "require_code_owner_review": True,
                        "require_last_push_approval": True
                    }
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=ruleset_config)
            
            if response.status_code == 201:
                print("✅ Quality gates ruleset created successfully")
                return True
            elif response.status_code == 403:
                print("⚠️ Insufficient permissions to create rulesets")
                return False
            else:
                print(f"❌ Failed to create ruleset: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating ruleset: {e}")
            return False


def main():
    """Main function to set up branch protection."""
    # Get configuration from environment
    repo_owner = os.getenv("GITHUB_REPOSITORY_OWNER", "CA-git-com-co")
    repo_name = os.getenv("GITHUB_REPOSITORY_NAME", "ACGS")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    # Initialize branch protection manager
    manager = BranchProtectionManager(repo_owner, repo_name, github_token)
    
    # Branches to protect
    protected_branches = ["main", "master", "develop"]
    
    print("🔧 Setting up ACGS Enterprise Branch Protection...")
    print(f"Repository: {repo_owner}/{repo_name}")
    print(f"Protected branches: {protected_branches}")
    print()
    
    success_count = 0
    total_branches = len(protected_branches)
    
    # Set up protection for each branch
    for branch in protected_branches:
        print(f"Configuring branch protection for '{branch}'...")
        if manager.setup_branch_protection(branch):
            if manager.verify_branch_protection(branch):
                success_count += 1
            else:
                print(f"⚠️ Branch protection setup but verification failed for '{branch}'")
        print()
    
    # Create quality gates ruleset
    print("Creating enterprise quality gates ruleset...")
    manager.create_quality_gates_ruleset()
    print()
    
    # Summary
    print("📊 Branch Protection Setup Summary")
    print("=" * 40)
    print(f"Successfully configured: {success_count}/{total_branches} branches")
    
    if success_count == total_branches:
        print("✅ All branch protection rules configured successfully!")
        print("🎯 Quality gates will now block merges when coverage < 90%")
    else:
        print("⚠️ Some branch protection rules may need manual configuration")
        print("   Check repository settings for complete setup")
    
    return success_count == total_branches


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
