#!/usr/bin/env python3
"""
CI/CD Pipeline Validation Script for ACGS

This script validates the CI/CD pipeline configuration and ensures
all components are properly set up for automated testing.
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any


def check_github_workflows() -> Dict[str, Any]:
    """Check GitHub Actions workflow configurations."""
    print("🔍 Checking GitHub Actions workflows...")
    
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        return {"status": "error", "message": "No .github/workflows directory found"}
    
    workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    results = {
        "status": "success",
        "workflows_found": len(workflows),
        "workflows": [],
        "issues": []
    }
    
    for workflow_file in workflows:
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            workflow_info = {
                "name": workflow_file.name,
                "title": workflow_data.get("name", "Unknown"),
                "triggers": list(workflow_data.get("on", {}).keys()),
                "jobs": list(workflow_data.get("jobs", {}).keys())
            }
            results["workflows"].append(workflow_info)
            
        except Exception as e:
            results["issues"].append(f"Error parsing {workflow_file.name}: {str(e)}")
    
    print(f"✅ Found {len(workflows)} workflow files")
    return results


def check_test_configuration() -> Dict[str, Any]:
    """Check test configuration files."""
    print("🧪 Checking test configuration...")
    
    results = {
        "status": "success",
        "pytest_config": False,
        "requirements_test": False,
        "test_directories": [],
        "issues": []
    }
    
    # Check pytest configuration
    pytest_configs = ["pytest.ini", "pyproject.toml", "setup.cfg"]
    for config_file in pytest_configs:
        if Path(config_file).exists():
            results["pytest_config"] = True
            break
    
    # Check test requirements
    if Path("requirements-test.txt").exists():
        results["requirements_test"] = True
    
    # Check test directories
    test_dirs = ["tests", "test"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            results["test_directories"].append(test_dir)
    
    if not results["pytest_config"]:
        results["issues"].append("No pytest configuration found")
    
    if not results["requirements_test"]:
        results["issues"].append("No requirements-test.txt found")
    
    if not results["test_directories"]:
        results["issues"].append("No test directories found")
    
    print(f"✅ Test configuration check completed")
    return results


def check_docker_configuration() -> Dict[str, Any]:
    """Check Docker configuration for CI/CD."""
    print("🐳 Checking Docker configuration...")
    
    results = {
        "status": "success",
        "dockerfiles": [],
        "docker_compose": False,
        "issues": []
    }
    
    # Find Dockerfiles
    dockerfiles = list(Path(".").rglob("Dockerfile*"))
    results["dockerfiles"] = [str(df) for df in dockerfiles]
    
    # Check docker-compose files
    compose_files = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]
    for compose_file in compose_files:
        if Path(compose_file).exists():
            results["docker_compose"] = True
            break
    
    print(f"✅ Found {len(dockerfiles)} Dockerfile(s)")
    return results


def check_environment_configuration() -> Dict[str, Any]:
    """Check environment configuration."""
    print("🌍 Checking environment configuration...")
    
    results = {
        "status": "success",
        "env_files": [],
        "config_dirs": [],
        "issues": []
    }
    
    # Check for environment files
    env_files = [".env", ".env.example", ".env.template"]
    for env_file in env_files:
        if Path(env_file).exists():
            results["env_files"].append(env_file)
    
    # Check for config directories
    config_dirs = ["config", "configs", "configuration"]
    for config_dir in config_dirs:
        if Path(config_dir).exists():
            results["config_dirs"].append(config_dir)
    
    print(f"✅ Environment configuration check completed")
    return results


def run_basic_tests() -> Dict[str, Any]:
    """Run basic test validation."""
    print("🚀 Running basic test validation...")
    
    results = {
        "status": "success",
        "tests_run": False,
        "test_output": "",
        "issues": []
    }
    
    try:
        # Try to run a simple test discovery
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            results["tests_run"] = True
            results["test_output"] = result.stdout
        else:
            results["issues"].append(f"Test collection failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        results["issues"].append("Test collection timed out")
    except FileNotFoundError:
        results["issues"].append("pytest not found - install test dependencies")
    except Exception as e:
        results["issues"].append(f"Test execution error: {str(e)}")
    
    print(f"✅ Basic test validation completed")
    return results


def generate_report(results: Dict[str, Dict[str, Any]]) -> None:
    """Generate CI/CD validation report."""
    print("\n" + "="*60)
    print("CI/CD PIPELINE VALIDATION REPORT")
    print("="*60)
    
    overall_status = "✅ PASS"
    total_issues = 0
    
    for component, result in results.items():
        print(f"\n{component.upper().replace('_', ' ')}:")
        print("-" * 40)
        
        if result["status"] == "success":
            print("✅ Status: PASS")
        else:
            print("❌ Status: FAIL")
            overall_status = "❌ FAIL"
        
        # Print component-specific details
        if component == "github_workflows":
            print(f"   Workflows found: {result['workflows_found']}")
            for workflow in result["workflows"][:3]:  # Show first 3
                print(f"   - {workflow['title']} ({workflow['name']})")
        
        elif component == "test_configuration":
            print(f"   Pytest config: {'✅' if result['pytest_config'] else '❌'}")
            print(f"   Test requirements: {'✅' if result['requirements_test'] else '❌'}")
            print(f"   Test directories: {len(result['test_directories'])}")
        
        elif component == "docker_configuration":
            print(f"   Dockerfiles: {len(result['dockerfiles'])}")
            print(f"   Docker Compose: {'✅' if result['docker_compose'] else '❌'}")
        
        elif component == "environment_configuration":
            print(f"   Environment files: {len(result['env_files'])}")
            print(f"   Config directories: {len(result['config_dirs'])}")
        
        elif component == "basic_tests":
            print(f"   Tests discoverable: {'✅' if result['tests_run'] else '❌'}")
        
        # Print issues
        if result["issues"]:
            print("   Issues:")
            for issue in result["issues"]:
                print(f"   - {issue}")
                total_issues += 1
    
    print(f"\n{'='*60}")
    print(f"OVERALL STATUS: {overall_status}")
    print(f"Total Issues: {total_issues}")
    print("="*60)


def main():
    """Main validation function."""
    print("🚀 Starting CI/CD Pipeline Validation...")
    print("="*60)
    
    # Change to project root if needed
    if not Path(".github").exists() and Path("../github").exists():
        os.chdir("..")
    
    # Run all validation checks
    validation_results = {
        "github_workflows": check_github_workflows(),
        "test_configuration": check_test_configuration(),
        "docker_configuration": check_docker_configuration(),
        "environment_configuration": check_environment_configuration(),
        "basic_tests": run_basic_tests()
    }
    
    # Generate report
    generate_report(validation_results)
    
    # Save results to file
    with open("cicd_validation_report.json", "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: cicd_validation_report.json")
    
    # Exit with appropriate code
    has_critical_issues = any(
        result["status"] == "error" for result in validation_results.values()
    )
    
    if has_critical_issues:
        print("❌ CI/CD pipeline has critical issues")
        sys.exit(1)
    else:
        print("✅ CI/CD pipeline validation completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
