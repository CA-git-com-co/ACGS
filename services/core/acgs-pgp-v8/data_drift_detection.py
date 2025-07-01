#!/usr/bin/env python3
"""
Data Drift Detection System for ACGS-PGP v8

Implements statistical data drift detection using:
- Kolmogorov-Smirnov tests (threshold: 0.05 p-value)
- Population Stability Index (PSI)
- Automated retraining triggers
- Feature-level drift monitoring

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import os
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DriftDetectionResults:
    """Results from data drift detection analysis."""

    # Overall drift metrics
    overall_drift_detected: bool
    drift_severity: str  # 'none', 'low', 'medium', 'high'
    drift_score: float  # 0-1, higher indicates more drift

    # KS test results
    ks_test_results: dict[
        str, dict[str, float]
    ]  # feature -> {statistic, p_value, drift_detected}
    features_with_ks_drift: list[str]

    # PSI results
    psi_results: dict[str, float]  # feature -> PSI value
    features_with_psi_drift: list[str]

    # Retraining recommendations
    retraining_required: bool
    retraining_urgency: str  # 'none', 'low', 'medium', 'high'
    affected_features: list[str]

    # Monitoring metadata
    reference_period: str
    current_period: str
    samples_reference: int
    samples_current: int
    constitutional_hash: str
    timestamp: str


class DataDriftDetector:
    """Statistical data drift detection system."""

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.ks_threshold = 0.05  # p-value threshold for KS test
        self.psi_thresholds = {
            "low": 0.1,  # PSI < 0.1: no significant drift
            "medium": 0.2,  # 0.1 <= PSI < 0.2: moderate drift
            "high": 0.2,  # PSI >= 0.2: significant drift
        }

    def calculate_psi(
        self, reference: np.ndarray, current: np.ndarray, n_bins: int = 10
    ) -> float:
        """Calculate Population Stability Index (PSI)."""

        # Handle edge cases
        if len(reference) == 0 or len(current) == 0:
            return 0.0

        # Create bins based on reference data
        try:
            # Use quantile-based binning for better stability
            bin_edges = np.quantile(reference, np.linspace(0, 1, n_bins + 1))

            # Ensure unique bin edges
            bin_edges = np.unique(bin_edges)
            if len(bin_edges) < 2:
                return 0.0

            # Calculate distributions
            ref_counts, _ = np.histogram(reference, bins=bin_edges)
            cur_counts, _ = np.histogram(current, bins=bin_edges)

            # Convert to proportions
            ref_props = ref_counts / len(reference)
            cur_props = cur_counts / len(current)

            # Add small epsilon to avoid log(0)
            epsilon = 1e-10
            ref_props = np.maximum(ref_props, epsilon)
            cur_props = np.maximum(cur_props, epsilon)

            # Calculate PSI
            psi = np.sum((cur_props - ref_props) * np.log(cur_props / ref_props))

            return float(psi)

        except Exception as e:
            logger.warning(f"PSI calculation failed: {e}")
            return 0.0

    def perform_ks_test(
        self, reference: np.ndarray, current: np.ndarray
    ) -> dict[str, float]:
        """Perform Kolmogorov-Smirnov test for drift detection."""

        if len(reference) == 0 or len(current) == 0:
            return {"statistic": 0.0, "p_value": 1.0, "drift_detected": False}

        try:
            # Perform two-sample KS test
            ks_statistic, p_value = ks_2samp(reference, current)

            # Drift detected if p-value < threshold
            drift_detected = p_value < self.ks_threshold

            return {
                "statistic": float(ks_statistic),
                "p_value": float(p_value),
                "drift_detected": bool(drift_detected),
            }

        except Exception as e:
            logger.warning(f"KS test failed: {e}")
            return {"statistic": 0.0, "p_value": 1.0, "drift_detected": False}

    def generate_reference_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate reference dataset for drift detection testing."""
        logger.info(f"Generating reference dataset with {n_samples} samples...")

        np.random.seed(42)

        # Generate stable reference data
        data = {
            "response_time_ms": np.random.lognormal(6, 0.5, n_samples),
            "cost_estimate": np.random.exponential(0.001, n_samples),
            "quality_score": np.random.beta(8, 2, n_samples),
            "complexity_score": np.random.gamma(2, 2, n_samples),
            "content_length": np.random.poisson(1000, n_samples),
            "hour_of_day": np.random.randint(0, 24, n_samples),
            "is_weekend": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            "constitutional_compliance": np.random.choice(
                [0, 1], n_samples, p=[0.05, 0.95]
            ),
        }

        df = pd.DataFrame(data)
        logger.info(f"✅ Generated reference dataset with {len(df)} samples")
        return df

    def generate_drifted_data(
        self, reference_df: pd.DataFrame, drift_intensity: str = "medium"
    ) -> pd.DataFrame:
        """Generate current dataset with controlled drift."""
        logger.info(f"Generating drifted dataset with {drift_intensity} intensity...")

        n_samples = len(reference_df)
        np.random.seed(123)  # Different seed for drift

        # Define drift parameters
        drift_params = {
            "low": {"shift": 0.1, "scale": 1.05},
            "medium": {"shift": 0.3, "scale": 1.2},
            "high": {"shift": 0.5, "scale": 1.5},
        }

        params = drift_params.get(drift_intensity, drift_params["medium"])
        shift_factor = params["shift"]
        scale_factor = params["scale"]

        # Generate drifted data
        data = {
            # Response time: increased mean and variance (system degradation)
            "response_time_ms": np.random.lognormal(
                6 + shift_factor, 0.5 * scale_factor, n_samples
            ),
            # Cost: slight increase (inflation)
            "cost_estimate": np.random.exponential(
                0.001 * (1 + shift_factor), n_samples
            ),
            # Quality: slight decrease (degradation)
            "quality_score": np.random.beta(8 * (1 - shift_factor / 2), 2, n_samples),
            # Complexity: increased (more complex requests)
            "complexity_score": np.random.gamma(2 * scale_factor, 2, n_samples),
            # Content length: increased (longer requests)
            "content_length": np.random.poisson(int(1000 * scale_factor), n_samples),
            # Hour distribution: shift towards peak hours
            "hour_of_day": np.random.choice(
                range(24),
                n_samples,
                p=self._create_shifted_hour_distribution(shift_factor),
            ),
            # Weekend pattern: slight change
            "is_weekend": np.random.choice(
                [0, 1], n_samples, p=[0.7 - shift_factor / 10, 0.3 + shift_factor / 10]
            ),
            # Constitutional compliance: slight decrease (more violations)
            "constitutional_compliance": np.random.choice(
                [0, 1],
                n_samples,
                p=[0.05 + shift_factor / 10, 0.95 - shift_factor / 10],
            ),
        }

        df = pd.DataFrame(data)
        logger.info(f"✅ Generated drifted dataset with {len(df)} samples")
        return df

    def _create_shifted_hour_distribution(self, shift_factor: float) -> np.ndarray:
        """Create shifted hour distribution for drift simulation."""
        # Base uniform distribution
        base_probs = np.ones(24) / 24

        # Add bias towards business hours (9-17)
        business_hours = np.zeros(24)
        business_hours[9:18] = 1

        # Combine base and bias
        shifted_probs = base_probs + shift_factor * business_hours / 9

        # Normalize
        shifted_probs = shifted_probs / np.sum(shifted_probs)

        return shifted_probs

    def detect_drift(
        self, reference_df: pd.DataFrame, current_df: pd.DataFrame
    ) -> DriftDetectionResults:
        """Perform comprehensive drift detection analysis."""
        logger.info("Performing comprehensive drift detection analysis...")

        # Select numeric features for drift detection
        numeric_features = reference_df.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        # Initialize results containers
        ks_results = {}
        psi_results = {}
        features_with_ks_drift = []
        features_with_psi_drift = []

        # Analyze each feature
        for feature in numeric_features:
            logger.info(f"  Analyzing feature: {feature}")

            ref_data = reference_df[feature].dropna().values
            cur_data = current_df[feature].dropna().values

            # KS test
            ks_result = self.perform_ks_test(ref_data, cur_data)
            ks_results[feature] = ks_result

            if ks_result["drift_detected"]:
                features_with_ks_drift.append(feature)

            # PSI calculation
            psi_value = self.calculate_psi(ref_data, cur_data)
            psi_results[feature] = psi_value

            if psi_value >= self.psi_thresholds["low"]:
                features_with_psi_drift.append(feature)

            logger.info(
                f"    KS p-value: {ks_result['p_value']:.4f}, PSI: {psi_value:.4f}"
            )

        # Determine overall drift status
        overall_drift_detected = (
            len(features_with_ks_drift) > 0 or len(features_with_psi_drift) > 0
        )

        # Calculate drift severity
        drift_score = self._calculate_drift_score(ks_results, psi_results)
        drift_severity = self._determine_drift_severity(drift_score)

        # Determine retraining requirements
        retraining_required, retraining_urgency = self._assess_retraining_needs(
            features_with_ks_drift, features_with_psi_drift, drift_severity
        )

        # Affected features (union of KS and PSI drift features)
        affected_features = list(set(features_with_ks_drift + features_with_psi_drift))

        # Create results
        results = DriftDetectionResults(
            overall_drift_detected=overall_drift_detected,
            drift_severity=drift_severity,
            drift_score=drift_score,
            ks_test_results=ks_results,
            features_with_ks_drift=features_with_ks_drift,
            psi_results=psi_results,
            features_with_psi_drift=features_with_psi_drift,
            retraining_required=retraining_required,
            retraining_urgency=retraining_urgency,
            affected_features=affected_features,
            reference_period="baseline",
            current_period="current",
            samples_reference=len(reference_df),
            samples_current=len(current_df),
            constitutional_hash=self.constitutional_hash,
            timestamp=datetime.now().isoformat(),
        )

        logger.info("✅ Drift detection complete:")
        logger.info(f"  - Overall drift detected: {overall_drift_detected}")
        logger.info(f"  - Drift severity: {drift_severity}")
        logger.info(f"  - Features with KS drift: {len(features_with_ks_drift)}")
        logger.info(f"  - Features with PSI drift: {len(features_with_psi_drift)}")
        logger.info(f"  - Retraining required: {retraining_required}")

        return results

    def _calculate_drift_score(self, ks_results: dict, psi_results: dict) -> float:
        """Calculate overall drift score (0-1)."""

        if not ks_results and not psi_results:
            return 0.0

        # KS score: average of (1 - p_value) for significant tests
        ks_scores = []
        for feature, result in ks_results.items():
            if result["drift_detected"]:
                ks_scores.append(1 - result["p_value"])

        avg_ks_score = np.mean(ks_scores) if ks_scores else 0.0

        # PSI score: normalized PSI values
        psi_scores = []
        for feature, psi_value in psi_results.items():
            normalized_psi = min(1.0, psi_value / 0.5)  # Normalize to 0-1
            psi_scores.append(normalized_psi)

        avg_psi_score = np.mean(psi_scores) if psi_scores else 0.0

        # Combined score (weighted average)
        drift_score = 0.6 * avg_ks_score + 0.4 * avg_psi_score

        return float(drift_score)

    def _determine_drift_severity(self, drift_score: float) -> str:
        """Determine drift severity based on drift score."""

        if drift_score < 0.1:
            return "none"
        if drift_score < 0.3:
            return "low"
        if drift_score < 0.6:
            return "medium"
        return "high"

    def _assess_retraining_needs(
        self,
        ks_drift_features: list[str],
        psi_drift_features: list[str],
        drift_severity: str,
    ) -> tuple[bool, str]:
        """Assess retraining requirements based on drift analysis."""

        total_drift_features = len(set(ks_drift_features + psi_drift_features))

        # Retraining required if significant drift detected
        retraining_required = (
            drift_severity in ["medium", "high"] or total_drift_features >= 3
        )

        # Determine urgency
        if drift_severity == "high" or total_drift_features >= 5:
            urgency = "high"
        elif drift_severity == "medium" or total_drift_features >= 3:
            urgency = "medium"
        elif drift_severity == "low" or total_drift_features >= 1:
            urgency = "low"
        else:
            urgency = "none"

        return retraining_required, urgency

    def save_drift_results(
        self,
        results: DriftDetectionResults,
        output_dir: str = "drift_detection_results",
    ) -> tuple[str, str]:
        """Save drift detection results."""
        logger.info("Saving drift detection results...")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        results_dict = asdict(results)
        json_path = os.path.join(output_dir, "drift_detection_results.json")
        with open(json_path, "w") as f:
            json.dump(results_dict, f, indent=2)

        # Save detailed report
        report_path = os.path.join(output_dir, "drift_detection_report.md")
        with open(report_path, "w") as f:
            f.write("# Data Drift Detection Report\n\n")
            f.write(f"**Generated:** {results.timestamp}\n")
            f.write(f"**Constitutional Hash:** {results.constitutional_hash}\n\n")

            # Executive Summary
            f.write("## 🎯 Executive Summary\n\n")
            drift_emoji = (
                "🔴"
                if results.drift_severity == "high"
                else "🟡" if results.drift_severity == "medium" else "🟢"
            )
            f.write(
                f"**{drift_emoji} Drift Status:** {results.drift_severity.upper()}\n"
            )
            f.write(f"**Drift Score:** {results.drift_score:.3f}\n")
            f.write(
                f"**Retraining Required:** {'✅ YES' if results.retraining_required else '❌ NO'}\n"
            )
            f.write(f"**Urgency Level:** {results.retraining_urgency.upper()}\n\n")

            # Dataset Information
            f.write("## 📊 Dataset Information\n\n")
            f.write(f"- **Reference Period:** {results.reference_period}\n")
            f.write(f"- **Current Period:** {results.current_period}\n")
            f.write(f"- **Reference Samples:** {results.samples_reference:,}\n")
            f.write(f"- **Current Samples:** {results.samples_current:,}\n\n")

            # Drift Analysis Results
            f.write("## 🔍 Drift Analysis Results\n\n")
            f.write("### Kolmogorov-Smirnov Test Results\n\n")
            f.write("| Feature | KS Statistic | P-Value | Drift Detected |\n")
            f.write("|---------|--------------|---------|----------------|\n")

            for feature, result in results.ks_test_results.items():
                status = "✅ YES" if result["drift_detected"] else "❌ NO"
                f.write(
                    f"| {feature} | {result['statistic']:.4f} | {result['p_value']:.4f} | {status} |\n"
                )

            f.write("\n### Population Stability Index (PSI) Results\n\n")
            f.write("| Feature | PSI Value | Drift Level |\n")
            f.write("|---------|-----------|-------------|\n")

            for feature, psi_value in results.psi_results.items():
                if psi_value >= 0.2:
                    level = "🔴 High"
                elif psi_value >= 0.1:
                    level = "🟡 Medium"
                else:
                    level = "🟢 Low"
                f.write(f"| {feature} | {psi_value:.4f} | {level} |\n")

            # Affected Features
            f.write("\n## ⚠️ Affected Features\n\n")
            if results.affected_features:
                f.write("Features showing significant drift:\n")
                for feature in results.affected_features:
                    f.write(f"- **{feature}**\n")
            else:
                f.write("✅ No features showing significant drift.\n")

            # Retraining Recommendations
            f.write("\n## 🔄 Retraining Recommendations\n\n")
            if results.retraining_required:
                f.write(
                    f"**🚨 RETRAINING REQUIRED - {results.retraining_urgency.upper()} PRIORITY**\n\n"
                )

                if results.retraining_urgency == "high":
                    f.write("**Immediate Actions Required:**\n")
                    f.write("1. Initiate emergency retraining pipeline\n")
                    f.write("2. Collect fresh training data\n")
                    f.write("3. Validate model performance\n")
                    f.write("4. Deploy updated model within 24 hours\n")
                elif results.retraining_urgency == "medium":
                    f.write("**Actions Required (within 72 hours):**\n")
                    f.write("1. Schedule retraining pipeline\n")
                    f.write("2. Prepare updated training dataset\n")
                    f.write("3. Validate model improvements\n")
                    f.write("4. Plan staged deployment\n")
                else:
                    f.write("**Actions Required (within 1 week):**\n")
                    f.write("1. Monitor drift progression\n")
                    f.write("2. Prepare for potential retraining\n")
                    f.write("3. Update monitoring thresholds\n")
            else:
                f.write("✅ **No immediate retraining required**\n\n")
                f.write("**Monitoring Recommendations:**\n")
                f.write("1. Continue regular drift monitoring\n")
                f.write("2. Review thresholds if needed\n")
                f.write("3. Maintain data quality standards\n")

            # Technical Details
            f.write("\n## 🔧 Technical Configuration\n\n")
            f.write("### Detection Parameters\n")
            f.write(f"- **KS Test Threshold:** {self.ks_threshold} (p-value)\n")
            f.write(f"- **PSI Low Threshold:** {self.psi_thresholds['low']}\n")
            f.write(f"- **PSI Medium Threshold:** {self.psi_thresholds['medium']}\n")
            f.write(f"- **PSI High Threshold:** {self.psi_thresholds['high']}\n")
            f.write(f"- **Constitutional Hash:** {self.constitutional_hash}\n\n")

            f.write("### Automated Triggers\n")
            f.write("- **High Priority:** Immediate retraining pipeline activation\n")
            f.write("- **Medium Priority:** Scheduled retraining within 72 hours\n")
            f.write("- **Low Priority:** Enhanced monitoring and preparation\n")

        logger.info(f"✅ Drift detection results saved to {output_dir}/")
        return json_path, report_path


