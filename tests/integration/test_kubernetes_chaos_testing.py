"""
Integration tests for Kubernetes Chaos Testing Framework

Tests comprehensive chaos engineering with Kubernetes and Chaos Mesh simulation
for 99.9% uptime validation and resilience testing.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.core.policy_governance.chaos_testing.kubernetes_chaos_framework import (
    KubernetesChaosTestingFramework,
    KubernetesClusterSimulator,
    ChaosMeshSimulator,
    ChaosExperiment,
    ChaosExperimentType,
    ChaosScope,
    ExperimentStatus,
    KubernetesResource,
    get_chaos_framework,
    CONSTITUTIONAL_HASH
)


class TestKubernetesClusterSimulator:
    """Test Kubernetes cluster simulator functionality."""
    
    @pytest.fixture
    def cluster_simulator(self):
        return KubernetesClusterSimulator()
    
    def test_cluster_initialization(self, cluster_simulator):
        """Test cluster simulator initialization."""
        assert len(cluster_simulator.namespaces) == 3
        assert "acgs-2" in cluster_simulator.namespaces
        assert "monitoring" in cluster_simulator.namespaces
        assert "chaos-mesh" in cluster_simulator.namespaces
        
        # Check services are defined
        assert "policy-governance-compiler" in cluster_simulator.services["acgs-2"]
        assert "prometheus" in cluster_simulator.services["monitoring"]
        
        # Check resources are initialized
        assert len(cluster_simulator.cluster_resources) > 0
        
        # Check constitutional compliance
        for resource in cluster_simulator.cluster_resources:
            assert resource.constitutional_hash == CONSTITUTIONAL_HASH
    
    def test_resource_selector(self, cluster_simulator):
        """Test resource selection by various criteria."""
        # Test by namespace
        acgs_resources = cluster_simulator.get_resources_by_selector(namespace="acgs-2")
        assert len(acgs_resources) > 0
        assert all(r.namespace == "acgs-2" for r in acgs_resources)
        
        # Test by resource type
        pods = cluster_simulator.get_resources_by_selector(resource_type="pod")
        assert len(pods) > 0
        assert all(r.resource_type == "pod" for r in pods)
        
        # Test by labels
        pgc_resources = cluster_simulator.get_resources_by_selector(
            labels={"app": "policy-governance-compiler"}
        )
        assert len(pgc_resources) > 0
        assert all(r.labels.get("app") == "policy-governance-compiler" for r in pgc_resources)
    
    @pytest.mark.asyncio
    async def test_pod_kill_experiment(self, cluster_simulator):
        """Test pod kill chaos experiment."""
        # Get a pod to kill
        pods = cluster_simulator.get_resources_by_selector(
            namespace="acgs-2",
            resource_type="pod"
        )
        assert len(pods) > 0
        
        target_pod = pods[0]
        
        # Create experiment
        experiment = ChaosExperiment(
            experiment_id="test-pod-kill",
            name="Test Pod Kill",
            experiment_type=ChaosExperimentType.POD_KILL,
            scope=ChaosScope.SINGLE_POD,
            target_resources=[target_pod],
            duration_seconds=30
        )
        
        # Apply experiment
        results = await cluster_simulator.apply_chaos_experiment(experiment)
        
        assert experiment.status == ExperimentStatus.COMPLETED
        assert "affected_pods" in results
        assert "recovery_time_seconds" in results
        assert results["constitutional_compliance_maintained"] == True
    
    @pytest.mark.asyncio
    async def test_network_partition_experiment(self, cluster_simulator):
        """Test network partition chaos experiment."""
        # Get service resources
        services = cluster_simulator.get_resources_by_selector(
            namespace="acgs-2",
            resource_type="service"
        )
        
        experiment = ChaosExperiment(
            experiment_id="test-network-partition",
            name="Test Network Partition",
            experiment_type=ChaosExperimentType.NETWORK_PARTITION,
            scope=ChaosScope.ENTIRE_SERVICE,
            target_resources=services[:2],
            duration_seconds=60
        )
        
        # Apply experiment
        results = await cluster_simulator.apply_chaos_experiment(experiment)
        
        assert experiment.status == ExperimentStatus.COMPLETED
        assert "partition_duration_seconds" in results
        assert "network_recovery_time" in results
        assert results["constitutional_compliance_maintained"] == True
    
    def test_cluster_health_monitoring(self, cluster_simulator):
        """Test cluster health monitoring."""
        health = cluster_simulator.get_cluster_health()
        
        assert "overall_health" in health
        assert "service_health" in health
        assert "network_health" in health
        assert "constitutional_hash" in health
        
        assert health["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert 0.0 <= health["overall_health"] <= 1.0
        assert 0.0 <= health["network_health"] <= 1.0
        
        # Check service health
        for service_name, health_score in health["service_health"].items():
            assert 0.0 <= health_score <= 1.0


class TestChaosMeshSimulator:
    """Test Chaos Mesh simulator functionality."""
    
    @pytest.fixture
    def cluster_simulator(self):
        return KubernetesClusterSimulator()
    
    @pytest.fixture
    def chaos_mesh(self, cluster_simulator):
        return ChaosMeshSimulator(cluster_simulator)
    
    def test_chaos_mesh_initialization(self, chaos_mesh):
        """Test Chaos Mesh simulator initialization."""
        assert chaos_mesh.cluster is not None
        assert len(chaos_mesh.active_experiments) == 0
        assert len(chaos_mesh.experiment_history) == 0
        assert len(chaos_mesh.chaos_templates) > 0
        
        # Check templates have constitutional compliance
        for template in chaos_mesh.chaos_templates.values():
            assert "apiVersion" in template
            assert "kind" in template
    
    @pytest.mark.asyncio
    async def test_create_chaos_experiment(self, chaos_mesh):
        """Test chaos experiment creation."""
        experiment = await chaos_mesh.create_chaos_experiment(
            name="Test Pod Kill Experiment",
            experiment_type=ChaosExperimentType.POD_KILL,
            scope=ChaosScope.SINGLE_POD,
            target_selector={
                "namespace": "acgs-2",
                "labels": {"app": "policy-governance-compiler"},
                "resource_type": "pod"
            },
            duration_seconds=30
        )
        
        assert experiment.name == "Test Pod Kill Experiment"
        assert experiment.experiment_type == ChaosExperimentType.POD_KILL
        assert experiment.scope == ChaosScope.SINGLE_POD
        assert experiment.duration_seconds == 30
        assert experiment.constitutional_hash == CONSTITUTIONAL_HASH
        assert len(experiment.target_resources) > 0
    
    @pytest.mark.asyncio
    async def test_run_experiment(self, chaos_mesh):
        """Test running a chaos experiment."""
        experiment = await chaos_mesh.create_chaos_experiment(
            name="Test CPU Stress",
            experiment_type=ChaosExperimentType.CPU_STRESS,
            scope=ChaosScope.SINGLE_POD,
            target_selector={
                "namespace": "acgs-2",
                "resource_type": "pod"
            },
            duration_seconds=60,
            parameters={"cpu_percentage": 80}
        )
        
        # Run experiment
        results = await chaos_mesh.run_experiment(experiment)
        
        assert experiment.status == ExperimentStatus.COMPLETED
        assert "cpu_stress_percentage" in results
        assert results["constitutional_compliance_maintained"] == True
        assert experiment in chaos_mesh.experiment_history
    
    def test_experiment_status_tracking(self, chaos_mesh):
        """Test experiment status tracking."""
        # Create a mock experiment
        experiment = ChaosExperiment(
            experiment_id="test-status",
            name="Test Status",
            experiment_type=ChaosExperimentType.POD_KILL,
            scope=ChaosScope.SINGLE_POD,
            target_resources=[],
            duration_seconds=30
        )
        
        # Add to history
        chaos_mesh.experiment_history.append(experiment)
        
        # Test retrieval
        retrieved = chaos_mesh.get_experiment_status("test-status")
        assert retrieved is not None
        assert retrieved.experiment_id == "test-status"
        
        # Test listing
        experiments = chaos_mesh.list_experiments()
        assert len(experiments) >= 1
        assert any(exp.experiment_id == "test-status" for exp in experiments)


class TestKubernetesChaosTestingFramework:
    """Test comprehensive chaos testing framework."""
    
    @pytest.fixture
    def chaos_framework(self):
        return KubernetesChaosTestingFramework()
    
    def test_framework_initialization(self, chaos_framework):
        """Test chaos testing framework initialization."""
        assert chaos_framework.cluster_simulator is not None
        assert chaos_framework.chaos_mesh is not None
        assert chaos_framework.uptime_target == 0.999
        assert chaos_framework.constitutional_compliance_target == 1.0
        assert chaos_framework.test_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_comprehensive_chaos_test_short(self, chaos_framework):
        """Test comprehensive chaos testing with short duration."""
        # Run short test (2 minutes instead of 60)
        result = await chaos_framework.run_comprehensive_chaos_test(
            duration_minutes=2,
            experiment_interval_seconds=30
        )
        
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert result.experiment_count > 0
        assert result.total_duration_minutes > 0
        assert 0.0 <= result.uptime_percentage <= 1.0
        assert 0.0 <= result.constitutional_compliance_rate <= 1.0
        assert isinstance(result.service_availability, dict)
        assert isinstance(result.performance_impact, dict)
        assert isinstance(result.recovery_times, list)
    
    def test_framework_metrics(self, chaos_framework):
        """Test framework metrics collection."""
        metrics = chaos_framework.get_framework_metrics()
        
        assert "total_experiments" in metrics
        assert "constitutional_violations" in metrics
        assert "uptime_percentage" in metrics
        assert "cluster_health" in metrics
        assert "constitutional_hash" in metrics
        
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        # Check cluster health is included
        cluster_health = metrics["cluster_health"]
        assert "overall_health" in cluster_health
        assert "constitutional_hash" in cluster_health
    
    @pytest.mark.asyncio
    async def test_uptime_target_validation(self, chaos_framework):
        """Test uptime target validation."""
        # Framework should target 99.9% uptime
        assert chaos_framework.uptime_target == 0.999
        
        # Run a minimal test to check uptime calculation
        result = await chaos_framework.run_comprehensive_chaos_test(
            duration_minutes=1,
            experiment_interval_seconds=60
        )
        
        # Should achieve high uptime with minimal chaos
        assert result.uptime_percentage > 0.95
        assert result.constitutional_compliance_rate > 0.9


@pytest.mark.integration
class TestChaosTestingIntegration:
    """Integration tests for chaos testing framework."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_chaos_testing(self):
        """Test complete chaos testing workflow."""
        framework = KubernetesChaosTestingFramework()
        
        # Run comprehensive test
        result = await framework.run_comprehensive_chaos_test(
            duration_minutes=3,  # Short test for CI
            experiment_interval_seconds=45
        )
        
        # Validate results
        assert result.constitutional_hash == CONSTITUTIONAL_HASH
        assert result.experiment_count >= 2  # Should run at least 2 experiments
        assert result.constitutional_compliance_rate > 0.8
        
        # Check that experiments were actually run
        experiments = framework.chaos_mesh.list_experiments()
        assert len(experiments) >= 2
        
        # Check that all experiments maintain constitutional compliance
        for experiment in experiments:
            assert experiment.constitutional_hash == CONSTITUTIONAL_HASH
            if experiment.results:
                # Most experiments should maintain constitutional compliance
                assert experiment.results.get("constitutional_compliance_maintained", True)
        
        # Check framework metrics
        metrics = framework.get_framework_metrics()
        assert metrics["total_experiments"] >= 2
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
        
        print("✅ End-to-end chaos testing workflow completed successfully")
        print(f"Experiments Run: {result.experiment_count}")
        print(f"Uptime Achieved: {result.uptime_percentage:.4f}")
        print(f"Constitutional Compliance: {result.constitutional_compliance_rate:.1%}")
        print(f"Constitutional Violations: {result.constitutional_violations}")
    
    @pytest.mark.asyncio
    async def test_global_framework_instance(self):
        """Test global framework instance management."""
        framework1 = await get_chaos_framework()
        framework2 = await get_chaos_framework()
        
        # Should return the same instance
        assert framework1 is framework2
        assert framework1.test_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_under_chaos(self):
        """Test that constitutional compliance is maintained under chaos conditions."""
        framework = KubernetesChaosTestingFramework()
        
        # Create specific experiments that test constitutional compliance
        chaos_mesh = framework.chaos_mesh
        
        # Test 1: Pod kill should maintain constitutional compliance
        pod_kill_experiment = await chaos_mesh.create_chaos_experiment(
            name="Constitutional Compliance - Pod Kill",
            experiment_type=ChaosExperimentType.POD_KILL,
            scope=ChaosScope.SINGLE_POD,
            target_selector={
                "namespace": "acgs-2",
                "labels": {"constitutional-hash": CONSTITUTIONAL_HASH},
                "resource_type": "pod"
            }
        )
        
        results = await chaos_mesh.run_experiment(pod_kill_experiment)
        assert results["constitutional_compliance_maintained"] == True
        
        # Test 2: Network partition should maintain constitutional compliance
        network_experiment = await chaos_mesh.create_chaos_experiment(
            name="Constitutional Compliance - Network Partition",
            experiment_type=ChaosExperimentType.NETWORK_PARTITION,
            scope=ChaosScope.ENTIRE_SERVICE,
            target_selector={
                "namespace": "acgs-2",
                "labels": {"constitutional-hash": CONSTITUTIONAL_HASH}
            }
        )
        
        results = await chaos_mesh.run_experiment(network_experiment)
        assert results["constitutional_compliance_maintained"] == True
        
        print("✅ Constitutional compliance maintained under chaos conditions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
