#!/usr/bin/env python3
"""
Test Script for Comprehensive Evaluation Metrics Implementation

Tests multiple evaluation metrics (MAE, RMSE, R², MAPE), business-specific metrics
(cost efficiency, response time accuracy, constitutional compliance rate), and
evaluation dashboard functionality.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import os
import sys

import numpy as np

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_ml_optimizer import ComprehensiveMetricsEvaluator, ProductionMLOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_comprehensive_metrics_evaluator():
    """Test the ComprehensiveMetricsEvaluator class directly."""
    logger.info("🧪 Testing ComprehensiveMetricsEvaluator...")

    # Initialize evaluator
    evaluator = ComprehensiveMetricsEvaluator("cdd01ef066bc6cf2")

    # Test initial state
    assert evaluator.constitutional_hash == "cdd01ef066bc6cf2"
    assert len(evaluator.metric_history) == 0
    assert evaluator.baseline_metrics is None

    logger.info(
        f"  ✅ Evaluator initialized with hash: {evaluator.constitutional_hash}"
    )

    return evaluator


def test_regression_metrics():
    """Test regression metrics calculation."""
    logger.info("🧪 Testing regression metrics calculation...")

    evaluator = ComprehensiveMetricsEvaluator()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(200, 10)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(200) * 0.1

    # Train a simple model
    from sklearn.linear_model import LinearRegression

    model = LinearRegression()
    model.fit(X, y)

    # Calculate comprehensive metrics
    metrics = evaluator.calculate_comprehensive_metrics(model, X, y)

    # Validate regression metrics
    assert hasattr(metrics, "mae")
    assert hasattr(metrics, "rmse")
    assert hasattr(metrics, "r2_score")
    assert hasattr(metrics, "mape")

    assert metrics.mae > 0
    assert metrics.rmse > 0
    assert 0 <= metrics.r2_score <= 1
    assert metrics.mape >= 0

    logger.info("  📊 Regression Metrics:")
    logger.info(f"    MAE: {metrics.mae:.4f}")
    logger.info(f"    RMSE: {metrics.rmse:.4f}")
    logger.info(f"    R²: {metrics.r2_score:.4f}")
    logger.info(f"    MAPE: {metrics.mape:.2f}%")

    return metrics


def test_business_metrics():
    """Test business-specific metrics calculation."""
    logger.info("🧪 Testing business metrics calculation...")

    evaluator = ComprehensiveMetricsEvaluator()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(150, 8)
    y = X[:, 0] * 3 + X[:, 1] * 2 + np.random.randn(150) * 0.1

    # Train model
    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)

    # Generate synthetic business data
    response_times = np.random.uniform(100, 1000, len(y))  # Response times in ms
    costs = np.random.uniform(0.1, 2.0, len(y))  # Costs in dollars

    # Calculate metrics with business data
    metrics = evaluator.calculate_comprehensive_metrics(
        model, X, y, response_times=response_times, costs=costs
    )

    # Validate business metrics
    assert hasattr(metrics, "cost_efficiency")
    assert hasattr(metrics, "response_time_accuracy")
    assert hasattr(metrics, "constitutional_compliance_rate")

    assert 0 <= metrics.cost_efficiency <= 1
    assert 0 <= metrics.response_time_accuracy <= 1
    assert 0 <= metrics.constitutional_compliance_rate <= 1

    logger.info("  💼 Business Metrics:")
    logger.info(f"    Cost Efficiency: {metrics.cost_efficiency:.3f}")
    logger.info(f"    Response Time Accuracy: {metrics.response_time_accuracy:.3f}")
    logger.info(
        f"    Constitutional Compliance: {metrics.constitutional_compliance_rate:.3f}"
    )

    return metrics


def test_performance_metrics():
    """Test additional performance metrics."""
    logger.info("🧪 Testing performance metrics calculation...")

    evaluator = ComprehensiveMetricsEvaluator()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(100, 6)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(100) * 0.1

    # Train model
    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor(n_estimators=30, random_state=42)
    model.fit(X, y)

    # Calculate metrics
    metrics = evaluator.calculate_comprehensive_metrics(model, X, y)

    # Validate performance metrics
    assert hasattr(metrics, "prediction_stability")
    assert hasattr(metrics, "model_confidence")
    assert hasattr(metrics, "feature_importance_stability")

    assert 0 <= metrics.prediction_stability <= 1
    assert 0 <= metrics.model_confidence <= 1
    assert 0 <= metrics.feature_importance_stability <= 1

    logger.info("  🔧 Performance Metrics:")
    logger.info(f"    Prediction Stability: {metrics.prediction_stability:.3f}")
    logger.info(f"    Model Confidence: {metrics.model_confidence:.3f}")
    logger.info(
        f"    Feature Importance Stability: {metrics.feature_importance_stability:.3f}"
    )

    return metrics


def test_metric_trends():
    """Test metric trend analysis."""
    logger.info("🧪 Testing metric trend analysis...")

    evaluator = ComprehensiveMetricsEvaluator()

    # Generate multiple evaluations to create trend data
    np.random.seed(42)

    for i in range(5):
        # Generate slightly different data for each evaluation
        X = np.random.randn(100, 5)
        y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(100) * (0.1 + i * 0.02)

        # Train model
        from sklearn.linear_model import LinearRegression

        model = LinearRegression()
        model.fit(X, y)

        # Calculate metrics
        metrics = evaluator.calculate_comprehensive_metrics(model, X, y)

        logger.info(
            f"    Evaluation {i + 1}: R² = {metrics.r2_score:.3f}, MAE = {metrics.mae:.3f}"
        )

    # Analyze trends
    trends = evaluator.analyze_metric_trends(window_size=3)

    # Validate trends
    assert len(trends) > 0

    for trend in trends:
        assert hasattr(trend, "metric_name")
        assert hasattr(trend, "trend_direction")
        assert hasattr(trend, "change_percentage")
        assert hasattr(trend, "trend_significance")

        logger.info(
            f"    {trend.metric_name}: {trend.trend_direction} "
            f"({trend.change_percentage:+.1f}%)"
        )

    return trends


def test_production_ml_optimizer_integration():
    """Test comprehensive metrics integration with ProductionMLOptimizer."""
    logger.info("🧪 Testing ProductionMLOptimizer comprehensive metrics integration...")

    # Initialize optimizer
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Generate training data
    np.random.seed(42)
    X = np.random.randn(250, 12)
    y = X[:, 0] * 3 + X[:, 1] * 2 + X[:, 2] * 1.5 + np.random.randn(250) * 0.1

    # Train a model
    training_result = optimizer.train_with_adaptive_architecture(X, y)
    model = training_result["model"]

    # Test comprehensive metrics evaluation
    metrics = optimizer.evaluate_comprehensive_metrics(model, X, y)

    # Validate metrics
    assert metrics.constitutional_hash == "cdd01ef066bc6cf2"
    assert metrics.sample_size == len(y)

    logger.info("  📊 Comprehensive Metrics Evaluation:")
    logger.info(f"    R²: {metrics.r2_score:.3f}")
    logger.info(f"    MAE: {metrics.mae:.3f}")
    logger.info(
        f"    Constitutional Compliance: {metrics.constitutional_compliance_rate:.3f}"
    )

    # Test comprehensive model evaluation
    evaluation_results = optimizer.comprehensive_model_evaluation(model, X, y)

    # Validate evaluation results
    assert "comprehensive_metrics" in evaluation_results
    assert "bootstrap_validation" in evaluation_results
    assert "statistical_validation" in evaluation_results
    assert "evaluation_summary" in evaluation_results

    summary = evaluation_results["evaluation_summary"]
    assert summary["constitutional_hash_verified"] == True
    assert "overall_quality_score" in summary

    logger.info("  🎯 Comprehensive Evaluation:")
    logger.info(f"    Overall Quality Score: {summary['overall_quality_score']:.3f}")
    logger.info(
        f"    Deployment Recommendation: {summary['deployment_recommendation']}"
    )

    return evaluation_results


def test_evaluation_dashboard():
    """Test evaluation dashboard data generation."""
    logger.info("🧪 Testing evaluation dashboard data generation...")

    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Generate multiple evaluations for dashboard
    np.random.seed(42)

    for i in range(3):
        X = np.random.randn(150, 8)
        y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(150) * 0.1

        # Train model
        training_result = optimizer.train_with_adaptive_architecture(X, y)
        model = training_result["model"]

        # Evaluate metrics
        optimizer.evaluate_comprehensive_metrics(model, X, y)

    # Get dashboard data
    dashboard_data = optimizer.get_evaluation_dashboard_data()

    # Validate dashboard data structure
    assert "current_metrics" in dashboard_data
    assert "trends" in dashboard_data
    assert "historical_data" in dashboard_data
    assert "summary" in dashboard_data
    assert "constitutional_verification" in dashboard_data

    # Check constitutional verification
    verification = dashboard_data["constitutional_verification"]
    assert verification["verified"] == True
    assert verification["hash"] == "cdd01ef066bc6cf2"

    # Check current metrics
    current_metrics = dashboard_data["current_metrics"]
    assert "regression_metrics" in current_metrics
    assert "business_metrics" in current_metrics
    assert "performance_metrics" in current_metrics

    logger.info("  📊 Dashboard Data Generated:")
    logger.info(
        f"    Total Evaluations: {dashboard_data['summary']['total_evaluations']}"
    )
    logger.info(f"    Constitutional Hash Verified: {verification['verified']}")
    logger.info(f"    Trends Available: {len(dashboard_data['trends'])}")

    return dashboard_data


def main():
    """Run all comprehensive metrics tests."""
    logger.info("🚀 Starting Comprehensive Evaluation Metrics Tests")
    logger.info("=" * 60)

    try:
        # Test 1: Comprehensive metrics evaluator
        evaluator = test_comprehensive_metrics_evaluator()
        logger.info("✅ Comprehensive metrics evaluator tests passed\n")

        # Test 2: Regression metrics
        test_regression_metrics()
        logger.info("✅ Regression metrics tests passed\n")

        # Test 3: Business metrics
        test_business_metrics()
        logger.info("✅ Business metrics tests passed\n")

        # Test 4: Performance metrics
        test_performance_metrics()
        logger.info("✅ Performance metrics tests passed\n")

        # Test 5: Metric trends
        test_metric_trends()
        logger.info("✅ Metric trends tests passed\n")

        # Test 6: Production ML optimizer integration
        test_production_ml_optimizer_integration()
        logger.info("✅ Production ML optimizer integration tests passed\n")

        # Test 7: Evaluation dashboard
        test_evaluation_dashboard()
        logger.info("✅ Evaluation dashboard tests passed\n")

        logger.info("🎉 ALL COMPREHENSIVE METRICS TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ Comprehensive evaluation metrics successfully implemented:")
        logger.info("  • Multiple regression metrics: MAE, RMSE, R², MAPE")
        logger.info(
            "  • Business-specific metrics: cost efficiency, response time accuracy"
        )
        logger.info("  • Constitutional compliance rate monitoring")
        logger.info(
            "  • Performance metrics: stability, confidence, feature importance"
        )
        logger.info("  • Metric trend analysis with significance testing")
        logger.info("  • Evaluation dashboard with historical data")
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
