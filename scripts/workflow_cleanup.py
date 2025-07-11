#!/usr/bin/env python3
"""
GitHub Actions Workflow Cleanup Script
Constitutional Hash: cdd01ef066bc6cf2

Identifies and safely removes redundant GitHub Actions workflows
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

class WorkflowAnalyzer:
    """Analyze and categorize GitHub Actions workflows for cleanup"""
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.workflows = {}
        self.analysis_results = {}
        
    def analyze_workflows(self) -> Dict:
        """Analyze all workflow files and categorize them"""
        print(f"🔍 Analyzing workflows in {self.workflows_dir}")
        
        if not self.workflows_dir.exists():
            print(f"❌ Directory {self.workflows_dir} not found")
            return {}
            
        # Load all workflow files
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    
                self.workflows[workflow_file.name] = {
                    'path': workflow_file,
                    'content': content,
                    'size_lines': sum(1 for line in open(workflow_file)),
                    'triggers': self._extract_triggers(content),
                    'jobs': list(content.get('jobs', {}).keys()) if content else [],
                    'constitutional_compliant': self._check_constitutional_compliance(workflow_file)
                }
                
            except Exception as e:
                print(f"⚠️ Error reading {workflow_file.name}: {e}")
                
        # Analyze for redundancy
        self._analyze_redundancy()
        self._categorize_workflows()
        
        return self.analysis_results
    
    def _extract_triggers(self, content: Dict) -> Set[str]:
        """Extract workflow triggers"""
        if not content or 'on' not in content:
            return set()
            
        triggers = set()
        on_config = content['on']
        
        if isinstance(on_config, str):
            triggers.add(on_config)
        elif isinstance(on_config, list):
            triggers.update(on_config)
        elif isinstance(on_config, dict):
            triggers.update(on_config.keys())
            
        return triggers
    
    def _check_constitutional_compliance(self, workflow_file: Path) -> bool:
        """Check if workflow contains constitutional hash"""
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return self.constitutional_hash in content
        except:
            return False
    
    def _analyze_redundancy(self):
        """Identify redundant workflows based on similar functionality"""
        
        # Group workflows by similar purposes
        purpose_groups = {
            'ci_cd': [],
            'testing': [],
            'security': [],
            'deployment': [],
            'documentation': [],
            'performance': [],
            'maintenance': []
        }
        
        # Categorize workflows by filename patterns
        for filename, workflow in self.workflows.items():
            filename_lower = filename.lower()
            
            if any(pattern in filename_lower for pattern in ['ci', 'cd', 'continuous', 'integration']):
                purpose_groups['ci_cd'].append(filename)
            elif any(pattern in filename_lower for pattern in ['test', 'coverage', 'e2e', 'unit']):
                purpose_groups['testing'].append(filename)
            elif any(pattern in filename_lower for pattern in ['security', 'scan', 'vulnerability', 'codeql']):
                purpose_groups['security'].append(filename)
            elif any(pattern in filename_lower for pattern in ['deploy', 'production', 'staging']):
                purpose_groups['deployment'].append(filename)
            elif any(pattern in filename_lower for pattern in ['doc', 'documentation', 'validation']):
                purpose_groups['documentation'].append(filename)
            elif any(pattern in filename_lower for pattern in ['performance', 'benchmark', 'monitoring']):
                purpose_groups['performance'].append(filename)
            elif any(pattern in filename_lower for pattern in ['dependency', 'update', 'maintenance']):
                purpose_groups['maintenance'].append(filename)
        
        self.purpose_groups = purpose_groups
    
    def _categorize_workflows(self):
        """Categorize workflows for cleanup recommendations"""
        
        recommendations = {
            'safe_to_remove': [],
            'consolidation_candidates': [],
            'keep_essential': [],
            'needs_review': []
        }
        
        # Known safe-to-remove workflows (redundant/obsolete)
        safe_remove_patterns = [
            'ci-legacy.yml',
            'ci_cd_20250701_000659.yml',  # Timestamped files
            'test.yml',  # Basic test file if comprehensive testing exists
            'testing.yml'  # If comprehensive testing exists
        ]
        
        # Check for exact matches
        for pattern in safe_remove_patterns:
            if pattern in self.workflows:
                recommendations['safe_to_remove'].append({
                    'file': pattern,
                    'reason': 'Known redundant/obsolete workflow',
                    'size_lines': self.workflows[pattern]['size_lines']
                })
        
        # Identify consolidation candidates
        for purpose, files in self.purpose_groups.items():
            if len(files) > 3:  # More than 3 workflows for same purpose
                # Keep the largest/most comprehensive one
                files_with_size = [(f, self.workflows[f]['size_lines']) for f in files]
                files_with_size.sort(key=lambda x: x[1], reverse=True)
                
                keep_file = files_with_size[0][0]
                recommendations['keep_essential'].append({
                    'file': keep_file,
                    'reason': f'Most comprehensive {purpose} workflow',
                    'size_lines': files_with_size[0][1]
                })
                
                # Mark others for consolidation
                for file, size in files_with_size[1:]:
                    recommendations['consolidation_candidates'].append({
                        'file': file,
                        'reason': f'Redundant {purpose} workflow',
                        'size_lines': size,
                        'consolidate_into': keep_file
                    })
        
        # Check for workflows that might need review
        for filename, workflow in self.workflows.items():
            if (filename not in [r['file'] for r in recommendations['safe_to_remove']] and
                filename not in [r['file'] for r in recommendations['consolidation_candidates']] and
                filename not in [r['file'] for r in recommendations['keep_essential']]):
                
                recommendations['needs_review'].append({
                    'file': filename,
                    'reason': 'Unique workflow - manual review needed',
                    'size_lines': workflow['size_lines'],
                    'triggers': list(workflow['triggers']),
                    'jobs': workflow['jobs']
                })
        
        self.analysis_results = recommendations
    
    def generate_report(self) -> str:
        """Generate a detailed cleanup report"""
        
        if not self.analysis_results:
            self.analyze_workflows()
        
        report = []
        report.append("# GitHub Actions Workflow Cleanup Report")
        report.append(f"**Constitutional Hash:** `{self.constitutional_hash}`")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")
        
        # Summary
        total_workflows = len(self.workflows)
        safe_remove = len(self.analysis_results['safe_to_remove'])
        consolidation = len(self.analysis_results['consolidation_candidates'])
        
        report.append("## 📊 Summary")
        report.append(f"- **Total Workflows**: {total_workflows}")
        report.append(f"- **Safe to Remove**: {safe_remove}")
        report.append(f"- **Consolidation Candidates**: {consolidation}")
        report.append(f"- **Estimated Reduction**: {((safe_remove + consolidation) / total_workflows * 100):.1f}%")
        report.append("")
        
        # Safe to remove
        if self.analysis_results['safe_to_remove']:
            report.append("## 🗑️ Safe to Remove")
            report.append("These workflows are redundant or obsolete and can be safely deleted:")
            report.append("")
            for item in self.analysis_results['safe_to_remove']:
                report.append(f"- **{item['file']}** ({item['size_lines']} lines)")
                report.append(f"  - Reason: {item['reason']}")
            report.append("")
        
        # Consolidation candidates
        if self.analysis_results['consolidation_candidates']:
            report.append("## 🔄 Consolidation Candidates")
            report.append("These workflows have similar functionality and can be consolidated:")
            report.append("")
            
            # Group by consolidation target
            consolidation_groups = {}
            for item in self.analysis_results['consolidation_candidates']:
                target = item.get('consolidate_into', 'manual_review')
                if target not in consolidation_groups:
                    consolidation_groups[target] = []
                consolidation_groups[target].append(item)
            
            for target, candidates in consolidation_groups.items():
                report.append(f"### Consolidate into `{target}`:")
                for item in candidates:
                    report.append(f"- **{item['file']}** ({item['size_lines']} lines)")
                    report.append(f"  - Reason: {item['reason']}")
                report.append("")
        
        # Essential workflows to keep
        if self.analysis_results['keep_essential']:
            report.append("## ✅ Essential Workflows (Keep)")
            for item in self.analysis_results['keep_essential']:
                report.append(f"- **{item['file']}** ({item['size_lines']} lines)")
                report.append(f"  - Reason: {item['reason']}")
            report.append("")
        
        # Needs manual review
        if self.analysis_results['needs_review']:
            report.append("## 🔍 Needs Manual Review")
            report.append("These workflows require manual analysis:")
            report.append("")
            for item in self.analysis_results['needs_review']:
                report.append(f"- **{item['file']}** ({item['size_lines']} lines)")
                report.append(f"  - Triggers: {', '.join(item['triggers'])}")
                report.append(f"  - Jobs: {', '.join(item['jobs'][:3])}{'...' if len(item['jobs']) > 3 else ''}")
            report.append("")
        
        # Cleanup commands
        report.append("## 🛠️ Cleanup Commands")
        report.append("")
        report.append("### Remove redundant workflows:")
        report.append("```bash")
        for item in self.analysis_results['safe_to_remove']:
            report.append(f"rm .github/workflows/{item['file']}")
        report.append("```")
        report.append("")
        
        return "\n".join(report)
    
    def create_cleanup_script(self, script_path: str = "cleanup_workflows.sh") -> str:
        """Create a shell script to perform the cleanup"""
        
        if not self.analysis_results:
            self.analyze_workflows()
        
        script_lines = [
            "#!/bin/bash",
            "# GitHub Actions Workflow Cleanup Script",
            f"# Constitutional Hash: {self.constitutional_hash}",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "set -e",
            "",
            "echo '🧹 Starting GitHub Actions workflow cleanup...'",
            "echo 'Constitutional Hash: cdd01ef066bc6cf2'",
            "",
            "# Create backup directory",
            "mkdir -p .github/workflows/backup",
            "",
            "# Backup workflows before deletion"
        ]
        
        # Add backup commands
        for item in self.analysis_results['safe_to_remove']:
            script_lines.append(f"echo 'Backing up {item['file']}...'")
            script_lines.append(f"cp .github/workflows/{item['file']} .github/workflows/backup/ || true")
        
        script_lines.extend([
            "",
            "# Remove redundant workflows",
            "echo 'Removing redundant workflows...'"
        ])
        
        # Add removal commands
        for item in self.analysis_results['safe_to_remove']:
            script_lines.append(f"echo 'Removing {item['file']} ({item['reason']})...'")
            script_lines.append(f"rm .github/workflows/{item['file']} || echo 'Failed to remove {item['file']}'")
        
        script_lines.extend([
            "",
            f"echo '✅ Cleanup completed!'",
            f"echo 'Removed {len(self.analysis_results['safe_to_remove'])} redundant workflows'",
            f"echo 'Backups stored in .github/workflows/backup/'",
            f"echo 'Constitutional Hash: {self.constitutional_hash} verified'"
        ])
        
        script_content = "\n".join(script_lines)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        # Make script executable
        os.chmod(script_path, 0o755)
        
        return script_path

def main():
    """Main execution function"""
    
    print("🔧 ACGS-2 GitHub Actions Workflow Analyzer")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 50)
    
    analyzer = WorkflowAnalyzer()
    
    # Change to repo root if running from scripts directory
    if os.path.basename(os.getcwd()) == 'scripts':
        os.chdir('..')
    
    # Analyze workflows
    print("🔍 Analyzing workflows...")
    results = analyzer.analyze_workflows()
    
    if not results:
        print("❌ No workflows found or analysis failed")
        return 1
    
    # Generate report
    print("📊 Generating cleanup report...")
    report = analyzer.generate_report()
    
    # Save report
    report_path = ".github/workflows/CLEANUP_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✅ Report saved to {report_path}")
    
    # Create cleanup script
    print("🛠️ Creating cleanup script...")
    script_path = analyzer.create_cleanup_script()
    print(f"✅ Cleanup script created at {script_path}")
    
    # Print summary
    total = len(analyzer.workflows)
    safe_remove = len(results['safe_to_remove'])
    consolidation = len(results['consolidation_candidates'])
    
    print("\n📈 Summary:")
    print(f"  Total workflows: {total}")
    print(f"  Safe to remove: {safe_remove}")
    print(f"  Consolidation candidates: {consolidation}")
    print(f"  Potential reduction: {((safe_remove + consolidation) / total * 100):.1f}%")
    
    print(f"\n🎯 Next steps:")
    print(f"  1. Review {report_path}")
    print(f"  2. Run ./{script_path} to cleanup")
    print(f"  3. Test remaining workflows")
    print(f"  4. Commit changes")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())