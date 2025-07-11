#!/usr/bin/env python3
"""
GitHub Actions Runner Migration Script
Constitutional Hash: cdd01ef066bc6cf2

Automates migration from self-hosted to GitHub-hosted runners
with intelligent detection of workflows that require self-hosted runners.
"""

import os
import re
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

class RunnerMigrator:
    """Migrate GitHub Actions workflows from self-hosted to GitHub-hosted runners"""
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.backup_dir = self.workflows_dir / f"backup-runners-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Keywords that indicate a workflow should keep self-hosted runners
        self.keep_self_hosted_keywords = {
            'production', 'deploy', 'staging', 'gpu', 'internal',
            'database', 'migration', 'infrastructure', 'terraform',
            'ansible', 'vault', 'secrets', 'vpn', 'firewall',
            'on-premise', 'on-prem', 'datacenter', 'private'
        }
        
        # Patterns for different runner configurations
        self.runner_patterns = [
            (r'runs-on:\s*self-hosted\s*$', 'runs-on: ubuntu-latest'),
            (r'runs-on:\s*\[self-hosted\]', 'runs-on: ubuntu-latest'),
            (r'runs-on:\s*\[\s*self-hosted\s*\]', 'runs-on: ubuntu-latest'),
            (r'runs-on:\s*\[\s*"self-hosted"\s*\]', 'runs-on: ubuntu-latest'),
            (r'runs-on:\s*\[\s*\'self-hosted\'\s*\]', 'runs-on: ubuntu-latest'),
        ]
        
        self.migration_stats = {
            'total_workflows': 0,
            'migrated': 0,
            'skipped': 0,
            'errors': 0,
            'self_hosted_instances': 0,
            'github_hosted_instances': 0
        }
    
    def should_keep_self_hosted(self, content: str, filename: str) -> bool:
        """Determine if a workflow should keep self-hosted runners"""
        
        # Check filename
        filename_lower = filename.lower()
        for keyword in self.keep_self_hosted_keywords:
            if keyword in filename_lower:
                return True
        
        # Check content
        content_lower = content.lower()
        
        # Look for environment specifications
        if re.search(r'environment:\s*(production|staging)', content_lower):
            return True
        
        # Check for specific job names that indicate production use
        production_job_patterns = [
            r'deploy[-_]?production',
            r'deploy[-_]?to[-_]?prod',
            r'release[-_]?production',
            r'infrastructure[-_]?update',
            r'database[-_]?migration'
        ]
        
        for pattern in production_job_patterns:
            if re.search(pattern, content_lower):
                return True
        
        # Check for self-hosted with additional labels
        complex_runner_pattern = r'runs-on:\s*\[.*self-hosted.*,.*\]'
        if re.search(complex_runner_pattern, content):
            return True
        
        # Check for keywords in content
        for keyword in self.keep_self_hosted_keywords:
            if keyword in content_lower:
                # Do a more precise check to avoid false positives
                if re.search(rf'\b{keyword}\b', content_lower):
                    return True
        
        return False
    
    def analyze_workflow(self, workflow_path: Path) -> Dict:
        """Analyze a workflow file for runner usage"""
        
        analysis = {
            'path': workflow_path,
            'self_hosted_count': 0,
            'github_hosted_count': 0,
            'should_migrate': False,
            'migration_notes': []
        }
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count runner instances
            self_hosted_matches = re.findall(r'runs-on:.*self-hosted', content)
            github_hosted_matches = re.findall(r'runs-on:.*(?:ubuntu|windows|macos)-latest', content)
            
            analysis['self_hosted_count'] = len(self_hosted_matches)
            analysis['github_hosted_count'] = len(github_hosted_matches)
            
            if analysis['self_hosted_count'] > 0:
                if self.should_keep_self_hosted(content, workflow_path.name):
                    analysis['migration_notes'].append("Keep self-hosted: Contains production/specialized requirements")
                else:
                    analysis['should_migrate'] = True
                    analysis['migration_notes'].append("Can migrate to GitHub-hosted runners")
            
        except Exception as e:
            analysis['migration_notes'].append(f"Error analyzing: {e}")
            self.migration_stats['errors'] += 1
        
        return analysis
    
    def migrate_workflow(self, workflow_path: Path) -> bool:
        """Migrate a single workflow file"""
        
        try:
            # Create backup
            backup_path = self.backup_dir / workflow_path.name
            shutil.copy2(workflow_path, backup_path)
            
            # Read content
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply migration patterns
            for pattern, replacement in self.runner_patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Add migration comment if changes were made
            if content != original_content:
                # Add comment at the top of the file
                migration_comment = f"""# Runner Migration: {datetime.now().strftime('%Y-%m-%d')}
# Migrated from self-hosted to GitHub-hosted runners
# Constitutional Hash: {self.constitutional_hash}
# Original backed up to: {backup_path.relative_to(self.workflows_dir.parent)}

"""
                
                # Handle YAML front matter gracefully
                if content.startswith('---'):
                    parts = content.split('\n', 1)
                    content = parts[0] + '\n' + migration_comment + parts[1]
                else:
                    content = migration_comment + content
                
                # Write migrated content
                with open(workflow_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.migration_stats['migrated'] += 1
                return True
            else:
                self.migration_stats['skipped'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Error migrating {workflow_path}: {e}")
            self.migration_stats['errors'] += 1
            return False
    
    def generate_report(self, analyses: List[Dict]) -> str:
        """Generate a detailed migration report"""
        
        report = []
        report.append("# GitHub Actions Runner Migration Report")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Constitutional Hash:** `{self.constitutional_hash}`")
        report.append("")
        
        # Summary statistics
        report.append("## 📊 Summary")
        report.append(f"- **Total workflows analyzed:** {len(analyses)}")
        report.append(f"- **Workflows migrated:** {self.migration_stats['migrated']}")
        report.append(f"- **Workflows skipped:** {self.migration_stats['skipped']}")
        report.append(f"- **Errors encountered:** {self.migration_stats['errors']}")
        
        total_self_hosted = sum(a['self_hosted_count'] for a in analyses)
        total_github_hosted = sum(a['github_hosted_count'] for a in analyses)
        
        report.append(f"- **Total self-hosted instances:** {total_self_hosted}")
        report.append(f"- **Total GitHub-hosted instances:** {total_github_hosted}")
        report.append("")
        
        # Workflows that should migrate
        can_migrate = [a for a in analyses if a['should_migrate']]
        if can_migrate:
            report.append("## ✅ Workflows Migrated")
            report.append("These workflows were successfully migrated to GitHub-hosted runners:")
            report.append("")
            for analysis in can_migrate:
                report.append(f"- **{analysis['path'].name}** ({analysis['self_hosted_count']} instances)")
            report.append("")
        
        # Workflows that should keep self-hosted
        keep_self_hosted = [a for a in analyses if a['self_hosted_count'] > 0 and not a['should_migrate']]
        if keep_self_hosted:
            report.append("## 🔒 Workflows Keeping Self-Hosted Runners")
            report.append("These workflows require self-hosted runners due to specialized requirements:")
            report.append("")
            for analysis in keep_self_hosted:
                report.append(f"- **{analysis['path'].name}** ({analysis['self_hosted_count']} instances)")
                for note in analysis['migration_notes']:
                    report.append(f"  - {note}")
            report.append("")
        
        # Cost estimation
        report.append("## 💰 Cost Impact Estimation")
        
        # Rough estimates
        self_hosted_cost_per_instance = 17  # $17/month per self-hosted runner
        github_hosted_cost_per_minute = 0.008  # $0.008/minute for Linux
        avg_workflow_minutes = 10  # Average workflow duration
        avg_runs_per_month = 500  # Average runs per workflow per month
        
        current_self_hosted_cost = total_self_hosted * self_hosted_cost_per_instance
        new_self_hosted_cost = (total_self_hosted - self.migration_stats['migrated']) * self_hosted_cost_per_instance
        github_hosted_cost = (self.migration_stats['migrated'] * avg_workflow_minutes * 
                             avg_runs_per_month * github_hosted_cost_per_minute)
        
        report.append(f"- **Current self-hosted cost:** ${current_self_hosted_cost:,.2f}/month")
        report.append(f"- **New self-hosted cost:** ${new_self_hosted_cost:,.2f}/month")
        report.append(f"- **GitHub-hosted cost:** ${github_hosted_cost:,.2f}/month")
        report.append(f"- **Estimated savings:** ${(current_self_hosted_cost - new_self_hosted_cost - github_hosted_cost):,.2f}/month")
        report.append("")
        
        # Recommendations
        report.append("## 🎯 Recommendations")
        report.append("")
        report.append("1. **Review migrated workflows** in the next CI/CD run")
        report.append("2. **Monitor performance** differences between runner types")
        report.append("3. **Update documentation** with new runner strategy")
        report.append("4. **Consider caching** strategies for GitHub-hosted runners")
        report.append("5. **Set up alerts** for workflow failures during transition")
        report.append("")
        
        return "\n".join(report)
    
    def run(self, dry_run: bool = False):
        """Execute the migration process"""
        
        print(f"🔧 GitHub Actions Runner Migration Tool")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print("=" * 50)
        
        # Create backup directory
        if not dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created backup directory: {self.backup_dir}")
        
        # Get all workflow files
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        print(f"📂 Found {len(workflow_files)} workflow files")
        
        # Analyze all workflows
        analyses = []
        for workflow_file in workflow_files:
            print(f"\n🔍 Analyzing: {workflow_file.name}")
            analysis = self.analyze_workflow(workflow_file)
            analyses.append(analysis)
            
            if analysis['self_hosted_count'] > 0:
                print(f"  - Self-hosted runners: {analysis['self_hosted_count']}")
                print(f"  - Should migrate: {'Yes' if analysis['should_migrate'] else 'No'}")
                for note in analysis['migration_notes']:
                    print(f"  - {note}")
            
            # Perform migration if not dry run
            if not dry_run and analysis['should_migrate']:
                if self.migrate_workflow(workflow_file):
                    print(f"  ✅ Migrated successfully")
                else:
                    print(f"  ❌ Migration failed")
        
        # Generate report
        print("\n" + "=" * 50)
        report = self.generate_report(analyses)
        
        # Save report
        report_path = self.workflows_dir / f"RUNNER_MIGRATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_path}")
        print(f"\n✅ Migration {'simulation' if dry_run else 'process'} complete!")
        
        if dry_run:
            print("\n⚠️  This was a dry run. No files were modified.")
            print("Run without --dry-run flag to perform actual migration.")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate GitHub Actions workflows from self-hosted to GitHub-hosted runners"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without modifying files"
    )
    parser.add_argument(
        "--workflows-dir",
        default=".github/workflows",
        help="Path to workflows directory (default: .github/workflows)"
    )
    
    args = parser.parse_args()
    
    # Change to repo root if needed
    if os.path.basename(os.getcwd()) == 'scripts':
        os.chdir('..')
    
    migrator = RunnerMigrator(workflows_dir=args.workflows_dir)
    migrator.run(dry_run=args.dry_run)

if __name__ == "__main__":
    main()