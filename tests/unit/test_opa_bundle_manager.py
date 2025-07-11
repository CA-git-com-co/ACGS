"""
Unit tests for OPA Bundle Manager

Tests bundle compilation, validation, and deployment functionality
for RAG-generated Rego rules.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

import pytest

# Mock the imports to avoid dependency issues
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.core.policy_governance.pgc_service.app.core.opa_bundle_manager import (
    OPABundleManager,
    RegoValidator,
    BundleMetadata,
    CompilationResult,
    DeploymentResult,
    CONSTITUTIONAL_HASH
)
from services.core.policy_governance.pgc_service.app.core.rag_rule_generator import RegoRuleResult


class TestRegoValidator:
    """Test Rego rule validation functionality."""
    
    @pytest.fixture
    def validator(self):
        return RegoValidator()
    
    @pytest.mark.asyncio
    async def test_validate_valid_rego_rule(self, validator):
        """Test validation of a valid Rego rule."""
        valid_rule = f"""package test.policy

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.user_authenticated == true
}}"""
        
        result = await validator.validate_rego_rule(valid_rule, "test_rule_1")
        
        assert result["is_valid"] == True
        assert result["constitutional_compliance"] == True
        assert result["score"] > 0.8
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_invalid_rego_rule(self, validator):
        """Test validation of an invalid Rego rule."""
        invalid_rule = """# Missing package declaration
allow {
    input.user == "admin"
    # Missing constitutional hash
}"""
        
        result = await validator.validate_rego_rule(invalid_rule, "test_rule_2")
        
        assert result["is_valid"] == False
        assert result["constitutional_compliance"] == False
        assert result["score"] < 0.5
        assert len(result["errors"]) > 0
        assert "Missing package declaration" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_validate_rule_with_syntax_errors(self, validator):
        """Test validation of rule with syntax errors."""
        syntax_error_rule = f"""package test.policy

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.valid == true
    # Missing closing brace"""
        
        result = await validator.validate_rego_rule(syntax_error_rule, "test_rule_3")
        
        assert result["is_valid"] == False
        assert "Mismatched braces" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_validate_bundle_success(self, validator):
        """Test successful bundle validation."""
        rules = [
            ("rule1", f"""package policy.rule1
default allow = false
allow {{ input.constitutional_hash == "{CONSTITUTIONAL_HASH}" }}"""),
            ("rule2", f"""package policy.rule2
default deny = true
deny {{ input.constitutional_hash != "{CONSTITUTIONAL_HASH}" }}""")
        ]
        
        result = await validator.validate_bundle(rules)
        
        assert result["is_valid"] == True
        assert result["total_rules"] == 2
        assert result["valid_rules"] == 2
        assert result["invalid_rules"] == 0
        assert result["overall_score"] > 0.5
    
    @pytest.mark.asyncio
    async def test_validate_bundle_with_conflicts(self, validator):
        """Test bundle validation with package conflicts."""
        rules = [
            ("rule1", f"""package policy.same
default allow = false
allow {{ input.constitutional_hash == "{CONSTITUTIONAL_HASH}" }}"""),
            ("rule2", f"""package policy.same
default deny = true
deny {{ input.constitutional_hash != "{CONSTITUTIONAL_HASH}" }}""")
        ]
        
        result = await validator.validate_bundle(rules)
        
        assert result["is_valid"] == False
        assert "Duplicate package: policy.same" in result["bundle_errors"]


