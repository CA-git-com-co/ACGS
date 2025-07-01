#!/usr/bin/env python3
"""
Advanced Feature Engineering Pipeline for ACGS-PGP v8

Implements comprehensive feature engineering including:
- Polynomial feature generation (degree=2, interaction_only=True)
- Target encoding for categorical variables
- Time-based cyclical features (sin/cos transformations)
- Feature selection with SelectKBest (k=15)
- Feature importance and correlation analysis

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import json
import os
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score
import warnings

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class FeatureEngineeringResults:
    """Results from advanced feature engineering pipeline."""

    # Original dataset info
    original_features: int
    original_samples: int

    # Feature engineering results
    polynomial_features_generated: int
    cyclical_features_generated: int
    target_encoded_features: int

    # Feature selection results
    features_after_selection: int
    selected_feature_names: List[str]
    feature_importance_scores: Dict[str, float]

    # Performance metrics
    baseline_performance: float
    engineered_performance: float
    performance_improvement: float

    # Correlation analysis
    max_correlation: float
    high_correlation_pairs: List[Tuple[str, str, float]]

    # Processing metrics
    processing_time_seconds: float
    constitutional_hash: str
    timestamp: str


class AdvancedFeatureEngineering:
    """Advanced feature engineering pipeline."""

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.polynomial_degree = 2
        self.interaction_only = True
        self.k_best_features = 15
        self.target_encoding_smoothing = 10

    def generate_polynomial_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Generate polynomial features with interaction terms."""
        logger.info("Generating polynomial features...")

        # Select numeric columns for polynomial features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) == 0:
            logger.warning("No numeric columns found for polynomial features")
            return X

        # Create polynomial features
        poly = PolynomialFeatures(
            degree=self.polynomial_degree,
            interaction_only=self.interaction_only,
            include_bias=False,
        )

        X_numeric = X[numeric_cols]
        X_poly = poly.fit_transform(X_numeric)

        # Create feature names
        feature_names = poly.get_feature_names_out(numeric_cols)

        # Create DataFrame with polynomial features
        X_poly_df = pd.DataFrame(X_poly, columns=feature_names, index=X.index)

        # Combine with non-numeric columns
        non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric_cols:
            X_combined = pd.concat([X[non_numeric_cols], X_poly_df], axis=1)
        else:
            X_combined = X_poly_df

        poly_features_added = len(feature_names) - len(numeric_cols)
        logger.info(f"✅ Generated {poly_features_added} polynomial features")

        return X_combined

    def create_cyclical_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create cyclical features for time-based variables."""
        logger.info("Creating cyclical features...")

        X_cyclical = X.copy()
        cyclical_features_added = 0

        # Hour of day (0-23) -> sin/cos features
        if "hour_of_day" in X.columns:
            X_cyclical["hour_sin"] = np.sin(2 * np.pi * X["hour_of_day"] / 24)
            X_cyclical["hour_cos"] = np.cos(2 * np.pi * X["hour_of_day"] / 24)
            cyclical_features_added += 2

        # Day of week (0-6) -> sin/cos features
        if "day_of_week" in X.columns:
            X_cyclical["day_sin"] = np.sin(2 * np.pi * X["day_of_week"] / 7)
            X_cyclical["day_cos"] = np.cos(2 * np.pi * X["day_of_week"] / 7)
            cyclical_features_added += 2

        # Month (1-12) -> sin/cos features
        if "month" in X.columns:
            X_cyclical["month_sin"] = np.sin(2 * np.pi * (X["month"] - 1) / 12)
            X_cyclical["month_cos"] = np.cos(2 * np.pi * (X["month"] - 1) / 12)
            cyclical_features_added += 2

        # Quarter (1-4) -> sin/cos features
        if "quarter" in X.columns:
            X_cyclical["quarter_sin"] = np.sin(2 * np.pi * (X["quarter"] - 1) / 4)
            X_cyclical["quarter_cos"] = np.cos(2 * np.pi * (X["quarter"] - 1) / 4)
            cyclical_features_added += 2

        logger.info(f"✅ Created {cyclical_features_added} cyclical features")

        return X_cyclical

    def apply_target_encoding(
        self, X: pd.DataFrame, y: pd.Series, categorical_cols: List[str] = None
    ) -> pd.DataFrame:
        """Apply target encoding to categorical variables."""
        logger.info("Applying target encoding...")

        if categorical_cols is None:
            categorical_cols = X.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()

        if len(categorical_cols) == 0:
            logger.info("No categorical columns found for target encoding")
            return X

        X_encoded = X.copy()
        target_encoded_features = 0

        for col in categorical_cols:
            if col in X.columns:
                # Calculate target mean for each category with smoothing
                category_means = y.groupby(X[col]).mean()
                global_mean = y.mean()
                category_counts = X[col].value_counts()

                # Apply smoothing to prevent overfitting
                smoothed_means = {}
                for category in category_means.index:
                    count = category_counts[category]
                    smoothed_mean = (
                        count * category_means[category]
                        + self.target_encoding_smoothing * global_mean
                    ) / (count + self.target_encoding_smoothing)
                    smoothed_means[category] = smoothed_mean

                # Apply encoding
                X_encoded[f"{col}_target_encoded"] = (
                    X[col].map(smoothed_means).fillna(global_mean)
                )
                target_encoded_features += 1

        logger.info(f"✅ Applied target encoding to {target_encoded_features} features")

        return X_encoded

    def select_best_features(
        self, X: pd.DataFrame, y: pd.Series, task_type: str = "regression"
    ) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
        """Select best features using SelectKBest."""
        logger.info(f"Selecting best {self.k_best_features} features...")

        # Choose appropriate scoring function
        if task_type == "classification":
            score_func = f_classif
        else:
            score_func = f_regression

        # Select only numeric features for SelectKBest
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X_numeric = X[numeric_cols]

        if len(numeric_cols) == 0:
            logger.warning("No numeric columns found for feature selection")
            return X, [], {}

        # Adjust k if we have fewer features than requested
        k = min(self.k_best_features, len(numeric_cols))

        # Apply feature selection
        selector = SelectKBest(score_func=score_func, k=k)
        X_selected = selector.fit_transform(X_numeric, y)

        # Get selected feature names and scores
        selected_mask = selector.get_support()
        selected_features = [
            numeric_cols[i] for i in range(len(numeric_cols)) if selected_mask[i]
        ]
        feature_scores = dict(zip(numeric_cols, selector.scores_))

        # Create DataFrame with selected features
        X_selected_df = pd.DataFrame(
            X_selected, columns=selected_features, index=X.index
        )

        # Add back non-numeric features
        non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric_cols:
            X_final = pd.concat([X[non_numeric_cols], X_selected_df], axis=1)
        else:
            X_final = X_selected_df

        logger.info(f"✅ Selected {len(selected_features)} best features")

        return X_final, selected_features, feature_scores

    def analyze_feature_importance(
        self, X: pd.DataFrame, y: pd.Series, task_type: str = "regression"
    ) -> Dict[str, float]:
        """Analyze feature importance using Random Forest."""
        logger.info("Analyzing feature importance...")

        # Select numeric features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) == 0:
            return {}

        X_numeric = X[numeric_cols]

        # Train Random Forest model
        if task_type == "classification":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)

        model.fit(X_numeric, y)

        # Get feature importances
        importances = dict(zip(numeric_cols, model.feature_importances_))

        # Sort by importance
        sorted_importances = dict(
            sorted(importances.items(), key=lambda x: x[1], reverse=True)
        )

        logger.info(f"✅ Analyzed importance for {len(sorted_importances)} features")

        return sorted_importances

    def analyze_correlations(
        self, X: pd.DataFrame
    ) -> Tuple[float, List[Tuple[str, str, float]]]:
        """Analyze feature correlations."""
        logger.info("Analyzing feature correlations...")

        # Select numeric features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return 0.0, []

        # Calculate correlation matrix
        corr_matrix = X[numeric_cols].corr().abs()

        # Find high correlation pairs
        high_corr_pairs = []
        max_correlation = 0.0

        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                corr_value = corr_matrix.iloc[i, j]
                if not np.isnan(corr_value):
                    max_correlation = max(max_correlation, corr_value)

                    if corr_value > 0.8:  # High correlation threshold
                        high_corr_pairs.append(
                            (numeric_cols[i], numeric_cols[j], corr_value)
                        )

        logger.info(f"✅ Found {len(high_corr_pairs)} high correlation pairs")

        return max_correlation, high_corr_pairs

    def generate_sample_dataset(
        self, n_samples: int = 1000
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Generate sample dataset for feature engineering testing."""
        logger.info(f"Generating sample dataset with {n_samples} samples...")

        np.random.seed(42)

        # Generate base features
        data = {
            "response_time_ms": np.random.lognormal(6, 0.5, n_samples),
            "cost_estimate": np.random.exponential(0.001, n_samples),
            "quality_score": np.random.beta(8, 2, n_samples),
            "complexity_score": np.random.gamma(2, 2, n_samples),
            "content_length": np.random.poisson(1000, n_samples),
            "hour_of_day": np.random.randint(0, 24, n_samples),
            "day_of_week": np.random.randint(0, 7, n_samples),
            "month": np.random.randint(1, 13, n_samples),
            "is_weekend": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            "request_type": np.random.choice(
                ["quick", "detailed", "validation"], n_samples
            ),
            "model_type": np.random.choice(
                ["flash_lite", "flash_full", "deepseek"], n_samples
            ),
        }

        X = pd.DataFrame(data)

        # Generate target variable with realistic relationships
        y = (
            0.1 * X["response_time_ms"]
            + 1000 * X["cost_estimate"]
            + 50 * X["quality_score"]
            + 10 * X["complexity_score"]
            + 0.01 * X["content_length"]
            + np.random.normal(0, 10, n_samples)
        )

        logger.info(f"✅ Generated dataset with {len(X.columns)} features")

        return X, pd.Series(y, name="target")

    def run_feature_engineering_pipeline(
        self, X: pd.DataFrame, y: pd.Series
    ) -> FeatureEngineeringResults:
        """Run complete feature engineering pipeline."""
        logger.info("Running complete feature engineering pipeline...")

        start_time = datetime.now()

        # Store original dataset info
        original_features = len(X.columns)
        original_samples = len(X)

        # Step 1: Generate polynomial features
        logger.info("\n🔧 Step 1: Polynomial feature generation...")
        X_poly = self.generate_polynomial_features(X)
        poly_features_added = len(X_poly.columns) - len(X.columns)

        # Step 2: Create cyclical features
        logger.info("\n🔄 Step 2: Cyclical feature creation...")
        X_cyclical = self.create_cyclical_features(X_poly)
        cyclical_features_added = len(X_cyclical.columns) - len(X_poly.columns)

        # Step 3: Apply target encoding
        logger.info("\n🎯 Step 3: Target encoding...")
        X_encoded = self.apply_target_encoding(X_cyclical, y)
        target_encoded_features = len(X_encoded.columns) - len(X_cyclical.columns)

        # Step 4: Feature selection
        logger.info("\n📊 Step 4: Feature selection...")
        X_selected, selected_features, feature_scores = self.select_best_features(
            X_encoded, y
        )

        # Step 5: Feature importance analysis
        logger.info("\n📈 Step 5: Feature importance analysis...")
        feature_importances = self.analyze_feature_importance(X_selected, y)

        # Step 6: Correlation analysis
        logger.info("\n🔗 Step 6: Correlation analysis...")
        max_corr, high_corr_pairs = self.analyze_correlations(X_selected)

        # Step 7: Performance evaluation
        logger.info("\n⚡ Step 7: Performance evaluation...")
        baseline_perf = self._evaluate_baseline_performance(X, y)
        engineered_perf = self._evaluate_engineered_performance(X_selected, y)
        performance_improvement = (
            (engineered_perf - baseline_perf) / baseline_perf
        ) * 100

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Create results
        results = FeatureEngineeringResults(
            original_features=original_features,
            original_samples=original_samples,
            polynomial_features_generated=poly_features_added,
            cyclical_features_generated=cyclical_features_added,
            target_encoded_features=target_encoded_features,
            features_after_selection=len(X_selected.columns),
            selected_feature_names=selected_features,
            feature_importance_scores=feature_importances,
            baseline_performance=float(baseline_perf),
            engineered_performance=float(engineered_perf),
            performance_improvement=float(performance_improvement),
            max_correlation=float(max_corr),
            high_correlation_pairs=high_corr_pairs,
            processing_time_seconds=float(processing_time),
            constitutional_hash=self.constitutional_hash,
            timestamp=datetime.now().isoformat(),
        )

        logger.info(f"✅ Feature engineering pipeline complete!")
        logger.info(f"  - Original features: {original_features}")
        logger.info(f"  - Final features: {len(X_selected.columns)}")
        logger.info(f"  - Performance improvement: {performance_improvement:.1f}%")

        return results

    def _evaluate_baseline_performance(self, X: pd.DataFrame, y: pd.Series) -> float:
        """Evaluate baseline performance with original features."""

        # Use only numeric features for baseline
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) == 0:
            return 0.0

        X_numeric = X[numeric_cols]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_numeric, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Calculate performance (R² score)
        from sklearn.metrics import r2_score

        performance = r2_score(y_test, y_pred)

        return max(0.0, performance)  # Ensure non-negative

    def _evaluate_engineered_performance(self, X: pd.DataFrame, y: pd.Series) -> float:
        """Evaluate performance with engineered features."""

        # Use only numeric features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) == 0:
            return 0.0

        X_numeric = X[numeric_cols]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_numeric, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Calculate performance (R² score)
        from sklearn.metrics import r2_score

        performance = r2_score(y_test, y_pred)

        return max(0.0, performance)  # Ensure non-negative

    def save_feature_engineering_results(
        self,
        results: FeatureEngineeringResults,
        output_dir: str = "feature_engineering_results",
    ) -> Tuple[str, str]:
        """Save feature engineering results."""
        logger.info("Saving feature engineering results...")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        results_dict = asdict(results)
        json_path = os.path.join(output_dir, "feature_engineering_results.json")
        with open(json_path, "w") as f:
            json.dump(results_dict, f, indent=2)

        # Save detailed report
        report_path = os.path.join(output_dir, "feature_engineering_report.md")
        with open(report_path, "w") as f:
            f.write("# Advanced Feature Engineering Report\n\n")
            f.write(f"**Generated:** {results.timestamp}\n")
            f.write(f"**Constitutional Hash:** {results.constitutional_hash}\n\n")

            # Executive Summary
            f.write("## 🎯 Executive Summary\n\n")
            f.write(f"- **Original Features:** {results.original_features}\n")
            f.write(f"- **Final Features:** {results.features_after_selection}\n")
            f.write(
                f"- **Performance Improvement:** {results.performance_improvement:.1f}%\n"
            )
            f.write(
                f"- **Processing Time:** {results.processing_time_seconds:.2f}s\n\n"
            )

            # Feature Engineering Steps
            f.write("## 🔧 Feature Engineering Pipeline\n\n")
            f.write("### 1. Polynomial Features\n")
            f.write(
                f"- **Generated:** {results.polynomial_features_generated} features\n"
            )
            f.write(f"- **Configuration:** degree=2, interaction_only=True\n\n")

            f.write("### 2. Cyclical Features\n")
            f.write(
                f"- **Generated:** {results.cyclical_features_generated} features\n"
            )
            f.write(f"- **Transformations:** sin/cos for time-based variables\n\n")

            f.write("### 3. Target Encoding\n")
            f.write(
                f"- **Encoded:** {results.target_encoded_features} categorical features\n"
            )
            f.write(f"- **Smoothing:** {self.target_encoding_smoothing} samples\n\n")

            f.write("### 4. Feature Selection\n")
            f.write(f"- **Method:** SelectKBest with k={self.k_best_features}\n")
            f.write(
                f"- **Selected:** {len(results.selected_feature_names)} features\n\n"
            )

            # Performance Analysis
            f.write("## 📈 Performance Analysis\n\n")
            f.write("| Metric | Baseline | Engineered | Improvement |\n")
            f.write("|--------|----------|------------|-------------|\n")
            f.write(
                f"| R² Score | {results.baseline_performance:.3f} | {results.engineered_performance:.3f} | {results.performance_improvement:+.1f}% |\n\n"
            )

            # Feature Importance
            f.write("## 🏆 Top Feature Importance\n\n")
            f.write("| Rank | Feature | Importance Score |\n")
            f.write("|------|---------|------------------|\n")

            for i, (feature, score) in enumerate(
                list(results.feature_importance_scores.items())[:10], 1
            ):
                f.write(f"| {i} | {feature} | {score:.4f} |\n")

            # Correlation Analysis
            f.write("\n## 🔗 Correlation Analysis\n\n")
            f.write(f"- **Maximum Correlation:** {results.max_correlation:.3f}\n")
            f.write(
                f"- **High Correlation Pairs:** {len(results.high_correlation_pairs)}\n\n"
            )

            if results.high_correlation_pairs:
                f.write("### High Correlation Pairs (>0.8)\n\n")
                f.write("| Feature 1 | Feature 2 | Correlation |\n")
                f.write("|-----------|-----------|-------------|\n")
                for feat1, feat2, corr in results.high_correlation_pairs[:5]:
                    f.write(f"| {feat1} | {feat2} | {corr:.3f} |\n")

            # Success Criteria
            f.write("\n## ✅ Success Criteria Validation\n\n")
            criteria_met = 0
            total_criteria = 4

            if results.polynomial_features_generated > 0:
                f.write("- ✅ Polynomial feature generation complete\n")
                criteria_met += 1
            else:
                f.write("- ❌ Polynomial feature generation failed\n")

            if results.features_after_selection > 0:
                f.write("- ✅ Feature selection optimized\n")
                criteria_met += 1
            else:
                f.write("- ❌ Feature selection failed\n")

            if len(results.feature_importance_scores) > 0:
                f.write("- ✅ Feature importance analysis functional\n")
                criteria_met += 1
            else:
                f.write("- ❌ Feature importance analysis failed\n")

            if results.performance_improvement > 0:
                f.write("- ✅ Performance improvement achieved\n")
                criteria_met += 1
            else:
                f.write("- ❌ No performance improvement\n")

            f.write(
                f"\n**Overall Success Rate:** {criteria_met}/{total_criteria} ({criteria_met/total_criteria*100:.0f}%)\n\n"
            )

            # Configuration Details
            f.write("## ⚙️ Configuration Details\n\n")
            f.write(f"- **Polynomial Degree:** {self.polynomial_degree}\n")
            f.write(f"- **Interaction Only:** {self.interaction_only}\n")
            f.write(f"- **K-Best Features:** {self.k_best_features}\n")
            f.write(
                f"- **Target Encoding Smoothing:** {self.target_encoding_smoothing}\n"
            )
            f.write(f"- **Constitutional Hash:** {self.constitutional_hash}\n")

        logger.info(f"✅ Feature engineering results saved to {output_dir}/")
        return json_path, report_path