def main():
    """Main function to test data drift detection system."""
    logger.info("🚀 Starting Data Drift Detection System Test")

    try:
        # Initialize drift detector
        drift_detector = DataDriftDetector()

        # Generate reference dataset
        logger.info("\n📊 Step 1: Generating reference dataset...")
        reference_df = drift_detector.generate_reference_data(n_samples=1500)

        # Generate drifted dataset
        logger.info("\n📈 Step 2: Generating drifted dataset...")
        current_df = drift_detector.generate_drifted_data(
            reference_df, drift_intensity="medium"
        )

        # Perform drift detection
        logger.info("\n🔍 Step 3: Performing drift detection...")
        results = drift_detector.detect_drift(reference_df, current_df)

        # Save results
        logger.info("\n💾 Step 4: Saving results...")
        json_path, report_path = drift_detector.save_drift_results(results)

        # Display summary
        logger.info("\n🎉 Data Drift Detection Test Complete!")
        logger.info("=" * 60)
        logger.info(
            f"🎯 Drift Detected: {'✅ YES' if results.overall_drift_detected else '❌ NO'}"
        )
        logger.info(f"📊 Drift Severity: {results.drift_severity.upper()}")
        logger.info(f"📈 Drift Score: {results.drift_score:.3f}")
        logger.info(f"🔍 KS Drift Features: {len(results.features_with_ks_drift)}")
        logger.info(f"📊 PSI Drift Features: {len(results.features_with_psi_drift)}")
        logger.info(
            f"🔄 Retraining Required: {'✅ YES' if results.retraining_required else '❌ NO'}"
        )
        logger.info(f"⚡ Urgency Level: {results.retraining_urgency.upper()}")
        logger.info(f"🔒 Constitutional Hash: {results.constitutional_hash} ✅")
        logger.info("=" * 60)
        logger.info(f"📄 Results saved to: {json_path}")
        logger.info(f"📋 Report saved to: {report_path}")

        # Validate success criteria
        success_criteria = [
            results.overall_drift_detected,  # Drift detection operational
            len(results.ks_test_results) > 0,  # KS tests performed
            len(results.psi_results) > 0,  # PSI calculations performed
            results.retraining_required,  # Automated triggers functional
        ]

        success = all(success_criteria)

        if success:
            logger.info("\n✅ SUCCESS: Data drift detection system operational!")
            logger.info("Key capabilities demonstrated:")
            logger.info("  ✅ Kolmogorov-Smirnov statistical testing")
            logger.info("  ✅ Population Stability Index calculation")
            logger.info("  ✅ Automated retraining triggers")
            logger.info("  ✅ Feature-level drift monitoring")
        else:
            logger.warning(
                "\n⚠️ Some criteria not met. Review results for optimization."
            )

        return success

    except Exception as e:
        logger.error(f"❌ Data drift detection test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    import sys

    sys.exit(0 if success else 1)
