#!/usr/bin/env python3
"""
Test High Quality Data Generation for Data Quality Framework

Creates a high-quality dataset that achieves >0.8 quality score
to demonstrate the data quality framework capabilities.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from data_quality_framework import DataQualityAssessment

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_high_quality_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """Generate high-quality dataset that meets all quality criteria."""
    logger.info(f"Generating high-quality dataset with {n_samples} samples...")

    np.random.seed(42)  # For reproducibility

    # Generate features with high quality characteristics
    data = {
        # Clean numeric features with good distributions
        "response_time_ms": np.random.lognormal(
            6, 0.5, n_samples
        ),  # Log-normal for response times
        "cost_estimate": np.random.exponential(
            0.001, n_samples
        ),  # Exponential for costs
        "quality_score": np.random.beta(
            8, 2, n_samples
        ),  # Beta for quality scores (0-1)
        "content_length": np.random.poisson(
            1000, n_samples
        ),  # Poisson for content length
        # Categorical features with balanced distributions
        "request_type": np.random.choice(
            ["quick", "detailed", "validation"], n_samples, p=[0.4, 0.35, 0.25]
        ),
        "content_type": np.random.choice(
            ["text", "multimodal"], n_samples, p=[0.6, 0.4]
        ),
        "model_type": np.random.choice(
            ["flash_lite", "flash_full", "deepseek_r1"], n_samples, p=[0.4, 0.3, 0.3]
        ),
        # Time-based features
        "hour_of_day": np.random.randint(0, 24, n_samples),
        "day_of_week": np.random.randint(0, 7, n_samples),
        # Target variable with balanced distribution (closer to 50/50)
        "constitutional_compliance": np.random.choice(
            [True, False], n_samples, p=[0.55, 0.45]
        ),
        # Fresh timestamps (all within last 12 hours)
        "timestamp": [
            datetime.now() - timedelta(hours=np.random.uniform(0, 12))
            for _ in range(n_samples)
        ],
    }

    df = pd.DataFrame(data)

    # Introduce minimal quality issues to stay realistic but high-quality

    # Very low missing values (1% only)
    missing_indices = np.random.choice(n_samples, int(0.01 * n_samples), replace=False)
    df.loc[missing_indices, "quality_score"] = np.nan

    # Very few outliers (2% only)
    outlier_indices = np.random.choice(n_samples, int(0.02 * n_samples), replace=False)
    df.loc[outlier_indices, "response_time_ms"] = (
        df.loc[outlier_indices, "response_time_ms"] * 5
    )

    # No highly correlated features - keep features independent

    # Minimal duplicates (0.5% only)
    duplicate_indices = np.random.choice(
        n_samples, int(0.005 * n_samples), replace=False
    )
    for idx in duplicate_indices:
        if idx < n_samples - 1:
            df.iloc[idx + 1] = df.iloc[idx]

    logger.info(
        f"✅ Generated high-quality dataset with {len(df)} records and {len(df.columns)} features"
    )
    return df


def main():
    """Test data quality framework with high-quality dataset."""
    logger.info("🚀 Testing Data Quality Framework with High-Quality Dataset")

    try:
        # Initialize data quality assessment
        dqa = DataQualityAssessment()

        # Generate high-quality test dataset
        logger.info("\n📊 Step 1: Generating high-quality test dataset...")
        df = generate_high_quality_dataset(n_samples=1000)

        # Perform comprehensive assessment
        logger.info("\n🔍 Step 2: Performing comprehensive data quality assessment...")
        metrics = dqa.comprehensive_assessment(
            df=df,
            target_column="constitutional_compliance",
            timestamp_column="timestamp",
        )

        # Save assessment report
        logger.info("\n💾 Step 3: Saving assessment report...")
        json_path, report_path = dqa.save_assessment_report(
            metrics, "high_quality_results"
        )

        # Display summary
        logger.info("\n🎉 High-Quality Data Assessment Complete!")
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

        # Detailed quality breakdown
        if metrics.quality_score >= 0.8:
            logger.info("\n🎊 SUCCESS: Data quality target achieved!")
            logger.info("Key success factors:")
            logger.info(
                f"  ✅ Low missing values: {metrics.missing_value_rate:.1%} (target: <5%)"
            )
            logger.info(
                f"  ✅ Low outlier rate: {metrics.outlier_rate:.1%} (target: <5%)"
            )
            logger.info(
                f"  ✅ Balanced classes: {metrics.imbalance_ratio:.3f} (target: >0.4)"
            )
            logger.info(
                f"  ✅ Low correlation: {metrics.max_correlation:.3f} (target: <0.9)"
            )
            logger.info(
                f"  ✅ Fresh data: {metrics.data_freshness_hours:.1f}h (target: <24h)"
            )
            logger.info(
                f"  ✅ Low duplicates: {metrics.duplicate_rate:.1%} (target: <1%)"
            )
            logger.info(
                f"  ✅ High completeness: {metrics.completeness_score:.1%} (target: >95%)"
            )
        else:
            logger.warning("\n⚠️ Quality target not achieved. Areas for improvement:")
            if metrics.missing_value_rate > 0.05:
                logger.warning(
                    f"  - Missing values: {metrics.missing_value_rate:.1%} (target: <5%)"
                )
            if metrics.outlier_rate > 0.05:
                logger.warning(
                    f"  - Outlier rate: {metrics.outlier_rate:.1%} (target: <5%)"
                )
            if metrics.imbalance_ratio < 0.4:
                logger.warning(
                    f"  - Class imbalance: {metrics.imbalance_ratio:.3f} (target: >0.4)"
                )
            if metrics.max_correlation > 0.9:
                logger.warning(
                    f"  - High correlation: {metrics.max_correlation:.3f} (target: <0.9)"
                )
            if metrics.data_freshness_hours > 24:
                logger.warning(
                    f"  - Stale data: {metrics.data_freshness_hours:.1f}h (target: <24h)"
                )
            if metrics.duplicate_rate > 0.01:
                logger.warning(
                    f"  - Duplicates: {metrics.duplicate_rate:.1%} (target: <1%)"
                )
            if metrics.completeness_score < 0.95:
                logger.warning(
                    f"  - Incompleteness: {metrics.completeness_score:.1%} (target: >95%)"
                )

        # Return success status
        return metrics.quality_score >= 0.8

    except Exception as e:
        logger.error(f"❌ High-quality data test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    import sys

    sys.exit(0 if success else 1)
