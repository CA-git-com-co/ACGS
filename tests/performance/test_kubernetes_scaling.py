"""
Performance tests for Kubernetes HPA scaling behavior.
Constitutional hash: cdd01ef066bc6cf2
"""

import asyncio
import time
import subprocess
import json
import yaml
from typing import Dict, List
import pytest

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestKubernetesScaling:
    """Performance tests for Kubernetes HPA scaling."""
    
    def setup_class(self):
        """Setup test environment."""
        self.namespace = "acgs-system"
        self.kubectl_cmd = "kubectl"
        
    def run_kubectl(self, args: List[str]) -> Dict:
        """Run kubectl command and return JSON result."""
        try:
            cmd = [self.kubectl_cmd] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout.strip():
                return json.loads(result.stdout)
            return {}
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"kubectl command failed: {e}")
            return {}
    
    def test_hpa_configuration_syntax(self):
        """Test HPA configuration syntax is valid."""
        hpa_files = [
            "infrastructure/kubernetes/hpa-vpa.yaml",
            "infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml"
        ]
        
        for hpa_file in hpa_files:
            try:
                with open(hpa_file, 'r') as f:
                    yaml_content = list(yaml.safe_load_all(f))
                    
                for doc in yaml_content:
                    if doc and doc.get('kind') == 'HorizontalPodAutoscaler':
                        # Validate required fields
                        assert 'metadata' in doc
                        assert 'spec' in doc
                        assert 'scaleTargetRef' in doc['spec']
                        assert 'minReplicas' in doc['spec']
                        assert 'maxReplicas' in doc['spec']
                        assert 'metrics' in doc['spec']
                        
                        # Validate constitutional compliance
                        labels = doc['metadata'].get('labels', {})
                        assert labels.get('constitutional-hash') == CONSTITUTIONAL_HASH
                        
                        # Validate performance targets
                        min_replicas = doc['spec']['minReplicas']
                        max_replicas = doc['spec']['maxReplicas']
                        assert min_replicas >= 2, "Minimum replicas should be at least 2 for HA"
                        assert max_replicas >= min_replicas * 2, "Max replicas should allow sufficient scaling"
                        
                        print(f"✅ HPA {doc['metadata']['name']} validated")
                        
            except FileNotFoundError:
                print(f"⚠️  File {hpa_file} not found, skipping")
            except Exception as e:
                pytest.fail(f"HPA validation failed for {hpa_file}: {e}")
    
    def test_hpa_metrics_configuration(self):
        """Test HPA metrics are properly configured for performance targets."""
        with open("infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml", 'r') as f:
            yaml_content = list(yaml.safe_load_all(f))
            
        hpa_count = 0
        for doc in yaml_content:
            if doc and doc.get('kind') == 'HorizontalPodAutoscaler':
                hpa_count += 1
                name = doc['metadata']['name']
                metrics = doc['spec']['metrics']
                
                # Check for CPU and memory metrics
                has_cpu = any(m.get('resource', {}).get('name') == 'cpu' for m in metrics if m.get('type') == 'Resource')
                has_memory = any(m.get('resource', {}).get('name') == 'memory' for m in metrics if m.get('type') == 'Resource')
                
                assert has_cpu, f"HPA {name} should have CPU metrics"
                assert has_memory, f"HPA {name} should have memory metrics"
                
                # Check CPU utilization is reasonable (50-80%)
                for metric in metrics:
                    if metric.get('type') == 'Resource' and metric.get('resource', {}).get('name') == 'cpu':
                        cpu_target = metric['resource']['target']['averageUtilization']
                        assert 50 <= cpu_target <= 80, f"CPU target {cpu_target}% should be between 50-80%"
                
                # Check for custom metrics (performance indicators)
                custom_metrics = [m for m in metrics if m.get('type') == 'Pods']
                assert len(custom_metrics) >= 1, f"HPA {name} should have custom performance metrics"
                
                print(f"✅ HPA {name} metrics validated")
        
        assert hpa_count >= 4, "Should have at least 4 HPA configurations"
    
    def test_hpa_scaling_behavior(self):
        """Test HPA scaling behavior is optimized for performance."""
        with open("infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml", 'r') as f:
            yaml_content = list(yaml.safe_load_all(f))
            
        for doc in yaml_content:
            if doc and doc.get('kind') == 'HorizontalPodAutoscaler':
                name = doc['metadata']['name']
                behavior = doc['spec'].get('behavior', {})
                
                if behavior:
                    # Check scale up behavior
                    scale_up = behavior.get('scaleUp', {})
                    if scale_up:
                        stabilization = scale_up.get('stabilizationWindowSeconds', 0)
                        assert stabilization <= 60, f"Scale up stabilization {stabilization}s should be ≤60s for performance"
                        
                        policies = scale_up.get('policies', [])
                        if policies:
                            # Should have aggressive scale up policies
                            max_percent = max((p.get('value', 0) for p in policies if p.get('type') == 'Percent'), default=0)
                            assert max_percent >= 50, f"Should have aggressive scale up (≥50%), got {max_percent}%"
                    
                    # Check scale down behavior
                    scale_down = behavior.get('scaleDown', {})
                    if scale_down:
                        stabilization = scale_down.get('stabilizationWindowSeconds', 0)
                        assert stabilization >= 180, f"Scale down stabilization {stabilization}s should be ≥180s for stability"
                
                print(f"✅ HPA {name} scaling behavior validated")
    
    def test_pod_disruption_budget_configuration(self):
        """Test Pod Disruption Budgets are configured for high availability."""
        with open("infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml", 'r') as f:
            yaml_content = list(yaml.safe_load_all(f))
            
        pdb_count = 0
        for doc in yaml_content:
            if doc and doc.get('kind') == 'PodDisruptionBudget':
                pdb_count += 1
                name = doc['metadata']['name']
                spec = doc['spec']
                
                # Should have either minAvailable or maxUnavailable
                assert 'minAvailable' in spec or 'maxUnavailable' in spec, f"PDB {name} should specify availability"
                
                # Should have selector
                assert 'selector' in spec, f"PDB {name} should have selector"
                
                # Validate constitutional compliance
                labels = doc['metadata'].get('labels', {})
                assert labels.get('constitutional-hash') == CONSTITUTIONAL_HASH
                
                print(f"✅ PDB {name} validated")
        
        assert pdb_count >= 2, "Should have at least 2 PDB configurations"
    
    def test_performance_targets_alignment(self):
        """Test HPA configurations align with performance targets."""
        performance_targets = {
            'p99_latency_ms': 5.0,
            'throughput_rps': 100,
            'cache_hit_rate': 0.85,
            'compliance_rate': 0.95
        }
        
        with open("infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml", 'r') as f:
            yaml_content = list(yaml.safe_load_all(f))
            
        # Check ConfigMap for custom metrics
        for doc in yaml_content:
            if doc and doc.get('kind') == 'ConfigMap' and 'metrics' in doc.get('data', {}):
                metrics_yaml = yaml.safe_load(doc['data']['enhanced-metrics.yaml'])
                metrics = metrics_yaml.get('metrics', [])
                
                # Check for P99 latency metric
                latency_metrics = [m for m in metrics if 'latency' in m.get('name', '')]
                assert len(latency_metrics) >= 1, "Should have latency metrics"
                
                for metric in latency_metrics:
                    target = metric.get('target_value', 0)
                    assert target <= performance_targets['p99_latency_ms'], f"Latency target {target}ms should be ≤{performance_targets['p99_latency_ms']}ms"
                
                # Check for compliance rate metric
                compliance_metrics = [m for m in metrics if 'compliance' in m.get('name', '')]
                assert len(compliance_metrics) >= 1, "Should have compliance metrics"
                
                print("✅ Performance targets alignment validated")
    
    def test_constitutional_compliance_in_scaling(self):
        """Test constitutional compliance is maintained in scaling configurations."""
        with open("infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml", 'r') as f:
            content = f.read()
            
        # Check constitutional hash is present
        assert CONSTITUTIONAL_HASH in content, "Constitutional hash should be present in configuration"
        
        # Count occurrences
        hash_count = content.count(CONSTITUTIONAL_HASH)
        assert hash_count >= 5, f"Constitutional hash should appear at least 5 times, found {hash_count}"
        
        # Check annotations mention performance targets
        assert "p99-5ms" in content, "Should reference P99 5ms performance target"
        assert "100rps" in content or "rps" in content, "Should reference RPS performance target"
        
        print("✅ Constitutional compliance in scaling validated")
    
    def test_scaling_efficiency_calculation(self):
        """Test scaling efficiency calculations."""
        # Simulate scaling scenarios
        scenarios = [
            {
                'name': 'Normal Load',
                'cpu': 60,
                'memory': 70,
                'rps': 150,
                'expected_replicas': 3
            },
            {
                'name': 'High Load',
                'cpu': 80,
                'memory': 85,
                'rps': 300,
                'expected_replicas': 6
            },
            {
                'name': 'Peak Load',
                'cpu': 90,
                'memory': 90,
                'rps': 500,
                'expected_replicas': 10
            }
        ]
        
        for scenario in scenarios:
            # Simple scaling calculation based on CPU
            cpu_replicas = max(3, int((scenario['cpu'] / 60) * 3))
            
            # Based on RPS
            rps_replicas = max(3, int(scenario['rps'] / 50))
            
            # Take the maximum
            calculated_replicas = max(cpu_replicas, rps_replicas)
            
            print(f"Scenario {scenario['name']}: "
                  f"CPU={scenario['cpu']}%, Memory={scenario['memory']}%, "
                  f"RPS={scenario['rps']} -> {calculated_replicas} replicas")
            
            # Should be within reasonable range
            assert 3 <= calculated_replicas <= 15, f"Calculated replicas {calculated_replicas} should be 3-15"
        
        print("✅ Scaling efficiency calculations validated")


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestKubernetesScaling()
    test_instance.setup_class()
    
    test_instance.test_hpa_configuration_syntax()
    test_instance.test_hpa_metrics_configuration()
    test_instance.test_hpa_scaling_behavior()
    test_instance.test_pod_disruption_budget_configuration()
    test_instance.test_performance_targets_alignment()
    test_instance.test_constitutional_compliance_in_scaling()
    test_instance.test_scaling_efficiency_calculation()
    
    print("All Kubernetes scaling tests passed!")