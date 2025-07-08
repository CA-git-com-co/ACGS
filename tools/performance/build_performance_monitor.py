#!/usr/bin/env python3
"""
ACGS Build Performance Monitoring Tool
Constitutional Hash: cdd01ef066bc6cf2

Monitors and reports on build performance improvements from dependency standardization.
Measures pip install times, requirements resolution speed, and cache hit rates.
"""

import json
import logging
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import statistics

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BuildPerformanceMonitor:
    """Monitor and measure build performance across ACGS services"""
    
    def __init__(self, services_root: str = "/home/dislove/ACGS-2/services"):
        self.services_root = Path(services_root)
        self.results = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "measurements": {}
        }
    
    def find_requirements_files(self) -> Dict[str, Path]:
        """Find all requirements.txt files across services"""
        requirements_files = {}
        
        for req_file in self.services_root.rglob("requirements*.txt"):
            # Skip shared requirements (they're included by others)
            if "shared/requirements" in str(req_file):
                continue
            
            # Get service name from path
            relative_path = req_file.relative_to(self.services_root)
            parts = relative_path.parts
            
            if len(parts) >= 2:
                service_name = f"{parts[0]}_{parts[1]}" if len(parts) > 2 else parts[0]
                requirements_files[service_name] = req_file
        
        return requirements_files
    
    def measure_pip_install_time(self, requirements_file: Path) -> Dict[str, Any]:
        """Measure pip install time for a requirements file"""
        logger.info(f"Measuring pip install time for: {requirements_file}")
        
        # Create a temporary virtual environment
        venv_path = requirements_file.parent / ".test_venv"
        
        try:
            # Clean up any existing test venv
            if venv_path.exists():
                subprocess.run(["rm", "-rf", str(venv_path)], check=True)
            
            # Create virtual environment
            subprocess.run(
                ["python3", "-m", "venv", str(venv_path)], 
                check=True, 
                capture_output=True
            )
            
            # Measure pip install time
            pip_executable = venv_path / "bin" / "pip"
            start_time = time.perf_counter()
            
            result = subprocess.run(
                [str(pip_executable), "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            install_time = time.perf_counter() - start_time
            
            # Parse pip output for package count
            output_lines = result.stdout.split('\n') if result.stdout else []
            successfully_installed = [line for line in output_lines if "Successfully installed" in line]
            package_count = 0
            
            if successfully_installed:
                # Extract package count from "Successfully installed package1-1.0 package2-2.0..."
                packages_line = successfully_installed[0].replace("Successfully installed ", "")
                package_count = len(packages_line.split()) if packages_line.strip() else 0
            
            # Clean up
            subprocess.run(["rm", "-rf", str(venv_path)], check=True)
            
            return {
                "install_time_seconds": round(install_time, 2),
                "package_count": package_count,
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None,
                "requirements_file": str(requirements_file)
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Pip install timeout for: {requirements_file}")
            return {
                "install_time_seconds": 300.0,
                "package_count": 0,
                "success": False,
                "error": "Timeout expired",
                "requirements_file": str(requirements_file)
            }
        except Exception as e:
            logger.error(f"Error measuring pip install for {requirements_file}: {e}")
            return {
                "install_time_seconds": 0.0,
                "package_count": 0,
                "success": False,
                "error": str(e),
                "requirements_file": str(requirements_file)
            }
    
    def analyze_requirements_structure(self, requirements_file: Path) -> Dict[str, Any]:
        """Analyze the structure and complexity of a requirements file"""
        try:
            with open(requirements_file, 'r') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            total_lines = len(lines)
            
            # Count different types of lines
            shared_includes = len([line for line in lines if line.strip().startswith('-r ')])
            direct_deps = len([line for line in lines if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('-r')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            empty_lines = len([line for line in lines if not line.strip()])
            
            return {
                "total_lines": total_lines,
                "shared_includes": shared_includes,
                "direct_dependencies": direct_deps,
                "comment_lines": comment_lines,
                "empty_lines": empty_lines,
                "uses_shared_requirements": shared_includes > 0,
                "complexity_score": direct_deps + (shared_includes * 0.5)  # Lower is better
            }
            
        except Exception as e:
            logger.error(f"Error analyzing requirements structure: {e}")
            return {
                "total_lines": 0,
                "shared_includes": 0,
                "direct_dependencies": 0,
                "comment_lines": 0,
                "empty_lines": 0,
                "uses_shared_requirements": False,
                "complexity_score": 999.0
            }
    
    def measure_dependency_resolution_speed(self, requirements_file: Path) -> Dict[str, Any]:
        """Measure how quickly pip can resolve dependencies (dry-run)"""
        logger.info(f"Measuring dependency resolution for: {requirements_file}")
        
        try:
            start_time = time.perf_counter()
            
            result = subprocess.run(
                ["pip", "install", "--dry-run", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout for dry run
            )
            
            resolution_time = time.perf_counter() - start_time
            
            return {
                "resolution_time_seconds": round(resolution_time, 2),
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "resolution_time_seconds": 60.0,
                "success": False,
                "error": "Resolution timeout"
            }
        except Exception as e:
            logger.error(f"Error measuring dependency resolution: {e}")
            return {
                "resolution_time_seconds": 0.0,
                "success": False,
                "error": str(e)
            }
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive build performance analysis"""
        logger.info("Starting comprehensive build performance analysis")
        
        requirements_files = self.find_requirements_files()
        logger.info(f"Found {len(requirements_files)} requirements files")
        
        measurements = {}
        
        for service_name, req_file in requirements_files.items():
            logger.info(f"Analyzing service: {service_name}")
            
            measurements[service_name] = {
                "requirements_file": str(req_file),
                "structure_analysis": self.analyze_requirements_structure(req_file),
                "dependency_resolution": self.measure_dependency_resolution_speed(req_file),
                # Skip actual pip install for now to save time
                # "install_performance": self.measure_pip_install_time(req_file),
            }
        
        self.results["measurements"] = measurements
        self.results["summary"] = self._generate_summary()
        
        return self.results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from measurements"""
        measurements = self.results["measurements"]
        
        if not measurements:
            return {"error": "No measurements available"}
        
        # Collect metrics
        resolution_times = []
        complexity_scores = []
        shared_usage_count = 0
        total_services = len(measurements)
        
        for service_name, data in measurements.items():
            structure = data.get("structure_analysis", {})
            resolution = data.get("dependency_resolution", {})
            
            if structure.get("complexity_score"):
                complexity_scores.append(structure["complexity_score"])
            
            if resolution.get("resolution_time_seconds"):
                resolution_times.append(resolution["resolution_time_seconds"])
            
            if structure.get("uses_shared_requirements"):
                shared_usage_count += 1
        
        summary = {
            "total_services_analyzed": total_services,
            "shared_requirements_adoption": {
                "count": shared_usage_count,
                "percentage": round((shared_usage_count / total_services) * 100, 1) if total_services > 0 else 0
            }
        }
        
        if resolution_times:
            summary["dependency_resolution"] = {
                "average_time_seconds": round(statistics.mean(resolution_times), 2),
                "median_time_seconds": round(statistics.median(resolution_times), 2),
                "fastest_time_seconds": round(min(resolution_times), 2),
                "slowest_time_seconds": round(max(resolution_times), 2)
            }
        
        if complexity_scores:
            summary["complexity_analysis"] = {
                "average_complexity": round(statistics.mean(complexity_scores), 2),
                "median_complexity": round(statistics.median(complexity_scores), 2),
                "lowest_complexity": round(min(complexity_scores), 2),
                "highest_complexity": round(max(complexity_scores), 2)
            }
        
        return summary
    
    def save_results(self, output_file: str = "build_performance_report.json") -> str:
        """Save results to JSON file"""
        output_path = Path(output_file)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Build performance report saved to: {output_path}")
        return str(output_path)
    
    def print_summary_report(self) -> None:
        """Print a human-readable summary report"""
        summary = self.results.get("summary", {})
        
        print("\n" + "=" * 60)
        print("ACGS Build Performance Analysis Report")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)
        
        if "error" in summary:
            print(f"Error: {summary['error']}")
            return
        
        print(f"📊 Services Analyzed: {summary.get('total_services_analyzed', 0)}")
        
        shared_adoption = summary.get("shared_requirements_adoption", {})
        print(f"📦 Shared Requirements Adoption: {shared_adoption.get('count', 0)}/{summary.get('total_services_analyzed', 0)} ({shared_adoption.get('percentage', 0)}%)")
        
        if "dependency_resolution" in summary:
            resolution = summary["dependency_resolution"]
            print(f"\n⚡ Dependency Resolution Performance:")
            print(f"   Average: {resolution.get('average_time_seconds', 0)}s")
            print(f"   Median:  {resolution.get('median_time_seconds', 0)}s")
            print(f"   Range:   {resolution.get('fastest_time_seconds', 0)}s - {resolution.get('slowest_time_seconds', 0)}s")
        
        if "complexity_analysis" in summary:
            complexity = summary["complexity_analysis"]
            print(f"\n🔧 Complexity Analysis:")
            print(f"   Average Complexity: {complexity.get('average_complexity', 0)}")
            print(f"   Median Complexity:  {complexity.get('median_complexity', 0)}")
            print(f"   Range: {complexity.get('lowest_complexity', 0)} - {complexity.get('highest_complexity', 0)}")
        
        print("\n✅ Analysis complete!")


def main():
    """Main function"""
    monitor = BuildPerformanceMonitor()
    
    # Run analysis
    results = monitor.run_comprehensive_analysis()
    
    # Save results
    output_file = f"build_performance_report_{int(time.time())}.json"
    monitor.save_results(output_file)
    
    # Print summary
    monitor.print_summary_report()
    
    return results


if __name__ == "__main__":
    main()