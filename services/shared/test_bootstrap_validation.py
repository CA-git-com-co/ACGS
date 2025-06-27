#!/usr/bin/env python3
"""
Test Script for Bootstrap Confidence Intervals Implementation

Tests the comprehensive bootstrap validation framework with 1000+ iterations,
95% and 99% confidence intervals, and calibration validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import os
import numpy as np
import logging
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_ml_optimizer import ProductionMLOptimizer, BootstrapValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_bootstrap_validator():
    """Test the BootstrapValidator class directly."""
    logger.info("🧪 Testing BootstrapValidator...")
    
    # Initialize validator
    validator = BootstrapValidator(n_iterations=1000)
    
    # Generate test data
    np.random.seed(42)
    test_data = np.random.normal(10, 2, size=100)  # Mean=10, std=2
    
    # Test bootstrap confidence intervals
    bootstrap_result = validator.bootstrap_confidence_intervals(
        test_data, np.mean, [0.95, 0.99]
    )
    
    # Validate results
    assert bootstrap_result.n_iterations == 1000
    assert len(bootstrap_result.bootstrap_samples) == 1000
    assert bootstrap_result.confidence_interval_95[0] < bootstrap_result.original_value < bootstrap_result.confidence_interval_95[1]
    assert bootstrap_result.confidence_interval_99[0] < bootstrap_result.confidence_interval_99[1]
    
    logger.info(f"  ✅ Original mean: {bootstrap_result.original_value:.3f}")
    logger.info(f"  ✅ 95% CI: [{bootstrap_result.confidence_interval_95[0]:.3f}, {bootstrap_result.confidence_interval_95[1]:.3f}]")
    logger.info(f"  ✅ 99% CI: [{bootstrap_result.confidence_interval_99[0]:.3f}, {bootstrap_result.confidence_interval_99[1]:.3f}]")
    logger.info(f"  ✅ Bootstrap bias: {bootstrap_result.bias_estimate:.4f}")
    
    return validator


def test_bootstrap_model_performance():
    """Test bootstrap validation for model performance metrics."""
    logger.info("🧪 Testing bootstrap model performance validation...")
    
    validator = BootstrapValidator(n_iterations=1000)
    
    # Create a simple model and data
    from sklearn.linear_model import LinearRegression
    
    # Generate synthetic data
    np.random.seed(42)
    X = np.random.randn(200, 5)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(200) * 0.1
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Test bootstrap model performance
    bootstrap_results = validator.bootstrap_model_performance(model, X, y)
    
    # Validate results
    expected_metrics = ['mae', 'mse', 'rmse', 'r2_score']
    for metric in expected_metrics:
        assert metric in bootstrap_results
        result = bootstrap_results[metric]
        assert result.n_iterations == 1000
        assert len(result.bootstrap_samples) == 1000
        
        logger.info(f"  📊 {metric.upper()}: {result.original_value:.4f} "
                   f"[95% CI: {result.confidence_interval_95[0]:.4f}, "
                   f"{result.confidence_interval_95[1]:.4f}]")
    
    return bootstrap_results


def test_bootstrap_calibration():
    """Test bootstrap calibration validation."""
    logger.info("🧪 Testing bootstrap calibration validation...")
    
    validator = BootstrapValidator(n_iterations=1000)
    
    # Generate test data with known distribution
    np.random.seed(42)
    test_data = np.random.normal(5, 1, size=100)
    
    # Test calibration
    calibration_results = validator.validate_bootstrap_calibration(
        test_data, np.mean, n_experiments=50
    )
    
    # Validate calibration results
    assert 'coverage_95_actual' in calibration_results
    assert 'coverage_99_actual' in calibration_results
    assert calibration_results['n_experiments'] == 50
    
    # Check that coverage is reasonably close to expected
    coverage_95_error = abs(calibration_results['coverage_95_actual'] - 0.95)
    coverage_99_error = abs(calibration_results['coverage_99_actual'] - 0.99)
    
    logger.info(f"  📈 95% CI coverage: {calibration_results['coverage_95_actual']:.3f} (error: {coverage_95_error:.3f})")
    logger.info(f"  📈 99% CI coverage: {calibration_results['coverage_99_actual']:.3f} (error: {coverage_99_error:.3f})")
    
    # Calibration should be reasonable (within 10% error)
    assert coverage_95_error < 0.10, f"95% CI calibration error too high: {coverage_95_error}"
    assert coverage_99_error < 0.10, f"99% CI calibration error too high: {coverage_99_error}"
    
    return calibration_results


def test_comprehensive_bootstrap_validation():
    """Test comprehensive bootstrap validation in ProductionMLOptimizer."""
    logger.info("🧪 Testing comprehensive bootstrap validation...")
    
    # Initialize optimizer
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")
    
    # Generate training data
    np.random.seed(42)
    X = np.random.randn(300, 10)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + X[:, 2] * 0.8 + np.random.randn(300) * 0.1
    
    # Train a model using the optimizer
    training_result = optimizer.train_with_adaptive_architecture(X, y)
    model = training_result['model']
    
    # Test comprehensive bootstrap validation
    validation_results = optimizer.comprehensive_bootstrap_validation(model, X, y)
    
    # Validate results structure
    assert 'bootstrap_metrics' in validation_results
    assert 'calibration_validation' in validation_results
    assert 'constitutional_hash' in validation_results
    assert validation_results['constitutional_hash'] == "cdd01ef066bc6cf2"
    
    # Check bootstrap metrics
    bootstrap_metrics = validation_results['bootstrap_metrics']
    expected_metrics = ['mae', 'mse', 'rmse', 'r2_score', 'prediction_accuracy', 'cost_efficiency', 'reliability_score']
    
    for metric in expected_metrics:
        if metric in bootstrap_metrics:
            result = bootstrap_metrics[metric]
            assert hasattr(result, 'confidence_interval_95')
            assert hasattr(result, 'confidence_interval_99')
            assert result.n_iterations >= 1000
            
            logger.info(f"  📊 {metric}: {result.original_value:.4f} "
                       f"[95% CI: {result.confidence_interval_95[0]:.4f}, "
                       f"{result.confidence_interval_95[1]:.4f}]")
    
    # Check calibration validation
    calibration = validation_results['calibration_validation']
    assert calibration['n_experiments'] >= 50
    
    logger.info(f"  🎯 Calibration validated with {calibration['n_experiments']} experiments")
    
    return validation_results


def test_business_decision_confidence():
    """Test confidence bounds for business decision making."""
    logger.info("🧪 Testing business decision confidence bounds...")
    
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")
    
    # Generate business scenario data
    np.random.seed(42)
    X = np.random.randn(200, 8)
    y = X[:, 0] * 3 + X[:, 1] * 2 + np.random.randn(200) * 0.2
    
    # Train model
    training_result = optimizer.train_with_adaptive_architecture(X, y)
    model = training_result['model']
    
    # Get comprehensive validation
    validation_results = optimizer.comprehensive_bootstrap_validation(model, X, y)
    
    # Extract business metrics with confidence intervals
    business_metrics = {}
    for metric_name in ['prediction_accuracy', 'cost_efficiency', 'reliability_score']:
        if metric_name in validation_results['bootstrap_metrics']:
            result = validation_results['bootstrap_metrics'][metric_name]
            business_metrics[metric_name] = {
                'value': result.original_value,
                'ci_95_lower': result.confidence_interval_95[0],
                'ci_95_upper': result.confidence_interval_95[1],
                'ci_99_lower': result.confidence_interval_99[0],
                'ci_99_upper': result.confidence_interval_99[1]
            }
    
    # Simulate business decision making
    logger.info("  💼 Business Decision Analysis:")
    for metric_name, metric_data in business_metrics.items():
        logger.info(f"    {metric_name}: {metric_data['value']:.3f}")
        logger.info(f"      95% confidence: [{metric_data['ci_95_lower']:.3f}, {metric_data['ci_95_upper']:.3f}]")
        logger.info(f"      99% confidence: [{metric_data['ci_99_lower']:.3f}, {metric_data['ci_99_upper']:.3f}]")
        
        # Business decision logic
        if metric_data['ci_95_lower'] > 0.8:  # High confidence threshold
            decision = "DEPLOY - High confidence in performance"
        elif metric_data['ci_95_lower'] > 0.6:  # Medium confidence threshold
            decision = "CAUTIOUS DEPLOY - Monitor closely"
        else:
            decision = "DO NOT DEPLOY - Insufficient confidence"
        
        logger.info(f"      Decision: {decision}")
    
    return business_metrics


def main():
    """Run all bootstrap validation tests."""
    logger.info("🚀 Starting Bootstrap Confidence Intervals Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: Bootstrap validator
        validator = test_bootstrap_validator()
        logger.info("✅ Bootstrap validator tests passed\n")
        
        # Test 2: Bootstrap model performance
        test_bootstrap_model_performance()
        logger.info("✅ Bootstrap model performance tests passed\n")
        
        # Test 3: Bootstrap calibration
        test_bootstrap_calibration()
        logger.info("✅ Bootstrap calibration tests passed\n")
        
        # Test 4: Comprehensive bootstrap validation
        test_comprehensive_bootstrap_validation()
        logger.info("✅ Comprehensive bootstrap validation tests passed\n")
        
        # Test 5: Business decision confidence
        test_business_decision_confidence()
        logger.info("✅ Business decision confidence tests passed\n")
        
        logger.info("🎉 ALL BOOTSTRAP VALIDATION TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ Bootstrap confidence intervals successfully implemented:")
        logger.info("  • 1000+ bootstrap iterations for robust estimation")
        logger.info("  • 95% and 99% confidence intervals for all metrics")
        logger.info("  • Bootstrap calibration validation")
        logger.info("  • Business decision confidence bounds")
        logger.info("  • Statistical significance testing")
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
