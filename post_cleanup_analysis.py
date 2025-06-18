#!/usr/bin/env python3
"""
ACGS-1 Post-Cleanup Analysis Script
Comprehensive analysis of three critical directories after cleanup.
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class PostCleanupAnalyzer:
    """Comprehensive post-cleanup analysis for ACGS-1."""
    
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.analysis_timestamp = datetime.now().isoformat()
        self.report = {
            "analysis_timestamp": self.analysis_timestamp,
            "project_root": str(self.project_root),
            "directories_analyzed": ["blockchain", "core", "tools"],
            "constitutional_hash": "cdd01ef066bc6cf2",
            "analysis_results": {},
            "optimization_recommendations": [],
            "risk_assessment": {},
            "validation_status": {}
        }
    
    def analyze_blockchain_directory(self) -> Dict[str, Any]:
        """Analyze blockchain directory structure and Quantumagi deployment."""
        print("🔍 Analyzing blockchain directory...")
        
        blockchain_dir = self.project_root / "blockchain"
        analysis = {
            "directory_path": str(blockchain_dir),
            "exists": blockchain_dir.exists(),
            "anchor_programs": {},
            "quantumagi_deployment": {},
            "build_system": {},
            "structure_report": {}
        }
        
        if not blockchain_dir.exists():
            analysis["error"] = "Blockchain directory not found"
            return analysis
        
        # Analyze Anchor programs
        programs_dir = blockchain_dir / "programs"
        if programs_dir.exists():
            for program_dir in programs_dir.iterdir():
                if program_dir.is_dir():
                    cargo_toml = program_dir / "Cargo.toml"
                    src_dir = program_dir / "src"
                    analysis["anchor_programs"][program_dir.name] = {
                        "path": str(program_dir),
                        "has_cargo_toml": cargo_toml.exists(),
                        "has_src_dir": src_dir.exists(),
                        "buildable": cargo_toml.exists() and src_dir.exists()
                    }
        
        # Verify constitutional hash
        constitution_file = blockchain_dir / "constitution_data.json"
        if constitution_file.exists():
            try:
                with open(constitution_file, 'r') as f:
                    constitution_data = json.load(f)
                    stored_hash = constitution_data.get("constitution", {}).get("hash")
                    analysis["quantumagi_deployment"]["constitutional_hash_verified"] = (
                        stored_hash == "cdd01ef066bc6cf2"
                    )
                    analysis["quantumagi_deployment"]["stored_hash"] = stored_hash
            except Exception as e:
                analysis["quantumagi_deployment"]["constitution_error"] = str(e)
        
        # Check deployment files
        deployment_files = [
            "governance_accounts.json",
            "initial_policies.json", 
            "quantumagi-deployment/complete_deployment.sh"
        ]
        
        for file_path in deployment_files:
            full_path = blockchain_dir / file_path
            analysis["quantumagi_deployment"][file_path] = {
                "exists": full_path.exists(),
                "size_bytes": full_path.stat().st_size if full_path.exists() else 0
            }
        
        # Analyze build system
        anchor_toml = blockchain_dir / "Anchor.toml"
        cargo_toml = blockchain_dir / "Cargo.toml"
        target_dir = blockchain_dir / "target"
        
        analysis["build_system"] = {
            "anchor_toml_exists": anchor_toml.exists(),
            "cargo_toml_exists": cargo_toml.exists(),
            "target_dir_exists": target_dir.exists(),
            "target_dir_size_mb": self._get_directory_size_mb(target_dir) if target_dir.exists() else 0
        }
        
        # Generate structure report
        analysis["structure_report"] = self._generate_directory_structure(blockchain_dir, max_depth=2)
        
        return analysis
    
    def analyze_core_directory(self) -> Dict[str, Any]:
        """Analyze core directory and compare with services/core."""
        print("🔍 Analyzing core directory...")
        
        core_dir = self.project_root / "core"
        services_core_dir = self.project_root / "services" / "core"
        
        analysis = {
            "directory_path": str(core_dir),
            "exists": core_dir.exists(),
            "services_core_comparison": {},
            "duplication_assessment": {},
            "integration_analysis": {},
            "structure_report": {}
        }
        
        if not core_dir.exists():
            analysis["error"] = "Core directory not found"
            return analysis
        
        # Compare with services/core
        if services_core_dir.exists():
            core_files = list(core_dir.glob("**/*.py"))
            services_core_files = list(services_core_dir.glob("**/*.py"))
            
            analysis["services_core_comparison"] = {
                "core_python_files": len(core_files),
                "services_core_python_files": len(services_core_files),
                "core_file_list": [str(f.relative_to(core_dir)) for f in core_files],
                "potential_duplicates": self._find_potential_duplicates(core_files, services_core_files)
            }
        
        # Analyze file purposes
        for py_file in core_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                analysis["integration_analysis"][py_file.name] = {
                    "size_bytes": py_file.stat().st_size,
                    "purpose": self._analyze_file_purpose(py_file),
                    "imports_services": self._check_services_imports(py_file)
                }
        
        analysis["structure_report"] = self._generate_directory_structure(core_dir, max_depth=3)
        
        return analysis
    
    def analyze_tools_directory(self) -> Dict[str, Any]:
        """Analyze tools directory for conflicts and operational status."""
        print("🔍 Analyzing tools directory...")
        
        tools_dir = self.project_root / "tools"
        analysis = {
            "directory_path": str(tools_dir),
            "exists": tools_dir.exists(),
            "tool_inventory": {},
            "conflict_detection": {},
            "operational_integration": {},
            "structure_report": {}
        }
        
        if not tools_dir.exists():
            analysis["error"] = "Tools directory not found"
            return analysis
        
        # Inventory tools
        for item in tools_dir.iterdir():
            if item.is_file():
                analysis["tool_inventory"][item.name] = {
                    "type": "file",
                    "size_bytes": item.stat().st_size,
                    "extension": item.suffix,
                    "classification": self._classify_tool(item)
                }
            elif item.is_dir():
                analysis["tool_inventory"][item.name] = {
                    "type": "directory", 
                    "size_mb": self._get_directory_size_mb(item),
                    "classification": self._classify_tool_directory(item)
                }
        
        # Check for conflicts with cleanup scripts
        cleanup_scripts = [
            "comprehensive_cleanup_analysis.py",
            "comprehensive_cleanup_plan.py",
            "final_cleanup.py"
        ]
        
        for script in cleanup_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                analysis["conflict_detection"][script] = {
                    "exists_in_root": True,
                    "conflicts_with_tools": script in analysis["tool_inventory"]
                }
        
        analysis["structure_report"] = self._generate_directory_structure(tools_dir, max_depth=2)
        
        return analysis
    
    def _get_directory_size_mb(self, directory: Path) -> float:
        """Calculate directory size in MB."""
        try:
            total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    def _generate_directory_structure(self, directory: Path, max_depth: int = 2) -> Dict[str, Any]:
        """Generate directory structure report."""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "total_size_mb": 0.0,
            "file_types": {},
            "largest_files": []
        }
        
        try:
            all_files = list(directory.rglob('*'))
            files = [f for f in all_files if f.is_file()]
            dirs = [f for f in all_files if f.is_dir()]
            
            structure["total_files"] = len(files)
            structure["total_directories"] = len(dirs)
            structure["total_size_mb"] = self._get_directory_size_mb(directory)
            
            # Count file types
            for file in files:
                ext = file.suffix.lower() or "no_extension"
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
            
            # Find largest files
            file_sizes = [(f, f.stat().st_size) for f in files]
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            structure["largest_files"] = [
                {"path": str(f.relative_to(directory)), "size_mb": round(size / (1024 * 1024), 2)}
                for f, size in file_sizes[:10]
            ]
            
        except Exception as e:
            structure["error"] = str(e)
        
        return structure
    
    def _find_potential_duplicates(self, core_files: List[Path], services_files: List[Path]) -> List[str]:
        """Find potential duplicate files between core and services/core."""
        core_names = {f.name for f in core_files}
        services_names = {f.name for f in services_files}
        return list(core_names.intersection(services_names))
    
    def _analyze_file_purpose(self, file_path: Path) -> str:
        """Analyze file purpose from content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)  # Read first 500 chars
                if "constitutional" in content.lower():
                    return "constitutional_governance"
                elif "multi_model" in content.lower() or "consensus" in content.lower():
                    return "multi_model_consensus"
                elif "wina" in content.lower() or "oversight" in content.lower():
                    return "oversight_coordination"
                else:
                    return "utility_module"
        except:
            return "unknown"
    
    def _check_services_imports(self, file_path: Path) -> bool:
        """Check if file imports from services directory."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return "from services" in content or "import services" in content
        except:
            return False
    
    def _classify_tool(self, tool_path: Path) -> str:
        """Classify individual tool file."""
        if tool_path.suffix == ".py":
            if "benchmark" in tool_path.name.lower():
                return "performance_testing"
            elif "cleanup" in tool_path.name.lower():
                return "maintenance"
            else:
                return "development_utility"
        elif tool_path.suffix == ".md":
            return "documentation"
        else:
            return "configuration"
    
    def _classify_tool_directory(self, tool_dir: Path) -> str:
        """Classify tool directory."""
        name = tool_dir.name.lower()
        if "nemo" in name:
            return "ai_framework"
        elif "swe" in name or "agent" in name:
            return "development_agent"
        elif "evaluation" in name:
            return "testing_framework"
        elif "inspector" in name:
            return "debugging_tool"
        else:
            return "utility_collection"
    
    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Analyze results to generate recommendations
        blockchain_analysis = self.report["analysis_results"].get("blockchain", {})
        core_analysis = self.report["analysis_results"].get("core", {})
        tools_analysis = self.report["analysis_results"].get("tools", {})
        
        # Blockchain recommendations
        if blockchain_analysis.get("build_system", {}).get("target_dir_size_mb", 0) > 100:
            recommendations.append({
                "priority": "Medium",
                "category": "Storage Optimization",
                "description": "Large target directory detected in blockchain",
                "action": "Consider cleaning build artifacts with 'anchor clean'",
                "impact": "Reduce storage usage"
            })
        
        # Core directory recommendations
        if core_analysis.get("services_core_comparison", {}).get("potential_duplicates"):
            recommendations.append({
                "priority": "High", 
                "category": "Code Duplication",
                "description": "Potential duplicate files between core/ and services/core/",
                "action": "Review and consolidate duplicate implementations",
                "impact": "Reduce maintenance overhead and confusion"
            })
        
        # Tools recommendations
        tools_size = tools_analysis.get("structure_report", {}).get("total_size_mb", 0)
        if tools_size > 500:
            recommendations.append({
                "priority": "Low",
                "category": "Storage Optimization", 
                "description": "Large tools directory detected",
                "action": "Review and archive unused development tools",
                "impact": "Reduce repository size"
            })
        
        return recommendations
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete post-cleanup analysis."""
        print("🚀 Starting ACGS-1 Post-Cleanup Analysis...")
        print("=" * 50)
        
        # Analyze each directory
        self.report["analysis_results"]["blockchain"] = self.analyze_blockchain_directory()
        self.report["analysis_results"]["core"] = self.analyze_core_directory()
        self.report["analysis_results"]["tools"] = self.analyze_tools_directory()
        
        # Generate recommendations
        self.report["optimization_recommendations"] = self.generate_optimization_recommendations()
        
        # Validate Quantumagi deployment
        self.report["validation_status"]["quantumagi_deployment"] = self._validate_quantumagi_deployment()
        
        # Generate risk assessment
        self.report["risk_assessment"] = self._generate_risk_assessment()
        
        print("✅ Analysis completed successfully!")
        return self.report
    
    def _validate_quantumagi_deployment(self) -> Dict[str, Any]:
        """Validate Quantumagi deployment status."""
        blockchain_analysis = self.report["analysis_results"].get("blockchain", {})
        
        validation = {
            "constitutional_hash_preserved": False,
            "deployment_files_intact": False,
            "anchor_programs_buildable": False,
            "overall_status": "unknown"
        }
        
        # Check constitutional hash
        quantumagi_data = blockchain_analysis.get("quantumagi_deployment", {})
        validation["constitutional_hash_preserved"] = quantumagi_data.get("constitutional_hash_verified", False)
        
        # Check deployment files
        required_files = ["governance_accounts.json", "initial_policies.json", "quantumagi-deployment/complete_deployment.sh"]
        files_exist = all(
            quantumagi_data.get(file, {}).get("exists", False) 
            for file in required_files
        )
        validation["deployment_files_intact"] = files_exist
        
        # Check Anchor programs
        anchor_programs = blockchain_analysis.get("anchor_programs", {})
        programs_buildable = all(
            program.get("buildable", False) 
            for program in anchor_programs.values()
        )
        validation["anchor_programs_buildable"] = programs_buildable
        
        # Overall status
        if all([validation["constitutional_hash_preserved"], 
                validation["deployment_files_intact"], 
                validation["anchor_programs_buildable"]]):
            validation["overall_status"] = "fully_operational"
        elif validation["constitutional_hash_preserved"] and validation["deployment_files_intact"]:
            validation["overall_status"] = "operational_with_warnings"
        else:
            validation["overall_status"] = "requires_attention"
        
        return validation
    
    def _generate_risk_assessment(self) -> Dict[str, Any]:
        """Generate risk assessment for identified issues."""
        risk_assessment = {
            "critical_risks": [],
            "high_risks": [],
            "medium_risks": [],
            "low_risks": []
        }
        
        # Analyze for risks based on findings
        blockchain_analysis = self.report["analysis_results"].get("blockchain", {})
        core_analysis = self.report["analysis_results"].get("core", {})
        
        # Critical risks
        if not blockchain_analysis.get("quantumagi_deployment", {}).get("constitutional_hash_verified", False):
            risk_assessment["critical_risks"].append({
                "description": "Constitutional hash mismatch or missing",
                "impact": "Governance system integrity compromised",
                "mitigation": "Verify and restore constitutional data"
            })
        
        # High risks
        duplicates = core_analysis.get("services_core_comparison", {}).get("potential_duplicates", [])
        if duplicates:
            risk_assessment["high_risks"].append({
                "description": f"Potential code duplication: {', '.join(duplicates)}",
                "impact": "Maintenance complexity and potential inconsistencies",
                "mitigation": "Consolidate duplicate implementations"
            })
        
        return risk_assessment
    
    def save_report(self, filename: str = None) -> str:
        """Save analysis report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"post_cleanup_analysis_report_{timestamp}.json"
        
        report_path = self.project_root / filename
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        
        print(f"📄 Analysis report saved to: {report_path}")
        return str(report_path)


if __name__ == "__main__":
    analyzer = PostCleanupAnalyzer()
    report = analyzer.run_complete_analysis()
    report_file = analyzer.save_report()
    
    # Print summary
    print("\n" + "=" * 80)
    print("ACGS-1 POST-CLEANUP ANALYSIS SUMMARY")
    print("=" * 80)
    
    validation = report["validation_status"]["quantumagi_deployment"]
    print(f"\n🔍 Quantumagi Deployment Status: {validation['overall_status'].upper()}")
    print(f"   Constitutional Hash: {'✅' if validation['constitutional_hash_preserved'] else '❌'}")
    print(f"   Deployment Files: {'✅' if validation['deployment_files_intact'] else '❌'}")
    print(f"   Anchor Programs: {'✅' if validation['anchor_programs_buildable'] else '❌'}")
    
    print(f"\n📊 Optimization Recommendations: {len(report['optimization_recommendations'])}")
    for rec in report['optimization_recommendations']:
        print(f"   {rec['priority']}: {rec['description']}")
    
    print(f"\n⚠️  Risk Assessment:")
    risks = report['risk_assessment']
    print(f"   Critical: {len(risks['critical_risks'])}")
    print(f"   High: {len(risks['high_risks'])}")
    print(f"   Medium: {len(risks['medium_risks'])}")
    print(f"   Low: {len(risks['low_risks'])}")
    
    print(f"\n📄 Full report saved to: {report_file}")
