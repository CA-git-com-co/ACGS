"""
Causal Bias Detector Service
Constitutional Hash: cdd01ef066bc6cf2

Advanced bias detection service implementing CARMA methodology for identifying
causal vs spurious correlations in AI decision-making. Provides robust bias
detection resistant to superficial formatting and spurious attributes.
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union, Tuple
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from .constitutional_safety_framework import ConstitutionalSafetyValidator
from .blackboard import BlackboardService, KnowledgeItem
from .ai_model_service import AIModelService
from .constitutional_counterfactual_generator import ConstitutionalCounterfactualGenerator

# Configure logging
logger = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of bias that can be detected"""
    DEMOGRAPHIC = "demographic"
    ALGORITHMIC = "algorithmic"
    SELECTION = "selection"
    CONFIRMATION = "confirmation"
    REPRESENTATION = "representation"
    HISTORICAL = "historical"
    MEASUREMENT = "measurement"
    EVALUATION = "evaluation"

class CausalBiasAttribute(Enum):
    """Causal attributes that should legitimately influence decisions"""
    QUALIFICATIONS = "qualifications"
    PERFORMANCE_METRICS = "performance_metrics"
    RELEVANT_EXPERIENCE = "relevant_experience"
    OBJECTIVE_CRITERIA = "objective_criteria"
    MERIT_BASED_FACTORS = "merit_based_factors"
    DOMAIN_EXPERTISE = "domain_expertise"
    FACTUAL_ACCURACY = "factual_accuracy"
    LOGICAL_CONSISTENCY = "logical_consistency"

class SpuriousBiasAttribute(Enum):
    """Spurious attributes that should NOT influence decisions"""
    GENDER = "gender"
    RACE_ETHNICITY = "race_ethnicity"
    AGE = "age"
    RELIGION = "religion"
    SEXUAL_ORIENTATION = "sexual_orientation"
    NATIONALITY = "nationality"
    SOCIOECONOMIC_STATUS = "socioeconomic_status"
    PHYSICAL_APPEARANCE = "physical_appearance"
    NAME_ETHNICITY = "name_ethnicity"
    ACCENT_DIALECT = "accent_dialect"
    GEOGRAPHIC_LOCATION = "geographic_location"
    EDUCATIONAL_INSTITUTION_PRESTIGE = "educational_institution_prestige"

