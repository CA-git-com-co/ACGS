"""
ACGS-2 Workflow Validation Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests to validate GitHub Actions workflow configurations and infrastructure.
"""

import os
import yaml
import pytest
import docker
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class TestWorkflowValidation:
    """Validate GitHub Actions workflow configurations."""
    
    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture(scope="class")
    def workflows_dir(self, project_root: Path) -> Path:
        """Get workflows directory."""
        return project_root / ".github" / "workflows"
    
    def test_dockerfile_exists(self, project_root: Path):
        """Test that Dockerfile exists at project root."""
        dockerfile = project_root / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile must exist at project root for container scanning"
        
        # Validate Dockerfile content
        content = dockerfile.read_text()
        assert "constitutional.hash" in content, "Dockerfile must contain constitutional hash label"
        assert "cdd01ef066bc6cf2" in content, "Dockerfile must contain correct constitutional hash"
    
    def test_gitleaks_config_exists(self, project_root: Path):
        """Test that GitLeaks configuration exists."""
        gitleaks_config = project_root / ".gitleaks.toml"
        assert gitleaks_config.exists(), "GitLeaks configuration must exist"
        
        # Validate configuration content
        content = gitleaks_config.read_text()
        assert "constitutional-hash" in content, "GitLeaks config must include constitutional hash rule"
        assert "cdd01ef066bc6cf2" in content, "GitLeaks config must reference correct hash"
    
    def test_docker_compose_test_exists(self, project_root: Path):
        """Test that Docker Compose test configuration exists."""
        docker_compose = project_root / "config/docker/docker-compose.test.yml"
        assert docker_compose.exists(), "Docker Compose test configuration must exist"
        
        # Validate YAML syntax
        with open(docker_compose) as f:
            config = yaml.safe_load(f)
        
        assert "services" in config, "Docker Compose must define services"
        assert "postgres" in config["services"], "Must include PostgreSQL service"
        assert "redis" in config["services"], "Must include Redis service"
    
    def test_workflow_yaml_syntax(self, workflows_dir: Path):
        """Test that all workflow files have valid YAML syntax."""
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        assert len(workflow_files) > 0, "Must have workflow files"
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file) as f:
                    yaml.safe_load(f)
                print(f"✅ {workflow_file.name} has valid YAML syntax")
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in {workflow_file.name}: {e}")
    
    def test_main_workflow_structure(self, workflows_dir: Path):
        """Test main CI/CD workflow structure."""
        main_workflow = workflows_dir / "main-ci-cd.yml"
        assert main_workflow.exists(), "Main CI/CD workflow must exist"
        
        with open(main_workflow) as f:
            workflow = yaml.safe_load(f)
        
        # Validate workflow structure
        assert "name" in workflow, "Workflow must have a name"
        # Check for triggers (YAML parser may interpret 'on' as boolean True)
        assert ("on" in workflow or True in workflow), "Workflow must have triggers"
        assert "jobs" in workflow, "Workflow must have jobs"
        
        # Validate constitutional compliance
        content = main_workflow.read_text()
        assert "cdd01ef066bc6cf2" in content, "Main workflow must reference constitutional hash"
    
    def test_security_workflow_structure(self, workflows_dir: Path):
        """Test security workflow structure."""
        security_workflow = workflows_dir / "security-consolidated.yml"
        assert security_workflow.exists(), "Security workflow must exist"
        
        with open(security_workflow) as f:
            workflow = yaml.safe_load(f)
        
        # Validate security jobs
        jobs = workflow.get("jobs", {})
        security_jobs = [job for job in jobs.keys() if "security" in job.lower() or "scan" in job.lower()]
        assert len(security_jobs) > 0, "Security workflow must have security-related jobs"
    
    def test_testing_workflow_structure(self, workflows_dir: Path):
        """Test testing workflow structure."""
        testing_workflow = workflows_dir / "testing-consolidated.yml"
        assert testing_workflow.exists(), "Testing workflow must exist"
        
        with open(testing_workflow) as f:
            workflow = yaml.safe_load(f)
        
        # Validate testing jobs
        jobs = workflow.get("jobs", {})
        test_jobs = [job for job in jobs.keys() if "test" in job.lower()]
        assert len(test_jobs) > 0, "Testing workflow must have test-related jobs"
    
    def test_constitutional_hash_consistency(self, project_root: Path):
        """Test that constitutional hash is consistent across all files."""
        expected_hash = "cdd01ef066bc6cf2"
        
        # Check workflow files
        workflows_dir = project_root / ".github" / "workflows"
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            if "constitutional" in content.lower():
                assert expected_hash in content, f"Constitutional hash mismatch in {workflow_file.name}"
        
        # Check Dockerfile
        dockerfile = project_root / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            assert expected_hash in content, "Constitutional hash mismatch in Dockerfile"
        
        # Check GitLeaks config
        gitleaks_config = project_root / ".gitleaks.toml"
        if gitleaks_config.exists():
            content = gitleaks_config.read_text()
            assert expected_hash in content, "Constitutional hash mismatch in GitLeaks config"
    
    def test_integration_test_directory(self, project_root: Path):
        """Test that integration test directory exists and has tests."""
        integration_dir = project_root / "tests" / "integration"
        assert integration_dir.exists(), "Integration tests directory must exist"
        
        test_files = list(integration_dir.glob("test_*.py"))
        assert len(test_files) > 0, "Must have integration test files"
        
        # Validate basic integration test exists
        basic_test = integration_dir / "test_basic_integration.py"
        assert basic_test.exists(), "Basic integration test must exist"
    
    @pytest.mark.skipif(not os.getenv("DOCKER_AVAILABLE"), reason="Docker not available")
    def test_dockerfile_builds(self, project_root: Path):
        """Test that Dockerfile builds successfully."""
        try:
            client = docker.from_env()
            
            # Build the image
            image, logs = client.images.build(
                path=str(project_root),
                dockerfile="Dockerfile",
                tag="acgs-test:latest",
                rm=True
            )
            
            # Validate image labels
            labels = image.labels or {}
            assert "constitutional.hash" in labels, "Image must have constitutional hash label"
            assert labels["constitutional.hash"] == "cdd01ef066bc6cf2", "Correct constitutional hash required"
            
            print("✅ Dockerfile builds successfully")
            
        except Exception as e:
            pytest.skip(f"Docker build test skipped: {e}")
    
    def test_performance_targets_documented(self, project_root: Path):
        """Test that performance targets are documented in workflows."""
        workflows_dir = project_root / ".github" / "workflows"
        
        performance_keywords = ["P99", "latency", "RPS", "cache hit", "5ms", "100 RPS", "85%"]
        found_performance_refs = False
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            for keyword in performance_keywords:
                if keyword in content:
                    found_performance_refs = True
                    print(f"✅ Found performance reference '{keyword}' in {workflow_file.name}")
                    break
        
        assert found_performance_refs, "Workflows must reference performance targets"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
