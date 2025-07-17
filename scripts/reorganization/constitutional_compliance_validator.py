#!/usr/bin/env python3
"""
ACGS-2 Constitutional Compliance Validation Script
Constitutional Hash: cdd01ef066bc6cf2

This script implements comprehensive constitutional compliance validation by:
1. Verifying constitutional hash presence in all documentation
2. Validating performance targets documentation
3. Checking implementation status indicators
4. Ensuring compliance with ACGS-2 standards
5. Generating comprehensive compliance report
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

class ConstitutionalComplianceValidator:
    """Validate constitutional compliance across ACGS-2 project"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Performance targets that should be documented
        self.required_performance_targets = {
            "p99_latency": "<5ms",
            "throughput": ">100 RPS", 
            "cache_hit_rate": ">85%"
        }
        
        # Implementation status indicators
        self.status_indicators = [
            "✅ IMPLEMENTED",
            "🔄 IN PROGRESS", 
            "❌ PLANNED"
        ]
        
        # Required constitutional compliance elements
        self.compliance_requirements = {
            "constitutional_hash": self.constitutional_hash,
            "performance_targets": self.required_performance_targets,
            "status_indicators": self.status_indicators,
            "compliance_statement": "constitutional compliance",
            "audit_trail": "audit",
            "validation_framework": "validation"
        }
    
    def find_documentation_files(self) -> List[Path]:
        """Find all documentation files for compliance validation"""
        doc_files = []
        
        # CLAUDE.md files
        for file_path in self.project_root.rglob("CLAUDE.md"):
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                continue
            doc_files.append(file_path)
        
        # README files
        for file_path in self.project_root.rglob("README.md"):
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                continue
            doc_files.append(file_path)
        
        # Other important documentation
        for pattern in ["*.md", "*.yaml", "*.yml"]:
            for file_path in self.project_root.rglob(pattern):
                if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                    continue
                if file_path not in doc_files and file_path.stat().st_size > 0:
                    doc_files.append(file_path)
        
        return doc_files
    
    def validate_constitutional_hash(self, file_path: Path) -> Dict:
        """Validate constitutional hash presence in a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check for constitutional hash
            has_hash = self.constitutional_hash in content
            
            # Check for constitutional hash comment format
            has_comment_format = f"<!-- Constitutional Hash: {self.constitutional_hash} -->" in content
            
            # Check for constitutional hash in various formats
            hash_patterns = [
                f"Constitutional Hash: {self.constitutional_hash}",
                f"constitutional hash {self.constitutional_hash}",
                f"hash {self.constitutional_hash}",
                f"cdd01ef066bc6cf2"
            ]
            
            pattern_matches = sum(1 for pattern in hash_patterns if pattern.lower() in content.lower())
            
            return {
                "has_hash": has_hash,
                "has_comment_format": has_comment_format,
                "pattern_matches": pattern_matches,
                "compliance_score": min(pattern_matches, 3) / 3.0  # Max score of 1.0
            }
            
        except Exception as e:
            return {
                "has_hash": False,
                "has_comment_format": False,
                "pattern_matches": 0,
                "compliance_score": 0.0,
                "error": str(e)
            }
    
    def validate_performance_targets(self, file_path: Path) -> Dict:
        """Validate performance targets documentation in a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            targets_found = {}
            for target, value in self.required_performance_targets.items():
                # Check for exact value match
                exact_match = value in content
                
                # Check for target concept (more flexible)
                concept_patterns = {
                    "p99_latency": ["p99", "latency", "5ms", "<5ms"],
                    "throughput": ["rps", "throughput", "100", ">100"],
                    "cache_hit_rate": ["cache", "hit rate", "85%", ">85%"]
                }
                
                concept_matches = sum(1 for pattern in concept_patterns.get(target, []) 
                                    if pattern.lower() in content.lower())
                
                targets_found[target] = {
                    "exact_match": exact_match,
                    "concept_matches": concept_matches,
                    "present": exact_match or concept_matches > 0
                }
            
            total_targets = len(self.required_performance_targets)
            targets_present = sum(1 for t in targets_found.values() if t["present"])
            
            return {
                "targets_found": targets_found,
                "targets_present": targets_present,
                "total_targets": total_targets,
                "compliance_score": targets_present / total_targets if total_targets > 0 else 0.0
            }
            
        except Exception as e:
            return {
                "targets_found": {},
                "targets_present": 0,
                "total_targets": len(self.required_performance_targets),
                "compliance_score": 0.0,
                "error": str(e)
            }
    
    def validate_implementation_status(self, file_path: Path) -> Dict:
        """Validate implementation status indicators in a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            indicators_found = {}
            for indicator in self.status_indicators:
                count = content.count(indicator)
                indicators_found[indicator] = count
            
            total_indicators = sum(indicators_found.values())
            has_status_indicators = total_indicators > 0
            
            return {
                "indicators_found": indicators_found,
                "total_indicators": total_indicators,
                "has_status_indicators": has_status_indicators,
                "compliance_score": 1.0 if has_status_indicators else 0.0
            }
            
        except Exception as e:
            return {
                "indicators_found": {},
                "total_indicators": 0,
                "has_status_indicators": False,
                "compliance_score": 0.0,
                "error": str(e)
            }
    
    def validate_file_compliance(self, file_path: Path) -> Dict:
        """Validate complete constitutional compliance for a single file"""
        
        # Get file type and category
        file_type = file_path.suffix.lower()
        is_documentation = file_type in ['.md', '.txt', '.rst']
        is_config = file_type in ['.yaml', '.yml', '.json', '.toml']
        
        # Validate different aspects
        hash_validation = self.validate_constitutional_hash(file_path)
        performance_validation = self.validate_performance_targets(file_path)
        status_validation = self.validate_implementation_status(file_path)
        
        # Calculate overall compliance score
        weights = {
            "hash": 0.5,  # Constitutional hash is most important
            "performance": 0.3,  # Performance targets are important for docs
            "status": 0.2   # Status indicators are helpful
        }
        
        overall_score = (
            hash_validation["compliance_score"] * weights["hash"] +
            performance_validation["compliance_score"] * weights["performance"] +
            status_validation["compliance_score"] * weights["status"]
        )
        
        # Determine compliance level
        if overall_score >= 0.9:
            compliance_level = "EXCELLENT"
        elif overall_score >= 0.7:
            compliance_level = "GOOD"
        elif overall_score >= 0.5:
            compliance_level = "PARTIAL"
        else:
            compliance_level = "POOR"
        
        return {
            "file_path": str(file_path.relative_to(self.project_root)),
            "file_type": file_type,
            "is_documentation": is_documentation,
            "is_config": is_config,
            "hash_validation": hash_validation,
            "performance_validation": performance_validation,
            "status_validation": status_validation,
            "overall_score": overall_score,
            "compliance_level": compliance_level,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_compliance_summary(self, validation_results: List[Dict]) -> Dict:
        """Generate summary statistics from validation results"""
        
        total_files = len(validation_results)
        if total_files == 0:
            return {"error": "No files validated"}
        
        # Count by compliance level
        compliance_counts = {
            "EXCELLENT": 0,
            "GOOD": 0, 
            "PARTIAL": 0,
            "POOR": 0
        }
        
        # Aggregate scores
        total_score = 0
        hash_compliant = 0
        performance_compliant = 0
        status_compliant = 0
        
        for result in validation_results:
            compliance_counts[result["compliance_level"]] += 1
            total_score += result["overall_score"]
            
            if result["hash_validation"]["has_hash"]:
                hash_compliant += 1
            if result["performance_validation"]["compliance_score"] > 0.5:
                performance_compliant += 1
            if result["status_validation"]["has_status_indicators"]:
                status_compliant += 1
        
        average_score = total_score / total_files
        
        return {
            "total_files": total_files,
            "average_compliance_score": average_score,
            "compliance_distribution": compliance_counts,
            "hash_compliance_rate": (hash_compliant / total_files) * 100,
            "performance_compliance_rate": (performance_compliant / total_files) * 100,
            "status_compliance_rate": (status_compliant / total_files) * 100,
            "overall_compliance_rate": average_score * 100,
            "constitutional_hash": self.constitutional_hash,
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def execute_compliance_validation(self):
        """Execute comprehensive constitutional compliance validation"""
        print("🚀 Starting ACGS-2 Constitutional Compliance Validation")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        try:
            # Find documentation files
            doc_files = self.find_documentation_files()
            print(f"\n📁 Found {len(doc_files)} documentation files")
            
            # Validate each file
            print("\n🔍 Validating constitutional compliance...")
            validation_results = []
            
            for i, file_path in enumerate(doc_files, 1):
                if i % 20 == 0:  # Progress indicator
                    print(f"  Progress: {i}/{len(doc_files)} files validated")
                
                result = self.validate_file_compliance(file_path)
                validation_results.append(result)
            
            # Generate summary
            summary = self.generate_compliance_summary(validation_results)
            
            # Save detailed report
            report_path = self.project_root / "reports" / f"constitutional_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            full_report = {
                "summary": summary,
                "detailed_results": validation_results,
                "validation_metadata": {
                    "constitutional_hash": self.constitutional_hash,
                    "performance_targets": self.required_performance_targets,
                    "status_indicators": self.status_indicators,
                    "validation_timestamp": datetime.now().isoformat()
                }
            }
            
            with open(report_path, 'w') as f:
                json.dump(full_report, f, indent=2)
            
            # Print summary
            print(f"\n✅ Constitutional compliance validation completed!")
            print(f"📊 Summary:")
            print(f"  - Files validated: {summary['total_files']}")
            print(f"  - Overall compliance: {summary['overall_compliance_rate']:.1f}%")
            print(f"  - Hash compliance: {summary['hash_compliance_rate']:.1f}%")
            print(f"  - Performance compliance: {summary['performance_compliance_rate']:.1f}%")
            print(f"  - Status compliance: {summary['status_compliance_rate']:.1f}%")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            print(f"  - Report saved: {report_path}")
            
            # Compliance level breakdown
            print(f"\n📈 Compliance Distribution:")
            for level, count in summary['compliance_distribution'].items():
                percentage = (count / summary['total_files']) * 100
                print(f"  - {level}: {count} files ({percentage:.1f}%)")
            
            return summary['overall_compliance_rate'] >= 95.0
            
        except Exception as e:
            print(f"❌ Constitutional compliance validation failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    validator = ConstitutionalComplianceValidator(project_root)
    
    # Execute compliance validation
    success = validator.execute_compliance_validation()
    
    if success:
        print("\n🎉 ACGS-2 Constitutional Compliance Validation Complete!")
        print("✅ Target ≥95% compliance achieved!")
    else:
        print("\n🔄 Additional compliance improvements may be needed.")

if __name__ == "__main__":
    main()
