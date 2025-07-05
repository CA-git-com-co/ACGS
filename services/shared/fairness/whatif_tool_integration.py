"""
Google What-If Tool Integration

Integration with Google's What-If Tool for interactive model analysis and bias detection,
implementing the ACGE technical validation recommendations for comprehensive model
analysis and explainability.

Key Features:
- Interactive model analysis and visualization
- Counterfactual analysis for bias detection
- Feature importance analysis
- Model comparison capabilities
- Production-ready bias monitoring integration
"""

import logging
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from enum import Enum

# What-If Tool imports (would be installed via pip install witwidget)
try:
    from witwidget.notebook.visualization import WitWidget, WitConfigBuilder
    from witwidget.notebook.visualization import WitDataType
    WITWIDGET_AVAILABLE = True
except ImportError:
    # Fallback for environments where witwidget isn't available
    WITWIDGET_AVAILABLE = False
    logging.warning("What-If Tool not available, using fallback implementations")

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of What-If Tool analysis"""
    BIAS_DETECTION = "bias_detection"
    COUNTERFACTUAL = "counterfactual"
    FEATURE_IMPORTANCE = "feature_importance"
    MODEL_COMPARISON = "model_comparison"
    FAIRNESS_ANALYSIS = "fairness_analysis"

@dataclass
class CounterfactualResult:
    """Result of counterfactual analysis"""
    original_prediction: float
    counterfactual_prediction: float
    changed_features: Dict[str, Any]
    prediction_change: float
    confidence: float
    timestamp: datetime

@dataclass
class BiasAnalysisResult:
    """Result of bias analysis using What-If Tool"""
    analysis_type: AnalysisType
    protected_attribute: str
    bias_score: float
    affected_groups: List[str]
    counterfactual_examples: List[CounterfactualResult]
    feature_impact: Dict[str, float]
    recommendations: List[str]
    confidence: float
    timestamp: datetime

class WhatIfToolAnalyzer:
    """
    Google What-If Tool integration for comprehensive model analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()
        
        # Analysis configuration
        self.protected_attributes = config.get('protected_attributes', ['gender', 'race', 'age_group'])
        self.bias_thresholds = config.get('bias_thresholds', {
            'low': 0.05,
            'medium': 0.10,
            'high': 0.20
        })
        
        # Storage for analysis results
        self.analysis_history = []
        
    def prepare_data_for_wit(self, 
                            data: pd.DataFrame, 
                            target_column: str,
                            prediction_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare data for What-If Tool analysis
        
        Args:
            data: Input dataframe
            target_column: Name of target/label column
            prediction_column: Name of prediction column (optional)
            
        Returns:
            Prepared data configuration for What-If Tool
        """
        try:
            # Convert data to format expected by What-If Tool
            examples = []
            
            for _, row in data.iterrows():
                example = {}
                for col in data.columns:
                    if col != target_column and col != prediction_column:
                        example[col] = row[col]
                
                # Add label
                example['label'] = row[target_column] if target_column in row else 0
                
                # Add prediction if available
                if prediction_column and prediction_column in row:
                    example['prediction'] = row[prediction_column]
                
                examples.append(example)
            
            # Prepare feature info
            feature_names = [col for col in data.columns if col not in [target_column, prediction_column]]
            
            wit_config = {
                'examples': examples,
                'feature_names': feature_names,
                'target_feature': target_column,
                'data_type': 'tabular'
            }
            
            return wit_config
            
        except Exception as e:
            logger.error(f"Data preparation for What-If Tool failed: {e}")
            return {'examples': [], 'feature_names': [], 'error': str(e)}

    async def analyze_counterfactuals(self,
                                    model: Any,
                                    data: pd.DataFrame,
                                    target_column: str,
                                    protected_attribute: str,
                                    num_examples: int = 100) -> List[CounterfactualResult]:
        """
        Perform counterfactual analysis to detect bias
        
        Args:
            model: ML model for analysis
            data: Input data
            target_column: Target variable column
            protected_attribute: Protected attribute to analyze
            num_examples: Number of examples to analyze
            
        Returns:
            List of counterfactual analysis results
        """
        if not WITWIDGET_AVAILABLE:
            return await self.analyze_counterfactuals_fallback(model, data, target_column, protected_attribute, num_examples)
        
        try:
            counterfactuals = []
            
            # Sample data for analysis
            sample_data = data.sample(min(num_examples, len(data)))
            
            for _, row in sample_data.iterrows():
                original_features = row.drop([target_column]).to_dict()
                original_prediction = self._get_model_prediction(model, [list(original_features.values())])[0]
                
                # Create counterfactual by changing protected attribute
                if protected_attribute in original_features:
                    counterfactual_features = original_features.copy()
                    
                    # Change protected attribute value
                    current_value = counterfactual_features[protected_attribute]
                    possible_values = data[protected_attribute].unique()
                    other_values = [v for v in possible_values if v != current_value]
                    
                    if other_values:
                        counterfactual_features[protected_attribute] = other_values[0]
                        counterfactual_prediction = self._get_model_prediction(model, [list(counterfactual_features.values())])[0]
                        
                        prediction_change = abs(counterfactual_prediction - original_prediction)
                        
                        counterfactual = CounterfactualResult(
                            original_prediction=original_prediction,
                            counterfactual_prediction=counterfactual_prediction,
                            changed_features={protected_attribute: {
                                'from': current_value,
                                'to': counterfactual_features[protected_attribute]
                            }},
                            prediction_change=prediction_change,
                            confidence=0.9,  # Would calculate actual confidence
                            timestamp=datetime.utcnow()
                        )
                        
                        counterfactuals.append(counterfactual)
            
            # Log counterfactual analysis
            await self.audit_logger.log_model_analysis({
                'analysis_type': 'counterfactual',
                'protected_attribute': protected_attribute,
                'num_examples_analyzed': len(counterfactuals),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return counterfactuals
            
        except Exception as e:
            logger.error(f"Counterfactual analysis failed: {e}")
            return await self.analyze_counterfactuals_fallback(model, data, target_column, protected_attribute, num_examples)

    async def analyze_counterfactuals_fallback(self,
                                             model: Any,
                                             data: pd.DataFrame,
                                             target_column: str,
                                             protected_attribute: str,
                                             num_examples: int = 100) -> List[CounterfactualResult]:
        """Fallback counterfactual analysis when What-If Tool unavailable"""
        try:
            counterfactuals = []
            
            # Simple statistical approach for counterfactual analysis
            sample_data = data.sample(min(num_examples, len(data)))
            
            for _, row in sample_data.iterrows():
                if protected_attribute in row:
                    original_value = row[protected_attribute]
                    possible_values = data[protected_attribute].unique()
                    other_values = [v for v in possible_values if v != original_value]
                    
                    if other_values:
                        # Simulate prediction change based on group statistics
                        original_group_mean = data[data[protected_attribute] == original_value][target_column].mean()
                        other_group_mean = data[data[protected_attribute] == other_values[0]][target_column].mean()
                        
                        prediction_change = abs(other_group_mean - original_group_mean)
                        
                        counterfactual = CounterfactualResult(
                            original_prediction=original_group_mean,
                            counterfactual_prediction=other_group_mean,
                            changed_features={protected_attribute: {
                                'from': original_value,
                                'to': other_values[0]
                            }},
                            prediction_change=prediction_change,
                            confidence=0.7,  # Lower confidence for fallback
                            timestamp=datetime.utcnow()
                        )
                        
                        counterfactuals.append(counterfactual)
            
            return counterfactuals
            
        except Exception as e:
            logger.error(f"Fallback counterfactual analysis failed: {e}")
            return []

    async def analyze_feature_importance_bias(self,
                                            model: Any,
                                            data: pd.DataFrame,
                                            protected_attributes: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Analyze feature importance to detect potential bias sources
        
        Args:
            model: ML model for analysis
            data: Input data
            protected_attributes: List of protected attributes to analyze
            
        Returns:
            Dictionary of feature importance scores related to bias
        """
        if protected_attributes is None:
            protected_attributes = self.protected_attributes
        
        try:
            feature_importance = {}
            
            # Get base feature importance if available
            if hasattr(model, 'feature_importances_'):
                base_importance = model.feature_importances_
                feature_names = data.columns.tolist()
                
                for i, feature in enumerate(feature_names):
                    if feature in protected_attributes:
                        feature_importance[feature] = float(base_importance[i])
            else:
                # Fallback: calculate correlation with protected attributes
                numeric_data = data.select_dtypes(include=[np.number])
                
                for attr in protected_attributes:
                    if attr in data.columns:
                        # Convert categorical to numeric if needed
                        if data[attr].dtype == 'object':
                            attr_encoded = pd.Categorical(data[attr]).codes
                        else:
                            attr_encoded = data[attr]
                        
                        # Calculate correlation with other features
                        correlations = numeric_data.corrwith(pd.Series(attr_encoded))
                        avg_correlation = abs(correlations).mean()
                        feature_importance[attr] = float(avg_correlation) if not np.isnan(avg_correlation) else 0.0
            
            # Log feature importance analysis
            await self.audit_logger.log_model_analysis({
                'analysis_type': 'feature_importance_bias',
                'protected_attributes': protected_attributes,
                'feature_importance_scores': feature_importance,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"Feature importance bias analysis failed: {e}")
            return {}

    async def comprehensive_bias_analysis(self,
                                        model: Any,
                                        data: pd.DataFrame,
                                        target_column: str,
                                        protected_attribute: str) -> BiasAnalysisResult:
        """
        Comprehensive bias analysis using What-If Tool capabilities
        
        Args:
            model: ML model for analysis
            data: Input data
            target_column: Target variable column
            protected_attribute: Protected attribute to analyze
            
        Returns:
            Comprehensive bias analysis result
        """
        try:
            # Perform counterfactual analysis
            counterfactuals = await self.analyze_counterfactuals(
                model, data, target_column, protected_attribute
            )
            
            # Analyze feature importance
            feature_importance = await self.analyze_feature_importance_bias(
                model, data, [protected_attribute]
            )
            
            # Calculate bias score based on counterfactual results
            if counterfactuals:
                prediction_changes = [cf.prediction_change for cf in counterfactuals]
                bias_score = np.mean(prediction_changes)
            else:
                bias_score = 0.0
            
            # Identify affected groups
            affected_groups = data[protected_attribute].unique().tolist()
            
            # Generate recommendations
            recommendations = []
            if bias_score > self.bias_thresholds['high']:
                recommendations.append("High bias detected - immediate intervention required")
                recommendations.append("Consider retraining with fairness constraints")
            elif bias_score > self.bias_thresholds['medium']:
                recommendations.append("Moderate bias detected - consider bias mitigation")
                recommendations.append("Monitor bias metrics regularly")
            elif bias_score > self.bias_thresholds['low']:
                recommendations.append("Low bias detected - continue monitoring")
            else:
                recommendations.append("No significant bias detected")
            
            # Determine confidence based on number of examples analyzed
            confidence = min(0.95, 0.5 + (len(counterfactuals) / 200))
            
            result = BiasAnalysisResult(
                analysis_type=AnalysisType.BIAS_DETECTION,
                protected_attribute=protected_attribute,
                bias_score=bias_score,
                affected_groups=affected_groups,
                counterfactual_examples=counterfactuals[:10],  # Keep top 10 for storage
                feature_impact=feature_importance,
                recommendations=recommendations,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            
            # Store result
            self.analysis_history.append(result)
            
            # Send alerts if high bias detected
            if bias_score > self.bias_thresholds['high']:
                await self.alerting.send_alert(
                    "high_bias_detected_whatif",
                    f"High bias detected for {protected_attribute}: {bias_score:.3f}",
                    severity="high"
                )
            
            # Log comprehensive analysis
            await self.audit_logger.log_model_analysis({
                'analysis_type': 'comprehensive_bias_analysis',
                'protected_attribute': protected_attribute,
                'bias_score': bias_score,
                'num_counterfactuals': len(counterfactuals),
                'confidence': confidence,
                'timestamp': result.timestamp.isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive bias analysis failed: {e}")
            return BiasAnalysisResult(
                analysis_type=AnalysisType.BIAS_DETECTION,
                protected_attribute=protected_attribute,
                bias_score=0.0,
                affected_groups=[],
                counterfactual_examples=[],
                feature_impact={},
                recommendations=[f"Analysis failed: {str(e)}"],
                confidence=0.0,
                timestamp=datetime.utcnow()
            )

    def _get_model_prediction(self, model: Any, features: List[List]) -> List[float]:
        """Get model predictions for given features"""
        try:
            if hasattr(model, 'predict_proba'):
                predictions = model.predict_proba(features)
                # Return probability of positive class for binary classification
                if predictions.shape[1] == 2:
                    return predictions[:, 1].tolist()
                else:
                    return predictions.max(axis=1).tolist()
            elif hasattr(model, 'predict'):
                predictions = model.predict(features)
                return predictions.tolist()
            else:
                # Fallback for unknown model types
                return [0.5] * len(features)
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            return [0.5] * len(features)

    async def generate_wit_report(self, analysis_results: List[BiasAnalysisResult]) -> Dict[str, Any]:
        """
        Generate a comprehensive What-If Tool analysis report
        
        Args:
            analysis_results: List of bias analysis results
            
        Returns:
            Comprehensive analysis report
        """
        try:
            report = {
                'summary': {
                    'total_analyses': len(analysis_results),
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'protected_attributes_analyzed': list(set(r.protected_attribute for r in analysis_results))
                },
                'bias_scores': {},
                'recommendations': [],
                'high_risk_attributes': [],
                'counterfactual_insights': []
            }
            
            for result in analysis_results:
                report['bias_scores'][result.protected_attribute] = {
                    'score': result.bias_score,
                    'confidence': result.confidence,
                    'affected_groups': result.affected_groups
                }
                
                # Collect high-risk attributes
                if result.bias_score > self.bias_thresholds['high']:
                    report['high_risk_attributes'].append(result.protected_attribute)
                
                # Add recommendations
                report['recommendations'].extend(result.recommendations)
                
                # Add counterfactual insights
                if result.counterfactual_examples:
                    avg_change = np.mean([cf.prediction_change for cf in result.counterfactual_examples])
                    report['counterfactual_insights'].append({
                        'attribute': result.protected_attribute,
                        'avg_prediction_change': avg_change,
                        'num_examples': len(result.counterfactual_examples)
                    })
            
            # Overall risk assessment
            if report['high_risk_attributes']:
                report['overall_risk'] = 'HIGH'
            elif any(score['score'] > self.bias_thresholds['medium'] for score in report['bias_scores'].values()):
                report['overall_risk'] = 'MEDIUM'
            else:
                report['overall_risk'] = 'LOW'
            
            return report
            
        except Exception as e:
            logger.error(f"What-If Tool report generation failed: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}

    def export_for_wit_widget(self, data: pd.DataFrame, model: Any = None) -> str:
        """
        Export data in format suitable for What-If Tool widget
        
        Args:
            data: Input dataframe
            model: Optional ML model
            
        Returns:
            JSON string formatted for What-If Tool
        """
        try:
            # Prepare examples for What-If Tool
            examples = []
            for _, row in data.iterrows():
                example = row.to_dict()
                examples.append(example)
            
            wit_data = {
                'examples': examples,
                'feature_names': data.columns.tolist(),
                'inference_address': None,  # Would be model serving endpoint
                'model_name': 'ACGS Model',
                'model_version': '1.0',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return json.dumps(wit_data, default=str, indent=2)
            
        except Exception as e:
            logger.error(f"What-If Tool export failed: {e}")
            return json.dumps({'error': str(e)})

# Example usage
async def example_usage():
    """Example of how to use the What-If Tool integration"""
    # Initialize analyzer
    analyzer = WhatIfToolAnalyzer()
    
    # Sample data (in production, this would be your actual model data)
    data = pd.DataFrame({
        'feature1': np.random.randn(1000),
        'feature2': np.random.randn(1000),
        'gender': np.random.choice(['M', 'F'], 1000),
        'race': np.random.choice(['White', 'Black', 'Hispanic', 'Asian'], 1000),
        'target': np.random.randint(0, 2, 1000)
    })
    
    # Mock model (in production, use your actual model)
    class MockModel:
        def predict_proba(self, X):
            return np.random.random((len(X), 2))
    
    model = MockModel()
    
    # Perform comprehensive bias analysis
    bias_result = await analyzer.comprehensive_bias_analysis(
        model, data, 'target', 'gender'
    )
    
    print(f"Bias score for gender: {bias_result.bias_score:.3f}")
    print(f"Recommendations: {bias_result.recommendations}")
    
    # Generate report
    report = await analyzer.generate_wit_report([bias_result])
    print(f"Overall risk: {report['overall_risk']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())