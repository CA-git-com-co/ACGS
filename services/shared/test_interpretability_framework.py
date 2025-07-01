#!/usr/bin/env python3
"""
Test Script for Model Interpretability Framework Implementation

Tests feature importance analysis, SHAP values for model explanations, prediction
confidence scoring, and interpretability dashboard functionality for constitutional
AI decision transparency and auditability.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import os
import sys

import numpy as np

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_ml_optimizer import (
    ModelInterpretabilityFramework,
    ProductionMLOptimizer,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_model_interpretability_framework():
    """Test the ModelInterpretabilityFramework class directly."""
    logger.info("🧪 Testing ModelInterpretabilityFramework...")

    # Initialize framework
    framework = ModelInterpretabilityFramework("cdd01ef066bc6cf2")

    # Test initial state
    assert framework.constitutional_hash == "cdd01ef066bc6cf2"
    assert len(framework.feature_importance_history) == 0
    assert len(framework.shap_analysis_cache) == 0

    logger.info(
        f"  ✅ Framework initialized with hash: {framework.constitutional_hash}"
    )

    return framework


def test_feature_importance_analysis():
    """Test feature importance analysis."""
    logger.info("🧪 Testing feature importance analysis...")

    framework = ModelInterpretabilityFramework()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(150, 8)
    y = X[:, 0] * 3 + X[:, 1] * 2 + X[:, 2] * 1.5 + np.random.randn(150) * 0.1

    # Train model
    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)

    # Test feature importance analysis
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    # Test tree-based importance
    importance_result = framework.analyze_feature_importance(
        model, X, feature_names, importance_type="tree_based"
    )

    # Validate results
    assert importance_result.importance_type == "tree_based"
    assert len(importance_result.feature_names) == X.shape[1]
    assert len(importance_result.importance_scores) == X.shape[1]
    assert len(importance_result.top_features) == min(
        10, X.shape[1]
    )  # Up to 10 or number of features
    assert importance_result.constitutional_hash == "cdd01ef066bc6cf2"

    logger.info("  📊 Feature Importance Analysis:")
    logger.info(f"    Importance type: {importance_result.importance_type}")
    logger.info(
        f"    Top feature: {importance_result.top_features[0][0]} ({importance_result.top_features[0][1]:.3f})"
    )
    logger.info(f"    Features analyzed: {len(importance_result.feature_names)}")

    # Test permutation importance
    perm_importance_result = framework.analyze_feature_importance(
        model, X, feature_names, importance_type="permutation"
    )

    assert perm_importance_result.importance_type == "permutation"

    return importance_result, perm_importance_result


def test_shap_analysis():
    """Test SHAP values analysis."""
    logger.info("🧪 Testing SHAP analysis...")

    framework = ModelInterpretabilityFramework()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(100, 6)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(100) * 0.1

    # Train model
    from sklearn.linear_model import LinearRegression

    model = LinearRegression()
    model.fit(X, y)

    # Test SHAP analysis
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    shap_result = framework.analyze_shap_values(model, X, feature_names, sample_size=50)

    # Validate results
    assert len(shap_result.shap_values) <= 50  # Sample size limit
    assert shap_result.expected_value is not None
    assert len(shap_result.feature_names) == X.shape[1]
    assert len(shap_result.sample_explanations) <= 5  # Top 5 samples
    assert len(shap_result.global_importance) == X.shape[1]
    assert shap_result.constitutional_hash == "cdd01ef066bc6cf2"

    logger.info("  📊 SHAP Analysis:")
    logger.info(f"    Expected value: {shap_result.expected_value:.3f}")
    logger.info(f"    Samples analyzed: {len(shap_result.shap_values)}")
    logger.info(f"    Global importance features: {len(shap_result.global_importance)}")
    logger.info(
        f"    Constitutional factors: {len(shap_result.constitutional_compliance_factors)}"
    )

    return shap_result


def test_prediction_confidence():
    """Test prediction confidence scoring."""
    logger.info("🧪 Testing prediction confidence scoring...")

    framework = ModelInterpretabilityFramework()

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(20, 5)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(20) * 0.1

    # Train model
    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor(n_estimators=30, random_state=42)
    model.fit(X, y)

    # Test prediction confidence
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    confidence_results = framework.calculate_prediction_confidence(
        model,
        X[:10],
        feature_names,  # First 10 samples
    )

    # Validate results
    assert len(confidence_results) == 10

    for confidence in confidence_results:
        assert hasattr(confidence, "prediction")
        assert hasattr(confidence, "confidence_score")
        assert hasattr(confidence, "confidence_interval")
        assert hasattr(confidence, "uncertainty_sources")
        assert hasattr(confidence, "constitutional_compliance_confidence")
        assert hasattr(confidence, "explanation")

        assert 0 <= confidence.confidence_score <= 1
        assert 0 <= confidence.constitutional_compliance_confidence <= 1
        assert len(confidence.confidence_interval) == 2
        assert isinstance(confidence.uncertainty_sources, dict)
        assert isinstance(confidence.explanation, str)

    avg_confidence = np.mean([c.confidence_score for c in confidence_results])
    avg_constitutional_confidence = np.mean(
        [c.constitutional_compliance_confidence for c in confidence_results]
    )

    logger.info("  📊 Prediction Confidence:")
    logger.info(f"    Samples analyzed: {len(confidence_results)}")
    logger.info(f"    Average confidence: {avg_confidence:.3f}")
    logger.info(
        f"    Average constitutional confidence: {avg_constitutional_confidence:.3f}"
    )

    return confidence_results


def test_production_ml_optimizer_integration():
    """Test interpretability framework integration with ProductionMLOptimizer."""
    logger.info("🧪 Testing ProductionMLOptimizer interpretability integration...")

    # Initialize optimizer
    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Generate training data
    np.random.seed(42)
    X = np.random.randn(200, 10)
    y = X[:, 0] * 3 + X[:, 1] * 2 + X[:, 2] * 1.5 + np.random.randn(200) * 0.1

    # Train a model
    training_result = optimizer.train_with_adaptive_architecture(X, y)
    model = training_result["model"]

    # Test model interpretability analysis
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    interpretability_results = optimizer.analyze_model_interpretability(
        model, X, feature_names
    )

    # Validate interpretability results
    assert "feature_importance" in interpretability_results
    assert "shap_analysis" in interpretability_results
    assert "prediction_confidence" in interpretability_results
    assert "interpretability_summary" in interpretability_results

    # Check feature importance
    feature_importance = interpretability_results["feature_importance"]
    assert "top_features" in feature_importance
    assert "constitutional_hash" in feature_importance
    assert feature_importance["constitutional_hash"] == "cdd01ef066bc6cf2"

    # Check SHAP analysis
    shap_analysis = interpretability_results["shap_analysis"]
    assert "expected_value" in shap_analysis
    assert "global_importance" in shap_analysis
    assert "constitutional_compliance_factors" in shap_analysis
    assert shap_analysis["constitutional_hash"] == "cdd01ef066bc6cf2"

    # Check prediction confidence
    prediction_confidence = interpretability_results["prediction_confidence"]
    assert "average_confidence" in prediction_confidence
    assert "average_constitutional_confidence" in prediction_confidence
    assert "confidence_distribution" in prediction_confidence

    # Check interpretability summary
    summary = interpretability_results["interpretability_summary"]
    assert summary["constitutional_hash_verified"] == True
    assert "transparency_score" in summary
    assert "auditability_score" in summary

    logger.info("  📊 Interpretability Integration:")
    logger.info(f"    Top feature: {feature_importance['top_features'][0][0]}")
    logger.info(
        f"    Average confidence: {prediction_confidence['average_confidence']:.3f}"
    )
    logger.info(f"    Transparency score: {summary['transparency_score']:.3f}")
    logger.info(f"    Auditability score: {summary['auditability_score']:.3f}")

    return interpretability_results


def test_prediction_explanation():
    """Test individual prediction explanation."""
    logger.info("🧪 Testing individual prediction explanation...")

    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Generate test data
    np.random.seed(42)
    X = np.random.randn(100, 8)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(100) * 0.1

    # Train model
    training_result = optimizer.train_with_adaptive_architecture(X, y)
    model = training_result["model"]

    # Test prediction explanation for a single sample
    sample = X[0]
    feature_names = [f"feature_{i}" for i in range(len(sample))]

    explanation = optimizer.explain_prediction(model, sample, feature_names)

    # Validate explanation
    assert "prediction" in explanation
    assert "feature_contributions" in explanation
    assert "top_contributing_features" in explanation
    assert "uncertainty_analysis" in explanation
    assert "constitutional_compliance" in explanation
    assert "explanation_metadata" in explanation

    # Check prediction details
    prediction_details = explanation["prediction"]
    assert "value" in prediction_details
    assert "confidence_score" in prediction_details
    assert "confidence_interval" in prediction_details
    assert "explanation" in prediction_details

    # Check constitutional compliance
    constitutional = explanation["constitutional_compliance"]
    assert "confidence" in constitutional
    assert "hash_verified" in constitutional
    assert constitutional["hash_verified"] == True

    logger.info("  📊 Prediction Explanation:")
    logger.info(f"    Prediction: {prediction_details['value']:.3f}")
    logger.info(f"    Confidence: {prediction_details['confidence_score']:.3f}")
    logger.info(
        f"    Top feature: {explanation['top_contributing_features'][0]['feature_name']}"
    )
    logger.info(f"    Constitutional confidence: {constitutional['confidence']:.3f}")

    return explanation


def test_interpretability_dashboard():
    """Test interpretability dashboard data generation."""
    logger.info("🧪 Testing interpretability dashboard...")

    optimizer = ProductionMLOptimizer("cdd01ef066bc6cf2")

    # Generate test data and perform some analyses
    np.random.seed(42)
    X = np.random.randn(150, 6)
    y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(150) * 0.1

    # Train model
    training_result = optimizer.train_with_adaptive_architecture(X, y)
    model = training_result["model"]

    # Perform interpretability analysis to populate data
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    optimizer.analyze_model_interpretability(model, X, feature_names)

    # Get dashboard data
    dashboard_data = optimizer.get_interpretability_dashboard_data()

    # Validate dashboard data structure
    assert "feature_importance_history" in dashboard_data
    assert "shap_analysis_cache" in dashboard_data
    assert "constitutional_verification" in dashboard_data
    assert "interpretability_capabilities" in dashboard_data
    assert "system_status" in dashboard_data

    # Check constitutional verification
    verification = dashboard_data["constitutional_verification"]
    assert verification["verified"] == True
    assert verification["hash"] == "cdd01ef066bc6cf2"
    assert verification["interpretability_framework_verified"] == True

    # Check capabilities
    capabilities = dashboard_data["interpretability_capabilities"]
    expected_capabilities = [
        "feature_importance_analysis",
        "shap_value_analysis",
        "prediction_confidence_scoring",
        "constitutional_compliance_transparency",
        "uncertainty_quantification",
    ]

    for capability in expected_capabilities:
        assert capability in capabilities
        assert capabilities[capability] == True

    # Check system status
    status = dashboard_data["system_status"]
    assert status["interpretability_framework_operational"] == True
    assert status["constitutional_hash_integrity"] == True

    logger.info("  📊 Dashboard Data Generated:")
    logger.info(f"    Constitutional hash verified: {verification['verified']}")
    logger.info(
        f"    Feature importance analyses: {status['feature_importance_analyses']}"
    )
    logger.info(f"    SHAP analyses cached: {status['shap_analyses_cached']}")
    logger.info(f"    Capabilities: {len(capabilities)} features enabled")

    return dashboard_data


def main():
    """Run all model interpretability framework tests."""
    logger.info("🚀 Starting Model Interpretability Framework Tests")
    logger.info("=" * 60)

    try:
        # Test 1: Model interpretability framework
        framework = test_model_interpretability_framework()
        logger.info("✅ Model interpretability framework tests passed\n")

        # Test 2: Feature importance analysis
        test_feature_importance_analysis()
        logger.info("✅ Feature importance analysis tests passed\n")

        # Test 3: SHAP analysis
        test_shap_analysis()
        logger.info("✅ SHAP analysis tests passed\n")

        # Test 4: Prediction confidence
        test_prediction_confidence()
        logger.info("✅ Prediction confidence tests passed\n")

        # Test 5: Production ML optimizer integration
        test_production_ml_optimizer_integration()
        logger.info("✅ Production ML optimizer integration tests passed\n")

        # Test 6: Prediction explanation
        test_prediction_explanation()
        logger.info("✅ Prediction explanation tests passed\n")

        # Test 7: Interpretability dashboard
        test_interpretability_dashboard()
        logger.info("✅ Interpretability dashboard tests passed\n")

        logger.info("🎉 ALL MODEL INTERPRETABILITY TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("✅ Model interpretability framework successfully implemented:")
        logger.info("  • Feature importance analysis (tree-based, permutation)")
        logger.info("  • SHAP values for model explanations")
        logger.info("  • Prediction confidence scoring with uncertainty quantification")
        logger.info("  • Constitutional AI decision transparency and auditability")
        logger.info("  • Interpretability dashboard with historical data")
        logger.info("  • Individual prediction explanations")
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