class TestOPABundleManager:
    """Test OPA Bundle Manager functionality."""
    
    @pytest.fixture
    def mock_opa_client(self):
        client = AsyncMock()
        client.health_check.return_value = True
        client.get_server_info.return_value = {"version": "0.45.0"}
        client.upload_policy_bundle.return_value = Mock(
            compilation_time_ms=50.0,
            policies_compiled=2,
            success=True
        )
        return client
    
    @pytest.fixture
    def bundle_manager(self, mock_opa_client):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OPABundleManager(opa_client=mock_opa_client)
            manager.bundle_storage_path = Path(temp_dir)
            return manager
    
    @pytest.fixture
    def sample_rag_results(self):
        return [
            RegoRuleResult(
                rule_id="rag_rule_1",
                rule_content=f"""package privacy.policy

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.data_type != "sensitive"
    input.user_consent == true
}}""",
                confidence_score=0.85,
                source_principles=["privacy_principle_1"],
                reasoning="Generated from privacy principle",
                constitutional_hash=CONSTITUTIONAL_HASH
            ),
            RegoRuleResult(
                rule_id="rag_rule_2",
                rule_content=f"""package security.policy

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.security_level >= "medium"
    input.authentication == true
}}""",
                confidence_score=0.92,
                source_principles=["security_principle_1"],
                reasoning="Generated from security principle",
                constitutional_hash=CONSTITUTIONAL_HASH
            )
        ]
    
    @pytest.mark.asyncio
    async def test_compile_rag_rules_to_bundle(self, bundle_manager, sample_rag_results):
        """Test compilation of RAG rules to bundle."""
        metadata, compilation_results = await bundle_manager.compile_rag_rules_to_bundle(
            sample_rag_results,
            bundle_name="test_bundle",
            bundle_version="v1.0.0"
        )
        
        assert isinstance(metadata, BundleMetadata)
        assert metadata.name == "test_bundle"
        assert metadata.version == "v1.0.0"
        assert metadata.rules_count == 2
        assert metadata.constitutional_hash == CONSTITUTIONAL_HASH
        
        assert len(compilation_results) == 2
        assert all(isinstance(r, CompilationResult) for r in compilation_results)
        assert all(r.compiled_successfully for r in compilation_results)
    
    @pytest.mark.asyncio
    async def test_compile_invalid_rules(self, bundle_manager):
        """Test compilation with invalid rules."""
        invalid_rag_results = [
            RegoRuleResult(
                rule_id="invalid_rule",
                rule_content="# Invalid rule without package",
                confidence_score=0.3,
                source_principles=[],
                reasoning="Invalid rule for testing",
                constitutional_hash=CONSTITUTIONAL_HASH
            )
        ]
        
        metadata, compilation_results = await bundle_manager.compile_rag_rules_to_bundle(
            invalid_rag_results
        )
        
        assert len(compilation_results) == 1
        assert compilation_results[0].compiled_successfully == False
        assert len(compilation_results[0].compilation_errors) > 0
        assert metadata.validation_results["is_valid"] == False
    
    @pytest.mark.asyncio
    async def test_create_bundle_archive(self, bundle_manager, sample_rag_results):
        """Test creation of bundle archive."""
        metadata, _ = await bundle_manager.compile_rag_rules_to_bundle(sample_rag_results)
        
        rules = [
            ("rule1", sample_rag_results[0].rule_content),
            ("rule2", sample_rag_results[1].rule_content)
        ]
        
        archive_path = await bundle_manager.create_bundle_archive(metadata, rules)
        
        assert archive_path.exists()
        assert archive_path.suffix == ".gz"
        assert metadata.bundle_id in archive_path.name
    
    @pytest.mark.asyncio
    async def test_deploy_bundle_to_opa_success(self, bundle_manager, sample_rag_results):
        """Test successful bundle deployment."""
        metadata, _ = await bundle_manager.compile_rag_rules_to_bundle(sample_rag_results)
        
        rules = [
            ("rule1", sample_rag_results[0].rule_content),
            ("rule2", sample_rag_results[1].rule_content)
        ]
        
        result = await bundle_manager.deploy_bundle_to_opa(metadata, rules)
        
        assert isinstance(result, DeploymentResult)
        assert result.success == True
        assert result.bundle_id == metadata.bundle_id
        assert result.deployed_at is not None
        assert result.rollback_available == True
        assert result.deployment_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_deploy_bundle_failure(self, bundle_manager, sample_rag_results):
        """Test bundle deployment failure."""
        # Mock OPA client to fail
        bundle_manager.opa_client.upload_policy_bundle.side_effect = Exception("OPA server error")
        
        metadata, _ = await bundle_manager.compile_rag_rules_to_bundle(sample_rag_results)
        rules = [("rule1", sample_rag_results[0].rule_content)]
        
        result = await bundle_manager.deploy_bundle_to_opa(metadata, rules)
        
        assert result.success == False
        assert result.error_message is not None
        assert "OPA server error" in result.error_message
    
    def test_metrics_tracking(self, bundle_manager):
        """Test metrics tracking functionality."""
        initial_metrics = bundle_manager.get_metrics()
        
        assert "bundles_created" in initial_metrics
        assert "bundles_deployed" in initial_metrics
        assert "deployment_failures" in initial_metrics
        assert "constitutional_hash" in initial_metrics
        assert initial_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, bundle_manager):
        """Test health check when system is healthy."""
        health = await bundle_manager.health_check()
        
        assert health["status"] == "healthy"
        assert health["bundle_manager_initialized"] == True
        assert health["storage_accessible"] == True
        assert health["opa_server_healthy"] == True
        assert health["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, bundle_manager):
        """Test health check when OPA server is unhealthy."""
        bundle_manager.opa_client.health_check.return_value = False
        
        health = await bundle_manager.health_check()
        
        assert health["status"] == "degraded"
        assert health["opa_server_healthy"] == False
    
    @pytest.mark.asyncio
    async def test_metrics_update_after_operations(self, bundle_manager, sample_rag_results):
        """Test that metrics are updated after operations."""
        initial_metrics = bundle_manager.get_metrics()
        initial_bundles_created = initial_metrics["bundles_created"]
        
        # Perform bundle compilation
        await bundle_manager.compile_rag_rules_to_bundle(sample_rag_results)
        
        updated_metrics = bundle_manager.get_metrics()
        assert updated_metrics["bundles_created"] == initial_bundles_created + 1
        assert updated_metrics["avg_compilation_time_ms"] > 0


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock OPA client
        mock_opa_client = AsyncMock()
        mock_opa_client.health_check.return_value = True
        mock_opa_client.get_server_info.return_value = {"version": "0.45.0"}
        mock_opa_client.upload_policy_bundle.return_value = Mock(
            compilation_time_ms=25.0,
            policies_compiled=1,
            success=True
        )
        
        # Create bundle manager
        manager = OPABundleManager(opa_client=mock_opa_client)
        manager.bundle_storage_path = Path(temp_dir)
        
        # Create sample RAG result
        rag_result = RegoRuleResult(
            rule_id="integration_test_rule",
            rule_content=f"""package integration.test

default allow = false

allow {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.test_mode == true
}}""",
            confidence_score=0.9,
            source_principles=["test_principle"],
            reasoning="Integration test rule",
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        # Test complete workflow
        metadata, compilation_results = await manager.compile_rag_rules_to_bundle([rag_result])
        
        assert metadata.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(compilation_results) == 1
        assert compilation_results[0].compiled_successfully == True
        
        # Test deployment
        rules = [(rag_result.rule_id, rag_result.rule_content)]
        deployment_result = await manager.deploy_bundle_to_opa(metadata, rules)
        
        assert deployment_result.success == True
        assert deployment_result.bundle_id == metadata.bundle_id


if __name__ == "__main__":
    pytest.main([__file__])
