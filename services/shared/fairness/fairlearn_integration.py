"""
Microsoft Fairlearn Integration

Production-ready bias detection and mitigation using Microsoft's Fairlearn library,
implementing the ACGE technical validation recommendations for replacing experimental
fairness tools with industry-standard solutions.

Key Features:
- Comprehensive bias metrics calculation
- Multiple fairness constraint implementations
- Post-processing bias mitigation
- Real-time fairness monitoring
- Integration with existing ACGS audit systems
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from enum import Enum

# Fairlearn imports (would be installed via pip install fairlearn)
try:
    from fairlearn.metrics import (
        MetricFrame, 
        demographic_parity_difference,
        demographic_parity_ratio,
        equalized_odds_difference,
        equalized_odds_ratio,
        false_positive_rate,
        false_negative_rate,
        selection_rate
    )
    from fairlearn.reductions import (
        ExponentiatedGradient,
        GridSearch,
        DemographicParity,
        EqualizedOdds,
        TruePositiveRateParity,
        FalsePositiveRateParity
    )
    from fairlearn.postprocessing import ThresholdOptimizer
    FAIRLEARN_AVAILABLE = True
except ImportError:
    # Fallback implementations for environments where Fairlearn isn't available
    FAIRLEARN_AVAILABLE = False
    logging.warning("Fairlearn not available, using fallback implementations")

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)

class FairnessMetric(Enum):
    """Supported fairness metrics"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    PREDICTIVE_PARITY = "predictive_parity"
    CALIBRATION = "calibration"

