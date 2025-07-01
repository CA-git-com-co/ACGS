#!/usr/bin/env python3
"""
Data Quality Assessment Framework for ACGS-PGP v8

Implements comprehensive data quality assessment including:
- Missing value analysis
- Outlier detection using statistical methods
- Class imbalance measurement
- Feature correlation analysis
- Data freshness monitoring
- Overall quality scoring (target: >0.8)

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import os
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import zscore

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Comprehensive data quality assessment metrics."""

    # Missing Value Analysis
    missing_value_rate: float  # 0-1, lower is better
    missing_patterns: dict[str, float]  # Missing patterns by feature

    # Outlier Detection
    outlier_rate: float  # 0-1, lower is better
    outlier_features: list[str]  # Features with high outlier rates

    # Class Imbalance
    imbalance_ratio: float  # 0-1, closer to 0.5 is better for binary
    class_distribution: dict[str, float]  # Distribution of target classes

    # Feature Correlation
    max_correlation: float  # 0-1, lower is better (avoid multicollinearity)
    high_correlation_pairs: list[tuple[str, str, float]]  # Highly correlated features

    # Data Freshness
    data_freshness_hours: float  # Hours since last update
    stale_data_rate: float  # 0-1, rate of stale records

    # Data Consistency
    duplicate_rate: float  # 0-1, lower is better
    inconsistency_rate: float  # 0-1, lower is better

    # Data Completeness
    completeness_score: float  # 0-1, higher is better
    feature_completeness: dict[str, float]  # Completeness by feature

    # Overall Quality Score
    quality_score: float  # 0-1, higher is better (target: >0.8)

    # Metadata
    assessment_timestamp: str
    sample_size: int
    features_analyzed: int


