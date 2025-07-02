#!/usr/bin/env python3
"""
ACGS-1 Branch Protection Setup Script

This script configures GitHub branch protection rules to enforce the new
modernized workflows and security standards.
"""

import subprocess
import json
import sys
from typing import Dict, List

class BranchProtectionManager:
    """Manage GitHub branch protection rules for ACGS-1."""
    
    def __init__(self):
        self.repository = "CA-git-com-co/ACGS"
        self.protected_branches = ["master", "main", "develop"]
        
        # Modern workflow names that should be required
        self.required_workflows = [
            "unified-ci-modern.yml / quality-gates",
            "security-focused.yml / security-summary", 
            "solana-anchor.yml / Rust Security Audit"
        ]
        
        # Legacy workflow names to be removed from protection
        self.legacy_workflows = [
            "ci-legacy.yml",
            "security-comprehensive.yml", 
            "enhanced-parallel-ci.yml",
            "cost-optimized-ci.yml",
            "optimized-ci.yml"
        ]
    
    def check_gh_cli_available(self) -> bool:
        """Check if GitHub CLI is available and authenticated."""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                 capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_current_protection(self, branch: str) -> Dict:
        """Get current branch protection settings."""
        try:
            result = subprocess.run([
                'gh', 'api', f'repos/{self.repository}/branches/{branch}/protection'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                # Branch protection might not exist
                return {}
        except Exception as e:
            print(f"⚠️ Could not retrieve protection for {branch}: {e}")
            return {}
    
    def create_protection_config(self, branch: str) -> Dict:
        """Create optimal branch protection configuration."""
        
        # Base configuration for enterprise-grade protection
        config = {
            "required_status_checks": {
                "strict": True,  # Require branches to be up to date
                "contexts": []   # Will be populated with workflow names
            },
            "enforce_admins": False,  # Allow admins to bypass for emergency fixes
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": False,
                "require_last_push_approval": True
            },
            "restrictions": None,  # No user/team restrictions
            "required_linear_history": False,  # Allow merge commits
            "allow_force_pushes": False,
            "allow_deletions": False
        }
        
        # Branch-specific configurations
        if branch in ["master", "main"]:
            # Production branch - strictest protection
            config["required_pull_request_reviews"]["required_approving_review_count"] = 2
            config["required_pull_request_reviews"]["require_code_owner_reviews"] = True
            config["required_status_checks"]["contexts"] = [
                "quality-gates",  # From unified-ci-modern.yml
                "security-summary",  # From security-focused.yml  
                "blockchain-validation",  # From unified-ci-modern.yml
                "container-security"  # From unified-ci-modern.yml
            ]
        elif branch == "develop":
            # Development branch - balanced protection
            config["required_status_checks"]["contexts"] = [
                "quality-gates",  # From unified-ci-modern.yml
                "security-summary"  # From security-focused.yml
            ]
        else:
            # Feature branches - minimal but secure
            config["required_status_checks"]["contexts"] = [
                "quality-gates"  # From unified-ci-modern.yml
            ]
        
        return config
    
    def apply_branch_protection(self, branch: str, config: Dict) -> bool:
        """Apply branch protection configuration."""
        print(f"🛡️ Applying protection to {branch} branch...")
        
        try:
            # Convert config to JSON
            config_json = json.dumps(config)
            
            # Apply protection using GitHub API
            result = subprocess.run([
                'gh', 'api', 
                f'repos/{self.repository}/branches/{branch}/protection',
                '--method', 'PUT',
                '--input', '-'
            ], input=config_json, text=True, capture_output=True)
            
            if result.returncode == 0:
                print(f"  ✅ Protection applied to {branch}")
                return True
            else:
                print(f"  ❌ Failed to apply protection to {branch}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error applying protection to {branch}: {e}")
            return False
    
    def setup_branch_protection(self) -> bool:
        """Set up branch protection for all protected branches."""
        print("🔧 Setting up branch protection rules...")
        
        if not self.check_gh_cli_available():
            print("❌ GitHub CLI not available or not authenticated")
            print("Setup instructions:")
            print("1. Install GitHub CLI: https://cli.github.com/")
            print("2. Authenticate: gh auth login")
            return False
        
        success_count = 0
        
        for branch in self.protected_branches:
            # Check if branch exists
            result = subprocess.run([
                'gh', 'api', f'repos/{self.repository}/branches/{branch}'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️ Branch {branch} does not exist, skipping...")
                continue
            
            # Create and apply protection config
            config = self.create_protection_config(branch)
            if self.apply_branch_protection(branch, config):
                success_count += 1
        
        return success_count > 0
    
    def verify_protection_setup(self) -> bool:
        """Verify that branch protection is correctly configured."""
        print("🔍 Verifying branch protection setup...")
        
        all_verified = True
        
        for branch in self.protected_branches:
            protection = self.get_current_protection(branch)
            
            if not protection:
                print(f"  ❌ {branch}: No protection configured")
                all_verified = False
                continue
            
            # Check required status checks
            status_checks = protection.get("required_status_checks", {})
            contexts = status_checks.get("contexts", [])
            
            if not contexts:
                print(f"  ⚠️ {branch}: No required status checks")
                all_verified = False
            else:
                print(f"  ✅ {branch}: {len(contexts)} required status checks")
                for context in contexts:
                    print(f"    - {context}")
            
            # Check PR reviews
            pr_reviews = protection.get("required_pull_request_reviews", {})
            review_count = pr_reviews.get("required_approving_review_count", 0)
            print(f"  📝 {branch}: {review_count} required review(s)")
        
        return all_verified
    
    def generate_protection_report(self) -> str:
        """Generate a report on branch protection status."""
        print("\n📊 Branch Protection Status Report")
        print("=" * 50)
        
        report = []
        report.append("# ACGS-1 Branch Protection Status Report")
        report.append(f"Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
        report.append("")
        
        for branch in self.protected_branches:
            protection = self.get_current_protection(branch)
            
            report.append(f"## {branch.title()} Branch")
            
            if not protection:
                report.append("❌ **Status**: No protection configured")
                report.append("")
                continue
            
            report.append("✅ **Status**: Protected")
            
            # Status checks
            status_checks = protection.get("required_status_checks", {})
            contexts = status_checks.get("contexts", [])
            strict = status_checks.get("strict", False)
            
            report.append(f"**Required Status Checks**: {len(contexts)}")
            report.append(f"**Strict Mode**: {'Yes' if strict else 'No'}")
            for context in contexts:
                report.append(f"- {context}")
            
            # PR reviews
            pr_reviews = protection.get("required_pull_request_reviews", {})
            if pr_reviews:
                review_count = pr_reviews.get("required_approving_review_count", 0)
                dismiss_stale = pr_reviews.get("dismiss_stale_reviews", False)
                code_owners = pr_reviews.get("require_code_owner_reviews", False)
                
                report.append(f"**Required Reviews**: {review_count}")
                report.append(f"**Dismiss Stale Reviews**: {'Yes' if dismiss_stale else 'No'}")
                report.append(f"**Code Owner Reviews**: {'Yes' if code_owners else 'No'}")
            
            # Security settings
            admin_enforcement = protection.get("enforce_admins", {}).get("enabled", False)
            force_push = protection.get("allow_force_pushes", {}).get("enabled", True)
            deletions = protection.get("allow_deletions", {}).get("enabled", True)
            
            report.append(f"**Admin Enforcement**: {'Yes' if admin_enforcement else 'No'}")
            report.append(f"**Allow Force Push**: {'Yes' if force_push else 'No'}")
            report.append(f"**Allow Branch Deletion**: {'Yes' if deletions else 'No'}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("1. **Required Workflows**: Ensure the following workflows are required:")
        for workflow in self.required_workflows:
            report.append(f"   - {workflow}")
        report.append("")
        report.append("2. **Legacy Cleanup**: Remove legacy workflow requirements:")
        for workflow in self.legacy_workflows:
            report.append(f"   - {workflow}")
        report.append("")
        report.append("3. **Security Best Practices**:")
        report.append("   - Enable admin enforcement for production branches")
        report.append("   - Require code owner reviews for critical changes")
        report.append("   - Set up CODEOWNERS file for automatic reviewer assignment")
        
        report_content = "\n".join(report)
        
        # Save report
        with open('BRANCH_PROTECTION_REPORT.md', 'w') as f:
            f.write(report_content)
        
        print(report_content)
        return report_content
    
    def create_codeowners_file(self) -> None:
        """Create a CODEOWNERS file for automatic reviewer assignment."""
        codeowners_content = """# ACGS-1 Code Owners
# This file defines code ownership for automatic reviewer assignment

# Global ownership
* @acgs-team

# GitHub Actions workflows
.github/workflows/ @acgs-devops @acgs-security

# Security-related files  
/security/ @acgs-security
SECURITY*.md @acgs-security
*.security.* @acgs-security

# Blockchain and smart contracts
/blockchain/ @acgs-blockchain @acgs-security
/quantumagi_core/ @acgs-blockchain

# Core services
/services/core/ @acgs-core-team
/services/platform_services/ @acgs-platform-team

# Infrastructure and deployment
/infrastructure/ @acgs-devops
/scripts/deploy* @acgs-devops
docker-compose*.yml @acgs-devops
Dockerfile* @acgs-devops

# Configuration and secrets
/config/ @acgs-security @acgs-devops
*.env.* @acgs-security
*requirements*.txt @acgs-security

# Documentation
/docs/ @acgs-docs
README.md @acgs-docs
CHANGELOG.md @acgs-docs

# Legal and compliance
/legal/ @acgs-legal
LICENSE* @acgs-legal
SECURITY_POLICY.yml @acgs-security @acgs-legal"""
        
        with open('.github/CODEOWNERS', 'w') as f:
            f.write(codeowners_content)
        
        print("📋 Created CODEOWNERS file: .github/CODEOWNERS")

def main():
    """Main branch protection setup function."""
    manager = BranchProtectionManager()
    
    print("🚀 Starting ACGS-1 Branch Protection Setup")
    print("=" * 50)
    
    try:
        # Set up branch protection
        success = manager.setup_branch_protection()
        
        if success:
            # Verify setup
            manager.verify_protection_setup()
            
            # Generate report
            manager.generate_protection_report()
            
            # Create CODEOWNERS file
            manager.create_codeowners_file()
            
            print("\n✅ Branch protection setup completed successfully!")
            print("🛡️ All protected branches now have modern workflow requirements.")
            print("📋 Review BRANCH_PROTECTION_REPORT.md for details.")
        else:
            print("\n⚠️ Branch protection setup had issues.")
            print("Check GitHub CLI authentication and repository permissions.")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Branch protection setup failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()