class BiasLevel(Enum):
    """Bias severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FairnessResult:
    """Result of fairness evaluation"""
    metric: FairnessMetric
    value: float
    bias_level: BiasLevel
    affected_groups: List[str]
    recommendation: str
    timestamp: datetime
    confidence: float

@dataclass
class BiasDetectionResult:
    """Comprehensive bias detection result"""
    overall_bias_level: BiasLevel
    fairness_results: List[FairnessResult]
    summary_metrics: Dict[str, float]
    recommendations: List[str]
    requires_mitigation: bool
    affected_protected_attributes: List[str]
    timestamp: datetime

class FairlearnBiasDetector:
    """
    Production-ready bias detection using Microsoft Fairlearn
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()
        
        # Fairness thresholds (configurable)
        self.thresholds = {
            FairnessMetric.DEMOGRAPHIC_PARITY: {
                'difference': {'low': 0.05, 'medium': 0.10, 'high': 0.20},
                'ratio': {'low': 0.95, 'medium': 0.90, 'high': 0.80}
            },
            FairnessMetric.EQUALIZED_ODDS: {
                'difference': {'low': 0.05, 'medium': 0.10, 'high': 0.20},
                'ratio': {'low': 0.95, 'medium': 0.90, 'high': 0.80}
            }
        }
        
        # Initialize metrics tracking
        self.bias_detection_history = []
        self.protected_attributes = ['race', 'gender', 'age_group', 'disability_status']
        
    def _calculate_bias_level(self, metric: FairnessMetric, value: float, metric_type: str = 'difference') -> BiasLevel:
        """Calculate bias level based on metric value and thresholds"""
        if metric not in self.thresholds:
            # Default thresholds for unsupported metrics
            if metric_type == 'difference':
                if abs(value) <= 0.05:
                    return BiasLevel.NONE
                elif abs(value) <= 0.10:
                    return BiasLevel.LOW
                elif abs(value) <= 0.20:
                    return BiasLevel.MEDIUM
                else:
                    return BiasLevel.HIGH
            else:  # ratio
                if 0.95 <= value <= 1.05:
                    return BiasLevel.NONE
                elif 0.90 <= value <= 1.10:
                    return BiasLevel.LOW
                elif 0.80 <= value <= 1.20:
                    return BiasLevel.MEDIUM
                else:
                    return BiasLevel.HIGH
        
        thresholds = self.thresholds[metric][metric_type]
        abs_value = abs(value) if metric_type == 'difference' else min(value, 2.0 - value)
        
        if metric_type == 'difference':
            if abs_value <= thresholds['low']:
                return BiasLevel.NONE
            elif abs_value <= thresholds['medium']:
                return BiasLevel.LOW
            elif abs_value <= thresholds['high']:
                return BiasLevel.MEDIUM
            else:
                return BiasLevel.HIGH
        else:  # ratio
            if abs_value >= thresholds['low']:
                return BiasLevel.NONE
            elif abs_value >= thresholds['medium']:
                return BiasLevel.LOW
            elif abs_value >= thresholds['high']:
                return BiasLevel.MEDIUM
            else:
                return BiasLevel.HIGH

    async def detect_bias_fairlearn(self, 
                                   y_true: np.ndarray,
                                   y_pred: np.ndarray, 
                                   sensitive_features: pd.DataFrame) -> BiasDetectionResult:
        """
        Comprehensive bias detection using Fairlearn
        
        Args:
            y_true: True labels
            y_pred: Predicted labels or probabilities
            sensitive_features: DataFrame with protected attributes
            
        Returns:
            Comprehensive bias detection result
        """
        if not FAIRLEARN_AVAILABLE:
            return await self.detect_bias_fallback(y_true, y_pred, sensitive_features)
        
        fairness_results = []
        affected_attributes = []
        
        try:
            # Calculate demographic parity
            dp_diff = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_features)
            dp_ratio = demographic_parity_ratio(y_true, y_pred, sensitive_features=sensitive_features)
            
            dp_diff_level = self._calculate_bias_level(FairnessMetric.DEMOGRAPHIC_PARITY, dp_diff, 'difference')
            dp_ratio_level = self._calculate_bias_level(FairnessMetric.DEMOGRAPHIC_PARITY, dp_ratio, 'ratio')
            
            fairness_results.append(FairnessResult(
                metric=FairnessMetric.DEMOGRAPHIC_PARITY,
                value=dp_diff,
                bias_level=max(dp_diff_level, dp_ratio_level, key=lambda x: x.value),
                affected_groups=self._identify_affected_groups(sensitive_features, dp_diff),
                recommendation=self._get_recommendation(FairnessMetric.DEMOGRAPHIC_PARITY, dp_diff_level),
                timestamp=datetime.utcnow(),
                confidence=0.95
            ))
            
            # Calculate equalized odds if we have binary classification
            if len(np.unique(y_true)) == 2:
                eo_diff = equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive_features)
                eo_ratio = equalized_odds_ratio(y_true, y_pred, sensitive_features=sensitive_features)
                
                eo_diff_level = self._calculate_bias_level(FairnessMetric.EQUALIZED_ODDS, eo_diff, 'difference')
                eo_ratio_level = self._calculate_bias_level(FairnessMetric.EQUALIZED_ODDS, eo_ratio, 'ratio')
                
                fairness_results.append(FairnessResult(
                    metric=FairnessMetric.EQUALIZED_ODDS,
                    value=eo_diff,
                    bias_level=max(eo_diff_level, eo_ratio_level, key=lambda x: x.value),
                    affected_groups=self._identify_affected_groups(sensitive_features, eo_diff),
                    recommendation=self._get_recommendation(FairnessMetric.EQUALIZED_ODDS, eo_diff_level),
                    timestamp=datetime.utcnow(),
                    confidence=0.95
                ))
            
            # Use MetricFrame for comprehensive analysis
            metric_frame = MetricFrame(
                metrics={
                    'accuracy': lambda y_true, y_pred: np.mean(y_true == y_pred),
                    'false_positive_rate': false_positive_rate,
                    'false_negative_rate': false_negative_rate,
                    'selection_rate': selection_rate
                },
                y_true=y_true,
                y_pred=y_pred,
                sensitive_features=sensitive_features
            )
            
            # Identify overall bias level
            bias_levels = [result.bias_level for result in fairness_results]
            overall_bias = max(bias_levels, key=lambda x: x.value) if bias_levels else BiasLevel.NONE
            
            # Generate summary metrics
            summary_metrics = {
                'demographic_parity_difference': dp_diff,
                'demographic_parity_ratio': dp_ratio,
                'max_group_accuracy_difference': metric_frame.difference()['accuracy'] if 'accuracy' in metric_frame.difference() else 0.0,
                'overall_bias_score': self._calculate_overall_bias_score(fairness_results)
            }
            
            # Generate recommendations
            recommendations = [result.recommendation for result in fairness_results if result.bias_level != BiasLevel.NONE]
            if overall_bias in [BiasLevel.HIGH, BiasLevel.CRITICAL]:
                recommendations.append("Immediate bias mitigation required")
            
            # Determine mitigation requirement
            requires_mitigation = overall_bias in [BiasLevel.MEDIUM, BiasLevel.HIGH, BiasLevel.CRITICAL]
            
            result = BiasDetectionResult(
                overall_bias_level=overall_bias,
                fairness_results=fairness_results,
                summary_metrics=summary_metrics,
                recommendations=recommendations,
                requires_mitigation=requires_mitigation,
                affected_protected_attributes=affected_attributes,
                timestamp=datetime.utcnow()
            )
            
            # Log for audit trail
            await self.audit_logger.log_bias_detection({
                'overall_bias_level': overall_bias.value,
                'num_fairness_violations': len([r for r in fairness_results if r.bias_level != BiasLevel.NONE]),
                'requires_mitigation': requires_mitigation,
                'timestamp': result.timestamp.isoformat()
            })
            
            # Send alerts if necessary
            if overall_bias in [BiasLevel.HIGH, BiasLevel.CRITICAL]:
                await self.alerting.send_alert(
                    "high_bias_detected",
                    f"High bias level detected: {overall_bias.value}",
                    severity="high" if overall_bias == BiasLevel.HIGH else "critical"
                )
            
            self.bias_detection_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Fairlearn bias detection failed: {e}")
            return await self.detect_bias_fallback(y_true, y_pred, sensitive_features)

    async def detect_bias_fallback(self, 
                                  y_true: np.ndarray,
                                  y_pred: np.ndarray, 
                                  sensitive_features: pd.DataFrame) -> BiasDetectionResult:
        """
        Fallback bias detection when Fairlearn is unavailable
        """
        try:
            # Simple bias detection using statistical measures
            fairness_results = []
            
            for attr in sensitive_features.columns:
                groups = sensitive_features[attr].unique()
                group_metrics = {}
                
                for group in groups:
                    mask = sensitive_features[attr] == group
                    if np.sum(mask) > 0:
                        group_accuracy = np.mean(y_true[mask] == y_pred[mask])
                        group_positive_rate = np.mean(y_pred[mask])
                        group_metrics[group] = {
                            'accuracy': group_accuracy,
                            'positive_rate': group_positive_rate
                        }
                
                # Calculate differences between groups
                if len(group_metrics) >= 2:
                    accuracies = [metrics['accuracy'] for metrics in group_metrics.values()]
                    positive_rates = [metrics['positive_rate'] for metrics in group_metrics.values()]
                    
                    accuracy_diff = max(accuracies) - min(accuracies)
                    positive_rate_diff = max(positive_rates) - min(positive_rates)
                    
                    # Use positive rate difference as proxy for demographic parity
                    bias_level = self._calculate_bias_level(FairnessMetric.DEMOGRAPHIC_PARITY, positive_rate_diff)
                    
                    fairness_results.append(FairnessResult(
                        metric=FairnessMetric.DEMOGRAPHIC_PARITY,
                        value=positive_rate_diff,
                        bias_level=bias_level,
                        affected_groups=list(groups),
                        recommendation=self._get_recommendation(FairnessMetric.DEMOGRAPHIC_PARITY, bias_level),
                        timestamp=datetime.utcnow(),
                        confidence=0.8  # Lower confidence for fallback
                    ))
            
            # Determine overall bias level
            bias_levels = [result.bias_level for result in fairness_results]
            overall_bias = max(bias_levels, key=lambda x: x.value) if bias_levels else BiasLevel.NONE
            
            return BiasDetectionResult(
                overall_bias_level=overall_bias,
                fairness_results=fairness_results,
                summary_metrics={'fallback_detection': True},
                recommendations=["Consider installing Fairlearn for comprehensive bias detection"],
                requires_mitigation=overall_bias in [BiasLevel.MEDIUM, BiasLevel.HIGH],
                affected_protected_attributes=list(sensitive_features.columns),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Fallback bias detection failed: {e}")
            return BiasDetectionResult(
                overall_bias_level=BiasLevel.NONE,
                fairness_results=[],
                summary_metrics={'error': str(e)},
                recommendations=["Bias detection failed - manual review required"],
                requires_mitigation=True,  # Conservative approach
                affected_protected_attributes=[],
                timestamp=datetime.utcnow()
            )

    def _identify_affected_groups(self, sensitive_features: pd.DataFrame, metric_value: float) -> List[str]:
        """Identify which groups are most affected by bias"""
        # This is a simplified implementation - in production you'd do per-group analysis
        if abs(metric_value) > 0.1:
            return list(sensitive_features.columns)
        return []

    def _get_recommendation(self, metric: FairnessMetric, bias_level: BiasLevel) -> str:
        """Get recommendation based on metric and bias level"""
        recommendations = {
            (FairnessMetric.DEMOGRAPHIC_PARITY, BiasLevel.NONE): "No action required",
            (FairnessMetric.DEMOGRAPHIC_PARITY, BiasLevel.LOW): "Monitor demographic parity metrics",
            (FairnessMetric.DEMOGRAPHIC_PARITY, BiasLevel.MEDIUM): "Apply demographic parity constraints",
            (FairnessMetric.DEMOGRAPHIC_PARITY, BiasLevel.HIGH): "Implement threshold optimization",
            (FairnessMetric.EQUALIZED_ODDS, BiasLevel.MEDIUM): "Apply equalized odds constraints",
            (FairnessMetric.EQUALIZED_ODDS, BiasLevel.HIGH): "Retrain with fairness constraints"
        }
        
        return recommendations.get((metric, bias_level), "Review model for potential bias")

    def _calculate_overall_bias_score(self, fairness_results: List[FairnessResult]) -> float:
        """Calculate an overall bias score from individual fairness results"""
        if not fairness_results:
            return 0.0
        
        # Weight different bias levels
        weights = {BiasLevel.NONE: 0, BiasLevel.LOW: 1, BiasLevel.MEDIUM: 2, BiasLevel.HIGH: 3, BiasLevel.CRITICAL: 4}
        total_weight = sum(weights[result.bias_level] for result in fairness_results)
        
        return total_weight / len(fairness_results)

    async def monitor_bias_drift(self, 
                                current_results: BiasDetectionResult,
                                baseline_results: Optional[BiasDetectionResult] = None) -> Dict[str, Any]:
        """
        Monitor bias drift over time
        
        Args:
            current_results: Current bias detection results
            baseline_results: Baseline results for comparison
            
        Returns:
            Bias drift analysis
        """
        if baseline_results is None and len(self.bias_detection_history) > 1:
            baseline_results = self.bias_detection_history[-2]  # Use previous result
        
        if baseline_results is None:
            return {'drift_detected': False, 'message': 'No baseline available for comparison'}
        
        # Compare overall bias levels
        current_level = current_results.overall_bias_level
        baseline_level = baseline_results.overall_bias_level
        
        level_values = {BiasLevel.NONE: 0, BiasLevel.LOW: 1, BiasLevel.MEDIUM: 2, BiasLevel.HIGH: 3, BiasLevel.CRITICAL: 4}
        level_change = level_values[current_level] - level_values[baseline_level]
        
        # Check for significant metric changes
        metric_drifts = []
        for current_result in current_results.fairness_results:
            baseline_result = next(
                (r for r in baseline_results.fairness_results if r.metric == current_result.metric),
                None
            )
            if baseline_result:
                metric_drift = abs(current_result.value - baseline_result.value)
                if metric_drift > 0.05:  # 5% drift threshold
                    metric_drifts.append({
                        'metric': current_result.metric.value,
                        'drift': metric_drift,
                        'current_value': current_result.value,
                        'baseline_value': baseline_result.value
                    })
        
        drift_detected = level_change > 0 or len(metric_drifts) > 0
        
        # Send alert if significant drift detected
        if drift_detected and (level_change >= 2 or len(metric_drifts) >= 2):
            await self.alerting.send_alert(
                "significant_bias_drift",
                f"Bias level changed from {baseline_level.value} to {current_level.value}",
                severity="medium"
            )
        
        return {
            'drift_detected': drift_detected,
            'level_change': level_change,
            'metric_drifts': metric_drifts,
            'current_bias_level': current_level.value,
            'baseline_bias_level': baseline_level.value,
            'timestamp': datetime.utcnow().isoformat()
        }

class FairnessMitigator:
    """
    Bias mitigation using Microsoft Fairlearn constraints and post-processing
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.audit_logger = AuditLogger()
        
    async def apply_fairness_constraints(self,
                                       model,
                                       X_train: np.ndarray,
                                       y_train: np.ndarray,
                                       sensitive_features: pd.DataFrame,
                                       constraint_type: str = "demographic_parity") -> Any:
        """
        Apply fairness constraints during training using Fairlearn
        
        Args:
            model: Base ML model
            X_train: Training features
            y_train: Training labels
            sensitive_features: Protected attributes
            constraint_type: Type of fairness constraint
            
        Returns:
            Fair model with applied constraints
        """
        if not FAIRLEARN_AVAILABLE:
            logger.warning("Fairlearn not available, returning original model")
            return model
        
        try:
            # Choose constraint based on type
            if constraint_type == "demographic_parity":
                constraint = DemographicParity()
            elif constraint_type == "equalized_odds":
                constraint = EqualizedOdds()
            elif constraint_type == "true_positive_rate_parity":
                constraint = TruePositiveRateParity()
            elif constraint_type == "false_positive_rate_parity":
                constraint = FalsePositiveRateParity()
            else:
                constraint = DemographicParity()  # Default
            
            # Apply constraint using ExponentiatedGradient
            mitigator = ExponentiatedGradient(model, constraint)
            mitigator.fit(X_train, y_train, sensitive_features=sensitive_features)
            
            # Log mitigation applied
            await self.audit_logger.log_bias_mitigation({
                'constraint_type': constraint_type,
                'method': 'exponentiated_gradient',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return mitigator
            
        except Exception as e:
            logger.error(f"Fairness constraint application failed: {e}")
            return model

    async def apply_post_processing(self,
                                   model,
                                   X_val: np.ndarray,
                                   y_val: np.ndarray,
                                   sensitive_features: pd.DataFrame,
                                   constraint_type: str = "demographic_parity") -> Any:
        """
        Apply post-processing bias mitigation using threshold optimization
        
        Args:
            model: Trained model
            X_val: Validation features
            y_val: Validation labels
            sensitive_features: Protected attributes
            constraint_type: Type of fairness constraint
            
        Returns:
            Post-processed fair model
        """
        if not FAIRLEARN_AVAILABLE:
            logger.warning("Fairlearn not available, returning original model")
            return model
        
        try:
            # Choose constraint
            if constraint_type == "demographic_parity":
                constraint = "demographic_parity"
            elif constraint_type == "equalized_odds":
                constraint = "equalized_odds"
            else:
                constraint = "demographic_parity"  # Default
            
            # Apply threshold optimization
            postprocessor = ThresholdOptimizer(
                estimator=model,
                constraints=constraint,
                prefit=True
            )
            
            postprocessor.fit(X_val, y_val, sensitive_features=sensitive_features)
            
            # Log post-processing applied
            await self.audit_logger.log_bias_mitigation({
                'constraint_type': constraint_type,
                'method': 'threshold_optimization',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return postprocessor
            
        except Exception as e:
            logger.error(f"Post-processing bias mitigation failed: {e}")
            return model

# Example usage
async def example_usage():
    """Example of how to use the Fairlearn integration"""
    # Initialize detector
    detector = FairlearnBiasDetector()
    
    # Sample data (in production, this would be your actual model data)
    y_true = np.random.randint(0, 2, 1000)
    y_pred = np.random.randint(0, 2, 1000)
    sensitive_features = pd.DataFrame({
        'gender': np.random.choice(['M', 'F'], 1000),
        'race': np.random.choice(['White', 'Black', 'Hispanic', 'Asian'], 1000)
    })
    
    # Detect bias
    bias_result = await detector.detect_bias_fairlearn(y_true, y_pred, sensitive_features)
    
    print(f"Overall bias level: {bias_result.overall_bias_level.value}")
    print(f"Requires mitigation: {bias_result.requires_mitigation}")
    
    # Apply mitigation if needed
    if bias_result.requires_mitigation:
        mitigator = FairnessMitigator()
        # Would apply mitigation to actual model
        print("Bias mitigation would be applied")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())