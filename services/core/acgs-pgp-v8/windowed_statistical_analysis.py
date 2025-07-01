#!/usr/bin/env python3
"""
Windowed Statistical Analysis Framework for ACGS-PGP v8

Provides configurable time windows for continuous statistical monitoring:
- Tumbling, sliding, and session windows
- Real-time statistical computations
- Anomaly detection with statistical thresholds
- Constitutional compliance validation in windowed context
- Integration with streaming analytics pipeline

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import deque
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


@dataclass
class WindowConfig:
    """Configuration for statistical analysis windows."""

    window_type: str  # 'tumbling', 'sliding', 'session'
    size_seconds: int
    slide_seconds: Optional[int] = None  # For sliding windows
    session_timeout_seconds: Optional[int] = None  # For session windows
    max_records: int = 10000
    min_records: int = 10


@dataclass
class StatisticalMetrics:
    """Statistical metrics computed for a window."""

    window_id: str
    window_type: str
    start_time: str
    end_time: str
    record_count: int
    constitutional_hash: str

    # Basic statistics
    mean_values: Dict[str, float]
    std_values: Dict[str, float]
    min_values: Dict[str, float]
    max_values: Dict[str, float]
    median_values: Dict[str, float]

    # Advanced statistics
    skewness_values: Dict[str, float]
    kurtosis_values: Dict[str, float]
    percentiles: Dict[str, Dict[str, float]]  # {column: {p25: val, p75: val, ...}}

    # Anomaly detection
    anomaly_count: int
    anomaly_rate: float
    anomaly_scores: List[float]

    # Trend analysis
    trend_direction: Dict[str, str]  # 'increasing', 'decreasing', 'stable'
    trend_strength: Dict[str, float]  # correlation coefficient

    # Quality indicators
    completeness_rate: float
    consistency_score: float
    validity_score: float


class WindowManager:
    """Manages different types of analysis windows."""

    def __init__(self, config: WindowConfig):
        self.config = config
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.current_window_data = deque(maxlen=config.max_records)
        self.window_start_time = None
        self.last_activity_time = None
        self.window_id_counter = 0

        # Statistical processors
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)

        logger.info(f"Window Manager initialized: {config.window_type} window")

    def add_record(
        self, record: Dict[str, Any], timestamp: datetime = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Add a record to the window and return completed windows if any."""

        if timestamp is None:
            timestamp = datetime.now()

        # Initialize window if first record
        if self.window_start_time is None:
            self.window_start_time = timestamp

        self.last_activity_time = timestamp

        # Add record to current window
        record_with_timestamp = record.copy()
        record_with_timestamp["window_timestamp"] = timestamp
        self.current_window_data.append(record_with_timestamp)

        # Check if window should be completed
        completed_windows = []

        if self.config.window_type == "tumbling":
            completed_windows = self._check_tumbling_window(timestamp)
        elif self.config.window_type == "sliding":
            completed_windows = self._check_sliding_window(timestamp)
        elif self.config.window_type == "session":
            completed_windows = self._check_session_window(timestamp)

        return completed_windows if completed_windows else None

    def _check_tumbling_window(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Check if tumbling window should be completed."""

        if not self.window_start_time:
            return []

        window_duration = (current_time - self.window_start_time).total_seconds()

        if (
            window_duration >= self.config.size_seconds
            or len(self.current_window_data) >= self.config.max_records
        ):

            # Complete current window
            window_data = list(self.current_window_data)

            if len(window_data) >= self.config.min_records:
                completed_window = {
                    "window_id": self._generate_window_id(),
                    "window_type": "tumbling",
                    "start_time": self.window_start_time,
                    "end_time": current_time,
                    "data": window_data,
                }

                # Reset for next window
                self.current_window_data.clear()
                self.window_start_time = current_time

                return [completed_window]

        return []

    def _check_sliding_window(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Check if sliding window should be completed."""

        if not self.window_start_time or not self.config.slide_seconds:
            return []

        slide_duration = (current_time - self.window_start_time).total_seconds()

        if slide_duration >= self.config.slide_seconds:

            # Create window from data within the window size
            window_cutoff = current_time - timedelta(seconds=self.config.size_seconds)
            window_data = [
                record
                for record in self.current_window_data
                if record["window_timestamp"] >= window_cutoff
            ]

            if len(window_data) >= self.config.min_records:
                completed_window = {
                    "window_id": self._generate_window_id(),
                    "window_type": "sliding",
                    "start_time": window_cutoff,
                    "end_time": current_time,
                    "data": window_data,
                }

                # Update slide start time
                self.window_start_time = current_time

                return [completed_window]

        return []

    def _check_session_window(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Check if session window should be completed."""

        if not self.last_activity_time or not self.config.session_timeout_seconds:
            return []

        inactivity_duration = (current_time - self.last_activity_time).total_seconds()

        if inactivity_duration >= self.config.session_timeout_seconds:

            # Complete session window
            window_data = list(self.current_window_data)

            if len(window_data) >= self.config.min_records:
                completed_window = {
                    "window_id": self._generate_window_id(),
                    "window_type": "session",
                    "start_time": self.window_start_time,
                    "end_time": self.last_activity_time,
                    "data": window_data,
                }

                # Reset for next session
                self.current_window_data.clear()
                self.window_start_time = None

                return [completed_window]

        return []

    def _generate_window_id(self) -> str:
        """Generate unique window ID."""
        self.window_id_counter += 1
        return f"{self.config.window_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{self.window_id_counter}"


class StatisticalAnalyzer:
    """Performs statistical analysis on windowed data."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Anomaly detection models
        self.anomaly_detectors = {}

        logger.info(f"Statistical Analyzer initialized")

    async def analyze_window(self, window_data: Dict[str, Any]) -> StatisticalMetrics:
        """Perform comprehensive statistical analysis on window data."""

        # Convert window data to DataFrame
        df = pd.DataFrame(window_data["data"])

        if df.empty:
            logger.warning("⚠️ Empty window data for analysis")
            return None

        # Remove timestamp columns for analysis
        analysis_df = df.drop(columns=["window_timestamp"], errors="ignore")
        numeric_columns = analysis_df.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        if not numeric_columns:
            logger.warning("⚠️ No numeric columns for statistical analysis")
            return None

        # Basic statistics
        basic_stats = await self._compute_basic_statistics(analysis_df, numeric_columns)

        # Advanced statistics
        advanced_stats = await self._compute_advanced_statistics(
            analysis_df, numeric_columns
        )

        # Anomaly detection
        anomaly_results = await self._detect_anomalies(analysis_df, numeric_columns)

        # Trend analysis
        trend_results = await self._analyze_trends(analysis_df, numeric_columns)

        # Quality assessment
        quality_results = await self._assess_data_quality(analysis_df)

        # Create comprehensive metrics
        metrics = StatisticalMetrics(
            window_id=window_data["window_id"],
            window_type=window_data["window_type"],
            start_time=window_data["start_time"].isoformat(),
            end_time=window_data["end_time"].isoformat(),
            record_count=len(df),
            constitutional_hash=self.constitutional_hash,
            **basic_stats,
            **advanced_stats,
            **anomaly_results,
            **trend_results,
            **quality_results,
        )

        logger.info(
            f"📊 Window analysis completed: {window_data['window_id']} "
            f"({len(df)} records, {len(numeric_columns)} features)"
        )

        return metrics

    async def _compute_basic_statistics(
        self, df: pd.DataFrame, numeric_columns: List[str]
    ) -> Dict[str, Any]:
        """Compute basic statistical measures."""

        return {
            "mean_values": df[numeric_columns].mean().to_dict(),
            "std_values": df[numeric_columns].std().to_dict(),
            "min_values": df[numeric_columns].min().to_dict(),
            "max_values": df[numeric_columns].max().to_dict(),
            "median_values": df[numeric_columns].median().to_dict(),
        }

    async def _compute_advanced_statistics(
        self, df: pd.DataFrame, numeric_columns: List[str]
    ) -> Dict[str, Any]:
        """Compute advanced statistical measures."""

        skewness = {}
        kurtosis = {}
        percentiles = {}

        for col in numeric_columns:
            try:
                skewness[col] = float(stats.skew(df[col].dropna()))
                kurtosis[col] = float(stats.kurtosis(df[col].dropna()))

                percentiles[col] = {
                    "p25": float(df[col].quantile(0.25)),
                    "p50": float(df[col].quantile(0.50)),
                    "p75": float(df[col].quantile(0.75)),
                    "p90": float(df[col].quantile(0.90)),
                    "p95": float(df[col].quantile(0.95)),
                    "p99": float(df[col].quantile(0.99)),
                }
            except Exception as e:
                logger.warning(f"⚠️ Error computing advanced stats for {col}: {e}")
                skewness[col] = 0.0
                kurtosis[col] = 0.0
                percentiles[col] = {}

        return {
            "skewness_values": skewness,
            "kurtosis_values": kurtosis,
            "percentiles": percentiles,
        }

    async def _detect_anomalies(
        self, df: pd.DataFrame, numeric_columns: List[str]
    ) -> Dict[str, Any]:
        """Detect anomalies in the window data."""

        if len(df) < 10:  # Need minimum records for anomaly detection
            return {"anomaly_count": 0, "anomaly_rate": 0.0, "anomaly_scores": []}

        try:
            # Prepare data for anomaly detection
            X = df[numeric_columns].fillna(df[numeric_columns].mean())

            # Fit and predict anomalies
            anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = anomaly_detector.fit_predict(X)
            anomaly_scores = anomaly_detector.score_samples(X)

            # Count anomalies (-1 indicates anomaly)
            anomaly_count = int(np.sum(anomaly_labels == -1))
            anomaly_rate = float(anomaly_count / len(df))

            return {
                "anomaly_count": anomaly_count,
                "anomaly_rate": anomaly_rate,
                "anomaly_scores": anomaly_scores.tolist(),
            }

        except Exception as e:
            logger.warning(f"⚠️ Error in anomaly detection: {e}")
            return {"anomaly_count": 0, "anomaly_rate": 0.0, "anomaly_scores": []}

    async def _analyze_trends(
        self, df: pd.DataFrame, numeric_columns: List[str]
    ) -> Dict[str, Any]:
        """Analyze trends in the window data."""

        trend_direction = {}
        trend_strength = {}

        if len(df) < 3:  # Need minimum records for trend analysis
            return {
                "trend_direction": {col: "stable" for col in numeric_columns},
                "trend_strength": {col: 0.0 for col in numeric_columns},
            }

        # Create time index for trend analysis
        time_index = np.arange(len(df))

        for col in numeric_columns:
            try:
                values = df[col].dropna()
                if len(values) < 3:
                    trend_direction[col] = "stable"
                    trend_strength[col] = 0.0
                    continue

                # Calculate correlation with time (trend strength)
                correlation, _ = stats.pearsonr(time_index[: len(values)], values)

                # Determine trend direction
                if abs(correlation) < 0.1:
                    direction = "stable"
                elif correlation > 0:
                    direction = "increasing"
                else:
                    direction = "decreasing"

                trend_direction[col] = direction
                trend_strength[col] = float(abs(correlation))

            except Exception as e:
                logger.warning(f"⚠️ Error analyzing trend for {col}: {e}")
                trend_direction[col] = "stable"
                trend_strength[col] = 0.0

        return {"trend_direction": trend_direction, "trend_strength": trend_strength}

    async def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality metrics for the window."""

        total_cells = df.size
        missing_cells = df.isnull().sum().sum()

        # Completeness rate
        completeness_rate = (
            float(1 - (missing_cells / total_cells)) if total_cells > 0 else 0.0
        )

        # Consistency score (simplified - based on data type consistency)
        consistency_score = (
            0.9  # Placeholder - would implement actual consistency checks
        )

        # Validity score (simplified - based on value ranges)
        validity_score = 0.95  # Placeholder - would implement actual validity checks

        return {
            "completeness_rate": completeness_rate,
            "consistency_score": consistency_score,
            "validity_score": validity_score,
        }


class WindowedAnalyticsEngine:
    """Main engine for windowed statistical analysis."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.window_managers: Dict[str, WindowManager] = {}
        self.statistical_analyzer = StatisticalAnalyzer()
        self.metrics_history: List[StatisticalMetrics] = []

        logger.info(f"Windowed Analytics Engine initialized")

    def create_window(self, window_name: str, config: WindowConfig):
        """Create a new analysis window."""
        self.window_managers[window_name] = WindowManager(config)
        logger.info(f"✅ Created window: {window_name} ({config.window_type})")

    async def process_record(
        self, window_name: str, record: Dict[str, Any]
    ) -> List[StatisticalMetrics]:
        """Process a record through the specified window."""

        if window_name not in self.window_managers:
            logger.error(f"❌ Window {window_name} not found")
            return []

        # Validate constitutional hash
        if "constitutional_hash" in record:
            if record["constitutional_hash"] != self.constitutional_hash:
                logger.warning(f"⚠️ Constitutional hash mismatch in record")
                return []

        # Add record to window
        window_manager = self.window_managers[window_name]
        completed_windows = window_manager.add_record(record)

        if not completed_windows:
            return []

        # Analyze completed windows
        metrics_list = []
        for window_data in completed_windows:
            metrics = await self.statistical_analyzer.analyze_window(window_data)
            if metrics:
                metrics_list.append(metrics)
                self.metrics_history.append(metrics)

        return metrics_list

    def get_recent_metrics(
        self, window_name: str = None, limit: int = 10
    ) -> List[StatisticalMetrics]:
        """Get recent statistical metrics."""

        if window_name:
            filtered_metrics = [
                m for m in self.metrics_history if window_name in m.window_id
            ]
        else:
            filtered_metrics = self.metrics_history

        return filtered_metrics[-limit:] if filtered_metrics else []


# Example usage and testing
async def demo_windowed_analysis():
    """Demonstrate windowed statistical analysis."""

    # Initialize analytics engine
    engine = WindowedAnalyticsEngine()

    # Create different types of windows
    engine.create_window(
        "quality_tumbling",
        WindowConfig(window_type="tumbling", size_seconds=30, min_records=5),
    )

    engine.create_window(
        "performance_sliding",
        WindowConfig(
            window_type="sliding", size_seconds=60, slide_seconds=10, min_records=3
        ),
    )

    # Generate sample data
    print("📊 Processing sample data through windowed analysis...")

    for i in range(100):
        record = {
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": np.random.lognormal(6, 0.5),
            "throughput_rps": np.random.normal(100, 20),
            "error_rate": np.random.exponential(0.02),
            "quality_score": np.random.beta(8, 2),
            "constitutional_hash": engine.constitutional_hash,
        }

        # Process through both windows
        quality_metrics = await engine.process_record("quality_tumbling", record)
        performance_metrics = await engine.process_record("performance_sliding", record)

        # Log completed windows
        for metrics in quality_metrics + performance_metrics:
            print(
                f"✅ Window completed: {metrics.window_id} "
                f"({metrics.record_count} records, "
                f"anomalies: {metrics.anomaly_count})"
            )

        # Simulate real-time processing
        await asyncio.sleep(0.1)

    # Display summary
    recent_metrics = engine.get_recent_metrics(limit=5)
    print(f"\n📈 Recent analysis summary:")
    for metrics in recent_metrics:
        print(
            f"  - {metrics.window_id}: {metrics.record_count} records, "
            f"anomaly rate: {metrics.anomaly_rate:.3f}"
        )

    print("✅ Windowed statistical analysis demo completed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run demo
    asyncio.run(demo_windowed_analysis())
