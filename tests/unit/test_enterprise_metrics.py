"""
Unit tests for Enterprise Metrics and Monitoring System

Tests Prometheus metrics export, HPA auto-scaling support, and enterprise-grade 
monitoring with 1247 RPS target and 99.9% uptime validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from services.core.policy_governance.pgc_service.app.monitoring.enterprise_metrics import (
        EnterpriseMonitoringSystem,
        PrometheusMetricsCollector,
        SLATarget,
        AlertRule,
        HPAMetrics,
        ServiceHealth,
        AlertSeverity,
        CONSTITUTIONAL_HASH
    )
except ImportError as e:
    import pytest
    pytest.skip(f"Required module not available: {e}", allow_module_level=True)


class TestSLATarget:
    """Test SLA target functionality."""
    
    def test_sla_target_creation(self):
        """Test SLA target creation."""
        target = SLATarget(
            name="Test RPS",
            target_value=1247.0,
            current_value=1200.0,
            unit="RPS",
            description="Test RPS target"
        )
        
        assert target.name == "Test RPS"
        assert target.target_value == 1247.0
        assert target.current_value == 1200.0
        assert target.constitutional_hash == CONSTITUTIONAL_HASH
    
    def test_sla_breach_detection(self):
        """Test SLA breach detection."""
        target = SLATarget(
            name="Test Target",
            target_value=100.0,
            current_value=90.0,  # 10% below target
            breach_threshold=0.05  # 5% tolerance
        )
        
        # Should be breached (10% > 5% tolerance)
        assert target.is_breached() == True
        
        # Update to within tolerance
        target.current_value = 96.0  # 4% below target
        assert target.is_breached() == False
    
    def test_compliance_percentage(self):
        """Test compliance percentage calculation."""
        target = SLATarget(
            name="Test Target",
            target_value=1000.0,
            current_value=950.0
        )
        
        compliance = target.compliance_percentage()
        assert compliance == 95.0
        
        # Test exceeding target
        target.current_value = 1100.0
        compliance = target.compliance_percentage()
        assert compliance == 100.0


class TestAlertRule:
    """Test alert rule functionality."""
    
    def test_alert_rule_creation(self):
        """Test alert rule creation."""
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Alert",
            description="Test alert rule",
            metric_name="test_metric",
            threshold=100.0,
            operator="gt",
            severity=AlertSeverity.WARNING
        )
        
        assert rule.rule_id == "test_rule"
        assert rule.severity == AlertSeverity.WARNING
        assert rule.constitutional_hash == CONSTITUTIONAL_HASH
    
    def test_alert_triggering(self):
        """Test alert triggering logic."""
        rule = AlertRule(
            rule_id="high_cpu",
            name="High CPU",
            description="CPU too high",
            metric_name="cpu_utilization",
            threshold=80.0,
            operator="gt",
            severity=AlertSeverity.WARNING
        )
        
        # Should trigger
        assert rule.should_trigger(85.0) == True
        
        # Should not trigger
        assert rule.should_trigger(75.0) == False
        
        # Test different operators
        rule.operator = "lt"
        assert rule.should_trigger(75.0) == True
        assert rule.should_trigger(85.0) == False
    
    def test_alert_cooldown(self):
        """Test alert cooldown functionality."""
        rule = AlertRule(
            rule_id="test_cooldown",
            name="Test Cooldown",
            description="Test cooldown",
            metric_name="test_metric",
            threshold=50.0,
            operator="gt",
            severity=AlertSeverity.WARNING,
            cooldown_seconds=300  # 5 minutes
        )
        
        # First trigger should work
        assert rule.should_trigger(60.0) == True
        
        # Set last triggered to now
        rule.last_triggered = datetime.now(timezone.utc)
        
        # Should not trigger due to cooldown
        assert rule.should_trigger(60.0) == False
        
        # Set last triggered to past cooldown period
        rule.last_triggered = datetime.now(timezone.utc) - timedelta(seconds=400)
        
        # Should trigger again
        assert rule.should_trigger(60.0) == True


class TestHPAMetrics:
    """Test HPA metrics functionality."""
    
    def test_hpa_metrics_creation(self):
        """Test HPA metrics creation."""
        hpa = HPAMetrics(
            current_replicas=3,
            min_replicas=2,
            max_replicas=10,
            target_cpu_utilization=70.0
        )
        
        assert hpa.current_replicas == 3
        assert hpa.constitutional_hash == CONSTITUTIONAL_HASH
    
    def test_scale_up_decision(self):
        """Test scale up decision logic."""
        hpa = HPAMetrics(
            current_replicas=3,
            max_replicas=10,
            target_cpu_utilization=70.0,
            current_cpu_utilization=85.0  # Above target
        )
        
        # Should scale up
        assert hpa.should_scale_up() == True
        
        # Test at max replicas
        hpa.current_replicas = 10
        assert hpa.should_scale_up() == False
    
    def test_scale_down_decision(self):
        """Test scale down decision logic."""
        hpa = HPAMetrics(
            current_replicas=5,
            min_replicas=2,
            target_cpu_utilization=70.0,
            current_cpu_utilization=30.0,  # Well below target
            target_memory_utilization=80.0,
            current_memory_utilization=35.0  # Well below target
        )
        
        # Should scale down
        assert hpa.should_scale_down() == True
        
        # Test at min replicas
        hpa.current_replicas = 2
        assert hpa.should_scale_down() == False


class TestPrometheusMetricsCollector:
    """Test Prometheus metrics collector."""
    
    @pytest.fixture
    def metrics_collector(self):
        return PrometheusMetricsCollector()
    
    def test_metrics_collector_initialization(self, metrics_collector):
        """Test metrics collector initialization."""
        assert metrics_collector.metrics is not None
        assert 'requests_total' in metrics_collector.metrics
        assert 'rps_current' in metrics_collector.metrics
        assert 'constitutional_compliance_rate' in metrics_collector.metrics
    
    def test_record_request(self, metrics_collector):
        """Test request recording."""
        # Should not raise exception
        metrics_collector.record_request("pgc", "POST", "200", 5.0)
        
        # Test with different parameters
        metrics_collector.record_request("pgc", "GET", "404", 2.5)
    
    def test_update_metrics(self, metrics_collector):
        """Test metric updates."""
        # Test RPS update
        metrics_collector.update_rps("pgc", 1247.0)
        
        # Test uptime update
        metrics_collector.update_uptime("pgc", 99.95)
        
        # Test constitutional compliance update
        metrics_collector.update_constitutional_compliance("pgc", 1.0)
        
        # Test resource utilization update
        metrics_collector.update_resource_utilization("pgc", "pod-1", 75.0, 80.0)
    
    def test_business_metrics(self, metrics_collector):
        """Test business metrics recording."""
        # Test rule generation recording
        metrics_collector.record_rule_generation("pgc", "privacy")
        metrics_collector.record_rule_generation("pgc", "security")
        
        # Test human review recording
        metrics_collector.record_human_review("pgc", "low_confidence")
        metrics_collector.record_human_review("pgc", "complex_rule")
    
    def test_metrics_text_generation(self, metrics_collector):
        """Test Prometheus metrics text generation."""
        metrics_text = metrics_collector.get_metrics_text()
        
        assert isinstance(metrics_text, str)
        assert len(metrics_text) > 0
        assert CONSTITUTIONAL_HASH in metrics_text


class TestEnterpriseMonitoringSystem:
    """Test enterprise monitoring system."""
    
    @pytest.fixture
    def monitoring_system(self):
        return EnterpriseMonitoringSystem()
    
    def test_monitoring_system_initialization(self, monitoring_system):
        """Test monitoring system initialization."""
        assert monitoring_system.service_health == ServiceHealth.HEALTHY
        assert len(monitoring_system.sla_targets) > 0
        assert len(monitoring_system.alert_rules) > 0
        assert monitoring_system.hpa_metrics is not None
        
        # Check SLA targets
        assert 'rps_target' in monitoring_system.sla_targets
        assert 'uptime_target' in monitoring_system.sla_targets
        assert 'constitutional_compliance_target' in monitoring_system.sla_targets
        
        # Verify constitutional compliance
        for target in monitoring_system.sla_targets.values():
            assert target.constitutional_hash == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_record_request(self, monitoring_system):
        """Test request recording and metric updates."""
        # Record some requests
        await monitoring_system.record_request("pgc", "POST", "200", 3.5)
        await monitoring_system.record_request("pgc", "GET", "200", 2.1)
        await monitoring_system.record_request("pgc", "POST", "201", 4.2)
        
        assert monitoring_system.request_count == 3
        assert len(monitoring_system.request_times) == 3
    
    @pytest.mark.asyncio
    async def test_sla_target_updates(self, monitoring_system):
        """Test SLA target updates."""
        # Record requests to trigger updates
        for i in range(10):
            await monitoring_system.record_request("pgc", "POST", "200", 2.0 + i * 0.1)
        
        # Check that SLA targets are updated
        rps_target = monitoring_system.sla_targets['rps_target']
        uptime_target = monitoring_system.sla_targets['uptime_target']
        
        assert rps_target.current_value >= 0
        assert uptime_target.current_value > 0
    
    @pytest.mark.asyncio
    async def test_alert_triggering(self, monitoring_system):
        """Test alert triggering."""
        # Set up conditions that should trigger alerts
        monitoring_system.sla_targets['rps_target'].current_value = 500.0  # Below 1000 threshold
        
        # Trigger alert check
        await monitoring_system._check_alerts()
        
        # Should have triggered low RPS alert
        assert len(monitoring_system.active_alerts) > 0
        
        # Check alert details
        alert = monitoring_system.active_alerts[0]
        assert alert['rule_id'] == 'low_rps'
        assert alert['constitutional_hash'] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_hpa_scaling(self, monitoring_system):
        """Test HPA scaling functionality."""
        # Test scale up scenario
        await monitoring_system.update_hpa_metrics(85.0, 90.0)  # High utilization
        
        # Should have triggered scale up
        assert len(monitoring_system.hpa_metrics.scaling_events) > 0
        
        scaling_event = monitoring_system.hpa_metrics.scaling_events[0]
        assert scaling_event['action'] == 'scale_up'
        assert scaling_event['constitutional_hash'] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_monitoring(self, monitoring_system):
        """Test constitutional compliance monitoring."""
        # Set compliance below 100%
        monitoring_system.sla_targets['constitutional_compliance_target'].current_value = 99.5
        
        # Trigger alert check
        await monitoring_system._check_alerts()
        
        # Should trigger emergency alert
        emergency_alerts = [
            alert for alert in monitoring_system.active_alerts 
            if alert['rule_id'] == 'constitutional_compliance_breach'
        ]
        
        assert len(emergency_alerts) > 0
        assert emergency_alerts[0]['severity'] == 'emergency'
    
    def test_health_status(self, monitoring_system):
        """Test health status reporting."""
        health_status = monitoring_system.get_health_status()
        
        assert 'service_health' in health_status
        assert 'sla_compliance' in health_status
        assert 'hpa_status' in health_status
        assert 'constitutional_hash' in health_status
        
        assert health_status['constitutional_hash'] == CONSTITUTIONAL_HASH
        
        # Check SLA compliance structure
        sla_compliance = health_status['sla_compliance']
        assert 'rps_target' in sla_compliance
        assert 'uptime_target' in sla_compliance
        
        for target_name, target_data in sla_compliance.items():
            assert 'target' in target_data
            assert 'current' in target_data
            assert 'compliance' in target_data
            assert 'breached' in target_data
    
    def test_prometheus_metrics_export(self, monitoring_system):
        """Test Prometheus metrics export."""
        metrics_text = monitoring_system.get_prometheus_metrics()
        
        assert isinstance(metrics_text, str)
        assert len(metrics_text) > 0
        assert 'acgs_' in metrics_text  # Should contain ACGS metrics
        assert CONSTITUTIONAL_HASH in metrics_text
    
    @pytest.mark.asyncio
    async def test_enterprise_sla_targets(self, monitoring_system):
        """Test enterprise SLA targets (1247 RPS, 99.9% uptime)."""
        # Simulate achieving enterprise targets
        monitoring_system.sla_targets['rps_target'].current_value = 1247.0
        monitoring_system.sla_targets['uptime_target'].current_value = 99.95
        
        # Check compliance
        rps_compliance = monitoring_system.sla_targets['rps_target'].compliance_percentage()
        uptime_compliance = monitoring_system.sla_targets['uptime_target'].compliance_percentage()
        
        assert rps_compliance == 100.0
        assert uptime_compliance == 100.0
        
        # Check no breaches
        assert not monitoring_system.sla_targets['rps_target'].is_breached()
        assert not monitoring_system.sla_targets['uptime_target'].is_breached()


@pytest.mark.integration
class TestEnterpriseMonitoringIntegration:
    """Integration tests for enterprise monitoring."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        monitoring_system = EnterpriseMonitoringSystem()
        
        # Simulate enterprise load (1247 RPS target)
        for i in range(100):
            await monitoring_system.record_request("pgc", "POST", "200", 2.0 + (i % 10) * 0.1)
        
        # Update HPA metrics
        await monitoring_system.update_hpa_metrics(65.0, 70.0)  # Normal utilization
        
        # Get health status
        health_status = monitoring_system.get_health_status()
        
        # Get Prometheus metrics
        metrics_text = monitoring_system.get_prometheus_metrics()
        
        # Validate end-to-end results
        assert health_status['constitutional_hash'] == CONSTITUTIONAL_HASH
        assert health_status['service_health'] == ServiceHealth.HEALTHY.value
        assert CONSTITUTIONAL_HASH in metrics_text
        
        # Check SLA compliance
        sla_compliance = health_status['sla_compliance']
        constitutional_compliance = sla_compliance['constitutional_compliance_target']
        assert constitutional_compliance['current'] == 100.0
        assert not constitutional_compliance['breached']
        
        print("✅ End-to-end enterprise monitoring workflow completed successfully")
        print(f"Service Health: {health_status['service_health']}")
        print(f"Constitutional Compliance: {constitutional_compliance['current']}%")
        print(f"Active Alerts: {health_status['active_alerts']}")
        print(f"HPA Replicas: {health_status['hpa_status']['current_replicas']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
