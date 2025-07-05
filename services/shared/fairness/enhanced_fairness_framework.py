"""
Enhanced Fairness Framework

Comprehensive fairness and bias detection framework combining Microsoft Fairlearn
and Google What-If Tool, implementing the ACGE technical validation recommendations
for industry-standard fairness evaluation.

Key Features:
- Multi-algorithm fairness evaluation
- Real-time bias monitoring and alerting
- Comprehensive bias mitigation strategies
- Integration with existing ACGS audit and monitoring systems
- Production-ready bias drift detection
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .fairlearn_integration import FairlearnBiasDetector, FairnessMitigator, BiasDetectionResult, BiasLevel
from .whatif_tool_integration import WhatIfToolAnalyzer, BiasAnalysisResult, AnalysisType
from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)

class FairnessFrameworkMode(Enum):
    """Framework operation modes"""
    FAIRLEARN_ONLY = "fairlearn_only"
    WHATIF_ONLY = "whatif_only"
    COMBINED = "combined"
    ADAPTIVE = "adaptive"

@dataclass
class ComprehensiveFairnessResult:
    """Combined result from multiple fairness evaluation methods"""
    overall_bias_level: BiasLevel
    fairlearn_result: Optional[BiasDetectionResult]
    whatif_result: Optional[BiasAnalysisResult]
    combined_score: float
    consensus_recommendations: List[str]
    requires_immediate_action: bool
    affected_attributes: List[str]
    confidence: float
    timestamp: datetime

@dataclass
class FairnessDriftResult:
    """Result of fairness drift analysis"""
    drift_detected: bool
    drift_magnitude: float
    affected_metrics: List[str]
    trend_direction: str  # "improving", "degrading", "stable"
    time_period_days: int
    recommendations: List[str]
    timestamp: datetime

class EnhancedFairnessFramework:
    """
    Comprehensive fairness framework combining multiple state-of-the-art tools
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize component detectors
        self.fairlearn_detector = FairlearnBiasDetector(config)
        self.fairness_mitigator = FairnessMitigator(config)
        self.whatif_analyzer = WhatIfToolAnalyzer(config)
        
        # Framework configuration
        self.mode = FairnessFrameworkMode(config.get('mode', 'combined'))
        self.protected_attributes = config.get('protected_attributes', ['race', 'gender', 'age_group', 'disability_status'])
        self.bias_thresholds = config.get('bias_thresholds', {
            'low': 0.05,
            'medium': 0.10,
            'high': 0.20,
            'critical': 0.30
        })
        
        # Monitoring and alerting
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()
        
        # Historical data for drift detection
        self.fairness_history = []
        self.drift_detection_window = config.get('drift_window_days', 7)
        
        # Performance metrics
        self.evaluation_metrics = {
            'total_evaluations': 0,
            'high_bias_detections': 0,
            'mitigations_applied': 0,
            'avg_evaluation_time': 0.0
        }

    async def evaluate_comprehensive_fairness(self,
                                            model: Any,
                                            data: pd.DataFrame,
                                            target_column: str,
                                            predictions: Optional[np.ndarray] = None) -> ComprehensiveFairnessResult:
        """
        Comprehensive fairness evaluation using multiple methodologies
        
        Args:
            model: ML model to evaluate
            data: Dataset including features and labels
            target_column: Name of target variable column
            predictions: Optional pre-computed predictions
            
        Returns:
            Comprehensive fairness evaluation result
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate predictions if not provided
            if predictions is None:
                if hasattr(model, 'predict'):
                    predictions = model.predict(data.drop(columns=[target_column]))
                else:
                    raise ValueError("No predictions provided and model doesn't have predict method")
            
            fairlearn_result = None
            whatif_result = None
            
            # Prepare sensitive features for Fairlearn
            sensitive_features = data[self.protected_attributes].copy()
            y_true = data[target_column].values
            
            # Run evaluations based on mode
            if self.mode in [FairnessFrameworkMode.FAIRLEARN_ONLY, FairnessFrameworkMode.COMBINED, FairnessFrameworkMode.ADAPTIVE]:
                try:
                    fairlearn_result = await self.fairlearn_detector.detect_bias_fairlearn(
                        y_true, predictions, sensitive_features
                    )
                except Exception as e:
                    logger.warning(f"Fairlearn evaluation failed: {e}")
                    
            if self.mode in [FairnessFrameworkMode.WHATIF_ONLY, FairnessFrameworkMode.COMBINED, FairnessFrameworkMode.ADAPTIVE]:
                try:
                    # Run What-If Tool analysis for primary protected attribute
                    primary_attribute = self.protected_attributes[0] if self.protected_attributes else 'gender'
                    whatif_result = await self.whatif_analyzer.comprehensive_bias_analysis(
                        model, data, target_column, primary_attribute
                    )
                except Exception as e:
                    logger.warning(f"What-If Tool evaluation failed: {e}")
            
            # Combine results
            combined_result = await self._combine_fairness_results(fairlearn_result, whatif_result)
            
            # Update metrics
            evaluation_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_evaluation_metrics(evaluation_time, combined_result.overall_bias_level)
            
            # Store in history for drift detection
            self.fairness_history.append(combined_result)
            
            # Keep only recent history
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            self.fairness_history = [
                r for r in self.fairness_history 
                if r.timestamp > cutoff_date
            ]
            
            # Log evaluation
            await self.audit_logger.log_fairness_evaluation({
                'overall_bias_level': combined_result.overall_bias_level.value,
                'combined_score': combined_result.combined_score,
                'requires_immediate_action': combined_result.requires_immediate_action,
                'evaluation_time_seconds': evaluation_time,
                'timestamp': combined_result.timestamp.isoformat()
            })
            
            # Send alerts if necessary
            if combined_result.overall_bias_level in [BiasLevel.HIGH, BiasLevel.CRITICAL]:
                await self.alerting.send_alert(
                    "high_bias_comprehensive",
                    f"High bias detected: {combined_result.overall_bias_level.value}, Score: {combined_result.combined_score:.3f}",
                    severity="high" if combined_result.overall_bias_level == BiasLevel.HIGH else "critical"
                )
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Comprehensive fairness evaluation failed: {e}")
            return ComprehensiveFairnessResult(
                overall_bias_level=BiasLevel.CRITICAL,
                fairlearn_result=None,
                whatif_result=None,
                combined_score=1.0,
                consensus_recommendations=[f"Evaluation failed: {str(e)}"],
                requires_immediate_action=True,
                affected_attributes=self.protected_attributes,
                confidence=0.0,
                timestamp=datetime.utcnow()
            )

    async def _combine_fairness_results(self,
                                      fairlearn_result: Optional[BiasDetectionResult],
                                      whatif_result: Optional[BiasAnalysisResult]) -> ComprehensiveFairnessResult:
        """
        Combine results from multiple fairness evaluation methods
        """
        try:
            # Determine overall bias level
            bias_levels = []
            if fairlearn_result:
                bias_levels.append(fairlearn_result.overall_bias_level)
            if whatif_result:
                # Convert What-If Tool bias score to bias level
                whatif_bias_level = self._score_to_bias_level(whatif_result.bias_score)
                bias_levels.append(whatif_bias_level)
            
            # Take the maximum bias level (most conservative)
            overall_bias_level = max(bias_levels, key=lambda x: x.value) if bias_levels else BiasLevel.NONE
            
            # Calculate combined score
            scores = []
            if fairlearn_result:
                scores.append(fairlearn_result.summary_metrics.get('overall_bias_score', 0.0))
            if whatif_result:
                scores.append(whatif_result.bias_score)
            
            combined_score = max(scores) if scores else 0.0
            
            # Combine recommendations
            recommendations = []
            if fairlearn_result:
                recommendations.extend(fairlearn_result.recommendations)
            if whatif_result:
                recommendations.extend(whatif_result.recommendations)
            
            # Remove duplicates and prioritize
            consensus_recommendations = list(set(recommendations))
            
            # Determine if immediate action is required
            requires_immediate_action = (
                overall_bias_level in [BiasLevel.HIGH, BiasLevel.CRITICAL] or
                combined_score > self.bias_thresholds['high']
            )
            
            # Identify affected attributes
            affected_attributes = []
            if fairlearn_result:
                affected_attributes.extend(fairlearn_result.affected_protected_attributes)
            if whatif_result:
                affected_attributes.append(whatif_result.protected_attribute)
            
            affected_attributes = list(set(affected_attributes))
            
            # Calculate confidence based on availability of both methods
            confidence = 0.8
            if fairlearn_result and whatif_result:
                confidence = 0.95
            elif fairlearn_result or whatif_result:
                confidence = 0.85
            else:
                confidence = 0.5
            
            return ComprehensiveFairnessResult(
                overall_bias_level=overall_bias_level,
                fairlearn_result=fairlearn_result,
                whatif_result=whatif_result,
                combined_score=combined_score,
                consensus_recommendations=consensus_recommendations,
                requires_immediate_action=requires_immediate_action,
                affected_attributes=affected_attributes,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Result combination failed: {e}")
            return ComprehensiveFairnessResult(
                overall_bias_level=BiasLevel.CRITICAL,
                fairlearn_result=fairlearn_result,
                whatif_result=whatif_result,
                combined_score=1.0,
                consensus_recommendations=["Result combination failed - manual review required"],
                requires_immediate_action=True,
                affected_attributes=self.protected_attributes,
                confidence=0.0,
                timestamp=datetime.utcnow()
            )

    def _score_to_bias_level(self, score: float) -> BiasLevel:
        """Convert numeric bias score to bias level"""
        if score >= self.bias_thresholds['critical']:
            return BiasLevel.CRITICAL
        elif score >= self.bias_thresholds['high']:
            return BiasLevel.HIGH
        elif score >= self.bias_thresholds['medium']:
            return BiasLevel.MEDIUM
        elif score >= self.bias_thresholds['low']:
            return BiasLevel.LOW
        else:
            return BiasLevel.NONE

    async def detect_fairness_drift(self, lookback_days: Optional[int] = None) -> FairnessDriftResult:
        """
        Detect drift in fairness metrics over time
        
        Args:
            lookback_days: Number of days to look back for drift detection
            
        Returns:
            Fairness drift analysis result
        """
        if lookback_days is None:
            lookback_days = self.drift_detection_window
        
        try:
            # Filter history to lookback period
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            recent_history = [
                r for r in self.fairness_history 
                if r.timestamp > cutoff_date
            ]
            
            if len(recent_history) < 2:
                return FairnessDriftResult(
                    drift_detected=False,
                    drift_magnitude=0.0,
                    affected_metrics=[],
                    trend_direction="stable",
                    time_period_days=lookback_days,
                    recommendations=["Insufficient data for drift detection"],
                    timestamp=datetime.utcnow()
                )
            
            # Sort by timestamp
            recent_history.sort(key=lambda x: x.timestamp)
            
            # Analyze trend in combined scores
            scores = [r.combined_score for r in recent_history]
            bias_levels = [r.overall_bias_level.value for r in recent_history]
            
            # Calculate drift metrics
            score_drift = abs(scores[-1] - scores[0])
            bias_level_drift = abs(bias_levels[-1] - bias_levels[0])
            
            # Determine trend direction
            if scores[-1] > scores[0] + 0.05:
                trend_direction = "degrading"
            elif scores[-1] < scores[0] - 0.05:
                trend_direction = "improving"
            else:
                trend_direction = "stable"
            
            # Detect drift
            drift_threshold = 0.1  # 10% change threshold
            drift_detected = score_drift > drift_threshold or bias_level_drift > 1
            
            # Identify affected metrics
            affected_metrics = []
            if score_drift > drift_threshold:
                affected_metrics.append("combined_bias_score")
            if bias_level_drift > 1:
                affected_metrics.append("bias_level")
            
            # Generate recommendations
            recommendations = []
            if drift_detected:
                if trend_direction == "degrading":
                    recommendations.extend([
                        "Bias metrics are degrading over time",
                        "Investigate recent model changes or data shifts",
                        "Consider implementing bias mitigation strategies"
                    ])
                elif trend_direction == "improving":
                    recommendations.extend([
                        "Bias metrics are improving",
                        "Continue current fairness practices",
                        "Monitor to ensure continued improvement"
                    ])
            else:
                recommendations.append("No significant fairness drift detected")
            
            # Calculate overall drift magnitude
            drift_magnitude = max(score_drift, bias_level_drift / 4.0)  # Normalize bias level change
            
            result = FairnessDriftResult(
                drift_detected=drift_detected,
                drift_magnitude=drift_magnitude,
                affected_metrics=affected_metrics,
                trend_direction=trend_direction,
                time_period_days=lookback_days,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
            # Send alert for significant drift
            if drift_detected and drift_magnitude > 0.2:
                await self.alerting.send_alert(
                    "significant_fairness_drift",
                    f"Significant fairness drift detected: {drift_magnitude:.3f} over {lookback_days} days",
                    severity="medium"
                )
            
            # Log drift analysis
            await self.audit_logger.log_fairness_drift({
                'drift_detected': drift_detected,
                'drift_magnitude': drift_magnitude,
                'trend_direction': trend_direction,
                'time_period_days': lookback_days,
                'timestamp': result.timestamp.isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Fairness drift detection failed: {e}")
            return FairnessDriftResult(
                drift_detected=True,  # Conservative: assume drift when detection fails
                drift_magnitude=1.0,
                affected_metrics=["detection_failure"],
                trend_direction="unknown",
                time_period_days=lookback_days,
                recommendations=[f"Drift detection failed: {str(e)}"],
                timestamp=datetime.utcnow()
            )

    async def apply_bias_mitigation(self,
                                  model: Any,
                                  X_train: np.ndarray,
                                  y_train: np.ndarray,
                                  sensitive_features: pd.DataFrame,
                                  mitigation_strategy: str = "auto") -> Any:
        """
        Apply bias mitigation strategies based on detected bias
        
        Args:
            model: Original model
            X_train: Training features
            y_train: Training labels
            sensitive_features: Protected attributes
            mitigation_strategy: Strategy to use ("auto", "constraints", "postprocessing")
            
        Returns:
            Mitigated model
        """
        try:
            # Determine mitigation strategy automatically if needed
            if mitigation_strategy == "auto":
                # Use recent fairness evaluation to determine strategy
                recent_results = self.fairness_history[-1] if self.fairness_history else None
                
                if recent_results and recent_results.overall_bias_level in [BiasLevel.HIGH, BiasLevel.CRITICAL]:
                    mitigation_strategy = "constraints"
                elif recent_results and recent_results.overall_bias_level == BiasLevel.MEDIUM:
                    mitigation_strategy = "postprocessing"
                else:
                    mitigation_strategy = "constraints"  # Default
            
            # Apply mitigation
            if mitigation_strategy == "constraints":
                mitigated_model = await self.fairness_mitigator.apply_fairness_constraints(
                    model, X_train, y_train, sensitive_features, "demographic_parity"
                )
            elif mitigation_strategy == "postprocessing":
                mitigated_model = await self.fairness_mitigator.apply_post_processing(
                    model, X_train, y_train, sensitive_features, "demographic_parity"
                )
            else:
                logger.warning(f"Unknown mitigation strategy: {mitigation_strategy}")
                mitigated_model = model
            
            # Update metrics
            self.evaluation_metrics['mitigations_applied'] += 1
            
            # Log mitigation
            await self.audit_logger.log_bias_mitigation({
                'strategy': mitigation_strategy,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return mitigated_model
            
        except Exception as e:
            logger.error(f"Bias mitigation failed: {e}")
            return model

    def _update_evaluation_metrics(self, evaluation_time: float, bias_level: BiasLevel):
        """Update framework performance metrics"""
        self.evaluation_metrics['total_evaluations'] += 1
        
        if bias_level in [BiasLevel.HIGH, BiasLevel.CRITICAL]:
            self.evaluation_metrics['high_bias_detections'] += 1
        
        # Update rolling average evaluation time
        current_avg = self.evaluation_metrics['avg_evaluation_time']
        total_evals = self.evaluation_metrics['total_evaluations']
        self.evaluation_metrics['avg_evaluation_time'] = (
            (current_avg * (total_evals - 1) + evaluation_time) / total_evals
        )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get framework performance summary"""
        high_bias_rate = (
            self.evaluation_metrics['high_bias_detections'] / 
            max(1, self.evaluation_metrics['total_evaluations'])
        )
        
        return {
            'total_evaluations': self.evaluation_metrics['total_evaluations'],
            'high_bias_detection_rate': high_bias_rate,
            'mitigations_applied': self.evaluation_metrics['mitigations_applied'],
            'avg_evaluation_time_seconds': self.evaluation_metrics['avg_evaluation_time'],
            'framework_mode': self.mode.value,
            'protected_attributes': self.protected_attributes,
            'recent_evaluations': len(self.fairness_history)
        }

    async def generate_fairness_report(self, period_days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive fairness report
        
        Args:
            period_days: Report period in days
            
        Returns:
            Comprehensive fairness report
        """
        try:
            # Get recent evaluations
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            recent_evaluations = [
                r for r in self.fairness_history 
                if r.timestamp > cutoff_date
            ]
            
            # Detect drift
            drift_result = await self.detect_fairness_drift(period_days)
            
            # Calculate summary statistics
            if recent_evaluations:
                bias_levels = [r.overall_bias_level for r in recent_evaluations]
                combined_scores = [r.combined_score for r in recent_evaluations]
                
                bias_level_counts = {level: bias_levels.count(level) for level in BiasLevel}
                avg_bias_score = np.mean(combined_scores)
                max_bias_score = np.max(combined_scores)
                
                # Identify trends
                if len(combined_scores) >= 2:
                    trend = "improving" if combined_scores[-1] < combined_scores[0] else "degrading"
                else:
                    trend = "stable"
            else:
                bias_level_counts = {level: 0 for level in BiasLevel}
                avg_bias_score = 0.0
                max_bias_score = 0.0
                trend = "no_data"
            
            report = {
                'report_period': {
                    'start_date': cutoff_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat(),
                    'period_days': period_days
                },
                'summary': {
                    'total_evaluations': len(recent_evaluations),
                    'avg_bias_score': avg_bias_score,
                    'max_bias_score': max_bias_score,
                    'trend': trend,
                    'bias_level_distribution': {level.value: count for level, count in bias_level_counts.items()}
                },
                'drift_analysis': {
                    'drift_detected': drift_result.drift_detected,
                    'drift_magnitude': drift_result.drift_magnitude,
                    'trend_direction': drift_result.trend_direction,
                    'affected_metrics': drift_result.affected_metrics
                },
                'recommendations': drift_result.recommendations,
                'performance_metrics': self.get_performance_summary(),
                'protected_attributes_status': {
                    attr: self._get_attribute_status(attr, recent_evaluations)
                    for attr in self.protected_attributes
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Fairness report generation failed: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }

    def _get_attribute_status(self, attribute: str, evaluations: List[ComprehensiveFairnessResult]) -> Dict[str, Any]:
        """Get status for a specific protected attribute"""
        affected_count = sum(1 for eval_result in evaluations if attribute in eval_result.affected_attributes)
        
        return {
            'times_affected': affected_count,
            'affect_rate': affected_count / max(1, len(evaluations)),
            'status': 'high_risk' if affected_count / max(1, len(evaluations)) > 0.5 else 'normal'
        }

# Example usage and factory function
async def create_enhanced_fairness_framework(config: Optional[Dict[str, Any]] = None) -> EnhancedFairnessFramework:
    """
    Factory function to create and initialize the enhanced fairness framework
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized EnhancedFairnessFramework
    """
    framework = EnhancedFairnessFramework(config)
    
    logger.info(f"Enhanced Fairness Framework initialized with mode: {framework.mode}")
    logger.info(f"Protected attributes: {framework.protected_attributes}")
    
    return framework

# Default configuration
DEFAULT_FAIRNESS_CONFIG = {
    'mode': 'combined',
    'protected_attributes': ['race', 'gender', 'age_group', 'disability_status'],
    'bias_thresholds': {
        'low': 0.05,
        'medium': 0.10,
        'high': 0.20,
        'critical': 0.30
    },
    'drift_window_days': 7
}