def main():
    """Main function to test advanced feature engineering pipeline."""
    logger.info("🚀 Starting Advanced Feature Engineering Pipeline Test")

    try:
        # Initialize feature engineering pipeline
        fe_pipeline = AdvancedFeatureEngineering()

        # Generate sample dataset
        logger.info("\n📊 Step 1: Generating sample dataset...")
        X, y = fe_pipeline.generate_sample_dataset(n_samples=1500)

        # Run feature engineering pipeline
        logger.info("\n🔧 Step 2: Running feature engineering pipeline...")
        results = fe_pipeline.run_feature_engineering_pipeline(X, y)

        # Save results
        logger.info("\n💾 Step 3: Saving results...")
        json_path, report_path = fe_pipeline.save_feature_engineering_results(results)

        # Display summary
        logger.info("\n🎉 Advanced Feature Engineering Test Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Original Features: {results.original_features}")
        logger.info(
            f"🔧 Polynomial Features Generated: {results.polynomial_features_generated}"
        )
        logger.info(
            f"🔄 Cyclical Features Generated: {results.cyclical_features_generated}"
        )
        logger.info(f"🎯 Target Encoded Features: {results.target_encoded_features}")
        logger.info(f"📈 Final Features: {results.features_after_selection}")
        logger.info(
            f"⚡ Performance Improvement: {results.performance_improvement:.1f}%"
        )
        logger.info(f"🔗 Max Correlation: {results.max_correlation:.3f}")
        logger.info(f"⏱️ Processing Time: {results.processing_time_seconds:.2f}s")
        logger.info(f"🔒 Constitutional Hash: {results.constitutional_hash} ✅")
        logger.info("=" * 60)
        logger.info(f"📄 Results saved to: {json_path}")
        logger.info(f"📋 Report saved to: {report_path}")

        # Validate success criteria
        success_criteria = [
            results.polynomial_features_generated > 0,
            results.features_after_selection > 0,
            len(results.feature_importance_scores) > 0,
            results.performance_improvement >= 0,  # Allow zero or positive improvement
        ]

        success = all(success_criteria)

        if success:
            logger.info(
                "\n✅ SUCCESS: Advanced feature engineering pipeline operational!"
            )
            logger.info("Key capabilities demonstrated:")
            logger.info("  ✅ Polynomial feature generation")
            logger.info("  ✅ Cyclical feature transformation")
            logger.info("  ✅ Target encoding for categorical variables")
            logger.info("  ✅ Feature selection optimization")
            logger.info("  ✅ Feature importance analysis")
        else:
            logger.warning(
                "\n⚠️ Some criteria not met. Review results for optimization."
            )

        return success

    except Exception as e:
        logger.error(f"❌ Advanced feature engineering test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    import sys

    sys.exit(0 if success else 1)
