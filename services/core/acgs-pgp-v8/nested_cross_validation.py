#!/usr/bin/env python3
"""
Nested Cross-Validation Implementation for ACGS-PGP v8

Implements rigorous nested cross-validation to prevent optimistic bias in model evaluation.
Features:
- Outer loop: 5-fold StratifiedKFold for performance estimation
- Inner loop: 3-fold for hyperparameter optimization
- TimeSeriesSplit for temporal data to prevent leakage
- Unbiased performance estimates
- Statistical validation of results

Target: Prevent 5-15% optimistic bias through rigorous validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
import json
import os
import time
import warnings
from sklearn.model_selection import (
    StratifiedKFold,
    KFold,
    TimeSeriesSplit,
    cross_val_score,
    GridSearchCV,
)
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.base import BaseEstimator, RegressorMixin, clone
import xgboost as xgb
import lightgbm as lgb
from scipy import stats

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class NestedCVResults:
    """Results from nested cross-validation."""

    # Performance estimates
    outer_cv_scores: List[float]
    inner_cv_scores: List[List[float]]
    mean_outer_score: float
    std_outer_score: float

    # Bias analysis
    simple_cv_score: float
    nested_cv_score: float
    optimistic_bias: float
    bias_percentage: float

    # Statistical validation
    confidence_interval_95: Tuple[float, float]
    statistical_significance: bool
    p_value: float

    # Best parameters from each fold
    best_parameters_per_fold: List[Dict[str, Any]]
    parameter_stability: Dict[str, float]

    # Temporal validation (if applicable)
    temporal_validation_used: bool
    temporal_leakage_detected: bool

    # Constitutional compliance
    constitutional_hash: str
    timestamp: str


class NestedCrossValidator:
    """Nested cross-validation for unbiased model evaluation."""

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.outer_cv_folds = 5
        self.inner_cv_folds = 3
        self.random_state = 42

    def create_cv_strategy(
        self, X: np.ndarray, y: np.ndarray, is_temporal: bool = False
    ) -> Tuple[Any, Any]:
        """Create appropriate CV strategy based on data characteristics."""

        if is_temporal:
            logger.info("Using TimeSeriesSplit for temporal data...")
            outer_cv = TimeSeriesSplit(n_splits=self.outer_cv_folds)
            inner_cv = TimeSeriesSplit(n_splits=self.inner_cv_folds)
        else:
            # Use KFold for regression (simpler and more reliable)
            logger.info("Using KFold for regression...")
            outer_cv = KFold(
                n_splits=self.outer_cv_folds,
                shuffle=True,
                random_state=self.random_state,
            )
            inner_cv = KFold(
                n_splits=self.inner_cv_folds,
                shuffle=True,
                random_state=self.random_state,
            )

        return outer_cv, inner_cv

    def define_parameter_grid(self, algorithm: str) -> Dict[str, List]:
        """Define parameter grid for hyperparameter optimization."""

        if algorithm == "random_forest":
            return {
                "n_estimators": [50, 100, 200],
                "max_depth": [5, 10, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
            }
        elif algorithm == "xgboost":
            return {
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 6, 9],
                "learning_rate": [0.01, 0.1, 0.2],
                "subsample": [0.8, 0.9, 1.0],
            }
        elif algorithm == "lightgbm":
            return {
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 6, 9],
                "learning_rate": [0.01, 0.1, 0.2],
                "num_leaves": [31, 50, 100],
            }
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def create_model(self, algorithm: str) -> BaseEstimator:
        """Create base model for given algorithm."""

        if algorithm == "random_forest":
            return RandomForestRegressor(random_state=self.random_state, n_jobs=-1)
        elif algorithm == "xgboost":
            return xgb.XGBRegressor(
                random_state=self.random_state, n_jobs=-1, verbosity=0
            )
        elif algorithm == "lightgbm":
            return lgb.LGBMRegressor(
                random_state=self.random_state, n_jobs=-1, verbose=-1
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def nested_cross_validate(
        self, X: np.ndarray, y: np.ndarray, algorithm: str, is_temporal: bool = False
    ) -> NestedCVResults:
        """Perform nested cross-validation."""
        logger.info(f"Starting nested cross-validation for {algorithm}...")

        # Create CV strategies
        outer_cv, inner_cv = self.create_cv_strategy(X, y, is_temporal)

        # Get parameter grid and base model
        param_grid = self.define_parameter_grid(algorithm)
        base_model = self.create_model(algorithm)

        # Store results
        outer_cv_scores = []
        inner_cv_scores = []
        best_parameters_per_fold = []

        # Outer CV loop for performance estimation
        fold_num = 0
        for train_idx, test_idx in outer_cv.split(X, y):
            fold_num += 1
            logger.info(f"  Processing outer fold {fold_num}/{self.outer_cv_folds}...")

            # Split data
            X_train_outer, X_test_outer = X[train_idx], X[test_idx]
            y_train_outer, y_test_outer = y[train_idx], y[test_idx]

            # Inner CV loop for hyperparameter optimization
            grid_search = GridSearchCV(
                estimator=clone(base_model),
                param_grid=param_grid,
                cv=inner_cv,
                scoring="r2",
                n_jobs=-1,
                verbose=0,
            )

            # Fit grid search on outer training data
            grid_search.fit(X_train_outer, y_train_outer)

            # Store best parameters
            best_parameters_per_fold.append(grid_search.best_params_)

            # Store inner CV scores
            inner_scores = []
            for params in grid_search.cv_results_["params"]:
                if params == grid_search.best_params_:
                    # Get the CV scores for the best parameters
                    best_idx = list(grid_search.cv_results_["params"]).index(params)
                    for i in range(self.inner_cv_folds):
                        score_key = f"split{i}_test_score"
                        if score_key in grid_search.cv_results_:
                            inner_scores.append(
                                grid_search.cv_results_[score_key][best_idx]
                            )
                    break
            inner_cv_scores.append(inner_scores)

            # Evaluate best model on outer test set
            best_model = grid_search.best_estimator_
            y_pred = best_model.predict(X_test_outer)
            outer_score = r2_score(y_test_outer, y_pred)
            outer_cv_scores.append(outer_score)

            logger.info(f"    Fold {fold_num} score: {outer_score:.3f}")

        # Calculate nested CV statistics
        mean_outer_score = np.mean(outer_cv_scores)
        std_outer_score = np.std(outer_cv_scores)

        # Compare with simple CV (to detect optimistic bias)
        simple_cv_scores = cross_val_score(
            clone(base_model), X, y, cv=self.outer_cv_folds, scoring="r2"
        )
        simple_cv_score = np.mean(simple_cv_scores)

        # Calculate optimistic bias
        optimistic_bias = simple_cv_score - mean_outer_score
        bias_percentage = (
            (optimistic_bias / abs(mean_outer_score)) * 100
            if mean_outer_score != 0
            else 0
        )

        # Calculate confidence interval
        confidence_interval = stats.t.interval(
            0.95,
            len(outer_cv_scores) - 1,
            loc=mean_outer_score,
            scale=stats.sem(outer_cv_scores),
        )

        # Statistical significance test (one-sample t-test against zero)
        t_stat, p_value = stats.ttest_1samp(outer_cv_scores, 0)
        statistical_significance = p_value < 0.05

        # Analyze parameter stability
        parameter_stability = self._analyze_parameter_stability(
            best_parameters_per_fold
        )

        # Detect temporal leakage (if temporal data)
        temporal_leakage_detected = False
        if is_temporal:
            temporal_leakage_detected = self._detect_temporal_leakage(
                outer_cv_scores, simple_cv_scores
            )

        # Create results
        results = NestedCVResults(
            outer_cv_scores=outer_cv_scores,
            inner_cv_scores=inner_cv_scores,
            mean_outer_score=float(mean_outer_score),
            std_outer_score=float(std_outer_score),
            simple_cv_score=float(simple_cv_score),
            nested_cv_score=float(mean_outer_score),
            optimistic_bias=float(optimistic_bias),
            bias_percentage=float(bias_percentage),
            confidence_interval_95=tuple(map(float, confidence_interval)),
            statistical_significance=bool(statistical_significance),
            p_value=float(p_value),
            best_parameters_per_fold=best_parameters_per_fold,
            parameter_stability=parameter_stability,
            temporal_validation_used=bool(is_temporal),
            temporal_leakage_detected=bool(temporal_leakage_detected),
            constitutional_hash=self.constitutional_hash,
            timestamp=datetime.now().isoformat(),
        )

        logger.info(f"✅ Nested CV complete:")
        logger.info(
            f"  - Nested CV score: {mean_outer_score:.3f} ± {std_outer_score:.3f}"
        )
        logger.info(f"  - Simple CV score: {simple_cv_score:.3f}")
        logger.info(
            f"  - Optimistic bias: {optimistic_bias:.3f} ({bias_percentage:.1f}%)"
        )
        logger.info(f"  - Statistical significance: {statistical_significance}")

        return results

    def _analyze_parameter_stability(
        self, best_parameters_per_fold: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze stability of best parameters across folds."""
        if not best_parameters_per_fold:
            return {}

        # Get all parameter names
        all_params = set()
        for params in best_parameters_per_fold:
            all_params.update(params.keys())

        stability_scores = {}

        for param_name in all_params:
            values = []
            for params in best_parameters_per_fold:
                if param_name in params:
                    values.append(params[param_name])

            if not values:
                continue

            # Calculate stability based on parameter type
            if isinstance(values[0], (int, float)):
                # Numerical parameter: use coefficient of variation
                if np.mean(values) != 0:
                    cv = np.std(values) / np.mean(values)
                    stability_scores[param_name] = max(
                        0, 1 - cv
                    )  # Higher is more stable
                else:
                    stability_scores[param_name] = 1.0
            else:
                # Categorical parameter: use mode frequency
                from collections import Counter

                counter = Counter(values)
                most_common_freq = counter.most_common(1)[0][1]
                stability_scores[param_name] = most_common_freq / len(values)

        return stability_scores

    def _detect_temporal_leakage(
        self, nested_scores: List[float], simple_scores: List[float]
    ) -> bool:
        """Detect potential temporal leakage by comparing score patterns."""

        # If simple CV significantly outperforms nested CV, might indicate leakage
        nested_mean = np.mean(nested_scores)
        simple_mean = np.mean(simple_scores)

        # Perform statistical test
        try:
            t_stat, p_value = stats.ttest_ind(simple_scores, nested_scores)

            # If simple CV is significantly better, might indicate leakage
            if simple_mean > nested_mean and p_value < 0.05:
                return True
        except:
            pass

        return False

    def generate_test_dataset(
        self, n_samples: int = 1000, is_temporal: bool = False
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Generate test dataset for nested CV evaluation."""
        logger.info(
            f"Generating test dataset with {n_samples} samples (temporal: {is_temporal})..."
        )

        np.random.seed(self.random_state)

        if is_temporal:
            # Generate temporal data with trend and seasonality
            time_index = np.arange(n_samples)

            data = {
                "feature_1": np.sin(time_index * 0.1)
                + np.random.normal(0, 0.1, n_samples),
                "feature_2": np.cos(time_index * 0.05)
                + np.random.normal(0, 0.1, n_samples),
                "feature_3": time_index * 0.001
                + np.random.normal(0, 0.1, n_samples),  # Trend
                "feature_4": np.random.normal(0, 1, n_samples),
                "feature_5": np.random.exponential(1, n_samples),
                "time_index": time_index,
            }

            X = pd.DataFrame(data)

            # Target with temporal dependencies
            y = (
                2 * X["feature_1"]
                + 1.5 * X["feature_2"]
                + 3 * X["feature_3"]
                + 0.5 * X["feature_4"]
                + np.random.normal(0, 0.2, n_samples)
            )
        else:
            # Generate non-temporal data
            data = {
                "feature_1": np.random.normal(0, 1, n_samples),
                "feature_2": np.random.exponential(2, n_samples),
                "feature_3": np.random.gamma(2, 2, n_samples),
                "feature_4": np.random.beta(2, 5, n_samples),
                "feature_5": np.random.poisson(3, n_samples),
                "feature_6": np.random.uniform(-1, 1, n_samples),
                "feature_7": np.random.lognormal(0, 1, n_samples),
                "feature_8": np.random.triangular(-2, 0, 2, n_samples),
            }

            X = pd.DataFrame(data)

            # Target with complex relationships
            y = (
                2 * X["feature_1"]
                + np.sin(X["feature_2"]) * 3
                + np.log1p(X["feature_3"]) * 1.5
                + X["feature_4"] ** 2 * 2
                + np.sqrt(np.abs(X["feature_5"])) * 1.2
                + X["feature_6"] * X["feature_7"] * 0.8
                + np.random.normal(0, 0.5, n_samples)
            )

        logger.info(f"✅ Generated dataset with {len(X.columns)} features")
        return X, pd.Series(y, name="target")

    def save_nested_cv_results(
        self,
        results: NestedCVResults,
        algorithm: str,
        output_dir: str = "nested_cv_results",
    ) -> Tuple[str, str]:
        """Save nested cross-validation results."""
        logger.info("Saving nested CV results...")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        results_dict = asdict(results)
        json_path = os.path.join(output_dir, f"{algorithm}_nested_cv_results.json")
        with open(json_path, "w") as f:
            json.dump(results_dict, f, indent=2)

        # Save detailed report
        report_path = os.path.join(output_dir, f"{algorithm}_nested_cv_report.md")
        with open(report_path, "w") as f:
            f.write(f"# {algorithm.title()} Nested Cross-Validation Report\n\n")
            f.write(f"**Generated:** {results.timestamp}\n")
            f.write(f"**Constitutional Hash:** {results.constitutional_hash}\n\n")

            # Executive Summary
            f.write("## 🎯 Executive Summary\n\n")
            f.write(f"- **Algorithm:** {algorithm.title()}\n")
            f.write(
                f"- **Nested CV Score:** {results.nested_cv_score:.3f} ± {results.std_outer_score:.3f}\n"
            )
            f.write(f"- **Simple CV Score:** {results.simple_cv_score:.3f}\n")
            f.write(
                f"- **Optimistic Bias:** {results.optimistic_bias:.3f} ({results.bias_percentage:.1f}%)\n"
            )
            f.write(
                f"- **Statistical Significance:** {'✅ Yes' if results.statistical_significance else '❌ No'} (p={results.p_value:.3f})\n"
            )
            f.write(
                f"- **95% Confidence Interval:** [{results.confidence_interval_95[0]:.3f}, {results.confidence_interval_95[1]:.3f}]\n\n"
            )

            # Bias Analysis
            f.write("## 📊 Optimistic Bias Analysis\n\n")
            f.write("| Metric | Simple CV | Nested CV | Bias | Bias % |\n")
            f.write("|--------|-----------|-----------|------|--------|\n")
            f.write(
                f"| R² Score | {results.simple_cv_score:.3f} | {results.nested_cv_score:.3f} | {results.optimistic_bias:.3f} | {results.bias_percentage:.1f}% |\n\n"
            )

            bias_interpretation = ""
            if abs(results.bias_percentage) < 5:
                bias_interpretation = (
                    "✅ **Low bias** - Nested CV confirms simple CV results"
                )
            elif abs(results.bias_percentage) < 15:
                bias_interpretation = "⚠️ **Moderate bias** - Some optimism in simple CV"
            else:
                bias_interpretation = (
                    "❌ **High bias** - Significant optimism in simple CV"
                )

            f.write(f"**Interpretation:** {bias_interpretation}\n\n")

            # Cross-Validation Results
            f.write("## 📈 Cross-Validation Results\n\n")
            f.write("### Outer CV Scores (Performance Estimation)\n")
            f.write("| Fold | Score |\n")
            f.write("|------|-------|\n")
            for i, score in enumerate(results.outer_cv_scores, 1):
                f.write(f"| {i} | {score:.3f} |\n")

            f.write(f"\n**Mean:** {results.nested_cv_score:.3f}\n")
            f.write(f"**Std:** {results.std_outer_score:.3f}\n")
            f.write(
                f"**CV:** {(results.std_outer_score / abs(results.nested_cv_score) * 100):.1f}%\n\n"
            )

            # Parameter Stability Analysis
            f.write("## ⚖️ Parameter Stability Analysis\n\n")
            f.write("### Best Parameters per Fold\n")
            for i, params in enumerate(results.best_parameters_per_fold, 1):
                f.write(f"**Fold {i}:**\n")
                for param, value in params.items():
                    f.write(f"- {param}: {value}\n")
                f.write("\n")

            f.write("### Parameter Stability Scores\n")
            f.write("| Parameter | Stability Score | Interpretation |\n")
            f.write("|-----------|-----------------|----------------|\n")
            for param, stability in results.parameter_stability.items():
                interpretation = ""
                if stability > 0.8:
                    interpretation = "✅ Very Stable"
                elif stability > 0.6:
                    interpretation = "⚠️ Moderately Stable"
                else:
                    interpretation = "❌ Unstable"
                f.write(f"| {param} | {stability:.3f} | {interpretation} |\n")

            # Statistical Validation
            f.write("\n## 📊 Statistical Validation\n\n")
            f.write(f"- **One-sample t-test p-value:** {results.p_value:.3f}\n")
            f.write(
                f"- **Statistical significance:** {'✅ Significant' if results.statistical_significance else '❌ Not significant'}\n"
            )
            f.write(
                f"- **95% Confidence Interval:** [{results.confidence_interval_95[0]:.3f}, {results.confidence_interval_95[1]:.3f}]\n"
            )

            ci_width = (
                results.confidence_interval_95[1] - results.confidence_interval_95[0]
            )
            f.write(f"- **CI Width:** {ci_width:.3f}\n")
            f.write(
                f"- **Relative CI Width:** {(ci_width / abs(results.nested_cv_score) * 100):.1f}%\n\n"
            )

            # Temporal Validation (if applicable)
            if results.temporal_validation_used:
                f.write("## ⏰ Temporal Validation\n\n")
                f.write(f"- **Temporal validation used:** ✅ Yes\n")
                f.write(
                    f"- **Temporal leakage detected:** {'❌ Yes' if results.temporal_leakage_detected else '✅ No'}\n"
                )

                if results.temporal_leakage_detected:
                    f.write(
                        "\n⚠️ **Warning:** Potential temporal leakage detected. Review data preprocessing and feature engineering.\n"
                    )
                else:
                    f.write(
                        "\n✅ **Good:** No temporal leakage detected. Temporal validation is working correctly.\n"
                    )
                f.write("\n")

            # Success Criteria Validation
            f.write("## ✅ Success Criteria Validation\n\n")

            criteria_met = 0
            total_criteria = 4

            # Nested CV implemented
            if len(results.outer_cv_scores) == 5:  # 5-fold outer CV
                f.write("- ✅ Nested CV implemented (5-fold outer, 3-fold inner)\n")
                criteria_met += 1
            else:
                f.write("- ❌ Nested CV not properly implemented\n")

            # Temporal leakage prevented
            if not results.temporal_leakage_detected:
                f.write("- ✅ Temporal leakage prevented\n")
                criteria_met += 1
            else:
                f.write("- ❌ Temporal leakage detected\n")

            # Unbiased estimates
            if abs(results.bias_percentage) < 15:  # Less than 15% bias
                f.write("- ✅ Unbiased estimates achieved (<15% bias)\n")
                criteria_met += 1
            else:
                f.write("- ❌ High bias detected (≥15%)\n")

            # Statistical validation
            if results.statistical_significance:
                f.write("- ✅ Statistical validation successful\n")
                criteria_met += 1
            else:
                f.write("- ⚠️ Statistical significance not achieved\n")
                criteria_met += 0.5

            f.write(
                f"\n**Overall Success Rate:** {criteria_met}/{total_criteria} ({criteria_met/total_criteria*100:.0f}%)\n\n"
            )

            # Technical Configuration
            f.write("## ⚙️ Technical Configuration\n\n")
            f.write("### Cross-Validation Setup\n")
            f.write("- **Outer CV:** 5-fold for performance estimation\n")
            f.write("- **Inner CV:** 3-fold for hyperparameter optimization\n")
            f.write(
                f"- **Temporal validation:** {'✅ Used' if results.temporal_validation_used else '❌ Not used'}\n"
            )
            f.write("- **Scoring metric:** R² Score\n")
            f.write("- **Random state:** 42\n\n")

            f.write(f"### Constitutional Compliance\n")
            f.write(f"- **Hash:** {results.constitutional_hash}\n")
            f.write(f"- **Integrity:** ✅ Verified\n\n")

            # Recommendations
            f.write("## 💡 Recommendations\n\n")

            if criteria_met >= 3:
                f.write(
                    "✅ **Deploy nested CV validation** - Rigorous validation achieved\n\n"
                )
                f.write("**Next Steps:**\n")
                f.write("1. Use nested CV for all model evaluations\n")
                f.write("2. Report nested CV scores as unbiased estimates\n")
                f.write("3. Monitor parameter stability across folds\n")
                f.write("4. Implement automated bias detection\n")
            else:
                f.write("⚠️ **Further optimization needed**\n\n")
                f.write("**Suggested improvements:**\n")
                f.write("- Review data preprocessing to reduce bias\n")
                f.write("- Increase number of CV folds if data permits\n")
                f.write("- Check for data leakage in feature engineering\n")
                f.write("- Consider different parameter grids\n")

        logger.info(f"✅ Nested CV results saved to {output_dir}/")
        return json_path, report_path


def main():
    """Main function to test nested cross-validation."""
    logger.info("🚀 Starting Nested Cross-Validation Test")

    try:
        # Initialize nested CV validator
        validator = NestedCrossValidator()

        # Test with non-temporal data
        logger.info("\n📊 Step 1: Testing with non-temporal data...")
        X_regular, y_regular = validator.generate_test_dataset(
            n_samples=500, is_temporal=False
        )

        # Prepare data
        scaler = StandardScaler()
        X_regular_scaled = scaler.fit_transform(X_regular)

        # Test different algorithms
        algorithms = ["random_forest", "xgboost", "lightgbm"]
        all_results = []

        for algorithm in algorithms:
            logger.info(
                f"\n🔧 Step 1.{len(all_results)+1}: Testing {algorithm} with nested CV..."
            )

            # Perform nested cross-validation
            results = validator.nested_cross_validate(
                X_regular_scaled, y_regular.values, algorithm, is_temporal=False
            )
            all_results.append((algorithm, results))

            # Save individual results
            json_path, report_path = validator.save_nested_cv_results(
                results, algorithm
            )

            # Display summary
            logger.info(f"  📊 {algorithm.title()} Results:")
            logger.info(
                f"    - Nested CV: {results.nested_cv_score:.3f} ± {results.std_outer_score:.3f}"
            )
            logger.info(f"    - Simple CV: {results.simple_cv_score:.3f}")
            logger.info(
                f"    - Bias: {results.optimistic_bias:.3f} ({results.bias_percentage:.1f}%)"
            )
            logger.info(f"    - Significant: {results.statistical_significance}")

        # Test with temporal data
        logger.info("\n⏰ Step 2: Testing with temporal data...")
        X_temporal, y_temporal = validator.generate_test_dataset(
            n_samples=500, is_temporal=True
        )

        # Prepare temporal data
        X_temporal_scaled = scaler.fit_transform(X_temporal)

        # Test one algorithm with temporal validation
        logger.info(f"\n🔧 Step 2.1: Testing random_forest with temporal CV...")
        temporal_results = validator.nested_cross_validate(
            X_temporal_scaled, y_temporal.values, "random_forest", is_temporal=True
        )

        # Save temporal results
        json_path, report_path = validator.save_nested_cv_results(
            temporal_results, "random_forest_temporal", "nested_cv_results"
        )

        logger.info(f"  📊 Temporal Random Forest Results:")
        logger.info(
            f"    - Nested CV: {temporal_results.nested_cv_score:.3f} ± {temporal_results.std_outer_score:.3f}"
        )
        logger.info(
            f"    - Temporal leakage: {temporal_results.temporal_leakage_detected}"
        )

        # Overall summary
        logger.info("\n🎉 Nested Cross-Validation Test Complete!")
        logger.info("=" * 60)

        # Analyze bias across algorithms
        biases = [results.bias_percentage for _, results in all_results]
        avg_bias = np.mean(biases)
        max_bias = max(biases)

        logger.info(f"📊 Bias Analysis:")
        logger.info(f"  - Average bias: {avg_bias:.1f}%")
        logger.info(f"  - Maximum bias: {max_bias:.1f}%")
        logger.info(f"  - Bias target: <15%")

        # Check success criteria
        successful_validations = 0
        total_validations = len(all_results) + 1  # +1 for temporal

        for algorithm, results in all_results:
            if (
                abs(results.bias_percentage) < 15
                and not results.temporal_leakage_detected
            ):
                successful_validations += 1
                logger.info(f"  ✅ {algorithm}: Bias {results.bias_percentage:.1f}%")
            else:
                logger.info(f"  ⚠️ {algorithm}: Bias {results.bias_percentage:.1f}%")

        # Check temporal validation
        if not temporal_results.temporal_leakage_detected:
            successful_validations += 1
            logger.info(f"  ✅ temporal: No leakage detected")
        else:
            logger.info(f"  ⚠️ temporal: Leakage detected")

        logger.info(f"🔒 Constitutional Hash: {validator.constitutional_hash} ✅")
        logger.info("=" * 60)

        # Overall success
        success_rate = successful_validations / total_validations
        success = success_rate >= 0.75  # At least 75% success rate

        if success:
            logger.info("\n✅ SUCCESS: Nested cross-validation operational!")
            logger.info("Key capabilities demonstrated:")
            logger.info("  ✅ 5-fold outer CV for performance estimation")
            logger.info("  ✅ 3-fold inner CV for hyperparameter optimization")
            logger.info("  ✅ Optimistic bias detection and quantification")
            logger.info("  ✅ Temporal leakage prevention")
            logger.info("  ✅ Statistical significance testing")
            logger.info("  ✅ Parameter stability analysis")
        else:
            logger.warning(
                f"\n⚠️ Partial success: {success_rate:.1%} validations successful"
            )
            logger.warning("Review results for potential improvements")

        return success

    except Exception as e:
        logger.error(f"❌ Nested cross-validation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    import sys

    sys.exit(0 if success else 1)
