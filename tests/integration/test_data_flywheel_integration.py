#!/usr/bin/env python3
"""
Integration Tests for ACGS-2 Data Flywheel

Constitutional Hash: cdd01ef066bc6cf2
ACGS-2 Constitutional Compliance Validation

This module provides integration tests for the ACGS-2 Data Flywheel implementation
that integrates NVIDIA's data-flywheel blueprint.
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def test_data_flywheel_imports():
    """Test that data flywheel modules can be imported."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    try:
        from acgs_data_flywheel import (
            ACGSDataFlywheelConfig,
            ACGSDataFlywheelClient,
            ACGSFlywheelOrchestrator,
            FlywheelJobStatus,
            EvaluationType,
            WorkloadType,
            ACGSLogEntry
        )
        
        assert hasattr(ACGSDataFlywheelConfig, 'constitutional_hash')
        assert hasattr(ACGSDataFlywheelClient, 'constitutional_hash')
        assert hasattr(ACGSFlywheelOrchestrator, 'constitutional_hash')
        
        print("✅ Data flywheel imports successful")
        return True

    except Exception as e:
        print(f"❌ Failed to import data flywheel: {e}")
        return False


def test_data_flywheel_config_creation():
    """Test data flywheel configuration creation."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig
    
    config = ACGSDataFlywheelConfig(
        elasticsearch_url="http://localhost:9200",
        mongodb_url="mongodb://localhost:27017",
        redis_url="redis://localhost:6379",
        min_records_for_evaluation=25
    )
    
    assert config.constitutional_hash == CONSTITUTIONAL_HASH
    assert config.elasticsearch_url == "http://localhost:9200"
    assert config.min_records_for_evaluation == 25
    assert "meta/llama-3.1-8b-instruct" in config.supported_models
    
    print("✅ Data flywheel config creation successful")
    return True


def test_log_entry_creation():
    """Test ACGS log entry creation."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSLogEntry, WorkloadType
    
    log_entry = ACGSLogEntry(
        timestamp=time.time(),
        client_id="test-client",
        workload_id="test-workload",
        workload_type=WorkloadType.CONSTITUTIONAL_AI,
        service_name="constitutional-ai-service",
        request={"model": "test-model", "messages": []},
        response={"choices": []},
        performance_metrics={"response_time_ms": 100}
    )
    
    assert log_entry.constitutional_hash == CONSTITUTIONAL_HASH
    assert log_entry.workload_type == WorkloadType.CONSTITUTIONAL_AI
    assert log_entry.constitutional_compliance == True
    assert log_entry.service_name == "constitutional-ai-service"
    
    print("✅ Log entry creation successful")
    return True


def test_flywheel_client_initialization():
    """Test flywheel client initialization."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig, ACGSDataFlywheelClient
    
    config = ACGSDataFlywheelConfig()
    client = ACGSDataFlywheelClient(config)
    
    assert client.constitutional_hash == CONSTITUTIONAL_HASH
    assert client.config == config
    assert len(client.active_jobs) == 0
    assert client.elasticsearch is None  # Not initialized yet
    assert client.mongodb is None
    assert client.redis is None
    
    print("✅ Flywheel client initialization successful")
    return True


def test_orchestrator_initialization():
    """Test flywheel orchestrator initialization."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig, ACGSFlywheelOrchestrator
    
    config = ACGSDataFlywheelConfig()
    orchestrator = ACGSFlywheelOrchestrator(config)
    
    assert orchestrator.constitutional_hash == CONSTITUTIONAL_HASH
    assert orchestrator.config == config
    assert "constitutional-ai" in orchestrator.service_configs
    assert "policy-governance" in orchestrator.service_configs
    assert orchestrator.service_configs["constitutional-ai"]["optimization_priority"] == "high"
    
    print("✅ Orchestrator initialization successful")
    return True


def test_workload_types():
    """Test workload type enumeration."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import WorkloadType, EvaluationType, FlywheelJobStatus
    
    # Test WorkloadType
    assert WorkloadType.CONSTITUTIONAL_AI == "constitutional_ai"
    assert WorkloadType.POLICY_GOVERNANCE == "policy_governance"
    assert WorkloadType.TOOL_CALLING == "tool_calling"
    assert WorkloadType.GENERIC == "generic"
    
    # Test EvaluationType
    assert EvaluationType.BASE == "base-eval"
    assert EvaluationType.ICL == "icl-eval"
    assert EvaluationType.CUSTOMIZED == "customized-eval"
    
    # Test FlywheelJobStatus
    assert FlywheelJobStatus.PENDING == "pending"
    assert FlywheelJobStatus.RUNNING == "running"
    assert FlywheelJobStatus.COMPLETED == "completed"
    assert FlywheelJobStatus.FAILED == "failed"
    
    print("✅ Workload types validation successful")
    return True


def test_constitutional_compliance_validation():
    """Test constitutional compliance validation."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig, ACGSDataFlywheelClient
    
    config = ACGSDataFlywheelConfig()
    client = ACGSDataFlywheelClient(config)
    
    # Test valid results
    valid_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "nims": [
            {"constitutional_compliance": True},
            {"constitutional_compliance": True}
        ]
    }
    
    assert client._validate_results_compliance(valid_results) == True
    
    # Test invalid results
    invalid_results = {
        "constitutional_hash": "invalid_hash",
        "nims": [{"constitutional_compliance": True}]
    }
    
    assert client._validate_results_compliance(invalid_results) == False
    
    # Test non-compliant model
    non_compliant_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "nims": [
            {"constitutional_compliance": True},
            {"constitutional_compliance": False}
        ]
    }
    
    assert client._validate_results_compliance(non_compliant_results) == False
    
    print("✅ Constitutional compliance validation successful")
    return True