class DataQualityAssessment:
    """Comprehensive data quality assessment framework."""

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.quality_thresholds = {
            "missing_value_rate": 0.05,  # Max 5% missing values
            "outlier_rate": 0.05,  # Max 5% outliers
            "max_correlation": 0.9,  # Max 90% correlation
            "duplicate_rate": 0.01,  # Max 1% duplicates
            "data_freshness_hours": 24,  # Max 24 hours old
            "completeness_score": 0.95,  # Min 95% complete
        }

    def assess_missing_values(self, df: pd.DataFrame) -> dict[str, Any]:
        """Assess missing value patterns and rates."""
        logger.info("Assessing missing values...")

        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        missing_rate = missing_cells / total_cells

        # Missing patterns by feature
        missing_patterns = {}
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_patterns[column] = missing_count / len(df)

        # Identify features with high missing rates
        high_missing_features = [
            col
            for col, rate in missing_patterns.items()
            if rate > self.quality_thresholds["missing_value_rate"]
        ]

        return {
            "missing_value_rate": missing_rate,
            "missing_patterns": missing_patterns,
            "high_missing_features": high_missing_features,
            "total_missing_cells": missing_cells,
        }

    def detect_outliers(self, df: pd.DataFrame) -> dict[str, Any]:
        """Detect outliers using statistical methods."""
        logger.info("Detecting outliers...")

        numeric_columns = df.select_dtypes(include=[np.number]).columns
        outlier_info = {}
        total_outliers = 0
        outlier_features = []

        for column in numeric_columns:
            if df[column].notna().sum() > 0:  # Skip if all NaN
                # Z-score method (|z| > 3)
                z_scores = np.abs(zscore(df[column].dropna()))
                outliers_zscore = np.sum(z_scores > 3)

                # IQR method
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers_iqr = np.sum(
                    (df[column] < lower_bound) | (df[column] > upper_bound)
                )

                # Use the more conservative estimate
                outliers = min(outliers_zscore, outliers_iqr)
                outlier_rate = outliers / len(df[column].dropna())

                outlier_info[column] = {
                    "outlier_count": outliers,
                    "outlier_rate": outlier_rate,
                    "method_used": "zscore_iqr_conservative",
                }

                total_outliers += outliers

                if outlier_rate > self.quality_thresholds["outlier_rate"]:
                    outlier_features.append(column)

        overall_outlier_rate = total_outliers / len(df) if len(df) > 0 else 0

        return {
            "outlier_rate": overall_outlier_rate,
            "outlier_features": outlier_features,
            "outlier_details": outlier_info,
            "total_outliers": total_outliers,
        }

    def analyze_class_imbalance(
        self, df: pd.DataFrame, target_column: str = None
    ) -> dict[str, Any]:
        """Analyze class imbalance in target variables."""
        logger.info("Analyzing class imbalance...")

        if target_column is None or target_column not in df.columns:
            # Try to infer target column (look for boolean or categorical with few unique values)
            potential_targets = []
            for col in df.columns:
                if df[col].dtype == "bool" or (
                    df[col].dtype == "object" and df[col].nunique() <= 10
                ):
                    potential_targets.append(col)

            if potential_targets:
                target_column = potential_targets[0]
            else:
                # Create a synthetic target for demonstration
                target_column = "synthetic_target"
                df[target_column] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])

        if target_column in df.columns:
            value_counts = df[target_column].value_counts()
            class_distribution = (value_counts / len(df)).to_dict()

            # Calculate imbalance ratio (for binary: min_class / max_class)
            if len(value_counts) == 2:
                imbalance_ratio = value_counts.min() / value_counts.max()
            else:
                # For multi-class: use entropy-based measure
                proportions = value_counts / len(df)
                entropy = -np.sum(proportions * np.log2(proportions + 1e-10))
                max_entropy = np.log2(len(value_counts))
                imbalance_ratio = entropy / max_entropy
        else:
            class_distribution = {}
            imbalance_ratio = 1.0  # Assume balanced if no target

        return {
            "imbalance_ratio": imbalance_ratio,
            "class_distribution": class_distribution,
            "target_column": target_column,
            "is_balanced": imbalance_ratio > 0.8,  # Consider balanced if > 80%
        }

    def analyze_feature_correlation(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze feature correlation to detect multicollinearity."""
        logger.info("Analyzing feature correlations...")

        numeric_df = df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) < 2:
            return {
                "max_correlation": 0.0,
                "high_correlation_pairs": [],
                "correlation_matrix": {},
            }

        # Calculate correlation matrix
        corr_matrix = numeric_df.corr().abs()

        # Find high correlation pairs (excluding self-correlation)
        high_corr_pairs = []
        max_correlation = 0.0

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if not np.isnan(corr_value):
                    max_correlation = max(max_correlation, corr_value)

                    if corr_value > self.quality_thresholds["max_correlation"]:
                        high_corr_pairs.append(
                            (corr_matrix.columns[i], corr_matrix.columns[j], corr_value)
                        )

        return {
            "max_correlation": max_correlation,
            "high_correlation_pairs": high_corr_pairs,
            "correlation_matrix": corr_matrix.to_dict(),
            "multicollinearity_detected": len(high_corr_pairs) > 0,
        }

    def assess_data_freshness(
        self, df: pd.DataFrame, timestamp_column: str = None
    ) -> dict[str, Any]:
        """Assess data freshness and staleness."""
        logger.info("Assessing data freshness...")

        current_time = datetime.now()

        if timestamp_column and timestamp_column in df.columns:
            # Convert timestamp column to datetime if needed
            try:
                timestamps = pd.to_datetime(df[timestamp_column])

                # Calculate freshness metrics
                latest_timestamp = timestamps.max()
                oldest_timestamp = timestamps.min()

                hours_since_latest = (
                    current_time - latest_timestamp
                ).total_seconds() / 3600

                # Calculate stale data rate (data older than threshold)
                threshold_time = current_time - timedelta(
                    hours=self.quality_thresholds["data_freshness_hours"]
                )
                stale_records = timestamps < threshold_time
                stale_rate = stale_records.sum() / len(df)

            except Exception as e:
                logger.warning(
                    f"Could not parse timestamp column {timestamp_column}: {e}"
                )
                hours_since_latest = 0.0
                stale_rate = 0.0
        else:
            # Use current time as baseline
            hours_since_latest = 0.0
            stale_rate = 0.0

        return {
            "data_freshness_hours": hours_since_latest,
            "stale_data_rate": stale_rate,
            "is_fresh": hours_since_latest
            <= self.quality_thresholds["data_freshness_hours"],
        }

    def assess_data_consistency(self, df: pd.DataFrame) -> dict[str, Any]:
        """Assess data consistency including duplicates."""
        logger.info("Assessing data consistency...")

        # Duplicate detection
        duplicate_rows = df.duplicated().sum()
        duplicate_rate = duplicate_rows / len(df) if len(df) > 0 else 0

        # Data type consistency
        inconsistencies = 0
        for column in df.columns:
            if df[column].dtype == "object":
                # Check for mixed types in object columns
                try:
                    # Try to convert to numeric
                    pd.to_numeric(df[column], errors="raise")
                except:
                    # Check for inconsistent string formats
                    non_null_values = df[column].dropna()
                    if len(non_null_values) > 0:
                        # Simple heuristic: check for mixed case patterns
                        has_upper = any(
                            str(val).isupper() for val in non_null_values.head(100)
                        )
                        has_lower = any(
                            str(val).islower() for val in non_null_values.head(100)
                        )
                        if has_upper and has_lower:
                            inconsistencies += 1

        inconsistency_rate = (
            inconsistencies / len(df.columns) if len(df.columns) > 0 else 0
        )

        return {
            "duplicate_rate": duplicate_rate,
            "duplicate_count": duplicate_rows,
            "inconsistency_rate": inconsistency_rate,
            "is_consistent": duplicate_rate
            <= self.quality_thresholds["duplicate_rate"],
        }

    def calculate_completeness_score(self, df: pd.DataFrame) -> dict[str, Any]:
        """Calculate data completeness scores."""
        logger.info("Calculating completeness scores...")

        # Overall completeness
        total_cells = df.shape[0] * df.shape[1]
        non_null_cells = total_cells - df.isnull().sum().sum()
        overall_completeness = non_null_cells / total_cells if total_cells > 0 else 0

        # Feature-level completeness
        feature_completeness = {}
        for column in df.columns:
            non_null_count = df[column].notna().sum()
            completeness = non_null_count / len(df) if len(df) > 0 else 0
            feature_completeness[column] = completeness

        return {
            "completeness_score": overall_completeness,
            "feature_completeness": feature_completeness,
            "is_complete": overall_completeness
            >= self.quality_thresholds["completeness_score"],
        }

    def calculate_overall_quality_score(self, assessments: dict[str, Any]) -> float:
        """Calculate overall data quality score (0-1, target: >0.8)."""
        logger.info("Calculating overall quality score...")

        # Define weights for different quality dimensions
        weights = {
            "missing_value_quality": 0.20,  # 20% weight
            "outlier_quality": 0.15,  # 15% weight
            "balance_quality": 0.10,  # 10% weight
            "correlation_quality": 0.15,  # 15% weight
            "freshness_quality": 0.10,  # 10% weight
            "consistency_quality": 0.15,  # 15% weight
            "completeness_quality": 0.15,  # 15% weight
        }

        # Calculate individual quality scores (0-1, higher is better)
        missing_quality = max(
            0, 1 - (assessments["missing"]["missing_value_rate"] / 0.2)
        )
        outlier_quality = max(0, 1 - (assessments["outliers"]["outlier_rate"] / 0.2))
        balance_quality = assessments["imbalance"]["imbalance_ratio"]
        correlation_quality = max(
            0, 1 - (assessments["correlation"]["max_correlation"] - 0.5) / 0.5
        )
        freshness_quality = max(
            0, 1 - (assessments["freshness"]["data_freshness_hours"] / 48)
        )
        consistency_quality = max(
            0, 1 - assessments["consistency"]["duplicate_rate"] / 0.1
        )
        completeness_quality = assessments["completeness"]["completeness_score"]

        # Calculate weighted average
        quality_score = (
            weights["missing_value_quality"] * missing_quality
            + weights["outlier_quality"] * outlier_quality
            + weights["balance_quality"] * balance_quality
            + weights["correlation_quality"] * correlation_quality
            + weights["freshness_quality"] * freshness_quality
            + weights["consistency_quality"] * consistency_quality
            + weights["completeness_quality"] * completeness_quality
        )

        return min(1.0, max(0.0, quality_score))

    def comprehensive_assessment(
        self, df: pd.DataFrame, target_column: str = None, timestamp_column: str = None
    ) -> DataQualityMetrics:
        """Perform comprehensive data quality assessment."""
        logger.info(
            f"Starting comprehensive data quality assessment on {len(df)} records..."
        )

        # Perform all assessments
        assessments = {
            "missing": self.assess_missing_values(df),
            "outliers": self.detect_outliers(df),
            "imbalance": self.analyze_class_imbalance(df, target_column),
            "correlation": self.analyze_feature_correlation(df),
            "freshness": self.assess_data_freshness(df, timestamp_column),
            "consistency": self.assess_data_consistency(df),
            "completeness": self.calculate_completeness_score(df),
        }

        # Calculate overall quality score
        overall_quality = self.calculate_overall_quality_score(assessments)

        # Create comprehensive metrics object
        metrics = DataQualityMetrics(
            # Missing Value Analysis
            missing_value_rate=assessments["missing"]["missing_value_rate"],
            missing_patterns=assessments["missing"]["missing_patterns"],
            # Outlier Detection
            outlier_rate=assessments["outliers"]["outlier_rate"],
            outlier_features=assessments["outliers"]["outlier_features"],
            # Class Imbalance
            imbalance_ratio=assessments["imbalance"]["imbalance_ratio"],
            class_distribution=assessments["imbalance"]["class_distribution"],
            # Feature Correlation
            max_correlation=assessments["correlation"]["max_correlation"],
            high_correlation_pairs=assessments["correlation"]["high_correlation_pairs"],
            # Data Freshness
            data_freshness_hours=assessments["freshness"]["data_freshness_hours"],
            stale_data_rate=assessments["freshness"]["stale_data_rate"],
            # Data Consistency
            duplicate_rate=assessments["consistency"]["duplicate_rate"],
            inconsistency_rate=assessments["consistency"]["inconsistency_rate"],
            # Data Completeness
            completeness_score=assessments["completeness"]["completeness_score"],
            feature_completeness=assessments["completeness"]["feature_completeness"],
            # Overall Quality Score
            quality_score=overall_quality,
            # Metadata
            assessment_timestamp=datetime.now().isoformat(),
            sample_size=len(df),
            features_analyzed=len(df.columns),
        )

        logger.info(
            f"✅ Data quality assessment complete. Overall score: {overall_quality:.3f}"
        )

        return metrics

    def save_assessment_report(
        self, metrics: DataQualityMetrics, output_dir: str = "data_quality_results"
    ) -> tuple[str, str]:
        """Save data quality assessment report."""
        logger.info("Saving data quality assessment report...")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        metrics_dict = asdict(metrics)
        json_path = os.path.join(output_dir, "data_quality_metrics.json")
        with open(json_path, "w") as f:
            json.dump(metrics_dict, f, indent=2)

        # Save detailed report
        report_path = os.path.join(output_dir, "data_quality_report.md")
        with open(report_path, "w") as f:
            f.write("# Data Quality Assessment Report\n\n")
            f.write(f"**Generated:** {metrics.assessment_timestamp}\n")
            f.write(f"**Sample Size:** {metrics.sample_size:,}\n")
            f.write(f"**Features Analyzed:** {metrics.features_analyzed}\n")
            f.write(f"**Constitutional Hash:** {self.constitutional_hash}\n\n")

            # Overall Quality Score
            f.write("## 🎯 Overall Quality Score\n\n")
            score_emoji = (
                "🟢"
                if metrics.quality_score >= 0.8
                else "🟡" if metrics.quality_score >= 0.6 else "🔴"
            )
            f.write(f"**{score_emoji} Quality Score: {metrics.quality_score:.1%}**\n")
            f.write(
                f"Target: >80% {'✅ ACHIEVED' if metrics.quality_score >= 0.8 else '❌ NOT ACHIEVED'}\n\n"
            )

            # Detailed Metrics
            f.write("## 📊 Detailed Quality Metrics\n\n")

            f.write("### Missing Values\n")
            f.write(f"- **Missing Rate:** {metrics.missing_value_rate:.1%}\n")
            f.write(
                f"- **Status:** {'✅ Good' if metrics.missing_value_rate <= 0.05 else '⚠️ High'}\n\n"
            )

            f.write("### Outliers\n")
            f.write(f"- **Outlier Rate:** {metrics.outlier_rate:.1%}\n")
            f.write(f"- **Affected Features:** {len(metrics.outlier_features)}\n")
            f.write(
                f"- **Status:** {'✅ Good' if metrics.outlier_rate <= 0.05 else '⚠️ High'}\n\n"
            )

            f.write("### Class Balance\n")
            f.write(f"- **Imbalance Ratio:** {metrics.imbalance_ratio:.3f}\n")
            f.write(
                f"- **Status:** {'✅ Balanced' if metrics.imbalance_ratio >= 0.8 else '⚠️ Imbalanced'}\n\n"
            )

            f.write("### Feature Correlation\n")
            f.write(f"- **Max Correlation:** {metrics.max_correlation:.3f}\n")
            f.write(
                f"- **High Correlation Pairs:** {len(metrics.high_correlation_pairs)}\n"
            )
            f.write(
                f"- **Status:** {'✅ Good' if metrics.max_correlation <= 0.9 else '⚠️ High Multicollinearity'}\n\n"
            )

            f.write("### Data Freshness\n")
            f.write(f"- **Hours Since Update:** {metrics.data_freshness_hours:.1f}\n")
            f.write(f"- **Stale Data Rate:** {metrics.stale_data_rate:.1%}\n")
            f.write(
                f"- **Status:** {'✅ Fresh' if metrics.data_freshness_hours <= 24 else '⚠️ Stale'}\n\n"
            )

            f.write("### Data Consistency\n")
            f.write(f"- **Duplicate Rate:** {metrics.duplicate_rate:.1%}\n")
            f.write(f"- **Inconsistency Rate:** {metrics.inconsistency_rate:.1%}\n")
            f.write(
                f"- **Status:** {'✅ Consistent' if metrics.duplicate_rate <= 0.01 else '⚠️ Issues Detected'}\n\n"
            )

            f.write("### Data Completeness\n")
            f.write(f"- **Completeness Score:** {metrics.completeness_score:.1%}\n")
            f.write(
                f"- **Status:** {'✅ Complete' if metrics.completeness_score >= 0.95 else '⚠️ Incomplete'}\n\n"
            )

            # Recommendations
            f.write("## 🔧 Recommendations\n\n")
            if metrics.quality_score >= 0.8:
                f.write(
                    "✅ **Data quality is excellent!** No immediate action required.\n\n"
                )
            else:
                f.write("⚠️ **Data quality improvements needed:**\n\n")

                if metrics.missing_value_rate > 0.05:
                    f.write("- Implement advanced imputation strategies (MICE)\n")
                if metrics.outlier_rate > 0.05:
                    f.write("- Apply outlier detection and treatment\n")
                if metrics.imbalance_ratio < 0.8:
                    f.write("- Use SMOTE or other balancing techniques\n")
                if metrics.max_correlation > 0.9:
                    f.write("- Remove highly correlated features\n")
                if metrics.data_freshness_hours > 24:
                    f.write("- Implement more frequent data updates\n")
                if metrics.duplicate_rate > 0.01:
                    f.write("- Remove duplicate records\n")
                if metrics.completeness_score < 0.95:
                    f.write("- Improve data collection processes\n")

        logger.info(f"✅ Data quality report saved to {output_dir}/")
        return json_path, report_path


def generate_test_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """Generate test dataset for data quality assessment."""
    logger.info(f"Generating test dataset with {n_samples} samples...")

    np.random.seed(42)  # For reproducibility

    # Generate features with various quality issues
    data = {
        # Clean numeric features
        "feature_1": np.random.normal(100, 15, n_samples),
        "feature_2": np.random.exponential(2, n_samples),
        # Feature with missing values
        "feature_with_missing": np.random.normal(50, 10, n_samples),
        # Feature with outliers
        "feature_with_outliers": np.random.normal(0, 1, n_samples),
        # Categorical features
        "category_a": np.random.choice(["A", "B", "C"], n_samples, p=[0.5, 0.3, 0.2]),
        "category_b": np.random.choice(["X", "Y"], n_samples, p=[0.8, 0.2]),
        # Correlated features
        "correlated_1": np.random.normal(0, 1, n_samples),
        # Target variable (imbalanced)
        "target": np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
        # Timestamp
        "timestamp": [
            datetime.now() - timedelta(hours=np.random.randint(0, 72))
            for _ in range(n_samples)
        ],
    }

    df = pd.DataFrame(data)

    # Introduce missing values (5% in feature_with_missing)
    missing_indices = np.random.choice(n_samples, int(0.05 * n_samples), replace=False)
    df.loc[missing_indices, "feature_with_missing"] = np.nan

    # Introduce outliers (3% in feature_with_outliers)
    outlier_indices = np.random.choice(n_samples, int(0.03 * n_samples), replace=False)
    df.loc[outlier_indices, "feature_with_outliers"] = (
        np.random.normal(0, 1, len(outlier_indices)) * 10
    )

    # Create highly correlated feature
    df["correlated_2"] = df["correlated_1"] * 0.95 + np.random.normal(0, 0.1, n_samples)

    # Introduce duplicates (1%)
    duplicate_indices = np.random.choice(
        n_samples, int(0.01 * n_samples), replace=False
    )
    for idx in duplicate_indices:
        if idx < n_samples - 1:
            df.iloc[idx + 1] = df.iloc[idx]

    logger.info(
        f"✅ Generated test dataset with {len(df)} records and {len(df.columns)} features"
    )
    return df


def main():
    """Main function to demonstrate data quality assessment."""
    logger.info("🚀 Starting Data Quality Assessment Framework Demo")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Initialize data quality assessment
        dqa = DataQualityAssessment()

        # Generate test dataset
        logger.info("\n📊 Step 1: Generating test dataset...")
        df = generate_test_dataset(n_samples=1000)

        # Perform comprehensive assessment
        logger.info("\n🔍 Step 2: Performing comprehensive data quality assessment...")
        metrics = dqa.comprehensive_assessment(
            df=df, target_column="target", timestamp_column="timestamp"
        )

        # Save assessment report
        logger.info("\n💾 Step 3: Saving assessment report...")
        json_path, report_path = dqa.save_assessment_report(metrics)

        # Display summary
        logger.info("\n🎉 Data Quality Assessment Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Overall Quality Score: {metrics.quality_score:.1%}")
        logger.info(
            f"🎯 Target Achievement: {'✅ ACHIEVED' if metrics.quality_score >= 0.8 else '❌ NOT ACHIEVED'}"
        )
        logger.info(f"📈 Missing Value Rate: {metrics.missing_value_rate:.1%}")
        logger.info(f"🔍 Outlier Rate: {metrics.outlier_rate:.1%}")
        logger.info(f"⚖️ Class Balance Ratio: {metrics.imbalance_ratio:.3f}")
        logger.info(f"🔗 Max Feature Correlation: {metrics.max_correlation:.3f}")
        logger.info(f"⏰ Data Freshness: {metrics.data_freshness_hours:.1f} hours")
        logger.info(f"🔄 Duplicate Rate: {metrics.duplicate_rate:.1%}")
        logger.info(f"✅ Completeness Score: {metrics.completeness_score:.1%}")
        logger.info("🔒 Constitutional Hash: cdd01ef066bc6cf2 ✅")
        logger.info("=" * 60)
        logger.info(f"📄 Metrics saved to: {json_path}")
        logger.info(f"📋 Report saved to: {report_path}")

        # Return success status
        return metrics.quality_score >= 0.8

    except Exception as e:
        logger.error(f"❌ Data quality assessment failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    import sys

    sys.exit(0 if success else 1)
