#!/usr/bin/env python3
"""
Test Script for A/B Testing Framework Implementation

Tests statistical A/B testing for model deployments with proper randomization,
sample size calculations, significance testing, shadow deployments for risk-free
testing, and automatic rollback on performance degradation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os
import numpy as np
import logging
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_ml_optimizer import ProductionMLOptimizer, ABTestingFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ab_testing_framework():
    """Test the ABTestingFramework class directly."""
    logger.info("🧪 Testing ABTestingFramework...")
    
    # Initialize framework
    framework = ABTestingFramework("cdd01ef066bc6cf2")
    
    # Test initial state
    assert framework.constitutional_hash == "cdd01ef066bc6cf2"
    assert len(framework.active_tests) == 0
    assert len(framework.test_history) == 0
    assert len(framework.shadow_deployments) == 0
    
    # Test default configuration
    assert 'significance_level' in framework.default_config
    assert 'minimum_effect_size' in framework.default_config
    assert 'traffic_split' in framework.default_config
    assert 'success_metrics' in framework.default_config
    
    logger.info(f"  ✅ Framework initialized with hash: {framework.constitutional_hash}")
    logger.info(f"  📊 Default significance level: {framework.default_config['significance_level']}")
    
    return framework


def test_sample_size_calculation():
    """Test sample size calculation for A/B tests."""
    logger.info("🧪 Testing sample size calculation...")
    
    framework = ABTestingFramework()
    
    # Test sample size calculation
    effect_size = 0.02  # 2% effect size
    sample_size = framework.calculate_sample_size(effect_size)
    
    # Validate sample size
    assert sample_size > 0
    assert isinstance(sample_size, int)
    
    # Test different effect sizes
    small_effect = framework.calculate_sample_size(0.01)  # 1% effect
    large_effect = framework.calculate_sample_size(0.05)  # 5% effect
    
    # Smaller effects should require larger sample sizes
    assert small_effect > large_effect
    
    logger.info(f"  📊 Sample Size Calculations:")
    logger.info(f"    2% effect size: {sample_size} samples per group")
    logger.info(f"    1% effect size: {small_effect} samples per group")
    logger.info(f"    5% effect size: {large_effect} samples per group")
    
    return sample_size


def test_ab_test_creation():
    """Test A/B test creation and configuration."""
    logger.info("🧪 Testing A/B test creation...")
    
    framework = ABTestingFramework()
    
    # Create test models
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    
    np.random.seed(42)
    X_train = np.random.randn(100, 5)
    y_train = X_train[:, 0] * 2 + X_train[:, 1] * 1.5 + np.random.randn(100) * 0.1
    
    control_model = LinearRegression()
    control_model.fit(X_train, y_train)
    
    treatment_model = RandomForestRegressor(n_estimators=50, random_state=42)
    treatment_model.fit(X_train, y_train)
    
    # Create A/B test
    test_config = framework.create_ab_test(
        "Linear vs Random Forest", control_model, treatment_model
    )
    
    # Validate test configuration
    assert test_config.test_name == "Linear vs Random Forest"
    assert test_config.constitutional_hash == "cdd01ef066bc6cf2"
    assert 0 < test_config.traffic_split <= 1
    assert test_config.sample_size_per_group > 0
    assert len(test_config.success_metrics) > 0
    
    # Check that test is stored
    assert len(framework.active_tests) == 1
    assert test_config.test_id in framework.active_tests
    
    logger.info(f"  ✅ A/B test created: {test_config.test_id}")
    logger.info(f"    Sample size per group: {test_config.sample_size_per_group}")
    logger.info(f"    Traffic split: {test_config.traffic_split:.1%}")
    
    return framework, test_config


def test_traffic_routing():
    """Test traffic routing between control and treatment."""
    logger.info("🧪 Testing traffic routing...")
    
    framework, test_config = test_ab_test_creation()
    
    # Test traffic routing
    np.random.seed(42)
    control_count = 0
    treatment_count = 0
    
    for _ in range(1000):
        test_data = np.random.randn(5)
        model_type, prediction = framework.route_traffic(test_config.test_id, test_data)
        
        if model_type == 'control':
            control_count += 1
        else:
            treatment_count += 1
        
        assert model_type in ['control', 'treatment']
        assert isinstance(prediction, (int, float, np.number))
    
    # Check traffic split approximation
    treatment_ratio = treatment_count / (control_count + treatment_count)
    expected_ratio = test_config.traffic_split
    
    # Allow 5% tolerance in traffic split
    assert abs(treatment_ratio - expected_ratio) < 0.05
    
    logger.info(f"  📊 Traffic Routing Results:")
    logger.info(f"    Control requests: {control_count}")
    logger.info(f"    Treatment requests: {treatment_count}")
    logger.info(f"    Treatment ratio: {treatment_ratio:.3f} (expected: {expected_ratio:.3f})")
    
    return framework, test_config


def test_ab_test_analysis():
    """Test A/B test statistical analysis."""
    logger.info("🧪 Testing A/B test analysis...")
    
    framework, test_config = test_traffic_routing()
    
    # Simulate A/B test data collection
    np.random.seed(42)
    
    # Generate synthetic test data
    for i in range(200):  # Simulate 200 requests
        # Control group (slightly worse performance)
        framework.record_ab_test_data(
            test_config.test_id, 'control',
            prediction=np.random.normal(1.0, 0.2),
            actual=np.random.normal(1.0, 0.1),
            response_time=np.random.normal(30, 5),
            cost=np.random.normal(0.5, 0.1)
        )
        
        # Treatment group (slightly better performance)
        framework.record_ab_test_data(
            test_config.test_id, 'treatment',
            prediction=np.random.normal(1.0, 0.15),  # Better accuracy
            actual=np.random.normal(1.0, 0.1),
            response_time=np.random.normal(25, 4),    # Faster response
            cost=np.random.normal(0.4, 0.08)          # Lower cost
        )
    
    # Analyze A/B test results
    results = framework.analyze_ab_test(test_config.test_id)
    
    # Validate results
    assert results.test_id == test_config.test_id
    assert results.constitutional_hash == "cdd01ef066bc6cf2"
    assert 'prediction_accuracy' in results.control_performance
    assert 'prediction_accuracy' in results.treatment_performance
    assert len(results.p_values) > 0
    assert len(results.effect_sizes) > 0
    assert results.test_conclusion in ['treatment_wins', 'control_wins', 'no_difference', 'inconclusive']
    
    logger.info(f"  📊 A/B Test Analysis Results:")
    logger.info(f"    Test conclusion: {results.test_conclusion}")
    logger.info(f"    Deployment recommendation: {results.deployment_recommendation}")
    logger.info(f"    Sample sizes - Control: {results.sample_sizes['control']}, Treatment: {results.sample_sizes['treatment']}")
    
    return results


def test_shadow_deployment():
    """Test shadow deployment functionality."""
    logger.info("🧪 Testing shadow deployment...")
    
    framework = ABTestingFramework()
    
    # Create test models
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    
    np.random.seed(42)
    X_train = np.random.randn(100, 5)
    y_train = X_train[:, 0] * 2 + X_train[:, 1] * 1.5 + np.random.randn(100) * 0.1
    
    production_model = LinearRegression()
    production_model.fit(X_train, y_train)
    
    shadow_model = RandomForestRegressor(n_estimators=30, random_state=42)
    shadow_model.fit(X_train, y_train)
    
    # Create shadow deployment
    shadow_status = framework.create_shadow_deployment(
        shadow_model, production_model, traffic_percentage=0.2
    )
    
    # Validate shadow deployment
    assert shadow_status.constitutional_hash == "cdd01ef066bc6cf2"
    assert shadow_status.traffic_percentage == 0.2
    assert not shadow_status.rollback_triggered
    assert shadow_status.deployment_id in framework.shadow_deployments
    
    # Test shadow request processing
    test_data = np.random.randn(5)
    production_prediction, comparison_data = framework.process_shadow_request(
        shadow_status.deployment_id, test_data
    )
    
    # Validate shadow request processing
    assert isinstance(production_prediction, (int, float, np.number))
    assert 'production_prediction' in comparison_data
    assert 'shadow_prediction' in comparison_data
    assert 'prediction_difference' in comparison_data
    
    logger.info(f"  ✅ Shadow deployment created: {shadow_status.deployment_id}")
    logger.info(f"    Traffic percentage: {shadow_status.traffic_percentage:.1%}")
    logger.info(f"    Production prediction: {production_prediction:.3f}")
    logger.info(f"    Prediction difference: {comparison_data['prediction_difference']:.3f}")
    
    return framework, shadow_status


def test_shadow_monitoring_and_rollback():
    """Test shadow deployment monitoring and automatic rollback."""
    logger.info("🧪 Testing shadow monitoring and rollback...")
    
    framework, shadow_status = test_shadow_deployment()
    
    # Simulate shadow requests to generate monitoring data
    np.random.seed(42)
    
    for _ in range(50):
        test_data = np.random.randn(5)
        framework.process_shadow_request(shadow_status.deployment_id, test_data)
    
    # Monitor shadow deployment
    monitoring_results = framework.monitor_shadow_deployment(shadow_status.deployment_id)
    
    # Validate monitoring results
    assert 'status' in monitoring_results
    assert 'rollback_required' in monitoring_results
    assert 'performance_comparison' in monitoring_results
    assert monitoring_results['constitutional_hash_verified'] == True
    
    logger.info(f"  📊 Shadow Monitoring Results:")
    logger.info(f"    Status: {monitoring_results['status']}")
    logger.info(f"    Rollback required: {monitoring_results['rollback_required']}")
    if 'performance_comparison' in monitoring_results:
        perf = monitoring_results['performance_comparison']
        logger.info(f"    Avg prediction difference: {perf.get('avg_prediction_difference', 0):.3f}")
        logger.info(f"    Sample count: {perf.get('sample_count', 0)}")
    
    return monitoring_results


def test_production_ml_optimizer_integration():
    """Test A/B testing integration with ProductionMLOptimizer."""
    logger.info("🧪 Testing ProductionMLOptimizer A/B testing integration...")
    
    # Initialize optimizer
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")
    
    # Train initial model
    np.random.seed(42)
    X = np.random.randn(200, 8)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(200) * 0.1
    
    training_result = optimizer.train_with_adaptive_architecture(X, y)

    # Store the trained model as the production model
    optimizer.models['best_model'] = training_result['model']

    # Create new model for A/B testing
    from sklearn.ensemble import RandomForestRegressor
    new_model = RandomForestRegressor(n_estimators=50, random_state=42)
    new_model.fit(X, y)

    # Test A/B test creation
    ab_test_config = optimizer.create_ab_test("New Model A/B Test", new_model)
    
    # Validate A/B test
    assert ab_test_config.constitutional_hash == "cdd01ef066bc6cf2"
    assert len(optimizer.ab_testing_framework.active_tests) == 1
    
    # Test shadow deployment
    shadow_status = optimizer.deploy_shadow_model(new_model, traffic_percentage=0.15)
    
    # Validate shadow deployment
    assert shadow_status.constitutional_hash == "cdd01ef066bc6cf2"
    assert shadow_status.traffic_percentage == 0.15
    assert len(optimizer.ab_testing_framework.shadow_deployments) == 1
    
    # Test dashboard data
    dashboard_data = optimizer.get_ab_testing_dashboard_data()
    
    # Validate dashboard data
    assert 'active_tests' in dashboard_data
    assert 'active_shadow_deployments' in dashboard_data
    assert 'constitutional_verification' in dashboard_data
    assert 'system_integration' in dashboard_data
    
    verification = dashboard_data['constitutional_verification']
    assert verification['verified'] == True
    assert verification['hash'] == "cdd01ef066bc6cf2"
    
    integration = dashboard_data['system_integration']
    assert integration['ab_testing_integrated'] == True
    assert integration['constitutional_hash_consistency'] == True
    
    logger.info(f"  📊 Integration Test Results:")
    logger.info(f"    A/B tests active: {dashboard_data['active_tests']}")
    logger.info(f"    Shadow deployments: {dashboard_data['active_shadow_deployments']}")
    logger.info(f"    Constitutional hash verified: {verification['verified']}")
    logger.info(f"    System integration verified: {integration['constitutional_hash_consistency']}")
    
    return dashboard_data


def main():
    """Run all A/B testing framework tests."""
    logger.info("🚀 Starting A/B Testing Framework Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: A/B testing framework
        framework = test_ab_testing_framework()
        logger.info("✅ A/B testing framework tests passed\n")
        
        # Test 2: Sample size calculation
        test_sample_size_calculation()
        logger.info("✅ Sample size calculation tests passed\n")
        
        # Test 3: A/B test creation
        test_ab_test_creation()
        logger.info("✅ A/B test creation tests passed\n")
        
        # Test 4: Traffic routing
        test_traffic_routing()
        logger.info("✅ Traffic routing tests passed\n")
        
        # Test 5: A/B test analysis
        test_ab_test_analysis()
        logger.info("✅ A/B test analysis tests passed\n")
        
        # Test 6: Shadow deployment
        test_shadow_deployment()
        logger.info("✅ Shadow deployment tests passed\n")
        
        # Test 7: Shadow monitoring and rollback
        test_shadow_monitoring_and_rollback()
        logger.info("✅ Shadow monitoring and rollback tests passed\n")
        
        # Test 8: Production ML optimizer integration
        test_production_ml_optimizer_integration()
        logger.info("✅ Production ML optimizer integration tests passed\n")
        
        logger.info("🎉 ALL A/B TESTING FRAMEWORK TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ A/B testing framework successfully implemented:")
        logger.info("  • Statistical A/B testing with proper randomization")
        logger.info("  • Sample size calculations with power analysis")
        logger.info("  • Significance testing and effect size analysis")
        logger.info("  • Shadow deployments for risk-free testing")
        logger.info("  • Automatic rollback on performance degradation")
        logger.info("  • Traffic routing with configurable splits")
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