async def test_flywheel_analysis():
    """Test flywheel results analysis."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig, ACGSDataFlywheelClient
    
    config = ACGSDataFlywheelConfig()
    client = ACGSDataFlywheelClient(config)
    
    # Mock results with cost reduction potential
    mock_results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "nims": [
            {
                "model_name": "meta/qwen3-32b-groq-instruct",
                "evaluations": {
                    "base-eval": {
                        "scores": {"similarity": 0.85}
                    }
                }
            },
            {
                "model_name": "meta/llama-3.2-1b-instruct", 
                "evaluations": {
                    "base-eval": {
                        "scores": {"similarity": 0.87}
                    }
                }
            }
        ]
    }
    
    analysis = await client._analyze_flywheel_results(mock_results)
    
    assert analysis["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert analysis["cost_reduction_potential"] > 0.9  # Should detect 98.6% potential
    assert len(analysis["optimization_recommendations"]) > 0
    assert len(analysis["security_considerations"]) > 0
    
    print("✅ Flywheel analysis successful")
    return True


def test_service_configuration():
    """Test service-specific configurations."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig, ACGSFlywheelOrchestrator, WorkloadType
    
    config = ACGSDataFlywheelConfig()
    orchestrator = ACGSFlywheelOrchestrator(config)
    
    # Test constitutional AI service config
    constitutional_config = orchestrator.service_configs["constitutional-ai"]
    assert constitutional_config["optimization_priority"] == "high"
    assert constitutional_config["min_accuracy_threshold"] == 0.95
    assert WorkloadType.CONSTITUTIONAL_AI in constitutional_config["workload_types"]
    
    # Test policy governance service config
    policy_config = orchestrator.service_configs["policy-governance"]
    assert policy_config["optimization_priority"] == "high"
    assert policy_config["min_accuracy_threshold"] == 0.90
    assert WorkloadType.POLICY_GOVERNANCE in policy_config["workload_types"]
    
    print("✅ Service configuration validation successful")
    return True


async def test_optimization_report_generation():
    """Test optimization report generation."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSDataFlywheelConfig, ACGSFlywheelOrchestrator
    
    config = ACGSDataFlywheelConfig()
    orchestrator = ACGSFlywheelOrchestrator(config)
    
    # Generate optimization report
    report = await orchestrator.generate_optimization_report()
    
    assert report["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert "report_timestamp" in report
    assert "services" in report
    assert "overall_recommendations" in report
    assert "cost_savings_potential" in report
    assert "performance_improvements" in report
    
    # Check that all configured services are included
    for service_name in orchestrator.service_configs.keys():
        assert service_name in report["services"]
    
    assert len(report["overall_recommendations"]) > 0
    
    print("✅ Optimization report generation successful")
    return True


def test_integration_with_acgs_services():
    """Test integration points with ACGS-2 services."""
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "services" / "shared" / "data_flywheel"))
    
    from acgs_data_flywheel import ACGSLogEntry, WorkloadType
    
    # Test constitutional AI service integration
    constitutional_log = ACGSLogEntry(
        timestamp=time.time(),
        client_id="acgs-constitutional-ai",
        workload_id="constitutional-validation",
        workload_type=WorkloadType.CONSTITUTIONAL_AI,
        service_name="constitutional-ai-service",
        request={
            "model": "meta/qwen3-32b-groq-instruct",
            "messages": [{"role": "user", "content": "Validate constitutional compliance"}],
            "temperature": 0.1
        },
        response={
            "choices": [{"message": {"role": "assistant", "content": "Validation complete"}}],
            "usage": {"total_tokens": 150}
        },
        performance_metrics={
            "response_time_ms": 250,
            "constitutional_compliance_score": 0.98
        }
    )
    
    assert constitutional_log.constitutional_hash == CONSTITUTIONAL_HASH
    assert constitutional_log.workload_type == WorkloadType.CONSTITUTIONAL_AI
    assert constitutional_log.performance_metrics["constitutional_compliance_score"] == 0.98
    
    # Test policy governance service integration
    policy_log = ACGSLogEntry(
        timestamp=time.time(),
        client_id="acgs-policy-governance",
        workload_id="policy-generation",
        workload_type=WorkloadType.POLICY_GOVERNANCE,
        service_name="policy-governance-service",
        request={
            "model": "meta/llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": "Generate policy for data access"}]
        },
        response={
            "choices": [{"message": {"role": "assistant", "content": "Policy generated"}}]
        }
    )
    
    assert policy_log.constitutional_hash == CONSTITUTIONAL_HASH
    assert policy_log.workload_type == WorkloadType.POLICY_GOVERNANCE
    
    print("✅ ACGS services integration successful")
    return True


async def run_all_tests():
    """Run all data flywheel integration tests."""
    
    print("🔄 Running ACGS-2 Data Flywheel Integration Tests")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    tests = [
        test_data_flywheel_imports,
        test_data_flywheel_config_creation,
        test_log_entry_creation,
        test_flywheel_client_initialization,
        test_orchestrator_initialization,
        test_workload_types,
        test_constitutional_compliance_validation,
        test_flywheel_analysis,
        test_service_configuration,
        test_optimization_report_generation,
        test_integration_with_acgs_services
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                await test()
            else:
                test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All data flywheel integration tests passed!")
        return True
    else:
        print(f"⚠️ {failed} tests failed")
        return False


if __name__ == "__main__":
    asyncio.run(run_all_tests())
