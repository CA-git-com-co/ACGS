"""
ACGS-2 Security and Quality Gates Validation Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests to validate security scanning, constitutional compliance, and quality assurance processes.
"""

import os
import yaml
import json
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class TestSecurityQualityGates:
    """Validate security and quality gate implementations."""
    
    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture(scope="class")
    def constitutional_hash(self) -> str:
        """Expected constitutional hash."""
        return "cdd01ef066bc6cf2"
    
    def test_constitutional_hash_environment(self, constitutional_hash: str):
        """Test that constitutional hash is properly set in environment."""
        env_hash = os.getenv("CONSTITUTIONAL_HASH")
        assert env_hash == constitutional_hash, f"Expected {constitutional_hash}, got {env_hash}"
    
    def test_security_workflow_structure(self, project_root: Path):
        """Test security workflow has proper structure and error handling."""
        security_workflow = project_root / ".github" / "workflows" / "security-consolidated.yml"
        assert security_workflow.exists(), "Security workflow must exist"
        
        with open(security_workflow) as f:
            workflow = yaml.safe_load(f)
        
        # Validate workflow structure
        assert "jobs" in workflow, "Security workflow must have jobs"
        jobs = workflow["jobs"]
        
        # Check for key security jobs
        expected_jobs = ["container-security", "secret-scan", "infrastructure-scan"]
        for job_name in expected_jobs:
            assert any(job_name in job_key for job_key in jobs.keys()), f"Missing security job: {job_name}"
    
    def test_constitutional_compliance_validation(self, project_root: Path, constitutional_hash: str):
        """Test constitutional compliance validation in security workflow."""
        security_workflow = project_root / ".github" / "workflows" / "security-consolidated.yml"
        content = security_workflow.read_text()
        
        # Check for constitutional compliance validation
        assert "Constitutional Compliance Validation" in content, "Missing constitutional compliance validation step"
        assert constitutional_hash in content, "Security workflow must reference constitutional hash"
        assert "CONSTITUTIONAL_HASH" in content, "Security workflow must use constitutional hash environment variable"
    
    def test_trivy_error_handling(self, project_root: Path):
        """Test Trivy container scanning has proper error handling."""
        security_workflow = project_root / ".github" / "workflows" / "security-consolidated.yml"
        content = security_workflow.read_text()
        
        # Check for Trivy configuration
        assert "trivy-action" in content, "Security workflow must include Trivy scanning"
        assert "continue-on-error: true" in content, "Trivy scan should have error handling"
        assert "Process Trivy Results" in content, "Must have Trivy results processing"
    
    def test_gitleaks_configuration_validation(self, project_root: Path, constitutional_hash: str):
        """Test GitLeaks configuration is properly set up."""
        gitleaks_config = project_root / ".gitleaks.toml"
        assert gitleaks_config.exists(), "GitLeaks configuration must exist"
        
        content = gitleaks_config.read_text()
        
        # Validate configuration content
        assert "constitutional-hash" in content, "GitLeaks config must include constitutional hash rule"
        assert constitutional_hash in content, "GitLeaks config must reference correct hash"
        assert "[allowlist]" in content, "GitLeaks config must have allowlist section"
        assert "regexes" in content, "GitLeaks config must have regex allowlist"
    
    def test_dockerfile_security_labels(self, project_root: Path, constitutional_hash: str):
        """Test Dockerfile has proper security labels."""
        dockerfile = project_root / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile must exist for security scanning"
        
        content = dockerfile.read_text()
        
        # Check for security labels
        assert "constitutional.hash" in content, "Dockerfile must have constitutional hash label"
        assert constitutional_hash in content, "Dockerfile must contain correct constitutional hash"
        assert "LABEL" in content, "Dockerfile must have metadata labels"
    
    def test_security_scan_artifacts(self, project_root: Path):
        """Test that security scan artifacts are properly configured."""
        security_workflow = project_root / ".github" / "workflows" / "security-consolidated.yml"
        content = security_workflow.read_text()
        
        # Check for artifact uploads
        assert "upload-sarif" in content, "Security workflow must upload SARIF results"
        assert "security-scan-summary.json" in content, "Must create security scan summary"
        assert "constitutional-compliance-report.json" in content, "Must create compliance report"
    
    def test_performance_targets_in_workflows(self, project_root: Path):
        """Test that performance targets are documented in workflows."""
        workflows_dir = project_root / ".github" / "workflows"
        
        performance_keywords = ["P99", "5ms", "100 RPS", "85%", "cache hit"]
        found_targets = False
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            for keyword in performance_keywords:
                if keyword in content:
                    found_targets = True
                    print(f"✅ Found performance target '{keyword}' in {workflow_file.name}")
                    break
        
        assert found_targets, "Workflows must reference ACGS-2 performance targets"
    
    def test_quality_gates_configuration(self, project_root: Path):
        """Test quality gates are properly configured."""
        main_workflow = project_root / ".github" / "workflows" / "main-ci-cd.yml"
        content = main_workflow.read_text()
        
        # Check for quality gate steps
        quality_checks = [
            "quality-gates",
            "Python Code Quality Checks",
            "Security Scanning",
            "Quality Check Summary"
        ]
        
        for check in quality_checks:
            assert check in content, f"Missing quality check: {check}"
    
    def test_error_handling_patterns(self, project_root: Path):
        """Test that workflows have proper error handling patterns."""
        workflows_dir = project_root / ".github" / "workflows"
        
        error_handling_patterns = [
            "continue-on-error",
            "if: always()",
            "|| echo",
            "|| true",
            "exit 1"
        ]
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            has_error_handling = any(pattern in content for pattern in error_handling_patterns)
            assert has_error_handling, f"Workflow {workflow_file.name} must have error handling"
    
    def test_constitutional_hash_consistency_across_workflows(self, project_root: Path, constitutional_hash: str):
        """Test constitutional hash consistency across all workflows."""
        workflows_dir = project_root / ".github" / "workflows"
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            if "constitutional" in content.lower():
                assert constitutional_hash in content, f"Constitutional hash mismatch in {workflow_file.name}"
                print(f"✅ Constitutional hash validated in {workflow_file.name}")
    
    def test_security_workflow_timeout_configuration(self, project_root: Path):
        """Test that security workflows have appropriate timeouts."""
        security_workflow = project_root / ".github" / "workflows" / "security-consolidated.yml"
        
        with open(security_workflow) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get("jobs", {})
        for job_name, job_config in jobs.items():
            if "timeout-minutes" in job_config:
                timeout = job_config["timeout-minutes"]
                assert timeout <= 30, f"Job {job_name} timeout too high: {timeout} minutes"
                print(f"✅ Job {job_name} has appropriate timeout: {timeout} minutes")
    
    def test_workflow_dependencies_and_needs(self, project_root: Path):
        """Test that workflows have proper job dependencies."""
        main_workflow = project_root / ".github" / "workflows" / "main-ci-cd.yml"
        
        with open(main_workflow) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get("jobs", {})
        
        # Check that critical jobs have proper dependencies
        if "deploy" in jobs:
            deploy_job = jobs["deploy"]
            needs = deploy_job.get("needs", [])
            assert "security-validation" in needs or any("security" in need for need in needs), "Deploy job must depend on security validation"
    
    @pytest.mark.skipif(not os.getenv("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
    def test_workflow_syntax_validation(self, project_root: Path):
        """Test that all workflows have valid YAML syntax and GitHub Actions structure."""
        workflows_dir = project_root / ".github" / "workflows"
        
        for workflow_file in workflows_dir.glob("*.yml"):
            try:
                # Validate YAML syntax
                with open(workflow_file) as f:
                    workflow = yaml.safe_load(f)
                
                # Validate basic GitHub Actions structure
                assert "name" in workflow or "on" in workflow or True in workflow, f"Invalid workflow structure in {workflow_file.name}"
                
                print(f"✅ {workflow_file.name} has valid syntax and structure")
                
            except Exception as e:
                pytest.fail(f"Workflow validation failed for {workflow_file.name}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
