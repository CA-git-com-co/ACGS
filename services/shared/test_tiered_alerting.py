#!/usr/bin/env python3
"""
Test Script for Tiered Performance Alerting System Implementation

Tests 3-tier alerting system (Warning/Critical/Emergency) for prediction accuracy,
response times, cost efficiency, and constitutional compliance with sub-40ms
latency requirement for ACGS-PGP integration.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os
import numpy as np
import logging
import time
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_ml_optimizer import ProductionMLOptimizer, TieredPerformanceAlertingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tiered_alerting_system():
    """Test the TieredPerformanceAlertingSystem class directly."""
    logger.info("🧪 Testing TieredPerformanceAlertingSystem...")
    
    # Initialize alerting system
    alerting_system = TieredPerformanceAlertingSystem("cdd01ef066bc6cf2")
    
    # Test initial state
    assert alerting_system.constitutional_hash == "cdd01ef066bc6cf2"
    assert len(alerting_system.active_alerts) == 0
    assert len(alerting_system.alert_history) == 0
    assert alerting_system._verify_constitutional_hash() == True
    
    # Test alert thresholds configuration
    assert 'prediction_accuracy' in alerting_system.alert_thresholds
    assert 'response_time' in alerting_system.alert_thresholds
    assert 'cost_efficiency' in alerting_system.alert_thresholds
    assert 'constitutional_compliance' in alerting_system.alert_thresholds
    
    logger.info(f"  ✅ Alerting system initialized with hash: {alerting_system.constitutional_hash}")
    logger.info(f"  📊 Monitoring {len(alerting_system.alert_thresholds)} metric types")
    
    return alerting_system


def test_baseline_metrics_setup():
    """Test baseline metrics setup."""
    logger.info("🧪 Testing baseline metrics setup...")
    
    alerting_system = TieredPerformanceAlertingSystem()
    
    # Set baseline metrics
    baseline_metrics = {
        'prediction_accuracy': 0.90,
        'response_time': 25.0,  # ms
        'cost_efficiency': 0.85,
        'constitutional_compliance': 0.95
    }
    
    alerting_system.set_baseline_metrics(baseline_metrics)
    
    # Validate baseline setup
    assert len(alerting_system.baseline_metrics) == 4
    assert alerting_system.baseline_metrics['prediction_accuracy'] == 0.90
    assert alerting_system.baseline_metrics['response_time'] == 25.0
    assert alerting_system.baseline_metrics['cost_efficiency'] == 0.85
    assert alerting_system.baseline_metrics['constitutional_compliance'] == 0.95
    
    logger.info(f"  ✅ Baseline metrics set: {list(baseline_metrics.keys())}")
    
    return alerting_system, baseline_metrics


def test_alert_generation():
    """Test alert generation for different severity levels."""
    logger.info("🧪 Testing alert generation...")
    
    alerting_system, baseline_metrics = test_baseline_metrics_setup()
    
    # Test case 1: No degradation (should not generate alerts)
    good_metrics = {
        'prediction_accuracy': 0.91,  # Better than baseline
        'response_time': 24.0,        # Better than baseline
        'cost_efficiency': 0.86,      # Better than baseline
        'constitutional_compliance': 0.96  # Better than baseline
    }
    
    alerts_good = alerting_system.check_performance_alerts(good_metrics)
    logger.info(f"    Good metrics alerts: {len(alerts_good)}")
    assert len(alerts_good) == 0
    
    # Test case 2: Warning level degradation (5-10%)
    warning_metrics = {
        'prediction_accuracy': 0.86,  # ~4.4% degradation (below warning)
        'response_time': 27.0,        # 8% increase (warning level)
        'cost_efficiency': 0.81,      # ~4.7% degradation (below warning)
        'constitutional_compliance': 0.93  # ~2.1% degradation (warning for compliance)
    }
    
    alerts_warning = alerting_system.check_performance_alerts(warning_metrics)
    warning_alerts = [a for a in alerts_warning if a.severity == 'warning']
    logger.info(f"    Warning level alerts: {len(warning_alerts)}")
    assert len(warning_alerts) >= 1  # Should have at least response_time and compliance warnings
    
    # Test case 3: Critical level degradation (10-15%)
    critical_metrics = {
        'prediction_accuracy': 0.80,  # ~11.1% degradation (critical)
        'response_time': 28.0,        # 12% increase (critical)
        'cost_efficiency': 0.76,      # ~10.6% degradation (critical)
        'constitutional_compliance': 0.90  # ~5.3% degradation (critical for compliance)
    }
    
    alerts_critical = alerting_system.check_performance_alerts(critical_metrics)
    critical_alerts = [a for a in alerts_critical if a.severity == 'critical']
    logger.info(f"    Critical level alerts: {len(critical_alerts)}")
    assert len(critical_alerts) >= 3  # Should have multiple critical alerts
    
    # Test case 4: Emergency level degradation (>15%)
    emergency_metrics = {
        'prediction_accuracy': 0.75,  # ~16.7% degradation (emergency)
        'response_time': 30.0,        # 20% increase (emergency)
        'cost_efficiency': 0.70,      # ~17.6% degradation (emergency)
        'constitutional_compliance': 0.85  # ~10.5% degradation (emergency for compliance)
    }
    
    alerts_emergency = alerting_system.check_performance_alerts(emergency_metrics)
    emergency_alerts = [a for a in alerts_emergency if a.severity == 'emergency']
    logger.info(f"    Emergency level alerts: {len(emergency_alerts)}")
    assert len(emergency_alerts) >= 3  # Should have multiple emergency alerts
    
    return alerts_warning, alerts_critical, alerts_emergency


def test_latency_performance():
    """Test sub-40ms latency requirement."""
    logger.info("🧪 Testing latency performance...")
    
    alerting_system, baseline_metrics = test_baseline_metrics_setup()
    
    # Test multiple alert checks to measure latency
    latencies = []
    
    for i in range(10):
        # Create test metrics with some degradation
        test_metrics = {
            'prediction_accuracy': 0.85,  # Some degradation
            'response_time': 28.0,
            'cost_efficiency': 0.80,
            'constitutional_compliance': 0.92
        }
        
        start_time = time.time()
        alerts = alerting_system.check_performance_alerts(test_metrics)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
    
    # Calculate latency statistics
    avg_latency = np.mean(latencies)
    max_latency = np.max(latencies)
    p95_latency = np.percentile(latencies, 95)
    
    logger.info(f"  ⏱️ Latency Performance:")
    logger.info(f"    Average: {avg_latency:.2f}ms")
    logger.info(f"    Maximum: {max_latency:.2f}ms")
    logger.info(f"    P95: {p95_latency:.2f}ms")
    
    # Verify sub-40ms requirement
    latency_compliant = p95_latency < 40.0
    logger.info(f"    Sub-40ms requirement met: {latency_compliant}")
    
    assert latency_compliant, f"Latency requirement not met: P95 = {p95_latency:.2f}ms"
    
    return avg_latency, max_latency, p95_latency


def test_production_ml_optimizer_integration():
    """Test alerting system integration with ProductionMLOptimizer."""
    logger.info("🧪 Testing ProductionMLOptimizer alerting integration...")
    
    # Initialize optimizer
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")
    
    # Setup baseline metrics
    baseline_metrics = {
        'prediction_accuracy': 0.88,
        'response_time': 30.0,
        'cost_efficiency': 0.82,
        'constitutional_compliance': 0.94
    }
    
    optimizer.setup_performance_alerting(baseline_metrics)
    
    # Verify setup
    assert len(optimizer.alerting_system.baseline_metrics) == 4
    assert optimizer.alerting_system.constitutional_hash == "cdd01ef066bc6cf2"
    
    # Test performance monitoring with good metrics
    good_metrics = {
        'prediction_accuracy': 0.89,
        'response_time': 29.0,
        'cost_efficiency': 0.83,
        'constitutional_compliance': 0.95
    }
    
    monitoring_results = optimizer.monitor_system_performance(good_metrics)
    
    # Validate monitoring results
    assert 'monitoring_timestamp' in monitoring_results
    assert 'performance_alerts' in monitoring_results
    assert 'alerting_system_status' in monitoring_results
    assert 'latency_performance' in monitoring_results
    assert 'constitutional_verification' in monitoring_results
    
    # Check constitutional verification
    verification = monitoring_results['constitutional_verification']
    assert verification['verified'] == True
    assert verification['hash'] == "cdd01ef066bc6cf2"
    
    logger.info(f"  📊 Monitoring Integration:")
    logger.info(f"    Alerts generated: {len(monitoring_results['performance_alerts'])}")
    logger.info(f"    System operational: {monitoring_results['alerting_system_status']['system_operational']}")
    logger.info(f"    Constitutional hash verified: {verification['verified']}")
    
    # Test with degraded metrics
    degraded_metrics = {
        'prediction_accuracy': 0.78,  # ~11.4% degradation
        'response_time': 35.0,        # ~16.7% increase
        'cost_efficiency': 0.73,      # ~11.0% degradation
        'constitutional_compliance': 0.89  # ~5.3% degradation
    }
    
    degraded_monitoring = optimizer.monitor_system_performance(degraded_metrics)
    
    # Should have multiple alerts
    assert len(degraded_monitoring['performance_alerts']) > 0
    
    logger.info(f"    Degraded metrics alerts: {len(degraded_monitoring['performance_alerts'])}")
    
    return monitoring_results, degraded_monitoring


def test_alerting_dashboard():
    """Test alerting dashboard data generation."""
    logger.info("🧪 Testing alerting dashboard...")
    
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")
    
    # Setup and generate some alerts
    baseline_metrics = {
        'prediction_accuracy': 0.90,
        'response_time': 25.0,
        'cost_efficiency': 0.85,
        'constitutional_compliance': 0.95
    }
    
    optimizer.setup_performance_alerting(baseline_metrics)
    
    # Generate alerts with degraded metrics
    degraded_metrics = {
        'prediction_accuracy': 0.80,  # Critical degradation
        'response_time': 30.0,        # Critical increase
        'cost_efficiency': 0.75,      # Critical degradation
        'constitutional_compliance': 0.88  # Critical degradation
    }
    
    optimizer.monitor_system_performance(degraded_metrics)
    
    # Get dashboard data
    dashboard_data = optimizer.get_alerting_dashboard_data()
    
    # Validate dashboard structure
    assert 'alert_statistics' in dashboard_data
    assert 'active_alerts_by_severity' in dashboard_data
    assert 'system_performance' in dashboard_data
    assert 'monitoring_configuration' in dashboard_data
    assert 'constitutional_verification' in dashboard_data
    assert 'system_integration' in dashboard_data
    
    # Check alert statistics
    stats = dashboard_data['alert_statistics']
    assert 'total_active_alerts' in stats
    assert 'emergency_alerts' in stats
    assert 'critical_alerts' in stats
    assert 'warning_alerts' in stats
    
    # Check constitutional verification
    verification = dashboard_data['constitutional_verification']
    assert verification['verified'] == True
    assert verification['hash'] == "cdd01ef066bc6cf2"
    
    # Check system integration
    integration = dashboard_data['system_integration']
    assert integration['alerting_system_integrated'] == True
    assert integration['constitutional_hash_consistency'] == True
    
    logger.info(f"  📊 Dashboard Data Generated:")
    logger.info(f"    Total active alerts: {stats['total_active_alerts']}")
    logger.info(f"    Critical alerts: {stats['critical_alerts']}")
    logger.info(f"    Constitutional hash verified: {verification['verified']}")
    logger.info(f"    System integration verified: {integration['constitutional_hash_consistency']}")
    
    return dashboard_data


def main():
    """Run all tiered alerting system tests."""
    logger.info("🚀 Starting Tiered Performance Alerting System Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: Tiered alerting system
        alerting_system = test_tiered_alerting_system()
        logger.info("✅ Tiered alerting system tests passed\n")
        
        # Test 2: Baseline metrics setup
        test_baseline_metrics_setup()
        logger.info("✅ Baseline metrics setup tests passed\n")
        
        # Test 3: Alert generation
        test_alert_generation()
        logger.info("✅ Alert generation tests passed\n")
        
        # Test 4: Latency performance
        test_latency_performance()
        logger.info("✅ Latency performance tests passed\n")
        
        # Test 5: Production ML optimizer integration
        test_production_ml_optimizer_integration()
        logger.info("✅ Production ML optimizer integration tests passed\n")
        
        # Test 6: Alerting dashboard
        test_alerting_dashboard()
        logger.info("✅ Alerting dashboard tests passed\n")
        
        logger.info("🎉 ALL TIERED ALERTING TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ Tiered performance alerting system successfully implemented:")
        logger.info("  • 3-tier alerting: Warning (5%), Critical (10%), Emergency (15%)")
        logger.info("  • Monitoring: prediction accuracy, response times, cost efficiency")
        logger.info("  • Constitutional compliance monitoring with stricter thresholds")
        logger.info("  • Sub-40ms latency requirement met for ACGS-PGP integration")
        logger.info("  • Comprehensive alerting dashboard with historical data")
        logger.info("  • Constitutional hash integrity maintained")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
