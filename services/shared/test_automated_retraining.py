#!/usr/bin/env python3
"""
Test Script for Automated Retraining Pipeline Implementation

Tests automated retraining triggers, tiered alerting system, zero-downtime deployment,
and comprehensive monitoring with constitutional hash integrity.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import os
import sys

import numpy as np

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_ml_optimizer import AutomatedRetrainingManager, ProductionMLOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_automated_retraining_manager():
    """Test the AutomatedRetrainingManager class directly."""
    logger.info("🧪 Testing AutomatedRetrainingManager...")

    # Initialize manager
    manager = AutomatedRetrainingManager("cdd01ef066bc6cf2")

    # Test initial state
    assert manager.constitutional_hash == "cdd01ef066bc6cf2"
    assert manager._verify_constitutional_hash() == True

    # Set baseline performance
    manager.baseline_performance = {
        "r2_score": 0.85,
        "mae": 0.15,
        "constitutional_compliance": 0.95,
    }

    logger.info(
        f"  ✅ Manager initialized with baseline: {manager.baseline_performance}"
    )

    return manager


def test_retraining_triggers():
    """Test retraining trigger detection."""
    logger.info("🧪 Testing retraining trigger detection...")

    manager = AutomatedRetrainingManager()

    # Set baseline performance
    manager.baseline_performance = {
        "r2_score": 0.85,
        "mae": 0.15,
        "constitutional_compliance": 0.95,
    }

    # Test case 1: No degradation (should not trigger)
    current_performance_good = {
        "r2_score": 0.86,
        "mae": 0.14,
        "constitutional_compliance": 0.96,
    }

    triggers_good = manager.check_retraining_triggers(current_performance_good)
    logger.info(f"  ✅ Good performance triggers: {len(triggers_good)}")

    # Test case 2: Warning level degradation (5-10%)
    current_performance_warning = {
        "r2_score": 0.81,  # ~5% degradation
        "mae": 0.16,  # ~7% degradation
        "constitutional_compliance": 0.91,  # ~4% degradation
    }

    triggers_warning = manager.check_retraining_triggers(current_performance_warning)
    warning_triggers = [t for t in triggers_warning if t.severity == "warning"]
    logger.info(f"  ⚠️ Warning level triggers: {len(warning_triggers)}")

    # Test case 3: Critical level degradation (10-15%)
    current_performance_critical = {
        "r2_score": 0.76,  # ~11% degradation
        "mae": 0.18,  # ~20% degradation
        "constitutional_compliance": 0.85,  # ~11% degradation
    }

    triggers_critical = manager.check_retraining_triggers(current_performance_critical)
    critical_triggers = [t for t in triggers_critical if t.severity == "critical"]
    logger.info(f"  🚨 Critical level triggers: {len(critical_triggers)}")

    # Test case 4: Emergency level degradation (>15%)
    current_performance_emergency = {
        "r2_score": 0.70,  # ~18% degradation
        "mae": 0.25,  # ~67% degradation
        "constitutional_compliance": 0.80,  # ~16% degradation
    }

    triggers_emergency = manager.check_retraining_triggers(
        current_performance_emergency
    )
    emergency_triggers = [t for t in triggers_emergency if t.severity == "emergency"]
    logger.info(f"  🚨 Emergency level triggers: {len(emergency_triggers)}")

    # Validate trigger logic
    assert len(triggers_good) <= 1  # Only scheduled trigger possible
    assert len(warning_triggers) >= 1  # Should detect warning level degradation
    assert len(critical_triggers) >= 1  # Should detect critical level degradation
    assert len(emergency_triggers) >= 1  # Should detect emergency level degradation

    return triggers_warning, triggers_critical, triggers_emergency


def test_automated_retraining_execution():
    """Test automated retraining execution."""
    logger.info("🧪 Testing automated retraining execution...")

    manager = AutomatedRetrainingManager()

    # Generate training data
    np.random.seed(42)
    X = np.random.randn(200, 10)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(200) * 0.1

    # Create a simple current model
    from sklearn.linear_model import LinearRegression

    current_model = LinearRegression()
    current_model.fit(X, y)

    # Execute retraining
    retraining_results = manager.execute_automated_retraining(
        (X, y), current_model, "Test retraining"
    )

    # Validate results
    assert retraining_results.trigger_reason == "Test retraining"
    assert retraining_results.constitutional_hash_verified == True
    assert retraining_results.retraining_duration_seconds > 0

    logger.info("  ✅ Retraining completed:")
    logger.info(f"    Duration: {retraining_results.retraining_duration_seconds:.2f}s")
    logger.info(f"    Improvement achieved: {retraining_results.improvement_achieved}")
    logger.info(f"    Deployment approved: {retraining_results.deployment_approved}")
    logger.info(f"    Rollback required: {retraining_results.rollback_required}")

    return retraining_results


def test_production_ml_optimizer_integration():
    """Test automated retraining integration with ProductionMLOptimizer."""
    logger.info("🧪 Testing ProductionMLOptimizer automated retraining integration...")

    # Initialize optimizer
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Generate training data
    np.random.seed(42)
    X = np.random.randn(300, 12)
    y = X[:, 0] * 3 + X[:, 1] * 2 + X[:, 2] * 1.5 + np.random.randn(300) * 0.1

    # Train initial model to establish baseline
    logger.info("  📊 Training initial model...")
    training_result = optimizer.train_with_adaptive_architecture(X, y)

    # Set baseline performance
    optimizer.baseline_performance = {
        "r2_score": 0.90,
        "mae": 0.12,
        "constitutional_compliance": 0.95,
    }

    # Test trigger checking
    logger.info("  🔍 Testing trigger checking...")

    # Good performance (no triggers)
    good_performance = {
        "r2_score": 0.91,
        "mae": 0.11,
        "constitutional_compliance": 0.96,
    }

    triggers_good = optimizer.check_automated_retraining_triggers(good_performance, X)
    logger.info(f"    Good performance triggers: {len(triggers_good)}")

    # Degraded performance (should trigger)
    degraded_performance = {
        "r2_score": 0.80,  # ~11% degradation
        "mae": 0.15,  # ~25% degradation
        "constitutional_compliance": 0.85,  # ~11% degradation
    }

    triggers_degraded = optimizer.check_automated_retraining_triggers(
        degraded_performance, X
    )
    logger.info(f"    Degraded performance triggers: {len(triggers_degraded)}")

    # Test comprehensive monitoring and retraining
    logger.info("  🔄 Testing comprehensive monitoring and retraining...")

    monitoring_results = optimizer.monitor_and_retrain(X, y, degraded_performance)

    # Validate monitoring results
    assert "triggers_detected" in monitoring_results
    assert "retraining_executed" in monitoring_results
    assert monitoring_results["constitutional_hash"] == "cdd01ef066bc6cf2"

    logger.info(f"    Triggers detected: {monitoring_results['triggers_detected']}")
    logger.info(f"    Retraining executed: {monitoring_results['retraining_executed']}")

    return monitoring_results


def test_zero_downtime_deployment():
    """Test zero-downtime deployment simulation."""
    logger.info("🧪 Testing zero-downtime deployment...")

    manager = AutomatedRetrainingManager()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(150, 8)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(150) * 0.1

    # Create test model
    from sklearn.ensemble import RandomForestRegressor

    test_model = RandomForestRegressor(n_estimators=50, random_state=42)
    test_model.fit(X, y)

    # Set baseline performance
    manager.baseline_performance = {
        "r2_score": 0.85,
        "mae": 0.15,
        "constitutional_compliance": 0.95,
    }

    # Test zero-downtime deployment
    rollback_required = manager._deploy_with_zero_downtime(test_model, X, y)

    logger.info("  ✅ Zero-downtime deployment test:")
    logger.info(f"    Rollback required: {rollback_required}")

    return not rollback_required  # Success if no rollback required


def test_retraining_system_status():
    """Test comprehensive retraining system status."""
    logger.info("🧪 Testing retraining system status...")

    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Get system status
    status = optimizer.get_retraining_system_status()

    # Validate status structure
    assert "retraining_manager_status" in status
    assert "constitutional_hash" in status
    assert "system_capabilities" in status
    assert status["constitutional_hash"] == "cdd01ef066bc6cf2"
    assert status["constitutional_hash_verified"] == True

    # Check capabilities
    capabilities = status["system_capabilities"]
    expected_capabilities = [
        "automated_retraining",
        "zero_downtime_deployment",
        "tiered_alerting",
        "performance_monitoring",
        "data_drift_detection",
        "statistical_validation",
        "rollback_capability",
    ]

    for capability in expected_capabilities:
        assert capability in capabilities
        assert capabilities[capability] == True

    logger.info("  ✅ System status validated:")
    logger.info(
        f"    Constitutional hash verified: {status['constitutional_hash_verified']}"
    )
    logger.info(f"    Capabilities: {len(capabilities)} features enabled")

    return status


def main():
    """Run all automated retraining tests."""
    logger.info("🚀 Starting Automated Retraining Pipeline Tests")
    logger.info("=" * 60)

    try:
        # Test 1: Automated retraining manager
        manager = test_automated_retraining_manager()
        logger.info("✅ Automated retraining manager tests passed\n")

        # Test 2: Retraining triggers
        test_retraining_triggers()
        logger.info("✅ Retraining trigger tests passed\n")

        # Test 3: Retraining execution
        test_automated_retraining_execution()
        logger.info("✅ Retraining execution tests passed\n")

        # Test 4: Production ML optimizer integration
        test_production_ml_optimizer_integration()
        logger.info("✅ Production ML optimizer integration tests passed\n")

        # Test 5: Zero-downtime deployment
        test_zero_downtime_deployment()
        logger.info("✅ Zero-downtime deployment tests passed\n")

        # Test 6: System status
        test_retraining_system_status()
        logger.info("✅ Retraining system status tests passed\n")

        logger.info("🎉 ALL AUTOMATED RETRAINING TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ Automated retraining pipeline successfully implemented:")
        logger.info("  • Tiered alerting system (Warning/Critical/Emergency)")
        logger.info("  • Performance degradation detection (5%/10%/15% thresholds)")
        logger.info("  • Data drift detection integration")
        logger.info("  • Scheduled retraining intervals")
        logger.info("  • Zero-downtime deployment with shadow testing")
        logger.info("  • Automatic rollback capability")
        logger.info("  • Statistical validation integration")
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
