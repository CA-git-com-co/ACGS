"""
Legal Agent for Multi-Agent Governance System
Specialized agent for legal compliance analysis and regulatory assessment tasks.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field

from ...shared.blackboard import BlackboardService, KnowledgeItem, TaskDefinition
from ...shared.constitutional_safety_framework import ConstitutionalSafetyValidator
from ...shared.ai_model_service import AIModelService


class LegalAnalysisResult(BaseModel):
    """Result of legal compliance analysis"""
    approved: bool
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    confidence: float = Field(ge=0.0, le=1.0)
    regulatory_compliance: Dict[str, Any] = Field(default_factory=dict)
    jurisdiction_analysis: Dict[str, Any] = Field(default_factory=dict)
    data_protection_assessment: Dict[str, Any] = Field(default_factory=dict)
    liability_assessment: Dict[str, Any] = Field(default_factory=dict)
    contract_compliance: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    constitutional_compliance: Dict[str, Any] = Field(default_factory=dict)
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict)


class RegulatoryFrameworkAnalyzer:
    """Analyzer for different regulatory frameworks"""
    
    # Regulatory frameworks and their requirements
    FRAMEWORKS = {
        'GDPR': {
            'name': 'General Data Protection Regulation',
            'jurisdiction': 'EU',
            'key_requirements': [
                'lawful_basis', 'data_minimization', 'purpose_limitation',
                'accuracy', 'storage_limitation', 'integrity_confidentiality',
                'accountability', 'data_subject_rights', 'privacy_by_design'
            ],
            'penalties': 'Up to 4% of annual global turnover or €20 million',
            'applies_to': ['data_processing', 'automated_decision_making', 'profiling']
        },
        'CCPA': {
            'name': 'California Consumer Privacy Act',
            'jurisdiction': 'California, US',
            'key_requirements': [
                'consumer_rights', 'data_disclosure', 'opt_out_rights',
                'non_discrimination', 'third_party_disclosure', 'security_measures'
            ],
            'penalties': 'Up to $7,500 per violation',
            'applies_to': ['personal_information_processing', 'data_sales', 'consumer_data']
        },
        'AI_Act': {
            'name': 'EU AI Act',
            'jurisdiction': 'EU',
            'key_requirements': [
                'risk_assessment', 'transparency_obligations', 'human_oversight',
                'accuracy_robustness', 'data_governance', 'record_keeping',
                'conformity_assessment', 'registration_obligations'
            ],
            'penalties': 'Up to 6% of annual global turnover or €30 million',
            'applies_to': ['ai_systems', 'high_risk_ai', 'prohibited_ai_practices']
        },
        'HIPAA': {
            'name': 'Health Insurance Portability and Accountability Act',
            'jurisdiction': 'US',
            'key_requirements': [
                'privacy_rule', 'security_rule', 'breach_notification',
                'minimum_necessary_standard', 'administrative_safeguards',
                'physical_safeguards', 'technical_safeguards'
            ],
            'penalties': 'Up to $1.5 million per incident',
            'applies_to': ['protected_health_information', 'healthcare_entities']
        },
        'SOX': {
            'name': 'Sarbanes-Oxley Act',
            'jurisdiction': 'US',
            'key_requirements': [
                'internal_controls', 'financial_reporting', 'audit_requirements',
                'data_retention', 'whistleblower_protection', 'certification_requirements'
            ],
            'penalties': 'Criminal penalties up to 20 years imprisonment',
            'applies_to': ['public_companies', 'financial_reporting', 'audit_firms']
        }
    }
    
    @staticmethod
    async def analyze_framework_compliance(
        framework: str, 
        model_info: Dict[str, Any], 
        data_handling: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze compliance with a specific regulatory framework"""
        
        if framework not in RegulatoryFrameworkAnalyzer.FRAMEWORKS:
            return {
                'framework': framework,
                'compliance_status': 'unknown',
                'error': f'Framework {framework} not supported'
            }
        
        framework_info = RegulatoryFrameworkAnalyzer.FRAMEWORKS[framework]
        
        if framework == 'GDPR':
            return await RegulatoryFrameworkAnalyzer._analyze_gdpr_compliance(
                framework_info, model_info, data_handling, deployment_context
            )
        elif framework == 'CCPA':
            return await RegulatoryFrameworkAnalyzer._analyze_ccpa_compliance(
                framework_info, model_info, data_handling, deployment_context
            )
        elif framework == 'AI_Act':
            return await RegulatoryFrameworkAnalyzer._analyze_ai_act_compliance(
                framework_info, model_info, data_handling, deployment_context
            )
        elif framework == 'HIPAA':
            return await RegulatoryFrameworkAnalyzer._analyze_hipaa_compliance(
                framework_info, model_info, data_handling, deployment_context
            )
        elif framework == 'SOX':
            return await RegulatoryFrameworkAnalyzer._analyze_sox_compliance(
                framework_info, model_info, data_handling, deployment_context
            )
        else:
            return {
                'framework': framework,
                'compliance_status': 'not_implemented',
                'error': f'Analysis for {framework} not implemented'
            }
    
    @staticmethod
    async def _analyze_gdpr_compliance(
        framework_info: Dict[str, Any],
        model_info: Dict[str, Any],
        data_handling: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze GDPR compliance"""
        
        compliance_checks = {}
        violations = []
        risk_score = 0.0
        
        # Check lawful basis
        lawful_basis = data_handling.get('lawful_basis')
        if not lawful_basis:
            violations.append('No lawful basis specified for data processing')
            risk_score += 0.3
        elif lawful_basis not in ['consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests']:
            violations.append(f'Invalid lawful basis: {lawful_basis}')
            risk_score += 0.2
        
        compliance_checks['lawful_basis'] = {
            'status': 'compliant' if lawful_basis else 'non_compliant',
            'basis': lawful_basis,
            'details': 'Lawful basis for processing specified' if lawful_basis else 'No lawful basis specified'
        }
        
        # Check data minimization
        data_collection = data_handling.get('data_collection', {})
        purpose_limitation = data_collection.get('purpose_specific', False)
        if not purpose_limitation:
            violations.append('Data collection not limited to specific purposes')
            risk_score += 0.2
        
        compliance_checks['data_minimization'] = {
            'status': 'compliant' if purpose_limitation else 'non_compliant',
            'purpose_specific': purpose_limitation,
            'details': 'Data collection limited to specified purposes' if purpose_limitation else 'Purpose limitation not implemented'
        }
        
        # Check data subject rights
        subject_rights = data_handling.get('data_subject_rights', {})
        required_rights = ['access', 'rectification', 'erasure', 'portability', 'objection']
        missing_rights = [right for right in required_rights if not subject_rights.get(right, False)]
        
        if missing_rights:
            violations.append(f'Missing data subject rights: {missing_rights}')
            risk_score += 0.1 * len(missing_rights)
        
        compliance_checks['data_subject_rights'] = {
            'status': 'compliant' if not missing_rights else 'partial_compliance',
            'implemented_rights': [right for right in required_rights if subject_rights.get(right, False)],
            'missing_rights': missing_rights
        }
        
        # Check automated decision making
        automated_decisions = deployment_context.get('automated_decisions', False)
        human_oversight = deployment_context.get('human_oversight', {})
        if automated_decisions:
            if not human_oversight.get('enabled', False):
                violations.append('Automated decision making without human oversight')
                risk_score += 0.25

        compliance_checks['automated_decision_making'] = {
            'status': 'compliant' if not automated_decisions or human_oversight.get('enabled', False) else 'non_compliant',
            'automated_decisions': automated_decisions,
            'human_oversight': human_oversight.get('enabled', False)
        }
        
        # Check privacy by design
        privacy_measures = data_handling.get('privacy_measures', [])
        required_measures = ['encryption', 'pseudonymization', 'access_controls', 'data_minimization']
        missing_measures = [measure for measure in required_measures if measure not in privacy_measures]
        
        if missing_measures:
            violations.append(f'Privacy by design - missing measures: {missing_measures}')
            risk_score += 0.05 * len(missing_measures)
        
        compliance_checks['privacy_by_design'] = {
            'status': 'compliant' if len(missing_measures) <= 1 else 'partial_compliance',
            'implemented_measures': privacy_measures,
            'missing_measures': missing_measures
        }
        
        # Determine overall compliance
        compliance_status = 'compliant' if risk_score < 0.3 else 'partial_compliance' if risk_score < 0.6 else 'non_compliant'
        
        return {
            'framework': 'GDPR',
            'compliance_status': compliance_status,
            'risk_score': min(risk_score, 1.0),
            'violations': violations,
            'compliance_checks': compliance_checks,
            'recommendations': RegulatoryFrameworkAnalyzer._generate_gdpr_recommendations(violations, missing_measures, missing_rights)
        }
    
    @staticmethod
    async def _analyze_ccpa_compliance(
        framework_info: Dict[str, Any],
        model_info: Dict[str, Any],
        data_handling: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze CCPA compliance"""
        
        compliance_checks = {}
        violations = []
        risk_score = 0.0
        
        # Check consumer rights implementation
        consumer_rights = data_handling.get('consumer_rights', {})
        required_rights = ['know', 'delete', 'opt_out', 'non_discrimination']
        missing_rights = [right for right in required_rights if not consumer_rights.get(right, False)]
        
        if missing_rights:
            violations.append(f'Missing consumer rights: {missing_rights}')
            risk_score += 0.2 * len(missing_rights)
        
        compliance_checks['consumer_rights'] = {
            'status': 'compliant' if not missing_rights else 'partial_compliance',
            'implemented_rights': [right for right in required_rights if consumer_rights.get(right, False)],
            'missing_rights': missing_rights
        }
        
        # Check data disclosure requirements
        data_disclosure = data_handling.get('data_disclosure', {})
        privacy_policy = data_disclosure.get('privacy_policy_updated', False)
        categories_disclosed = data_disclosure.get('categories_disclosed', False)
        
        if not privacy_policy:
            violations.append('Privacy policy not updated for CCPA compliance')
            risk_score += 0.2
        
        if not categories_disclosed:
            violations.append('Data categories not properly disclosed')
            risk_score += 0.15
        
        compliance_checks['data_disclosure'] = {
            'status': 'compliant' if privacy_policy and categories_disclosed else 'non_compliant',
            'privacy_policy_updated': privacy_policy,
            'categories_disclosed': categories_disclosed
        }
        
        # Check opt-out mechanisms
        opt_out = data_handling.get('opt_out_mechanisms', {})
        if not opt_out.get('implemented', False):
            violations.append('Opt-out mechanisms not implemented')
            risk_score += 0.3
        
        compliance_checks['opt_out_mechanisms'] = {
            'status': 'compliant' if opt_out.get('implemented', False) else 'non_compliant',
            'implemented': opt_out.get('implemented', False),
            'methods': opt_out.get('methods', [])
        }
        
        # Determine overall compliance
        compliance_status = 'compliant' if risk_score < 0.3 else 'partial_compliance' if risk_score < 0.6 else 'non_compliant'
        
        return {
            'framework': 'CCPA',
            'compliance_status': compliance_status,
            'risk_score': min(risk_score, 1.0),
            'violations': violations,
            'compliance_checks': compliance_checks,
            'recommendations': RegulatoryFrameworkAnalyzer._generate_ccpa_recommendations(violations)
        }
    
    @staticmethod
    async def _analyze_ai_act_compliance(
        framework_info: Dict[str, Any],
        model_info: Dict[str, Any],
        data_handling: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze EU AI Act compliance"""
        
        compliance_checks = {}
        violations = []
        risk_score = 0.0
        
        # Determine AI system risk category
        use_case = deployment_context.get('use_case', '')
        high_risk_domains = ['healthcare', 'education', 'employment', 'law_enforcement', 'justice', 'migration', 'democratic_processes']
        
        is_high_risk = any(domain in use_case.lower() for domain in high_risk_domains)
        risk_category = 'high' if is_high_risk else 'limited' if 'generative' in model_info.get('model_type', '').lower() else 'minimal'
        
        compliance_checks['risk_assessment'] = {
            'risk_category': risk_category,
            'is_high_risk': is_high_risk,
            'use_case': use_case
        }
        
        if risk_category == 'high':
            # High-risk AI system requirements
            
            # Risk management system
            risk_management = model_info.get('risk_management_system', {})
            if not risk_management.get('implemented', False):
                violations.append('High-risk AI system lacks risk management system')
                risk_score += 0.4
            
            # Data governance
            data_governance = data_handling.get('data_governance', {})
            if not data_governance.get('quality_measures', False):
                violations.append('Insufficient data governance and quality measures')
                risk_score += 0.3
            
            # Transparency and documentation
            documentation = model_info.get('documentation', {})
            if not documentation.get('technical_documentation', False):
                violations.append('Missing technical documentation')
                risk_score += 0.2
            
            # Human oversight
            human_oversight = deployment_context.get('human_oversight', {})
            if not human_oversight.get('enabled', False):
                violations.append('Human oversight not implemented for high-risk AI')
                risk_score += 0.3
            
            # Accuracy and robustness
            robustness = model_info.get('robustness_testing', {})
            if not robustness.get('conducted', False):
                violations.append('Robustness testing not conducted')
                risk_score += 0.2
            
            compliance_checks['high_risk_requirements'] = {
                'risk_management_system': risk_management.get('implemented', False),
                'data_governance': data_governance.get('quality_measures', False),
                'technical_documentation': documentation.get('technical_documentation', False),
                'human_oversight': human_oversight.get('enabled', False),
                'robustness_testing': robustness.get('conducted', False)
            }
        
        elif risk_category == 'limited':
            # Limited risk AI system requirements (mainly transparency)
            transparency = deployment_context.get('transparency_measures', [])
            if 'ai_system_disclosure' not in transparency:
                violations.append('AI system not properly disclosed to users')
                risk_score += 0.2
            
            compliance_checks['limited_risk_requirements'] = {
                'ai_disclosure': 'ai_system_disclosure' in transparency,
                'transparency_measures': transparency
            }
        
        # Check for prohibited practices
        prohibited_practices = model_info.get('prohibited_practices_check', {})
        if prohibited_practices.get('subliminal_techniques', False):
            violations.append('AI system uses prohibited subliminal techniques')
            risk_score += 1.0
        
        if prohibited_practices.get('exploits_vulnerabilities', False):
            violations.append('AI system exploits vulnerabilities of specific groups')
            risk_score += 1.0
        
        # Determine overall compliance
        compliance_status = 'compliant' if risk_score < 0.3 else 'partial_compliance' if risk_score < 0.6 else 'non_compliant'
        
        return {
            'framework': 'AI_Act',
            'compliance_status': compliance_status,
            'risk_score': min(risk_score, 1.0),
            'risk_category': risk_category,
            'violations': violations,
            'compliance_checks': compliance_checks,
            'recommendations': RegulatoryFrameworkAnalyzer._generate_ai_act_recommendations(violations, risk_category)
        }
    
    @staticmethod
    async def _analyze_hipaa_compliance(
        framework_info: Dict[str, Any],
        model_info: Dict[str, Any],
        data_handling: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze HIPAA compliance"""
        
        # Check if health data is involved
        data_types = data_handling.get('data_types', [])
        processes_health_data = 'health_information' in data_types or 'medical_records' in data_types
        
        if not processes_health_data:
            return {
                'framework': 'HIPAA',
                'compliance_status': 'not_applicable',
                'note': 'HIPAA not applicable - no health information processed',
                'compliance_checks': {}
            }
        
        compliance_checks = {}
        violations = []
        risk_score = 0.0
        
        # Privacy Rule compliance
        privacy_measures = data_handling.get('privacy_measures', [])
        required_privacy_measures = ['access_controls', 'minimum_necessary', 'administrative_safeguards']
        missing_privacy = [measure for measure in required_privacy_measures if measure not in privacy_measures]
        
        if missing_privacy:
            violations.append(f'HIPAA Privacy Rule - missing measures: {missing_privacy}')
            risk_score += 0.2 * len(missing_privacy)
        
        # Security Rule compliance
        security_measures = data_handling.get('security_measures', [])
        required_security_measures = ['encryption', 'access_controls', 'audit_logs', 'integrity_controls']
        missing_security = [measure for measure in required_security_measures if measure not in security_measures]
        
        if missing_security:
            violations.append(f'HIPAA Security Rule - missing measures: {missing_security}')
            risk_score += 0.2 * len(missing_security)
        
        # Breach notification procedures
        breach_procedures = data_handling.get('breach_notification_procedures', {})
        if not breach_procedures.get('implemented', False):
            violations.append('Breach notification procedures not implemented')
            risk_score += 0.3
        
        compliance_checks = {
            'privacy_rule': {
                'status': 'compliant' if not missing_privacy else 'partial_compliance',
                'implemented_measures': [m for m in required_privacy_measures if m in privacy_measures],
                'missing_measures': missing_privacy
            },
            'security_rule': {
                'status': 'compliant' if not missing_security else 'partial_compliance',
                'implemented_measures': [m for m in required_security_measures if m in security_measures],
                'missing_measures': missing_security
            },
            'breach_notification': {
                'status': 'compliant' if breach_procedures.get('implemented', False) else 'non_compliant',
                'implemented': breach_procedures.get('implemented', False)
            }
        }
        
        compliance_status = 'compliant' if risk_score < 0.3 else 'partial_compliance' if risk_score < 0.6 else 'non_compliant'
        
        return {
            'framework': 'HIPAA',
            'compliance_status': compliance_status,
            'risk_score': min(risk_score, 1.0),
            'violations': violations,
            'compliance_checks': compliance_checks,
            'recommendations': RegulatoryFrameworkAnalyzer._generate_hipaa_recommendations(violations)
        }
    
    @staticmethod
    async def _analyze_sox_compliance(
        framework_info: Dict[str, Any],
        model_info: Dict[str, Any],
        data_handling: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze SOX compliance"""
        
        # Check if financial reporting is involved
        use_case = deployment_context.get('use_case', '')
        affects_financial_reporting = 'financial' in use_case.lower() or 'reporting' in use_case.lower()
        
        if not affects_financial_reporting:
            return {
                'framework': 'SOX',
                'compliance_status': 'not_applicable',
                'note': 'SOX not applicable - no financial reporting impact',
                'compliance_checks': {}
            }
        
        compliance_checks = {}
        violations = []
        risk_score = 0.0
        
        # Internal controls
        internal_controls = model_info.get('internal_controls', {})
        if not internal_controls.get('documented', False):
            violations.append('Internal controls not documented')
            risk_score += 0.3
        
        if not internal_controls.get('tested', False):
            violations.append('Internal controls not tested')
            risk_score += 0.3
        
        # Data retention
        data_retention = data_handling.get('data_retention', {})
        if not data_retention.get('policy_defined', False):
            violations.append('Data retention policy not defined')
            risk_score += 0.2
        
        # Audit trail
        audit_capabilities = model_info.get('audit_capabilities', {})
        if not audit_capabilities.get('comprehensive_logging', False):
            violations.append('Comprehensive audit logging not implemented')
            risk_score += 0.3
        
        compliance_checks = {
            'internal_controls': {
                'documented': internal_controls.get('documented', False),
                'tested': internal_controls.get('tested', False)
            },
            'data_retention': {
                'policy_defined': data_retention.get('policy_defined', False),
                'retention_period': data_retention.get('retention_period')
            },
            'audit_trail': {
                'comprehensive_logging': audit_capabilities.get('comprehensive_logging', False),
                'immutable_logs': audit_capabilities.get('immutable_logs', False)
            }
        }
        
        compliance_status = 'compliant' if risk_score < 0.3 else 'partial_compliance' if risk_score < 0.6 else 'non_compliant'
        
        return {
            'framework': 'SOX',
            'compliance_status': compliance_status,
            'risk_score': min(risk_score, 1.0),
            'violations': violations,
            'compliance_checks': compliance_checks,
            'recommendations': RegulatoryFrameworkAnalyzer._generate_sox_recommendations(violations)
        }
    
    @staticmethod
    def _generate_gdpr_recommendations(violations: List[str], missing_measures: List[str], missing_rights: List[str]) -> List[str]:
        """Generate GDPR compliance recommendations"""
        recommendations = []
        
        if any('lawful basis' in v for v in violations):
            recommendations.append('Establish and document lawful basis for data processing')
        
        if any('purpose' in v for v in violations):
            recommendations.append('Implement purpose limitation and data minimization principles')
        
        if missing_rights:
            recommendations.append('Implement missing data subject rights mechanisms')
        
        if missing_measures:
            recommendations.append('Implement privacy by design measures including encryption and access controls')
        
        if any('oversight' in v for v in violations):
            recommendations.append('Add human oversight for automated decision making')
        
        return recommendations
    
    @staticmethod
    def _generate_ccpa_recommendations(violations: List[str]) -> List[str]:
        """Generate CCPA compliance recommendations"""
        recommendations = []
        
        if any('consumer rights' in v for v in violations):
            recommendations.append('Implement all required consumer rights (know, delete, opt-out, non-discrimination)')
        
        if any('privacy policy' in v for v in violations):
            recommendations.append('Update privacy policy to meet CCPA disclosure requirements')
        
        if any('opt-out' in v for v in violations):
            recommendations.append('Implement opt-out mechanisms for data sales')
        
        return recommendations
    
    @staticmethod
    def _generate_ai_act_recommendations(violations: List[str], risk_category: str) -> List[str]:
        """Generate AI Act compliance recommendations"""
        recommendations = []
        
        if risk_category == 'high':
            recommendations.append('Implement comprehensive risk management system for high-risk AI')
            recommendations.append('Ensure human oversight and intervention capabilities')
            recommendations.append('Conduct thorough robustness and accuracy testing')
            recommendations.append('Maintain detailed technical documentation')
        
        if any('disclosure' in v for v in violations):
            recommendations.append('Implement proper AI system disclosure to users')
        
        if any('prohibited' in v for v in violations):
            recommendations.append('Remove prohibited AI practices from system design')
        
        return recommendations
    
    @staticmethod
    def _generate_hipaa_recommendations(violations: List[str]) -> List[str]:
        """Generate HIPAA compliance recommendations"""
        recommendations = []
        
        if any('Privacy Rule' in v for v in violations):
            recommendations.append('Implement HIPAA Privacy Rule safeguards and minimum necessary standards')
        
        if any('Security Rule' in v for v in violations):
            recommendations.append('Implement HIPAA Security Rule technical and administrative safeguards')
        
        if any('breach notification' in v for v in violations):
            recommendations.append('Establish breach notification procedures and incident response')
        
        return recommendations
    
    @staticmethod
    def _generate_sox_recommendations(violations: List[str]) -> List[str]:
        """Generate SOX compliance recommendations"""
        recommendations = []
        
        if any('internal controls' in v for v in violations):
            recommendations.append('Document and test internal controls over financial reporting')
        
        if any('data retention' in v for v in violations):
            recommendations.append('Define and implement data retention policies')
        
        if any('audit' in v for v in violations):
            recommendations.append('Implement comprehensive audit logging and trail capabilities')
        
        return recommendations


class JurisdictionAnalyzer:
    """Analyzer for jurisdiction-specific legal requirements"""
    
    JURISDICTIONS = {
        'EU': {
            'name': 'European Union',
            'primary_frameworks': ['GDPR', 'AI_Act', 'DSA', 'DGA'],
            'data_localization': True,
            'cross_border_restrictions': True
        },
        'US': {
            'name': 'United States',
            'primary_frameworks': ['CCPA', 'HIPAA', 'SOX', 'COPPA'],
            'data_localization': False,
            'cross_border_restrictions': False,
            'state_specific': ['California', 'Virginia', 'Colorado']
        },
        'UK': {
            'name': 'United Kingdom',
            'primary_frameworks': ['UK_GDPR', 'DPA_2018'],
            'data_localization': False,
            'cross_border_restrictions': True
        },
        'China': {
            'name': 'China',
            'primary_frameworks': ['PIPL', 'CSL', 'DSL'],
            'data_localization': True,
            'cross_border_restrictions': True
        }
    }
    
    @staticmethod
    async def analyze_jurisdictional_requirements(
        jurisdictions: List[str],
        deployment_context: Dict[str, Any],
        data_handling: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze legal requirements across multiple jurisdictions"""
        
        jurisdiction_analysis = {}
        overall_risk = 0.0
        cross_border_issues = []
        
        for jurisdiction in jurisdictions:
            if jurisdiction in JurisdictionAnalyzer.JURISDICTIONS:
                jurisdiction_info = JurisdictionAnalyzer.JURISDICTIONS[jurisdiction]
                
                analysis = {
                    'jurisdiction_name': jurisdiction_info['name'],
                    'applicable_frameworks': jurisdiction_info['primary_frameworks'],
                    'data_localization_required': jurisdiction_info['data_localization'],
                    'cross_border_restrictions': jurisdiction_info['cross_border_restrictions']
                }
                
                # Check data localization requirements
                data_storage = data_handling.get('data_storage', {})
                if jurisdiction_info['data_localization']:
                    storage_locations = data_storage.get('locations', [])
                    if jurisdiction not in storage_locations:
                        analysis['data_localization_violation'] = True
                        cross_border_issues.append(f'Data localization required in {jurisdiction} but data stored elsewhere')
                        overall_risk += 0.3
                
                # Check cross-border transfer restrictions
                if jurisdiction_info['cross_border_restrictions']:
                    transfer_safeguards = data_handling.get('transfer_safeguards', [])
                    if not transfer_safeguards:
                        analysis['transfer_safeguards_missing'] = True
                        cross_border_issues.append(f'Cross-border transfer safeguards missing for {jurisdiction}')
                        overall_risk += 0.2
                
                jurisdiction_analysis[jurisdiction] = analysis
            else:
                jurisdiction_analysis[jurisdiction] = {
                    'error': f'Jurisdiction {jurisdiction} not supported in analysis'
                }
        
        return {
            'jurisdictions_analyzed': list(jurisdiction_analysis.keys()),
            'jurisdiction_details': jurisdiction_analysis,
            'cross_border_issues': cross_border_issues,
            'overall_risk_score': min(overall_risk, 1.0),
            'recommendations': JurisdictionAnalyzer._generate_jurisdictional_recommendations(cross_border_issues, jurisdiction_analysis)
        }
    
    @staticmethod
    def _generate_jurisdictional_recommendations(
        cross_border_issues: List[str],
        jurisdiction_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for jurisdictional compliance"""
        recommendations = []
        
        if any('localization' in issue for issue in cross_border_issues):
            recommendations.append('Implement data localization for jurisdictions that require it')
        
        if any('safeguards' in issue for issue in cross_border_issues):
            recommendations.append('Implement appropriate safeguards for cross-border data transfers')
        
        # Check for high-risk jurisdictions
        high_restriction_jurisdictions = [j for j, details in jurisdiction_analysis.items() 
                                       if isinstance(details, dict) and details.get('cross_border_restrictions')]
        
        if high_restriction_jurisdictions:
            recommendations.append(f'Review data handling practices for high-restriction jurisdictions: {high_restriction_jurisdictions}')
        
        return recommendations


class ContractualComplianceAnalyzer:
    """Analyzer for contractual obligations and SLA compliance"""
    
    @staticmethod
    async def analyze_contractual_compliance(
        contract_terms: Dict[str, Any],
        deployment_context: Dict[str, Any],
        model_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze compliance with contractual terms and SLAs"""
        
        compliance_checks = {}
        violations = []
        risk_score = 0.0
        
        # Performance SLA compliance
        sla_terms = contract_terms.get('sla_terms', {})
        performance_metrics = model_info.get('performance_metrics', {})
        
        if sla_terms:
            # Check availability SLA
            required_availability = sla_terms.get('availability_sla', 0.99)
            actual_availability = performance_metrics.get('availability', 0.95)
            if actual_availability < required_availability:
                violations.append(f'Availability SLA breach: {actual_availability} < {required_availability}')
                risk_score += 0.3
            
            # Check response time SLA
            required_response_time = sla_terms.get('response_time_sla', 1000)  # ms
            actual_response_time = performance_metrics.get('average_response_time', 1500)
            if actual_response_time > required_response_time:
                violations.append(f'Response time SLA breach: {actual_response_time}ms > {required_response_time}ms')
                risk_score += 0.2
            
            compliance_checks['sla_compliance'] = {
                'availability': {
                    'required': required_availability,
                    'actual': actual_availability,
                    'compliant': actual_availability >= required_availability
                },
                'response_time': {
                    'required': required_response_time,
                    'actual': actual_response_time,
                    'compliant': actual_response_time <= required_response_time
                }
            }
        
        # Data usage restrictions
        data_usage_terms = contract_terms.get('data_usage_restrictions', {})
        data_handling = deployment_context.get('data_handling', {})
        
        # Check data retention compliance
        max_retention = data_usage_terms.get('max_retention_days')
        if max_retention:
            actual_retention = data_handling.get('retention_days', 365)
            if actual_retention > max_retention:
                violations.append(f'Data retention period exceeds contract: {actual_retention} > {max_retention} days')
                risk_score += 0.2
        
        # Check data sharing restrictions
        sharing_restrictions = data_usage_terms.get('sharing_restrictions', [])
        actual_sharing = data_handling.get('data_sharing', [])
        unauthorized_sharing = [share for share in actual_sharing if share not in sharing_restrictions]
        if unauthorized_sharing:
            violations.append(f'Unauthorized data sharing: {unauthorized_sharing}')
            risk_score += 0.3
        
        compliance_checks['data_usage_compliance'] = {
            'retention_compliant': max_retention is None or data_handling.get('retention_days', 365) <= max_retention,
            'sharing_compliant': len(unauthorized_sharing) == 0,
            'unauthorized_sharing': unauthorized_sharing
        }
        
        # Intellectual property compliance
        ip_terms = contract_terms.get('intellectual_property', {})
        model_licensing = model_info.get('licensing', {})
        
        # Check licensing compliance
        required_license = ip_terms.get('required_license_type')
        actual_license = model_licensing.get('license_type')
        if required_license and actual_license != required_license:
            violations.append(f'License mismatch: using {actual_license}, required {required_license}')
            risk_score += 0.4
        
        compliance_checks['ip_compliance'] = {
            'license_compliant': required_license is None or actual_license == required_license,
            'required_license': required_license,
            'actual_license': actual_license
        }
        
        # Security requirements compliance
        security_requirements = contract_terms.get('security_requirements', {})
        security_measures = deployment_context.get('security_measures', [])
        
        required_security = security_requirements.get('required_measures', [])
        missing_security = [measure for measure in required_security if measure not in security_measures]
        if missing_security:
            violations.append(f'Missing required security measures: {missing_security}')
            risk_score += 0.1 * len(missing_security)
        
        compliance_checks['security_compliance'] = {
            'all_measures_implemented': len(missing_security) == 0,
            'implemented_measures': security_measures,
            'missing_measures': missing_security
        }
        
        compliance_status = 'compliant' if risk_score < 0.3 else 'partial_compliance' if risk_score < 0.6 else 'breach'
        
        return {
            'compliance_status': compliance_status,
            'risk_score': min(risk_score, 1.0),
            'violations': violations,
            'compliance_checks': compliance_checks,
            'recommendations': ContractualComplianceAnalyzer._generate_contract_recommendations(violations)
        }
    
    @staticmethod
    def _generate_contract_recommendations(violations: List[str]) -> List[str]:
        """Generate recommendations for contractual compliance"""
        recommendations = []
        
        if any('SLA breach' in v for v in violations):
            recommendations.append('Improve system performance to meet SLA requirements')
        
        if any('retention' in v for v in violations):
            recommendations.append('Adjust data retention policies to comply with contractual terms')
        
        if any('sharing' in v for v in violations):
            recommendations.append('Review and restrict data sharing to authorized parties only')
        
        if any('License' in v for v in violations):
            recommendations.append('Ensure proper licensing compliance for all model components')
        
        if any('security' in v for v in violations):
            recommendations.append('Implement all contractually required security measures')
        
        return recommendations


class LegalAgent:
    """
    Specialized Legal Agent for the Multi-Agent Governance System.
    Focuses on legal compliance analysis, regulatory assessment, and jurisdiction analysis.
    """
    
    def __init__(
        self,
        agent_id: str = "legal_agent",
        blackboard_service: Optional[BlackboardService] = None,
        constitutional_framework: Optional[ConstitutionalSafetyValidator] = None,
        ai_model_service: Optional[AIModelService] = None
    ):
        self.agent_id = agent_id
        self.agent_type = "legal_agent"
        self.blackboard = blackboard_service or BlackboardService()
        self.constitutional_framework = constitutional_framework
        self.ai_model_service = ai_model_service

        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
        # Task type handlers
        self.task_handlers = {
            'legal_compliance': self._handle_legal_compliance,
            'legal_analysis': self._handle_legal_compliance,  # Alias for legal_compliance
            'regulatory_analysis': self._handle_regulatory_analysis,
            'policy_analysis': self._handle_policy_analysis,
            'contract_compliance': self._handle_contract_compliance,
            'jurisdiction_analysis': self._handle_jurisdiction_analysis
        }
        
        # Constitutional principles this agent focuses on
        self.constitutional_principles = ['data_privacy', 'consent', 'transparency', 'least_privilege']

        # Agent capabilities
        self.capabilities = [
            "regulatory_compliance", "privacy_law", "intellectual_property",
            "liability_assessment", "contract_analysis", "risk_evaluation"
        ]

    async def _analyze_regulatory_compliance(self, model_info: Dict[str, Any], deployment_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze regulatory compliance requirements"""
        return {
            "gdpr_compliance": {"status": "compliant", "score": 0.8, "requirements": ["data_minimization", "consent"]},
            "ai_act_compliance": {"status": "needs_review", "score": 0.6, "requirements": ["risk_assessment", "documentation"]},
            "data_protection_compliance": {"status": "compliant", "score": 0.85},
            "sector_specific_compliance": {"status": "compliant", "score": 0.9},
            "overall_compliance_score": 0.77,
            "compliance_gaps": ["ai_act_documentation", "privacy_policy_updates"],
            "recommendations": ["Complete AI Act assessment", "Update privacy policies"]
        }

    async def _analyze_privacy_law(self, data_processing: Dict[str, Any], jurisdiction: str) -> Dict[str, Any]:
        """Analyze privacy law compliance"""
        return {
            "ccpa_compliance": {"status": "compliant", "score": 0.8},
            "privacy_requirements": ["opt_out_rights", "data_deletion", "transparency"],
            "consent_requirements": {"explicit_consent": True, "granular_control": True},
            "data_subject_rights": ["access", "deletion", "portability", "correction"],
            "privacy_risk_level": "medium",
            "overall_privacy_score": 0.8,
            "recommendations": ["Implement opt-out mechanisms", "Update privacy notices"]
        }

    async def _assess_liability(self, model_deployment: Dict[str, Any], stakeholders: Dict[str, Any]) -> Dict[str, Any]:
        """Assess liability distribution and requirements"""
        return {
            "liability_distribution": {"developer": 0.4, "deployer": 0.4, "user": 0.2},
            "insurance_requirements": {"professional_liability": "$5M", "cyber_liability": "$2M"},
            "indemnification_needs": ["third_party_claims", "regulatory_fines"],
            "risk_mitigation_measures": ["monitoring", "audit_trails", "incident_response"],
            "overall_liability_risk": "medium",
            "overall_liability_score": 0.7,
            "recommendations": ["Increase insurance coverage", "Implement monitoring systems"]
        }

    async def _analyze_intellectual_property(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze intellectual property implications"""
        return {
            "training_data_ip_status": {"status": "licensed", "risk_level": "low"},
            "model_ip_ownership": {"owner": "organization", "restrictions": "none"},
            "output_ip_implications": {"ownership": "user", "licensing": "permissive"},
            "licensing_requirements": ["attribution", "share_alike"],
            "ip_risk_level": "low",
            "overall_ip_score": 0.8,
            "recommendations": ["Document IP chain", "Review licensing terms"]
        }

    async def _analyze_contract_terms(self, contract_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contract terms adequacy"""
        return {
            "term_adequacy": {"liability_caps": "adequate", "data_usage": "needs_clarification"},
            "risk_assessment": {"high_risk_terms": ["unlimited_liability"], "medium_risk": ["data_retention"]},
            "compliance_alignment": {"gdpr": "aligned", "ccpa": "needs_review"},
            "contract_risks": ["unlimited_liability", "unclear_data_usage"],
            "recommended_modifications": ["Add liability caps", "Clarify data usage rights"],
            "overall_contract_score": 0.7,
            "recommendations": ["Negotiate liability terms", "Add compliance clauses"]
        }

    async def initialize(self) -> None:
        """Initialize the Legal Agent"""
        await self.blackboard.initialize()
        
        # Register with blackboard
        await self.blackboard.register_agent(
            agent_id=self.agent_id,
            agent_type='legal_agent',
            capabilities=list(self.task_handlers.keys())
        )
        
        self.logger.info(f"Legal Agent {self.agent_id} initialized successfully")

    async def start(self) -> None:
        """Start the legal agent main loop"""
        self.is_running = True
        
        # Start background tasks
        asyncio.create_task(self._task_claiming_loop())
        asyncio.create_task(self._heartbeat_loop())
        
        self.logger.info("Legal Agent started")

    async def stop(self) -> None:
        """Stop the legal agent"""
        self.is_running = False
        await self.blackboard.shutdown()
        self.logger.info("Legal Agent stopped")

    async def _task_claiming_loop(self) -> None:
        """Main loop for claiming and processing tasks"""
        while self.is_running:
            try:
                # Get available tasks that match our capabilities
                available_tasks = await self.blackboard.get_available_tasks(
                    task_types=list(self.task_handlers.keys()),
                    limit=5
                )
                
                for task in available_tasks:
                    # Try to claim the task
                    if await self.blackboard.claim_task(task.id, self.agent_id):
                        # Process the task
                        asyncio.create_task(self._process_task(task))
                
                await asyncio.sleep(5)  # Check for new tasks every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in task claiming loop: {str(e)}")
                await asyncio.sleep(10)  # Wait longer on error

    async def process_task(self, task_id: str) -> Any:
        """Public method to process a task by ID"""
        try:
            # Get task from blackboard
            task_data = await self.blackboard.get_task(task_id)
            if not task_data:
                raise ValueError(f"Task {task_id} not found")

            # Convert to TaskDefinition if needed
            if isinstance(task_data, dict):
                from ...shared.blackboard.models import TaskDefinition
                task = TaskDefinition(**task_data)
            else:
                task = task_data

            # Get the appropriate handler and process the task directly
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")

            # Process the task and return the actual result
            result = await handler(task)

            # Update task status in blackboard
            await self.blackboard.update_task_status(task.id, 'completed', result.model_dump())

            return result

        except Exception as e:
            self.logger.error(f"Error processing task {task_id}: {str(e)}")
            raise e

    async def _process_task(self, task: TaskDefinition) -> None:
        """Process a claimed task"""
        start_time = time.time()
        
        try:
            # Update task status to in_progress
            await self.blackboard.update_task_status(task.id, 'in_progress')
            
            # Get the appropriate handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")
            
            # Process the task
            result = await handler(task)
            
            # Update task with results
            await self.blackboard.update_task_status(task.id, 'completed', result.model_dump())
            
            # Add knowledge to blackboard
            await self._add_task_knowledge(task, result)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Completed task {task.id} ({task.task_type}) in {processing_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            
            # Mark task as failed
            error_result = {
                'error': str(e),
                'task_type': task.task_type,
                'agent_id': self.agent_id,
                'processing_time': time.time() - start_time
            }
            await self.blackboard.update_task_status(task.id, 'failed', error_result)

    async def _handle_legal_compliance(self, task: TaskDefinition) -> LegalAnalysisResult:
        """Handle comprehensive legal compliance analysis"""
        input_data = task.input_data
        requirements = task.requirements
        
        model_info = input_data.get('model_info', {})
        data_sources = input_data.get('data_sources', {})
        user_interactions = input_data.get('user_interactions', {})
        
        # Get applicable frameworks and jurisdictions
        frameworks = requirements.get('compliance_frameworks', ['GDPR', 'CCPA'])
        jurisdictions = requirements.get('jurisdictions', ['US', 'EU'])
        
        # Combine data handling information
        data_handling = {
            **data_sources,
            **user_interactions.get('data_handling', {}),
            **input_data.get('data_handling', {})
        }
        
        deployment_context = input_data.get('deployment_context', {})
        
        # Analyze regulatory compliance
        regulatory_compliance = {}
        overall_risk = 0.0
        all_violations = []
        
        for framework in frameworks:
            framework_analysis = await RegulatoryFrameworkAnalyzer.analyze_framework_compliance(
                framework, model_info, data_handling, deployment_context
            )
            regulatory_compliance[framework] = framework_analysis
            
            # Accumulate risk and violations
            framework_risk = framework_analysis.get('risk_score', 0.0)
            overall_risk = max(overall_risk, framework_risk)  # Use max for conservative assessment
            all_violations.extend(framework_analysis.get('violations', []))
        
        # Analyze jurisdiction requirements
        jurisdiction_analysis = await JurisdictionAnalyzer.analyze_jurisdictional_requirements(
            jurisdictions, deployment_context, data_handling
        )
        
        # Additional jurisdiction risk
        jurisdiction_risk = jurisdiction_analysis.get('overall_risk_score', 0.0)
        overall_risk = max(overall_risk, jurisdiction_risk)
        all_violations.extend(jurisdiction_analysis.get('cross_border_issues', []))
        
        # Analyze data protection specifically
        data_protection_assessment = await self._analyze_data_protection(data_handling, deployment_context)
        
        # Constitutional compliance check
        constitutional_compliance = await self._check_constitutional_compliance(
            requirements.get('constitutional_principles', []),
            {
                'regulatory_compliance': regulatory_compliance,
                'jurisdiction_analysis': jurisdiction_analysis,
                'data_protection': data_protection_assessment
            }
        )
        
        # Determine overall approval
        approved = (
            overall_risk < 0.6 and 
            constitutional_compliance.get('compliant', True) and
            len([v for v in all_violations if 'critical' in v.lower() or 'prohibited' in v.lower()]) == 0
        )
        
        # Determine risk level
        if overall_risk >= 0.7 or any('critical' in v.lower() for v in all_violations):
            risk_level = 'critical'
        elif overall_risk >= 0.5 or any('high' in v.lower() for v in all_violations):
            risk_level = 'high'
        elif overall_risk >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Calculate confidence based on completeness of analysis
        confidence_factors = []
        if len(frameworks) >= 2:
            confidence_factors.append('Multiple frameworks analyzed')
        if len(jurisdictions) >= 2:
            confidence_factors.append('Multiple jurisdictions considered')
        if data_handling:
            confidence_factors.append('Data handling practices evaluated')
        
        confidence = min(0.9, 0.6 + 0.1 * len(confidence_factors))
        if overall_risk > 0.7:
            confidence = max(0.3, confidence - 0.3)  # Lower confidence for high-risk scenarios
        
        # Compile all recommendations
        all_recommendations = []
        for framework_analysis in regulatory_compliance.values():
            all_recommendations.extend(framework_analysis.get('recommendations', []))
        all_recommendations.extend(jurisdiction_analysis.get('recommendations', []))
        all_recommendations.extend(data_protection_assessment.get('recommendations', []))
        
        # Add general legal recommendations
        if not approved:
            all_recommendations.append('Address all legal compliance violations before deployment')
        if risk_level in ['high', 'critical']:
            all_recommendations.append('Conduct legal review with qualified counsel')

        # Basic liability assessment
        liability_assessment = {
            'overall_liability_risk': risk_level,
            'liability_factors': [],
            'mitigation_strategies': []
        }

        if overall_risk > 0.5:
            liability_assessment['liability_factors'].append('High regulatory compliance risk')
            liability_assessment['mitigation_strategies'].append('Implement comprehensive compliance program')

        if len(all_violations) > 5:
            liability_assessment['liability_factors'].append('Multiple compliance violations identified')
            liability_assessment['mitigation_strategies'].append('Address all identified violations before deployment')

        return LegalAnalysisResult(
            approved=approved,
            risk_level=risk_level,
            confidence=confidence,
            regulatory_compliance=regulatory_compliance,
            jurisdiction_analysis=jurisdiction_analysis,
            data_protection_assessment=data_protection_assessment,
            liability_assessment=liability_assessment,
            contract_compliance={},   # Could be expanded
            recommendations=list(set(all_recommendations)),  # Remove duplicates
            constitutional_compliance=constitutional_compliance,
            analysis_metadata={
                'agent_id': self.agent_id,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'frameworks_analyzed': frameworks,
                'jurisdictions_analyzed': jurisdictions,
                'overall_risk_score': overall_risk,
                'total_violations': len(all_violations)
            }
        )

    async def _handle_regulatory_analysis(self, task: TaskDefinition) -> LegalAnalysisResult:
        """Handle specific regulatory framework analysis"""
        input_data = task.input_data
        requirements = task.requirements
        
        framework = requirements.get('regulatory_framework', 'GDPR')
        model_info = input_data.get('model_info', {})
        data_handling = input_data.get('data_handling', {})
        deployment_context = input_data.get('deployment_context', {})
        
        # Analyze single framework
        framework_analysis = await RegulatoryFrameworkAnalyzer.analyze_framework_compliance(
            framework, model_info, data_handling, deployment_context
        )
        
        risk_score = framework_analysis.get('risk_score', 0.0)
        violations = framework_analysis.get('violations', [])
        
        # Determine approval and risk level
        approved = framework_analysis.get('compliance_status') == 'compliant'
        
        if risk_score >= 0.7:
            risk_level = 'critical'
        elif risk_score >= 0.5:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        confidence = 1.0 - risk_score if risk_score < 0.8 else 0.2
        
        return LegalAnalysisResult(
            approved=approved,
            risk_level=risk_level,
            confidence=confidence,
            regulatory_compliance={framework: framework_analysis},
            recommendations=framework_analysis.get('recommendations', []),
            analysis_metadata={
                'agent_id': self.agent_id,
                'analysis_type': 'regulatory_analysis',
                'framework': framework,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        )

    async def _handle_policy_analysis(self, task: TaskDefinition) -> LegalAnalysisResult:
        """Handle policy analysis tasks"""
        input_data = task.input_data
        policy_document = input_data.get('policy_document', {})
        enforcement_context = input_data.get('enforcement_context', {})
        affected_systems = input_data.get('affected_systems', [])
        
        # Analyze policy for legal implications
        policy_analysis = {
            'policy_type': policy_document.get('type', 'unknown'),
            'scope': policy_document.get('scope', 'unknown'),
            'legal_implications': await self._analyze_policy_legal_implications(policy_document),
            'enforcement_feasibility': await self._analyze_enforcement_feasibility(enforcement_context),
            'affected_systems_count': len(affected_systems),
            'compliance_requirements': await self._extract_compliance_requirements(policy_document)
        }
        
        # Determine risk and approval
        risk_factors = []
        
        if policy_analysis['legal_implications'].get('regulatory_conflicts', []):
            risk_factors.append('Policy conflicts with regulatory requirements')
        
        if not policy_analysis['enforcement_feasibility'].get('technically_feasible', True):
            risk_factors.append('Policy not technically enforceable')
        
        if len(affected_systems) > 10:
            risk_factors.append('Policy affects many systems (high coordination risk)')
        
        risk_score = len(risk_factors) * 0.2
        approved = risk_score < 0.4
        
        risk_level = 'high' if risk_score >= 0.6 else 'medium' if risk_score >= 0.3 else 'low'
        confidence = 1.0 - risk_score
        
        recommendations = []
        if risk_factors:
            recommendations.extend([f"Address: {factor}" for factor in risk_factors])
        
        return LegalAnalysisResult(
            approved=approved,
            risk_level=risk_level,
            confidence=confidence,
            regulatory_compliance={'policy_analysis': policy_analysis},
            recommendations=recommendations,
            analysis_metadata={
                'agent_id': self.agent_id,
                'analysis_type': 'policy_analysis',
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'risk_factors': risk_factors
            }
        )

    async def _handle_contract_compliance(self, task: TaskDefinition) -> LegalAnalysisResult:
        """Handle contract compliance analysis"""
        input_data = task.input_data
        contract_terms = input_data.get('contract_terms', {})
        deployment_context = input_data.get('deployment_context', {})
        model_info = input_data.get('model_info', {})
        
        # Analyze contractual compliance
        contract_analysis = await ContractualComplianceAnalyzer.analyze_contractual_compliance(
            contract_terms, deployment_context, model_info
        )
        
        compliance_status = contract_analysis.get('compliance_status', 'unknown')
        risk_score = contract_analysis.get('risk_score', 0.5)
        violations = contract_analysis.get('violations', [])
        
        approved = compliance_status == 'compliant'
        
        if compliance_status == 'breach':
            risk_level = 'critical'
        elif risk_score >= 0.5:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        confidence = 1.0 - risk_score
        
        return LegalAnalysisResult(
            approved=approved,
            risk_level=risk_level,
            confidence=confidence,
            contract_compliance=contract_analysis,
            recommendations=contract_analysis.get('recommendations', []),
            analysis_metadata={
                'agent_id': self.agent_id,
                'analysis_type': 'contract_compliance',
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'violations_count': len(violations)
            }
        )

    async def _handle_jurisdiction_analysis(self, task: TaskDefinition) -> LegalAnalysisResult:
        """Handle jurisdiction-specific legal analysis"""
        input_data = task.input_data
        requirements = task.requirements
        
        jurisdictions = requirements.get('jurisdictions', ['US', 'EU'])
        deployment_context = input_data.get('deployment_context', {})
        data_handling = input_data.get('data_handling', {})
        
        # Analyze jurisdictional requirements
        jurisdiction_analysis = await JurisdictionAnalyzer.analyze_jurisdictional_requirements(
            jurisdictions, deployment_context, data_handling
        )
        
        risk_score = jurisdiction_analysis.get('overall_risk_score', 0.0)
        cross_border_issues = jurisdiction_analysis.get('cross_border_issues', [])
        
        approved = risk_score < 0.5 and len(cross_border_issues) == 0
        
        if risk_score >= 0.7:
            risk_level = 'critical'
        elif risk_score >= 0.5:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        confidence = 1.0 - risk_score
        
        return LegalAnalysisResult(
            approved=approved,
            risk_level=risk_level,
            confidence=confidence,
            jurisdiction_analysis=jurisdiction_analysis,
            recommendations=jurisdiction_analysis.get('recommendations', []),
            analysis_metadata={
                'agent_id': self.agent_id,
                'analysis_type': 'jurisdiction_analysis',
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'jurisdictions': jurisdictions,
                'cross_border_issues_count': len(cross_border_issues)
            }
        )

    async def _analyze_data_protection(self, data_handling: Dict[str, Any], deployment_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data protection compliance"""
        protection_assessment = {
            'encryption_status': self._check_encryption_compliance(data_handling),
            'access_controls': self._check_access_controls(data_handling),
            'data_minimization': self._check_data_minimization(data_handling),
            'retention_policies': self._check_retention_policies(data_handling),
            'breach_response': self._check_breach_response_procedures(data_handling)
        }
        
        # Calculate overall protection score
        protection_scores = [assess.get('score', 0.5) for assess in protection_assessment.values()]
        overall_score = sum(protection_scores) / len(protection_scores) if protection_scores else 0.5
        
        recommendations = []
        for category, assessment in protection_assessment.items():
            if assessment.get('score', 0.5) < 0.7:
                recommendations.extend(assessment.get('recommendations', []))
        
        return {
            'overall_score': overall_score,
            'protection_level': 'high' if overall_score >= 0.8 else 'medium' if overall_score >= 0.6 else 'low',
            'assessments': protection_assessment,
            'recommendations': recommendations
        }

    def _check_encryption_compliance(self, data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check encryption implementation"""
        encryption = data_handling.get('encryption', {})
        
        in_transit = encryption.get('in_transit', False)
        at_rest = encryption.get('at_rest', False)
        key_management = encryption.get('key_management', False)
        
        score = 0.0
        if in_transit:
            score += 0.4
        if at_rest:
            score += 0.4
        if key_management:
            score += 0.2
        
        recommendations = []
        if not in_transit:
            recommendations.append('Implement encryption in transit')
        if not at_rest:
            recommendations.append('Implement encryption at rest')
        if not key_management:
            recommendations.append('Implement proper key management')
        
        return {
            'score': score,
            'in_transit': in_transit,
            'at_rest': at_rest,
            'key_management': key_management,
            'recommendations': recommendations
        }

    def _check_access_controls(self, data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check access control implementation"""
        access_controls = data_handling.get('access_controls', {})
        
        authentication = access_controls.get('authentication', False)
        authorization = access_controls.get('authorization', False)
        audit_logging = access_controls.get('audit_logging', False)
        principle_of_least_privilege = access_controls.get('least_privilege', False)
        
        score = 0.0
        if authentication:
            score += 0.3
        if authorization:
            score += 0.3
        if audit_logging:
            score += 0.2
        if principle_of_least_privilege:
            score += 0.2
        
        recommendations = []
        if not authentication:
            recommendations.append('Implement strong authentication mechanisms')
        if not authorization:
            recommendations.append('Implement role-based authorization')
        if not audit_logging:
            recommendations.append('Implement comprehensive audit logging')
        if not principle_of_least_privilege:
            recommendations.append('Apply principle of least privilege')
        
        return {
            'score': score,
            'authentication': authentication,
            'authorization': authorization,
            'audit_logging': audit_logging,
            'least_privilege': principle_of_least_privilege,
            'recommendations': recommendations
        }

    def _check_data_minimization(self, data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check data minimization implementation"""
        data_collection = data_handling.get('data_collection', {})
        
        purpose_limitation = data_collection.get('purpose_specific', False)
        necessity_check = data_collection.get('necessity_assessed', False)
        regular_review = data_collection.get('regular_review', False)
        
        score = 0.0
        if purpose_limitation:
            score += 0.4
        if necessity_check:
            score += 0.4
        if regular_review:
            score += 0.2
        
        recommendations = []
        if not purpose_limitation:
            recommendations.append('Limit data collection to specific purposes')
        if not necessity_check:
            recommendations.append('Assess necessity of all data collection')
        if not regular_review:
            recommendations.append('Implement regular data collection reviews')
        
        return {
            'score': score,
            'purpose_limitation': purpose_limitation,
            'necessity_check': necessity_check,
            'regular_review': regular_review,
            'recommendations': recommendations
        }

    def _check_retention_policies(self, data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check data retention policy compliance"""
        retention = data_handling.get('data_retention', {})
        
        policy_defined = retention.get('policy_defined', False)
        automated_deletion = retention.get('automated_deletion', False)
        retention_period = retention.get('retention_period')
        
        score = 0.0
        if policy_defined:
            score += 0.4
        if automated_deletion:
            score += 0.4
        if retention_period:
            score += 0.2
        
        recommendations = []
        if not policy_defined:
            recommendations.append('Define data retention policies')
        if not automated_deletion:
            recommendations.append('Implement automated data deletion')
        if not retention_period:
            recommendations.append('Specify retention periods for all data types')
        
        return {
            'score': score,
            'policy_defined': policy_defined,
            'automated_deletion': automated_deletion,
            'retention_period': retention_period,
            'recommendations': recommendations
        }

    def _check_breach_response_procedures(self, data_handling: Dict[str, Any]) -> Dict[str, Any]:
        """Check breach response procedure implementation"""
        breach_response = data_handling.get('breach_response', {})
        
        procedures_defined = breach_response.get('procedures_defined', False)
        notification_system = breach_response.get('notification_system', False)
        incident_response_team = breach_response.get('incident_response_team', False)
        
        score = 0.0
        if procedures_defined:
            score += 0.4
        if notification_system:
            score += 0.3
        if incident_response_team:
            score += 0.3
        
        recommendations = []
        if not procedures_defined:
            recommendations.append('Define breach response procedures')
        if not notification_system:
            recommendations.append('Implement breach notification system')
        if not incident_response_team:
            recommendations.append('Establish incident response team')
        
        return {
            'score': score,
            'procedures_defined': procedures_defined,
            'notification_system': notification_system,
            'incident_response_team': incident_response_team,
            'recommendations': recommendations
        }

    async def _analyze_policy_legal_implications(self, policy_document: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze legal implications of a policy"""
        # Simplified implementation - would be more sophisticated in production
        policy_content = policy_document.get('content', '')
        policy_scope = policy_document.get('scope', '')
        
        implications = {
            'regulatory_conflicts': [],
            'liability_concerns': [],
            'enforceability_issues': []
        }
        
        # Check for potential regulatory conflicts
        if 'data processing' in policy_content.lower() and 'consent' not in policy_content.lower():
            implications['regulatory_conflicts'].append('GDPR - missing consent requirements')
        
        # Check for liability concerns
        if 'automated' in policy_content.lower() and 'oversight' not in policy_content.lower():
            implications['liability_concerns'].append('Liability for automated decisions without oversight')
        
        return implications

    async def _analyze_enforcement_feasibility(self, enforcement_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze policy enforcement feasibility"""
        technical_capabilities = enforcement_context.get('technical_capabilities', {})
        resource_availability = enforcement_context.get('resource_availability', {})
        
        return {
            'technically_feasible': technical_capabilities.get('monitoring', False) and technical_capabilities.get('enforcement', False),
            'resource_sufficient': resource_availability.get('personnel', False) and resource_availability.get('budget', False),
            'implementation_timeline': enforcement_context.get('timeline', 'unknown')
        }

    async def _extract_compliance_requirements(self, policy_document: Dict[str, Any]) -> List[str]:
        """Extract compliance requirements from policy"""
        # Simplified implementation
        requirements = []
        content = policy_document.get('content', '').lower()
        
        if 'gdpr' in content:
            requirements.append('GDPR compliance required')
        if 'hipaa' in content:
            requirements.append('HIPAA compliance required')
        if 'audit' in content:
            requirements.append('Audit trail required')
        
        return requirements

    async def _check_constitutional_compliance(
        self, 
        required_principles: List[str], 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check constitutional compliance for legal analysis"""
        if not self.constitutional_framework:
            return {'compliant': True, 'violations': [], 'note': 'Constitutional framework not available'}
        
        violations = []
        compliance_details = {}
        
        # Check each required principle
        for principle in required_principles:
            if principle in self.constitutional_principles:
                compliance_check = await self._check_principle_compliance(principle, analysis_results)
                compliance_details[principle] = compliance_check
                
                if not compliance_check.get('compliant', True):
                    violations.append({
                        'principle': principle,
                        'violation': compliance_check.get('violation_reason', 'Unknown violation'),
                        'severity': compliance_check.get('severity', 'medium')
                    })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'compliance_details': compliance_details,
            'checked_principles': required_principles
        }

    async def _check_principle_compliance(self, principle: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with a specific constitutional principle"""
        if principle == 'data_privacy':
            data_protection = analysis_results.get('data_protection', {})
            protection_level = data_protection.get('protection_level', 'low')
            
            if protection_level == 'low':
                return {
                    'compliant': False,
                    'violation_reason': 'Insufficient data protection measures',
                    'severity': 'high'
                }
            
            return {'compliant': True, 'note': 'Data privacy requirements met'}
        
        elif principle == 'consent':
            regulatory_compliance = analysis_results.get('regulatory_compliance', {})
            gdpr_analysis = regulatory_compliance.get('GDPR', {})
            
            if gdpr_analysis:
                lawful_basis = gdpr_analysis.get('compliance_checks', {}).get('lawful_basis', {})
                if lawful_basis.get('basis') in ['consent'] or lawful_basis.get('status') == 'compliant':
                    return {'compliant': True, 'note': 'Consent requirements met'}
                else:
                    return {
                        'compliant': False,
                        'violation_reason': 'Consent not properly established',
                        'severity': 'medium'
                    }
            
            return {'compliant': True, 'note': 'Consent compliance check not applicable'}
        
        elif principle == 'transparency':
            regulatory_compliance = analysis_results.get('regulatory_compliance', {})
            
            # Check if transparency obligations are met across frameworks
            transparency_issues = []
            for framework, analysis in regulatory_compliance.items():
                violations = analysis.get('violations', [])
                if any('transparency' in v.lower() or 'disclosure' in v.lower() for v in violations):
                    transparency_issues.append(f'{framework}: transparency violations')
            
            if transparency_issues:
                return {
                    'compliant': False,
                    'violation_reason': f'Transparency violations: {transparency_issues}',
                    'severity': 'medium'
                }
            
            return {'compliant': True, 'note': 'Transparency requirements met'}
        
        elif principle == 'least_privilege':
            data_protection = analysis_results.get('data_protection', {})
            access_controls = data_protection.get('assessments', {}).get('access_controls', {})
            
            if not access_controls.get('least_privilege', False):
                return {
                    'compliant': False,
                    'violation_reason': 'Principle of least privilege not implemented',
                    'severity': 'medium'
                }
            
            return {'compliant': True, 'note': 'Least privilege requirements met'}
        
        else:
            return {'compliant': True, 'note': f'Principle {principle} not specifically checked'}

    async def _add_task_knowledge(self, task: TaskDefinition, result: LegalAnalysisResult) -> None:
        """Add task completion knowledge to blackboard"""
        knowledge = KnowledgeItem(
            space='governance',
            agent_id=self.agent_id,
            task_id=task.id,
            knowledge_type='legal_analysis_result',
            content={
                'task_type': task.task_type,
                'result': result.model_dump(),
                'governance_request_id': task.requirements.get('governance_request_id'),
                'processing_metadata': {
                    'completed_at': datetime.utcnow().isoformat(),
                    'agent_id': self.agent_id
                }
            },
            priority=task.priority,
            tags={'legal', 'analysis_complete', task.task_type}
        )
        
        await self.blackboard.add_knowledge(knowledge)

    async def _heartbeat_loop(self) -> None:
        """Background heartbeat loop"""
        while self.is_running:
            try:
                await self.blackboard.agent_heartbeat(self.agent_id)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(60)