@dataclass
class BiasTestResult:
    """Result of a single bias test"""
    test_id: str
    bias_type: BiasType
    attribute_tested: Union[CausalBiasAttribute, SpuriousBiasAttribute]
    test_type: str  # "causal_sensitivity" or "spurious_invariance"
    
    # Test outcomes
    baseline_decision: Any
    intervention_decision: Any
    expected_change: bool
    actual_change: bool
    
    # Scores
    bias_score: float = Field(ge=0.0, le=1.0)  # Higher = more biased
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Metadata
    constitutional_hash: str = "cdd01ef066bc6cf2"
    test_scenarios: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CausalBiasAnalysisResult(BaseModel):
    """Comprehensive causal bias analysis result"""
    analysis_id: str
    constitutional_hash: str = "cdd01ef066bc6cf2"
    
    # Overall metrics
    overall_bias_score: float = Field(ge=0.0, le=1.0)
    causal_sensitivity_score: float = Field(ge=0.0, le=1.0)
    spurious_invariance_score: float = Field(ge=0.0, le=1.0)
    robustness_score: float = Field(ge=0.0, le=1.0)
    
    # Detailed results
    bias_test_results: List[BiasTestResult] = Field(default_factory=list)
    detected_biases: Dict[str, float] = Field(default_factory=dict)
    spurious_correlations: Dict[str, float] = Field(default_factory=dict)
    
    # Recommendations
    bias_mitigation_recommendations: List[str] = Field(default_factory=list)
    robustness_improvements: List[str] = Field(default_factory=list)
    
    # Statistics
    total_tests_performed: int = 0
    tests_passed: int = 0
    critical_biases_detected: int = 0
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CausalBiasDetector:
    """CARMA-inspired causal bias detection service"""
    
    # Bias severity thresholds
    BIAS_SEVERITY_THRESHOLDS = {
        'critical': 0.8,
        'high': 0.6,
        'medium': 0.4,
        'low': 0.2
    }
    
    # Expected sensitivity thresholds for causal attributes
    CAUSAL_SENSITIVITY_TARGETS = {
        CausalBiasAttribute.QUALIFICATIONS: 0.8,
        CausalBiasAttribute.PERFORMANCE_METRICS: 0.9,
        CausalBiasAttribute.RELEVANT_EXPERIENCE: 0.7,
        CausalBiasAttribute.OBJECTIVE_CRITERIA: 0.85,
        CausalBiasAttribute.MERIT_BASED_FACTORS: 0.8,
        CausalBiasAttribute.DOMAIN_EXPERTISE: 0.75,
        CausalBiasAttribute.FACTUAL_ACCURACY: 0.9,
        CausalBiasAttribute.LOGICAL_CONSISTENCY: 0.85
    }
    
    # Maximum allowed correlation for spurious attributes
    SPURIOUS_CORRELATION_LIMITS = {
        SpuriousBiasAttribute.GENDER: 0.05,
        SpuriousBiasAttribute.RACE_ETHNICITY: 0.03,
        SpuriousBiasAttribute.AGE: 0.1,
        SpuriousBiasAttribute.RELIGION: 0.02,
        SpuriousBiasAttribute.SEXUAL_ORIENTATION: 0.02,
        SpuriousBiasAttribute.NATIONALITY: 0.05,
        SpuriousBiasAttribute.SOCIOECONOMIC_STATUS: 0.08,
        SpuriousBiasAttribute.PHYSICAL_APPEARANCE: 0.03,
        SpuriousBiasAttribute.NAME_ETHNICITY: 0.04,
        SpuriousBiasAttribute.ACCENT_DIALECT: 0.05,
        SpuriousBiasAttribute.GEOGRAPHIC_LOCATION: 0.07,
        SpuriousBiasAttribute.EDUCATIONAL_INSTITUTION_PRESTIGE: 0.1
    }
    
    def __init__(
        self,
        constitutional_validator: ConstitutionalSafetyValidator,
        blackboard_service: BlackboardService,
        ai_model_service: Optional[AIModelService] = None
    ):
        """Initialize causal bias detector"""
        self.constitutional_validator = constitutional_validator
        self.blackboard = blackboard_service
        self.ai_model_service = ai_model_service
        self.logger = logging.getLogger(__name__)
        
        # Initialize counterfactual generator if AI service available
        if ai_model_service:
            self.counterfactual_generator = ConstitutionalCounterfactualGenerator(
                ai_model_service, blackboard_service
            )
        else:
            self.counterfactual_generator = None
        
        # Detection statistics
        self.detection_stats = {
            'total_analyses': 0,
            'biases_detected': 0,
            'spurious_correlations_found': 0,
            'robustness_improvements_suggested': 0
        }
    
    async def analyze_causal_bias(
        self,
        decision_scenario: Dict[str, Any],
        decision_function: callable,
        test_attributes: Optional[Dict[str, List]] = None,
        enable_counterfactual_testing: bool = True
    ) -> CausalBiasAnalysisResult:
        """Perform comprehensive causal bias analysis"""
        
        analysis_id = str(uuid4())
        self.logger.info(f"Starting causal bias analysis: {analysis_id}")
        
        # Validate constitutional compliance
        if decision_scenario.get('constitutional_hash') != 'cdd01ef066bc6cf2':
            raise ValueError("Constitutional hash validation required for bias analysis")
        
        # Set default test attributes if not provided
        if test_attributes is None:
            test_attributes = {
                'causal': list(CausalBiasAttribute),
                'spurious': list(SpuriousBiasAttribute)
            }
        
        all_test_results = []
        
        # Test causal attribute sensitivity
        causal_results = await self._test_causal_attribute_sensitivity(
            decision_scenario, decision_function, test_attributes.get('causal', []),
            enable_counterfactual_testing
        )
        all_test_results.extend(causal_results)
        
        # Test spurious attribute invariance
        spurious_results = await self._test_spurious_attribute_invariance(
            decision_scenario, decision_function, test_attributes.get('spurious', []),
            enable_counterfactual_testing
        )
        all_test_results.extend(spurious_results)
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_bias_metrics(all_test_results)
        
        # Detect specific biases
        detected_biases = self._identify_detected_biases(all_test_results)
        spurious_correlations = self._identify_spurious_correlations(all_test_results)
        
        # Generate recommendations
        bias_recommendations = self._generate_bias_mitigation_recommendations(
            detected_biases, spurious_correlations
        )
        robustness_improvements = self._generate_robustness_improvements(
            overall_metrics, detected_biases
        )
        
        # Calculate statistics
        tests_passed = sum(1 for result in all_test_results if self._is_test_passed(result))
        critical_biases = sum(1 for bias_score in detected_biases.values() if bias_score >= self.BIAS_SEVERITY_THRESHOLDS['critical'])
        
        # Create final analysis result
        analysis_result = CausalBiasAnalysisResult(
            analysis_id=analysis_id,
            overall_bias_score=overall_metrics['overall_bias_score'],
            causal_sensitivity_score=overall_metrics['causal_sensitivity_score'],
            spurious_invariance_score=overall_metrics['spurious_invariance_score'],
            robustness_score=overall_metrics['robustness_score'],
            bias_test_results=all_test_results,
            detected_biases=detected_biases,
            spurious_correlations=spurious_correlations,
            bias_mitigation_recommendations=bias_recommendations,
            robustness_improvements=robustness_improvements,
            total_tests_performed=len(all_test_results),
            tests_passed=tests_passed,
            critical_biases_detected=critical_biases
        )
        
        # Log analysis results
        await self._log_bias_analysis(analysis_result)
        
        # Update statistics
        self.detection_stats['total_analyses'] += 1
        if detected_biases:
            self.detection_stats['biases_detected'] += len(detected_biases)
        if spurious_correlations:
            self.detection_stats['spurious_correlations_found'] += len(spurious_correlations)
        if robustness_improvements:
            self.detection_stats['robustness_improvements_suggested'] += len(robustness_improvements)
        
        return analysis_result
    
    async def _test_causal_attribute_sensitivity(
        self,
        decision_scenario: Dict[str, Any],
        decision_function: callable,
        causal_attributes: List[CausalBiasAttribute],
        enable_counterfactual: bool
    ) -> List[BiasTestResult]:
        """Test sensitivity to causal attributes (should be high)"""
        
        test_results = []
        
        for attribute in causal_attributes:
            self.logger.debug(f"Testing causal sensitivity for {attribute.value}")
            
            try:
                # Get baseline decision
                baseline_decision = await self._safe_decision_call(decision_function, decision_scenario)
                
                # Generate counterfactual with improved causal attribute
                if enable_counterfactual and self.counterfactual_generator:
                    improved_scenario = await self._generate_causal_improvement(
                        decision_scenario, attribute
                    )
                    improved_decision = await self._safe_decision_call(decision_function, improved_scenario)
                    
                    # Generate counterfactual with degraded causal attribute
                    degraded_scenario = await self._generate_causal_degradation(
                        decision_scenario, attribute
                    )
                    degraded_decision = await self._safe_decision_call(decision_function, degraded_scenario)
                    
                    # Calculate sensitivity score
                    sensitivity_score = self._calculate_causal_sensitivity(
                        baseline_decision, improved_decision, degraded_decision
                    )
                    
                    # Check if sensitivity meets target
                    target_sensitivity = self.CAUSAL_SENSITIVITY_TARGETS.get(attribute, 0.7)
                    expected_change = True
                    actual_change = sensitivity_score >= target_sensitivity
                    
                    test_result = BiasTestResult(
                        test_id=f"causal_{attribute.value}_{uuid4()}",
                        bias_type=BiasType.ALGORITHMIC,
                        attribute_tested=attribute,
                        test_type="causal_sensitivity",
                        baseline_decision=baseline_decision,
                        intervention_decision={'improved': improved_decision, 'degraded': degraded_decision},
                        expected_change=expected_change,
                        actual_change=actual_change,
                        bias_score=1.0 - sensitivity_score,  # Lower sensitivity = higher bias
                        confidence=0.8,
                        test_scenarios={
                            'baseline': decision_scenario,
                            'improved': improved_scenario,
                            'degraded': degraded_scenario
                        }
                    )
                    
                else:
                    # Simplified test without counterfactuals
                    test_result = BiasTestResult(
                        test_id=f"causal_{attribute.value}_simple_{uuid4()}",
                        bias_type=BiasType.ALGORITHMIC,
                        attribute_tested=attribute,
                        test_type="causal_sensitivity_simple",
                        baseline_decision=baseline_decision,
                        intervention_decision=baseline_decision,
                        expected_change=True,
                        actual_change=False,  # Cannot test without counterfactuals
                        bias_score=0.5,  # Neutral score
                        confidence=0.3,  # Low confidence without proper testing
                        test_scenarios={'baseline': decision_scenario}
                    )
                
                test_results.append(test_result)
                
            except Exception as e:
                self.logger.warning(f"Failed to test causal attribute {attribute.value}: {e}")
                # Add failed test result
                failed_result = BiasTestResult(
                    test_id=f"causal_{attribute.value}_failed_{uuid4()}",
                    bias_type=BiasType.ALGORITHMIC,
                    attribute_tested=attribute,
                    test_type="causal_sensitivity_failed",
                    baseline_decision=None,
                    intervention_decision=None,
                    expected_change=True,
                    actual_change=False,
                    bias_score=1.0,  # Assume bias on failure
                    confidence=0.0,
                    test_scenarios={'error': str(e)}
                )
                test_results.append(failed_result)
        
        return test_results
    
    async def _test_spurious_attribute_invariance(
        self,
        decision_scenario: Dict[str, Any],
        decision_function: callable,
        spurious_attributes: List[SpuriousBiasAttribute],
        enable_counterfactual: bool
    ) -> List[BiasTestResult]:
        """Test invariance to spurious attributes (should be high)"""
        
        test_results = []
        
        for attribute in spurious_attributes:
            self.logger.debug(f"Testing spurious invariance for {attribute.value}")
            
            try:
                # Get baseline decision
                baseline_decision = await self._safe_decision_call(decision_function, decision_scenario)
                
                # Generate variation with spurious attribute change
                if enable_counterfactual and self.counterfactual_generator:
                    varied_scenario = await self._generate_spurious_variation(
                        decision_scenario, attribute
                    )
                    varied_decision = await self._safe_decision_call(decision_function, varied_scenario)
                    
                    # Calculate correlation strength (should be low)
                    correlation_strength = self._calculate_spurious_correlation(
                        baseline_decision, varied_decision
                    )
                    
                    # Check if correlation is within acceptable limits
                    correlation_limit = self.SPURIOUS_CORRELATION_LIMITS.get(attribute, 0.05)
                    expected_change = False  # Should NOT change
                    actual_change = correlation_strength > correlation_limit
                    
                    test_result = BiasTestResult(
                        test_id=f"spurious_{attribute.value}_{uuid4()}",
                        bias_type=BiasType.DEMOGRAPHIC if attribute in [
                            SpuriousBiasAttribute.GENDER, SpuriousBiasAttribute.RACE_ETHNICITY,
                            SpuriousBiasAttribute.AGE, SpuriousBiasAttribute.RELIGION
                        ] else BiasType.SELECTION,
                        attribute_tested=attribute,
                        test_type="spurious_invariance",
                        baseline_decision=baseline_decision,
                        intervention_decision=varied_decision,
                        expected_change=expected_change,
                        actual_change=actual_change,
                        bias_score=correlation_strength,  # Higher correlation = higher bias
                        confidence=0.8,
                        test_scenarios={
                            'baseline': decision_scenario,
                            'varied': varied_scenario
                        }
                    )
                    
                else:
                    # Simplified test without counterfactuals
                    test_result = BiasTestResult(
                        test_id=f"spurious_{attribute.value}_simple_{uuid4()}",
                        bias_type=BiasType.DEMOGRAPHIC,
                        attribute_tested=attribute,
                        test_type="spurious_invariance_simple",
                        baseline_decision=baseline_decision,
                        intervention_decision=baseline_decision,
                        expected_change=False,
                        actual_change=False,
                        bias_score=0.0,  # Assume no bias without proper testing
                        confidence=0.3,
                        test_scenarios={'baseline': decision_scenario}
                    )
                
                test_results.append(test_result)
                
            except Exception as e:
                self.logger.warning(f"Failed to test spurious attribute {attribute.value}: {e}")
                # Add failed test result
                failed_result = BiasTestResult(
                    test_id=f"spurious_{attribute.value}_failed_{uuid4()}",
                    bias_type=BiasType.DEMOGRAPHIC,
                    attribute_tested=attribute,
                    test_type="spurious_invariance_failed",
                    baseline_decision=None,
                    intervention_decision=None,
                    expected_change=False,
                    actual_change=True,  # Assume bias on failure
                    bias_score=1.0,
                    confidence=0.0,
                    test_scenarios={'error': str(e)}
                )
                test_results.append(failed_result)
        
        return test_results
    
    async def _safe_decision_call(
        self,
        decision_function: callable,
        scenario: Dict[str, Any]
    ) -> Any:
        """Safely call decision function with error handling"""
        
        try:
            if asyncio.iscoroutinefunction(decision_function):
                return await decision_function(scenario)
            else:
                return decision_function(scenario)
        except Exception as e:
            self.logger.warning(f"Decision function call failed: {e}")
            return {'error': str(e), 'approved': False}
    
    async def _generate_causal_improvement(
        self,
        scenario: Dict[str, Any],
        attribute: CausalBiasAttribute
    ) -> Dict[str, Any]:
        """Generate scenario with improved causal attribute"""
        
        improved_scenario = scenario.copy()
        
        # Apply attribute-specific improvements
        if attribute == CausalBiasAttribute.QUALIFICATIONS:
            improved_scenario['qualifications_enhanced'] = True
            improved_scenario['additional_certifications'] = ['relevant_certification']
        elif attribute == CausalBiasAttribute.PERFORMANCE_METRICS:
            improved_scenario['performance_metrics_improved'] = True
            improved_scenario['metric_scores'] = {'quality': 95, 'efficiency': 90}
        elif attribute == CausalBiasAttribute.RELEVANT_EXPERIENCE:
            improved_scenario['experience_enhanced'] = True
            improved_scenario['additional_experience_years'] = 2
        elif attribute == CausalBiasAttribute.DOMAIN_EXPERTISE:
            improved_scenario['domain_expertise_enhanced'] = True
            improved_scenario['specialized_knowledge'] = ['advanced_domain_skills']
        
        improved_scenario['causal_improvement'] = attribute.value
        improved_scenario['constitutional_hash'] = 'cdd01ef066bc6cf2'
        
        return improved_scenario
    
    async def _generate_causal_degradation(
        self,
        scenario: Dict[str, Any],
        attribute: CausalBiasAttribute
    ) -> Dict[str, Any]:
        """Generate scenario with degraded causal attribute"""
        
        degraded_scenario = scenario.copy()
        
        # Apply attribute-specific degradations
        if attribute == CausalBiasAttribute.QUALIFICATIONS:
            degraded_scenario['qualifications_reduced'] = True
            degraded_scenario['missing_requirements'] = ['key_qualification']
        elif attribute == CausalBiasAttribute.PERFORMANCE_METRICS:
            degraded_scenario['performance_metrics_degraded'] = True
            degraded_scenario['metric_scores'] = {'quality': 60, 'efficiency': 55}
        elif attribute == CausalBiasAttribute.RELEVANT_EXPERIENCE:
            degraded_scenario['experience_reduced'] = True
            degraded_scenario['experience_gap'] = 'insufficient_experience'
        elif attribute == CausalBiasAttribute.DOMAIN_EXPERTISE:
            degraded_scenario['domain_expertise_reduced'] = True
            degraded_scenario['knowledge_gaps'] = ['missing_domain_skills']
        
        degraded_scenario['causal_degradation'] = attribute.value
        degraded_scenario['constitutional_hash'] = 'cdd01ef066bc6cf2'
        
        return degraded_scenario
    
    async def _generate_spurious_variation(
        self,
        scenario: Dict[str, Any],
        attribute: SpuriousBiasAttribute
    ) -> Dict[str, Any]:
        """Generate scenario with spurious attribute variation"""
        
        varied_scenario = scenario.copy()
        
        # Apply spurious variations
        if attribute == SpuriousBiasAttribute.GENDER:
            varied_scenario['gender_variation'] = True
            varied_scenario['gender_indicators'] = ['alternative_gender_presentation']
        elif attribute == SpuriousBiasAttribute.RACE_ETHNICITY:
            varied_scenario['ethnicity_variation'] = True
            varied_scenario['ethnicity_indicators'] = ['alternative_ethnic_background']
        elif attribute == SpuriousBiasAttribute.AGE:
            varied_scenario['age_variation'] = True
            varied_scenario['age_indicators'] = ['different_age_group']
        elif attribute == SpuriousBiasAttribute.NAME_ETHNICITY:
            varied_scenario['name_variation'] = True
            varied_scenario['name_ethnicity'] = ['alternative_cultural_name']
        elif attribute == SpuriousBiasAttribute.GEOGRAPHIC_LOCATION:
            varied_scenario['location_variation'] = True
            varied_scenario['geographic_indicators'] = ['different_region']
        
        varied_scenario['spurious_variation'] = attribute.value
        varied_scenario['causal_content_preserved'] = True
        varied_scenario['constitutional_hash'] = 'cdd01ef066bc6cf2'
        
        return varied_scenario
    
    def _calculate_causal_sensitivity(
        self,
        baseline: Any,
        improved: Any,
        degraded: Any
    ) -> float:
        """Calculate sensitivity to causal changes"""
        
        baseline_approved = self._extract_decision(baseline)
        improved_approved = self._extract_decision(improved)
        degraded_approved = self._extract_decision(degraded)
        
        sensitivity_score = 0.0
        
        # Good sensitivity: improvements should increase approval probability
        if improved_approved and not baseline_approved:
            sensitivity_score += 0.4
        if improved_approved and baseline_approved:
            sensitivity_score += 0.2
        
        # Good sensitivity: degradations should decrease approval probability
        if not degraded_approved and baseline_approved:
            sensitivity_score += 0.4
        if not degraded_approved and not baseline_approved:
            sensitivity_score += 0.2
        
        return min(1.0, sensitivity_score)
    
    def _calculate_spurious_correlation(
        self,
        baseline: Any,
        varied: Any
    ) -> float:
        """Calculate correlation with spurious changes"""
        
        baseline_approved = self._extract_decision(baseline)
        varied_approved = self._extract_decision(varied)
        
        # Good invariance: spurious changes should not affect decision
        if baseline_approved == varied_approved:
            return 0.0  # No correlation (good)
        else:
            return 1.0  # High correlation (problematic)
    
    def _extract_decision(self, decision_result: Any) -> bool:
        """Extract boolean decision from result"""
        
        if isinstance(decision_result, bool):
            return decision_result
        elif isinstance(decision_result, dict):
            return decision_result.get('approved', False)
        elif hasattr(decision_result, 'approved'):
            return decision_result.approved
        else:
            return False
    
    def _calculate_overall_bias_metrics(
        self,
        test_results: List[BiasTestResult]
    ) -> Dict[str, float]:
        """Calculate overall bias metrics"""
        
        if not test_results:
            return {
                'overall_bias_score': 0.0,
                'causal_sensitivity_score': 0.0,
                'spurious_invariance_score': 0.0,
                'robustness_score': 0.0
            }
        
        # Separate causal and spurious tests
        causal_tests = [r for r in test_results if 'causal' in r.test_type]
        spurious_tests = [r for r in test_results if 'spurious' in r.test_type]
        
        # Calculate causal sensitivity (1 - bias_score for causal tests)
        if causal_tests:
            causal_sensitivity = 1.0 - statistics.mean([r.bias_score for r in causal_tests])
        else:
            causal_sensitivity = 0.0
        
        # Calculate spurious invariance (1 - bias_score for spurious tests)
        if spurious_tests:
            spurious_invariance = 1.0 - statistics.mean([r.bias_score for r in spurious_tests])
        else:
            spurious_invariance = 1.0
        
        # Overall bias score (higher = more biased)
        overall_bias = statistics.mean([r.bias_score for r in test_results])
        
        # Robustness score (weighted combination)
        robustness = (causal_sensitivity * 0.6 + spurious_invariance * 0.4)
        
        return {
            'overall_bias_score': overall_bias,
            'causal_sensitivity_score': causal_sensitivity,
            'spurious_invariance_score': spurious_invariance,
            'robustness_score': robustness
        }
    
    def _identify_detected_biases(
        self,
        test_results: List[BiasTestResult]
    ) -> Dict[str, float]:
        """Identify specific biases detected"""
        
        detected_biases = {}
        
        for result in test_results:
            if result.bias_score > self.BIAS_SEVERITY_THRESHOLDS['low']:
                attribute_name = result.attribute_tested.value
                bias_type = result.bias_type.value
                key = f"{bias_type}_{attribute_name}"
                detected_biases[key] = result.bias_score
        
        return detected_biases
    
    def _identify_spurious_correlations(
        self,
        test_results: List[BiasTestResult]
    ) -> Dict[str, float]:
        """Identify spurious correlations"""
        
        spurious_correlations = {}
        
        for result in test_results:
            if 'spurious' in result.test_type and isinstance(result.attribute_tested, SpuriousBiasAttribute):
                limit = self.SPURIOUS_CORRELATION_LIMITS.get(result.attribute_tested, 0.05)
                if result.bias_score > limit:
                    spurious_correlations[result.attribute_tested.value] = result.bias_score
        
        return spurious_correlations
    
    def _generate_bias_mitigation_recommendations(
        self,
        detected_biases: Dict[str, float],
        spurious_correlations: Dict[str, float]
    ) -> List[str]:
        """Generate bias mitigation recommendations"""
        
        recommendations = []
        
        if detected_biases:
            recommendations.append("Implement bias-aware training with balanced datasets")
            recommendations.append("Add fairness constraints to model optimization")
            recommendations.append("Increase diverse representation in training data")
        
        if spurious_correlations:
            recommendations.append("Apply CARMA-style neutral augmentations for spurious invariance")
            recommendations.append("Implement adversarial debiasing techniques")
            recommendations.append("Add spurious correlation detection to monitoring pipeline")
        
        # Specific recommendations based on bias types
        for bias_key, score in detected_biases.items():
            if score >= self.BIAS_SEVERITY_THRESHOLDS['critical']:
                recommendations.append(f"CRITICAL: Address {bias_key} bias immediately")
            elif 'demographic' in bias_key:
                recommendations.append("Implement demographic parity constraints")
            elif 'algorithmic' in bias_key:
                recommendations.append("Review algorithmic design for fairness")
        
        return recommendations
    
    def _generate_robustness_improvements(
        self,
        overall_metrics: Dict[str, float],
        detected_biases: Dict[str, float]
    ) -> List[str]:
        """Generate robustness improvement recommendations"""
        
        improvements = []
        
        if overall_metrics['causal_sensitivity_score'] < 0.7:
            improvements.append("Increase causal augmentation training to improve sensitivity")
            improvements.append("Add explicit causal attribute training examples")
        
        if overall_metrics['spurious_invariance_score'] < 0.8:
            improvements.append("Add neutral augmentations for spurious invariance training")
            improvements.append("Implement regularization against spurious correlations")
        
        if overall_metrics['robustness_score'] < 0.6:
            improvements.append("Apply comprehensive CARMA training methodology")
            improvements.append("Implement counterfactual robustness testing")
        
        return improvements
    
    def _is_test_passed(self, result: BiasTestResult) -> bool:
        """Determine if a bias test passed"""
        
        if 'causal' in result.test_type:
            # For causal tests, low bias score is good
            return result.bias_score < 0.3
        elif 'spurious' in result.test_type:
            # For spurious tests, low correlation is good
            if isinstance(result.attribute_tested, SpuriousBiasAttribute):
                limit = self.SPURIOUS_CORRELATION_LIMITS.get(result.attribute_tested, 0.05)
                return result.bias_score <= limit
        
        return result.bias_score < 0.3
    
    async def _log_bias_analysis(
        self,
        analysis_result: CausalBiasAnalysisResult
    ) -> None:
        """Log bias analysis results to blackboard"""
        
        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                'type': 'causal_bias_analysis',
                'analysis_id': analysis_result.analysis_id,
                'overall_metrics': {
                    'overall_bias_score': analysis_result.overall_bias_score,
                    'causal_sensitivity_score': analysis_result.causal_sensitivity_score,
                    'spurious_invariance_score': analysis_result.spurious_invariance_score,
                    'robustness_score': analysis_result.robustness_score
                },
                'detected_biases': analysis_result.detected_biases,
                'spurious_correlations': analysis_result.spurious_correlations,
                'test_statistics': {
                    'total_tests': analysis_result.total_tests_performed,
                    'tests_passed': analysis_result.tests_passed,
                    'critical_biases': analysis_result.critical_biases_detected
                },
                'constitutional_hash': 'cdd01ef066bc6cf2'
            },
            metadata={
                'source': 'causal_bias_detector',
                'timestamp': analysis_result.timestamp.isoformat(),
                'bias_severity': 'critical' if analysis_result.critical_biases_detected > 0 else 'medium' if analysis_result.overall_bias_score > 0.4 else 'low'
            },
            tags=['bias', 'causal', 'carma', 'analysis', 'robustness']
        )
        
        await self.blackboard.add_knowledge(knowledge_item)
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get bias detection statistics"""
        
        stats = self.detection_stats.copy()
        stats.update({
            'constitutional_hash': 'cdd01ef066bc6cf2',
            'detector_version': '1.0.0_carma_inspired',
            'bias_detection_rate': (
                stats.get('biases_detected', 0) / 
                max(1, stats.get('total_analyses', 1))
            ),
            'spurious_correlation_rate': (
                stats.get('spurious_correlations_found', 0) /
                max(1, stats.get('total_analyses', 1))
            )
        })
        
        return stats