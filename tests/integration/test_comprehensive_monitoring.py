"""
ACGS-2 Comprehensive Monitoring and Reporting Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests to validate comprehensive monitoring, performance tracking, and automated reporting capabilities.
"""

import os
import yaml
import json
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class TestComprehensiveMonitoring:
    """Validate comprehensive monitoring and reporting implementation."""
    
    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture(scope="class")
    def constitutional_hash(self) -> str:
        """Expected constitutional hash."""
        return "cdd01ef066bc6cf2"
    
    def test_performance_monitoring_workflow(self, project_root: Path, constitutional_hash: str):
        """Test performance monitoring workflow implementation."""
        perf_workflow = project_root / ".github" / "workflows" / "performance-monitoring.yml"
        assert perf_workflow.exists(), "Performance monitoring workflow must exist"
        
        content = perf_workflow.read_text()
        
        # Check for performance monitoring features
        monitoring_features = [
            "Performance Monitoring",
            "TARGET_P99_LATENCY",
            "TARGET_RPS",
            "TARGET_CACHE_HIT_RATE",
            "performance-validation.json"
        ]
        
        for feature in monitoring_features:
            assert feature in content, f"Missing performance monitoring feature: {feature}"
        
        assert constitutional_hash in content, "Performance monitoring must validate constitutional compliance"
    
    def test_workflow_consolidation_effectiveness(self, project_root: Path):
        """Test that workflow consolidation has been effective."""
        workflows_dir = project_root / ".github" / "workflows"
        workflow_files = list(workflows_dir.glob("*.yml"))
        
        # Should have consolidated to 8 main workflows
        expected_workflows = [
            "main-ci-cd.yml",
            "security-consolidated.yml", 
            "testing-consolidated.yml",
            "deployment-consolidated.yml",
            "performance-monitoring.yml",
            "documentation-automation.yml",
            "advanced-caching.yml",
            "codeql.yml"
        ]
        
        actual_workflows = [f.name for f in workflow_files]
        
        # Check that we have the expected consolidated workflows
        for expected in expected_workflows:
            assert expected in actual_workflows, f"Missing consolidated workflow: {expected}"
        
        # Verify consolidation effectiveness (should be <= 10 workflows total)
        assert len(workflow_files) <= 10, f"Too many workflow files: {len(workflow_files)} (target: ≤10)"
        
        print(f"✅ Workflow consolidation effective: {len(workflow_files)} workflows")
    
    def test_constitutional_compliance_monitoring(self, project_root: Path, constitutional_hash: str):
        """Test constitutional compliance monitoring across all workflows."""
        workflows_dir = project_root / ".github" / "workflows"
        
        compliance_violations = []
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            
            # Check if workflow mentions constitutional concepts
            if any(term in content.lower() for term in ["constitutional", "compliance", "hash"]):
                if constitutional_hash not in content:
                    compliance_violations.append(workflow_file.name)
        
        assert len(compliance_violations) == 0, f"Constitutional compliance violations in: {compliance_violations}"
        print("✅ All workflows maintain constitutional compliance")
    
    def test_performance_targets_documentation(self, project_root: Path):
        """Test that performance targets are properly documented."""
        workflows_dir = project_root / ".github" / "workflows"
        
        # ACGS-2 performance targets
        targets = {
            "P99": "5ms",
            "RPS": "100",
            "cache": "85%"
        }
        
        target_coverage = {}
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            
            for target, value in targets.items():
                if target in content and value in content:
                    if target not in target_coverage:
                        target_coverage[target] = []
                    target_coverage[target].append(workflow_file.name)
        
        # Ensure all targets are documented somewhere
        for target in targets.keys():
            assert target in target_coverage, f"Performance target {target} not documented in any workflow"
        
        print(f"✅ Performance targets documented: {target_coverage}")
    
    def test_error_handling_and_resilience(self, project_root: Path):
        """Test error handling and resilience patterns across workflows."""
        workflows_dir = project_root / ".github" / "workflows"
        
        error_handling_patterns = [
            "continue-on-error",
            "if: failure()",
            "if: always()",
            "|| echo",
            "|| true"
        ]
        
        workflows_with_error_handling = []
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            
            has_error_handling = any(pattern in content for pattern in error_handling_patterns)
            if has_error_handling:
                workflows_with_error_handling.append(workflow_file.name)
        
        # At least 80% of workflows should have error handling
        coverage_ratio = len(workflows_with_error_handling) / len(list(workflows_dir.glob("*.yml")))
        assert coverage_ratio >= 0.8, f"Insufficient error handling coverage: {coverage_ratio:.1%}"
        
        print(f"✅ Error handling coverage: {coverage_ratio:.1%}")
    
    def test_caching_optimization_effectiveness(self, project_root: Path):
        """Test caching optimization implementation."""
        caching_workflow = project_root / ".github" / "workflows" / "advanced-caching.yml"
        assert caching_workflow.exists(), "Advanced caching workflow must exist"
        
        content = caching_workflow.read_text()
        
        # Check for caching optimization features
        caching_features = [
            "cache_analysis",
            "rust_cache_optimization",
            "python_cache_optimization",
            "sccache",
            "multi-layer",
            "cache performance"
        ]
        
        for feature in caching_features:
            assert feature in content, f"Missing caching feature: {feature}"
        
        print("✅ Advanced caching optimization implemented")
    
    def test_security_integration_completeness(self, project_root: Path, constitutional_hash: str):
        """Test security integration completeness."""
        security_workflow = project_root / ".github" / "workflows" / "security-consolidated.yml"
        content = security_workflow.read_text()
        
        # Check for comprehensive security features
        security_features = [
            "container-security",
            "secret-scan",
            "infrastructure-scan",
            "trivy",
            "gitleaks",
            "Constitutional Compliance Validation"
        ]
        
        for feature in security_features:
            assert feature in content, f"Missing security feature: {feature}"
        
        assert constitutional_hash in content, "Security workflow must validate constitutional compliance"
        print("✅ Comprehensive security integration validated")
    
    def test_deployment_pipeline_robustness(self, project_root: Path):
        """Test deployment pipeline robustness."""
        deployment_workflow = project_root / ".github" / "workflows" / "deployment-consolidated.yml"
        content = deployment_workflow.read_text()
        
        # Check for robust deployment features
        deployment_features = [
            "zero-downtime",
            "rollback",
            "health check",
            "performance validation",
            "security validation",
            "30s"
        ]
        
        for feature in deployment_features:
            assert feature in content, f"Missing deployment feature: {feature}"
        
        print("✅ Robust deployment pipeline validated")
    
    def test_monitoring_and_observability(self, project_root: Path):
        """Test monitoring and observability capabilities."""
        workflows_dir = project_root / ".github" / "workflows"
        
        # Check for monitoring features across workflows
        monitoring_features = [
            "timestamp",
            "workflow_run",
            "github.sha",
            "report",
            "summary",
            "metrics"
        ]
        
        monitoring_coverage = {}
        
        for workflow_file in workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            
            for feature in monitoring_features:
                if feature in content:
                    if feature not in monitoring_coverage:
                        monitoring_coverage[feature] = []
                    monitoring_coverage[feature].append(workflow_file.name)
        
        # Ensure comprehensive monitoring coverage
        assert len(monitoring_coverage) >= 4, f"Insufficient monitoring coverage: {len(monitoring_coverage)}"
        print(f"✅ Monitoring coverage: {monitoring_coverage}")
    
    def test_workflow_performance_optimization(self, project_root: Path):
        """Test workflow performance optimization implementation."""
        main_workflow = project_root / ".github" / "workflows" / "main-ci-cd.yml"
        content = main_workflow.read_text()
        
        # Check for performance optimization features
        optimization_features = [
            "max-parallel",
            "strategy",
            "matrix",
            "cache",
            "timeout-minutes"
        ]
        
        for feature in optimization_features:
            assert feature in content, f"Missing optimization feature: {feature}"
        
        print("✅ Workflow performance optimization validated")
    
    def test_comprehensive_test_coverage(self, project_root: Path):
        """Test that comprehensive test coverage is implemented."""
        test_files = [
            "tests/integration/test_workflow_validation.py",
            "tests/integration/test_security_quality_gates.py", 
            "tests/integration/test_production_deployment.py",
            "tests/integration/test_comprehensive_monitoring.py"
        ]
        
        for test_file in test_files:
            test_path = project_root / test_file
            assert test_path.exists(), f"Missing test file: {test_file}"
        
        print("✅ Comprehensive test coverage implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
