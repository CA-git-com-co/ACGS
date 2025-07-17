"""
Compliance Checker - Validates content for constitutional compliance
Constitutional Hash: cdd01ef066bc6cf2
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

from ..models.schemas import (
    ComplianceCheck, 
    ComplianceLevel, 
    MessageRole,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class ComplianceChecker:
    """
    Validates conversation content for constitutional compliance.
    Implements multi-level compliance checking with configurable strictness.
    """
    
    def __init__(self):
        """Initialize compliance checker with rules and patterns."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Compliance rules and patterns
        self._setup_compliance_rules()
        
        # Content analysis patterns
        self._setup_content_patterns()
        
        # Scoring weights
        self.scoring_weights = {
            "toxicity": 0.3,
            "bias": 0.2,
            "safety": 0.25,
            "constitutional": 0.25
        }
    
    def _setup_compliance_rules(self):
        """Setup constitutional compliance rules."""
        # Prohibited content patterns
        self.prohibited_patterns = [
            r'\b(hate|discriminat|racist|sexist)\b',
            r'\b(violence|kill|murder|harm)\b',
            r'\b(illegal|criminal|fraud)\b',
            r'\b(nsfw|explicit|inappropriate)\b'
        ]
        
        # Sensitive topics that require careful handling
        self.sensitive_topics = [
            r'\b(politics|political|election|government)\b',
            r'\b(religion|religious|faith|belief)\b',
            r'\b(medical|health|treatment|diagnosis)\b',
            r'\b(legal|law|lawsuit|attorney)\b'
        ]
        
        # Constitutional compliance indicators
        self.constitutional_indicators = [
            r'\bconstitutional\b',
            r'\brights\b',
            r'\bfreedom\b',
            r'\bequality\b',
            r'\bfairness\b'
        ]
    
    def _setup_content_patterns(self):
        """Setup content analysis patterns."""
        # Positive indicators
        self.positive_patterns = [
            r'\b(helpful|assist|support|guide)\b',
            r'\b(respectful|polite|considerate)\b',
            r'\b(accurate|correct|truthful)\b',
            r'\b(safe|secure|protected)\b'
        ]
        
        # Quality indicators
        self.quality_patterns = [
            r'\b(clear|concise|detailed|comprehensive)\b',
            r'\b(relevant|appropriate|suitable)\b',
            r'\b(professional|formal|proper)\b'
        ]
        
        # Warning indicators
        self.warning_patterns = [
            r'\b(warning|caution|alert|notice)\b',
            r'\b(potential|possible|might|could)\b',
            r'\b(uncertain|unsure|unclear)\b'
        ]
    
    async def check_message_compliance(
        self, 
        content: str, 
        role: MessageRole, 
        compliance_level: ComplianceLevel = ComplianceLevel.MODERATE,
        context: Optional[str] = None
    ) -> ComplianceCheck:
        """
        Check message compliance with constitutional requirements.
        
        Args:
            content: Message content to check
            role: Message role (user/assistant/system)
            compliance_level: Strictness level
            context: Optional context information
            
        Returns:
            ComplianceCheck with detailed assessment
        """
        try:
            # Initialize compliance check
            violations = []
            categories = {}
            
            # Check for prohibited content
            prohibited_score = self._check_prohibited_content(content)
            categories["prohibited_content"] = prohibited_score
            if prohibited_score > self._get_threshold(compliance_level, "prohibited"):
                violations.append("prohibited_content")
            
            # Check for sensitive topics
            sensitive_score = self._check_sensitive_topics(content)
            categories["sensitive_topics"] = sensitive_score
            if sensitive_score > self._get_threshold(compliance_level, "sensitive"):
                violations.append("sensitive_topics")
            
            # Check constitutional compliance
            constitutional_score = self._check_constitutional_compliance(content)
            categories["constitutional_compliance"] = constitutional_score
            
            # Check content quality
            quality_score = self._check_content_quality(content)
            categories["content_quality"] = quality_score
            
            # Check role-specific compliance
            role_score = self._check_role_compliance(content, role)
            categories["role_compliance"] = role_score
            
            # Calculate overall compliance score
            overall_score = self._calculate_overall_score(categories)
            
            # Determine compliance status
            compliant = len(violations) == 0 and overall_score > 0.7
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                compliant, violations, overall_score, compliance_level
            )
            
            return ComplianceCheck(
                compliant=compliant,
                score=overall_score,
                violations=violations,
                categories=categories,
                recommendation=recommendation,
                constitutional_hash=self.constitutional_hash
            )
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return ComplianceCheck(
                compliant=False,
                score=0.0,
                violations=["compliance_check_error"],
                categories={"error": 1.0},
                recommendation="Content could not be validated for compliance",
                constitutional_hash=self.constitutional_hash
            )
    
    def _check_prohibited_content(self, content: str) -> float:
        """Check for prohibited content patterns."""
        content_lower = content.lower()
        matches = 0
        
        for pattern in self.prohibited_patterns:
            if re.search(pattern, content_lower):
                matches += 1
        
        # Return score based on matches (higher = more problematic)
        return min(1.0, matches / len(self.prohibited_patterns))
    
    def _check_sensitive_topics(self, content: str) -> float:
        """Check for sensitive topics that require careful handling."""
        content_lower = content.lower()
        matches = 0
        
        for pattern in self.sensitive_topics:
            if re.search(pattern, content_lower):
                matches += 1
        
        # Return score based on matches
        return min(1.0, matches / len(self.sensitive_topics))
    
    def _check_constitutional_compliance(self, content: str) -> float:
        """Check for constitutional compliance indicators."""
        content_lower = content.lower()
        matches = 0
        
        for pattern in self.constitutional_indicators:
            if re.search(pattern, content_lower):
                matches += 1
        
        # Return positive score for constitutional indicators
        return min(1.0, matches / len(self.constitutional_indicators))
    
    def _check_content_quality(self, content: str) -> float:
        """Check content quality indicators."""
        content_lower = content.lower()
        positive_matches = 0
        quality_matches = 0
        
        for pattern in self.positive_patterns:
            if re.search(pattern, content_lower):
                positive_matches += 1
        
        for pattern in self.quality_patterns:
            if re.search(pattern, content_lower):
                quality_matches += 1
        
        # Calculate quality score
        total_patterns = len(self.positive_patterns) + len(self.quality_patterns)
        total_matches = positive_matches + quality_matches
        
        return min(1.0, total_matches / total_patterns)
    
    def _check_role_compliance(self, content: str, role: MessageRole) -> float:
        """Check role-specific compliance requirements."""
        content_lower = content.lower()
        
        if role == MessageRole.ASSISTANT:
            # Assistant should be helpful and professional
            helpful_patterns = [
                r'\b(help|assist|support|guide|explain)\b',
                r'\b(understand|clarify|provide|offer)\b'
            ]
            
            matches = 0
            for pattern in helpful_patterns:
                if re.search(pattern, content_lower):
                    matches += 1
            
            return min(1.0, matches / len(helpful_patterns))
        
        elif role == MessageRole.USER:
            # User messages should be respectful
            respectful_patterns = [
                r'\b(please|thank|thanks|appreciate)\b',
                r'\b(help|assist|support|guide)\b'
            ]
            
            # Check for disrespectful patterns
            disrespectful_patterns = [
                r'\b(stupid|idiot|dumb|useless)\b',
                r'\b(shut up|go away|leave me alone)\b'
            ]
            
            respectful_matches = 0
            for pattern in respectful_patterns:
                if re.search(pattern, content_lower):
                    respectful_matches += 1
            
            disrespectful_matches = 0
            for pattern in disrespectful_patterns:
                if re.search(pattern, content_lower):
                    disrespectful_matches += 1
            
            # Return score (higher is better)
            if disrespectful_matches > 0:
                return 0.3
            elif respectful_matches > 0:
                return 1.0
            else:
                return 0.7  # Neutral
        
        elif role == MessageRole.SYSTEM:
            # System messages should be clear and authoritative
            return 1.0  # System messages are assumed compliant
        
        return 0.5  # Default neutral score
    
    def _calculate_overall_score(self, categories: Dict[str, float]) -> float:
        """Calculate overall compliance score."""
        # Weight the categories
        score = 0.0
        
        # Lower prohibited content and sensitive topics are better
        score += (1.0 - categories.get("prohibited_content", 0.0)) * 0.3
        score += (1.0 - categories.get("sensitive_topics", 0.0)) * 0.2
        
        # Higher constitutional compliance and quality are better
        score += categories.get("constitutional_compliance", 0.0) * 0.25
        score += categories.get("content_quality", 0.0) * 0.15
        score += categories.get("role_compliance", 0.0) * 0.1
        
        return min(1.0, max(0.0, score))
    
    def _get_threshold(self, level: ComplianceLevel, category: str) -> float:
        """Get compliance threshold for level and category."""
        thresholds = {
            ComplianceLevel.STRICT: {
                "prohibited": 0.1,
                "sensitive": 0.3
            },
            ComplianceLevel.MODERATE: {
                "prohibited": 0.3,
                "sensitive": 0.5
            },
            ComplianceLevel.PERMISSIVE: {
                "prohibited": 0.5,
                "sensitive": 0.7
            }
        }
        
        return thresholds.get(level, {}).get(category, 0.5)
    
    def _generate_recommendation(
        self, 
        compliant: bool, 
        violations: List[str], 
        score: float, 
        level: ComplianceLevel
    ) -> str:
        """Generate compliance recommendation."""
        if compliant and score > 0.9:
            return "Content is fully compliant and meets all constitutional requirements"
        elif compliant and score > 0.7:
            return "Content is compliant but could be improved for better constitutional alignment"
        elif not compliant and "prohibited_content" in violations:
            return "Content contains prohibited material and should be revised"
        elif not compliant and "sensitive_topics" in violations:
            return "Content addresses sensitive topics and requires careful review"
        else:
            return "Content requires review and improvement for constitutional compliance"
    
    async def check_conversation_compliance(
        self, 
        messages: List[Dict[str, str]], 
        compliance_level: ComplianceLevel = ComplianceLevel.MODERATE
    ) -> Dict[str, any]:
        """Check compliance for entire conversation."""
        try:
            total_messages = len(messages)
            compliant_messages = 0
            total_score = 0.0
            violations_summary = {}
            
            for message in messages:
                role = MessageRole(message.get("role", "user"))
                content = message.get("content", "")
                
                check = await self.check_message_compliance(
                    content, role, compliance_level
                )
                
                if check.compliant:
                    compliant_messages += 1
                
                total_score += check.score
                
                # Aggregate violations
                for violation in check.violations:
                    violations_summary[violation] = violations_summary.get(violation, 0) + 1
            
            compliance_rate = compliant_messages / total_messages if total_messages > 0 else 0.0
            average_score = total_score / total_messages if total_messages > 0 else 0.0
            
            return {
                "total_messages": total_messages,
                "compliant_messages": compliant_messages,
                "compliance_rate": compliance_rate,
                "average_score": average_score,
                "violations_summary": violations_summary,
                "constitutional_hash": self.constitutional_hash
            }
            
        except Exception as e:
            logger.error(f"Conversation compliance check failed: {e}")
            return {
                "error": str(e),
                "constitutional_hash": self.constitutional_hash
            }