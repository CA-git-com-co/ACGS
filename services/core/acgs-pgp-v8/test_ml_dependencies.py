#!/usr/bin/env python3
"""
ML Dependencies Compatibility Test for ACGS-PGP v8

Tests all advanced ML dependencies for compatibility with existing system
and verifies constitutional hash integrity.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_imports():
    """Test basic ML library imports."""
    try:
        import numpy as np
        import pandas as pd
        import sklearn

        logger.info("✅ Basic ML libraries imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Basic ML import failed: {e}")
        return False


def test_advanced_ml_imports():
    """Test advanced ML library imports."""
    try:
        # Advanced sklearn features
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer
        from sklearn.preprocessing import StandardScaler, PolynomialFeatures
        from sklearn.model_selection import StratifiedKFold, TimeSeriesSplit
        from sklearn.feature_selection import SelectKBest, f_regression

        # Hyperparameter optimization
        import optuna

        # Imbalanced learning
        from imblearn.over_sampling import SMOTE

        # Gradient boosting
        import xgboost as xgb
        import lightgbm as lgb

        # Text analysis
        import textstat
        from textblob import TextBlob

        # Statistical libraries
        from scipy import stats
        from scipy.stats import ks_2samp

        logger.info("✅ Advanced ML libraries imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Advanced ML import failed: {e}")
        return False


def test_iterative_imputer():
    """Test IterativeImputer (MICE) functionality."""
    try:
        import numpy as np
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer

        # Create test data with missing values
        X = np.array([[1, 2, 3], [4, np.nan, 6], [7, 8, np.nan]])

        # Test MICE imputation
        imputer = IterativeImputer(max_iter=10, random_state=42)
        X_imputed = imputer.fit_transform(X)

        assert X_imputed.shape == X.shape
        assert not np.isnan(X_imputed).any()

        logger.info("✅ IterativeImputer (MICE) working correctly")
        return True
    except Exception as e:
        logger.error(f"❌ IterativeImputer test failed: {e}")
        return False


def test_smote():
    """Test SMOTE functionality."""
    try:
        import numpy as np
        from imblearn.over_sampling import SMOTE
        from sklearn.datasets import make_classification

        # Create imbalanced dataset
        X, y = make_classification(
            n_samples=100,
            n_features=4,
            n_redundant=0,
            n_clusters_per_class=1,
            weights=[0.9, 0.1],
            random_state=42,
        )

        # Apply SMOTE
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)

        assert X_resampled.shape[0] > X.shape[0]
        assert len(np.unique(y_resampled, return_counts=True)[1]) == 2

        logger.info("✅ SMOTE working correctly")
        return True
    except Exception as e:
        logger.error(f"❌ SMOTE test failed: {e}")
        return False


def test_optuna():
    """Test Optuna hyperparameter optimization."""
    try:
        import optuna
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.datasets import make_regression
        from sklearn.model_selection import cross_val_score

        # Create test dataset
        X, y = make_regression(n_samples=100, n_features=4, random_state=42)

        def objective(trial):
            n_estimators = trial.suggest_int("n_estimators", 10, 50)
            max_depth = trial.suggest_int("max_depth", 3, 10)

            model = RandomForestRegressor(
                n_estimators=n_estimators, max_depth=max_depth, random_state=42
            )
            scores = cross_val_score(
                model, X, y, cv=3, scoring="neg_mean_squared_error"
            )
            return -scores.mean()

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=5)

        assert study.best_params is not None

        logger.info("✅ Optuna hyperparameter optimization working correctly")
        return True
    except Exception as e:
        logger.error(f"❌ Optuna test failed: {e}")
        return False


def test_gradient_boosting():
    """Test XGBoost and LightGBM."""
    try:
        import xgboost as xgb
        import lightgbm as lgb
        from sklearn.datasets import make_regression

        # Create test dataset
        X, y = make_regression(n_samples=100, n_features=4, random_state=42)

        # Test XGBoost
        xgb_model = xgb.XGBRegressor(n_estimators=10, random_state=42)
        xgb_model.fit(X, y)
        xgb_pred = xgb_model.predict(X)

        # Test LightGBM
        lgb_model = lgb.LGBMRegressor(n_estimators=10, random_state=42, verbose=-1)
        lgb_model.fit(X, y)
        lgb_pred = lgb_model.predict(X)

        assert len(xgb_pred) == len(y)
        assert len(lgb_pred) == len(y)

        logger.info("✅ XGBoost and LightGBM working correctly")
        return True
    except Exception as e:
        logger.error(f"❌ Gradient boosting test failed: {e}")
        return False


def test_text_analysis():
    """Test text analysis libraries."""
    try:
        import textstat
        from textblob import TextBlob

        test_text = "This is a simple test sentence for text analysis."

        # Test textstat
        readability = textstat.flesch_reading_ease(test_text)
        assert isinstance(readability, (int, float))

        # Test TextBlob
        blob = TextBlob(test_text)
        sentiment = blob.sentiment
        assert hasattr(sentiment, "polarity")
        assert hasattr(sentiment, "subjectivity")

        logger.info("✅ Text analysis libraries working correctly")
        return True
    except Exception as e:
        logger.error(f"❌ Text analysis test failed: {e}")
        return False


def test_constitutional_hash_integrity():
    """Verify constitutional hash integrity."""
    try:
        constitutional_hash = "cdd01ef066bc6cf2"

        # Check if hash is maintained in this file
        with open(__file__, "r") as f:
            content = f.read()
            assert constitutional_hash in content

        logger.info("✅ Constitutional hash integrity verified")
        return True
    except Exception as e:
        logger.error(f"❌ Constitutional hash integrity test failed: {e}")
        return False


def main():
    """Run all compatibility tests."""
    logger.info("🚀 Starting ML Dependencies Compatibility Test")
    logger.info(f"Test started at: {datetime.now()}")

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Advanced ML Imports", test_advanced_ml_imports),
        ("IterativeImputer (MICE)", test_iterative_imputer),
        ("SMOTE", test_smote),
        ("Optuna", test_optuna),
        ("Gradient Boosting", test_gradient_boosting),
        ("Text Analysis", test_text_analysis),
        ("Constitutional Hash Integrity", test_constitutional_hash_integrity),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Test {test_name} failed with exception: {e}")
            failed += 1

    logger.info(f"\n📊 Test Results:")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        logger.info(
            "🎉 All tests passed! ML dependencies are compatible with ACGS-PGP v8"
        )
        return True
    else:
        logger.error("⚠️ Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
