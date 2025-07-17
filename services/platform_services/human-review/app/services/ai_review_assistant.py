"""
AI Review Assistant - Advanced AI-powered review assistance
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, AutoModel
)
from sentence_transformers import SentenceTransformer
import json
import redis.asyncio as redis
from sklearn.metrics.pairwise import cosine_similarity
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy
from collections import defaultdict
import re
import hashlib

from ..models.schemas import (
    ReviewTask,
    AIAnalysis,
    AIInsight,
    ConstitutionalCompliance,
    BiasAnalysis,
    SentimentAnalysis,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class AIReviewAssistant:
    """Advanced AI assistant for human review processes."""
    
    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = None
        self.redis_url = redis_url
        
        # Initialize NLP models
        self._initialize_models()
        
        # Constitutional principles for evaluation
        self.constitutional_principles = [
            "respects human dignity and rights",
            "promotes fairness and equality",
            "avoids discrimination and bias",
            "protects privacy and autonomy",
            "promotes beneficial outcomes",
            "maintains transparency and accountability",
            "respects cultural diversity",
            "promotes democratic values"
        ]
        
        # Bias detection patterns
        self.bias_patterns = {
            'gender': [
                r'\b(he|she|his|her|him|man|woman|male|female|guy|girl|boy|girl)\b',
                r'\b(masculine|feminine|manly|womanly|girly|boyish)\b'
            ],
            'racial': [
                r'\b(race|racial|ethnic|nationality|heritage|ancestry)\b',
                r'\b(white|black|asian|hispanic|latino|native|indigenous)\b'
            ],
            'age': [
                r'\b(young|old|elderly|senior|junior|mature|age|aged)\b',
                r'\b(millennial|boomer|gen-z|generation)\b'
            ],
            'socioeconomic': [
                r'\b(poor|rich|wealthy|poverty|class|income|salary|wage)\b',
                r'\b(upper|middle|lower|working|elite|privileged)\b'
            ],
            'religious': [
                r'\b(christian|muslim|jewish|hindu|buddhist|atheist|religious)\b',
                r'\b(faith|belief|spiritual|sacred|holy|divine)\b'
            ],
            'disability': [
                r'\b(disabled|handicapped|impaired|disorder|condition)\b',
                r'\b(blind|deaf|mental|physical|cognitive|autism)\b'
            ]
        }
        
    def _initialize_models(self):
        """Initialize AI models for review assistance."""
        try:
            logger.info("Initializing AI review models...")
            
            # 1. Constitutional compliance model
            self.constitutional_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 2. Bias detection model
            self.bias_classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # 3. Sentiment analysis model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # 4. Zero-shot classification for general insights
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # 5. Named Entity Recognition for privacy detection
            self.nlp = spacy.load("en_core_web_sm")
            
            # 6. Readability analysis
            self.readability_analyzer = self._create_readability_analyzer()
            
            # 7. Hate speech detection
            self.hate_speech_detector = pipeline(
                "text-classification",
                model="martin-ha/toxic-comment-model",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("AI review models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def _create_readability_analyzer(self):
        """Create readability analysis function."""
        def analyze_readability(text: str) -> Dict[str, float]:
            try:
                return {
                    'flesch_reading_ease': flesch_reading_ease(text),
                    'flesch_kincaid_grade': flesch_kincaid_grade(text),
                    'word_count': len(text.split()),
                    'sentence_count': len(text.split('.'))
                }
            except Exception as e:
                logger.error(f"Readability analysis failed: {e}")
                return {
                    'flesch_reading_ease': 0.0,
                    'flesch_kincaid_grade': 0.0,
                    'word_count': 0,
                    'sentence_count': 0
                }
        
        return analyze_readability
    
    async def initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise
    
    async def analyze_content(
        self,
        content: str,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> AIAnalysis:
        """Comprehensive AI analysis of content."""
        try:
            start_time = datetime.utcnow()
            
            # Run all analyses in parallel
            analyses = await asyncio.gather(
                self._analyze_constitutional_compliance(content, context),
                self._analyze_bias(content),
                self._analyze_sentiment(content),
                self._analyze_content_safety(content),
                self._analyze_readability(content),
                self._analyze_privacy_concerns(content),
                self._generate_insights(content, context),
                return_exceptions=True
            )
            
            # Extract results
            constitutional_compliance = analyses[0] if not isinstance(analyses[0], Exception) else self._get_default_compliance()
            bias_analysis = analyses[1] if not isinstance(analyses[1], Exception) else self._get_default_bias()
            sentiment_analysis = analyses[2] if not isinstance(analyses[2], Exception) else self._get_default_sentiment()
            safety_analysis = analyses[3] if not isinstance(analyses[3], Exception) else {}
            readability_analysis = analyses[4] if not isinstance(analyses[4], Exception) else {}
            privacy_analysis = analyses[5] if not isinstance(analyses[5], Exception) else {}
            insights = analyses[6] if not isinstance(analyses[6], Exception) else []
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                constitutional_compliance,
                bias_analysis,
                sentiment_analysis,
                safety_analysis,
                readability_analysis
            )
            
            # Create comprehensive analysis
            analysis = AIAnalysis(
                overall_score=overall_score,
                insights=insights,
                constitutional_compliance=constitutional_compliance,
                bias_analysis=bias_analysis,
                sentiment_analysis=sentiment_analysis,
                safety_analysis=safety_analysis,
                readability_analysis=readability_analysis,
                privacy_analysis=privacy_analysis,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                constitutional_hash=self.constitutional_hash
            )
            
            # Cache analysis
            await self._cache_analysis(content, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise
    
    async def _analyze_constitutional_compliance(
        self,
        content: str,
        context: Dict[str, Any] = None
    ) -> ConstitutionalCompliance:
        """Analyze constitutional compliance."""
        try:
            # Encode content and principles
            content_embedding = self.constitutional_model.encode([content])
            principle_embeddings = self.constitutional_model.encode(self.constitutional_principles)
            
            # Calculate similarity scores
            similarities = cosine_similarity(content_embedding, principle_embeddings)[0]
            
            # Analyze for violations
            violations = []
            recommendations = []
            
            # Check for explicit violations
            violation_patterns = [
                (r'\b(discriminat|bias|prejudic|stereotype)\w*\b', 'Potential discrimination detected'),
                (r'\b(harm|damage|hurt|abuse|violence)\w*\b', 'Potential harmful content'),
                (r'\b(illegal|unlawful|criminal)\w*\b', 'Potential illegal content reference'),
                (r'\b(private|confidential|secret|personal)\w*\b', 'Potential privacy concern')
            ]
            
            content_lower = content.lower()
            for pattern, violation in violation_patterns:
                if re.search(pattern, content_lower):
                    violations.append(violation)
                    recommendations.append(f"Review and potentially modify content related to: {violation}")
            
            # Calculate compliance score
            compliance_score = float(np.mean(similarities))
            
            # Adjust score based on violations
            if violations:
                compliance_score *= (1 - len(violations) * 0.1)
            
            return ConstitutionalCompliance(
                score=max(0.0, min(1.0, compliance_score)),
                violations=violations,
                recommendations=recommendations,
                principle_scores=dict(zip(self.constitutional_principles, similarities.tolist())),
                constitutional_hash=self.constitutional_hash
            )
            
        except Exception as e:
            logger.error(f"Constitutional compliance analysis failed: {e}")
            return self._get_default_compliance()
    
    async def _analyze_bias(self, content: str) -> BiasAnalysis:
        """Analyze content for bias."""
        try:
            detected_bias = False
            bias_types = []
            mitigation_suggestions = []
            bias_scores = {}
            
            # Pattern-based bias detection
            content_lower = content.lower()
            
            for bias_type, patterns in self.bias_patterns.items():
                type_matches = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, content_lower))
                    type_matches += matches
                
                if type_matches > 0:
                    bias_score = min(type_matches / len(content.split()) * 10, 1.0)
                    bias_scores[bias_type] = bias_score
                    
                    if bias_score > 0.1:  # Threshold for bias detection
                        detected_bias = True
                        bias_types.append(bias_type)
                        mitigation_suggestions.append(f"Review {bias_type} references for potential bias")
            
            # ML-based toxicity detection
            try:
                toxicity_result = self.bias_classifier(content)
                if isinstance(toxicity_result, list):
                    toxicity_result = toxicity_result[0]
                
                if toxicity_result['label'] == 'TOXIC' and toxicity_result['score'] > 0.7:
                    detected_bias = True
                    bias_types.append('toxic_content')
                    mitigation_suggestions.append('Content flagged as potentially toxic')
                    bias_scores['toxicity'] = toxicity_result['score']
                    
            except Exception as e:
                logger.warning(f"Toxicity detection failed: {e}")
            
            return BiasAnalysis(
                detected_bias=detected_bias,
                bias_types=bias_types,
                mitigation_suggestions=mitigation_suggestions,
                bias_scores=bias_scores,
                constitutional_hash=self.constitutional_hash
            )
            
        except Exception as e:
            logger.error(f"Bias analysis failed: {e}")
            return self._get_default_bias()
    
    async def _analyze_sentiment(self, content: str) -> SentimentAnalysis:
        """Analyze sentiment of content."""
        try:
            # Sentiment analysis
            sentiment_result = self.sentiment_analyzer(content)
            if isinstance(sentiment_result, list):
                sentiment_result = sentiment_result[0]
            
            # Emotion detection patterns
            emotion_patterns = {
                'anger': [r'\b(angry|mad|furious|rage|hate|annoyed)\b'],
                'joy': [r'\b(happy|joy|excited|glad|cheerful|delighted)\b'],
                'sadness': [r'\b(sad|depressed|disappointed|grief|sorrow)\b'],
                'fear': [r'\b(afraid|scared|frightened|anxious|worried)\b'],
                'surprise': [r'\b(surprised|shocked|amazed|astonished)\b'],
                'disgust': [r'\b(disgusted|revolted|repulsed|sick)\b']
            }
            
            emotional_indicators = []
            content_lower = content.lower()
            
            for emotion, patterns in emotion_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower):
                        emotional_indicators.append(emotion)
                        break
            
            # Assess potential impact
            impact_score = sentiment_result['score']
            if sentiment_result['label'] == 'NEGATIVE' and impact_score > 0.8:
                potential_impact = 'High negative impact potential'
            elif sentiment_result['label'] == 'POSITIVE' and impact_score > 0.8:
                potential_impact = 'High positive impact potential'
            else:
                potential_impact = 'Moderate impact potential'
            
            return SentimentAnalysis(
                overall_sentiment=sentiment_result['label'],
                sentiment_score=impact_score,
                emotional_indicators=emotional_indicators,
                potential_impact=potential_impact,
                constitutional_hash=self.constitutional_hash
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._get_default_sentiment()
    
    async def _analyze_content_safety(self, content: str) -> Dict[str, Any]:
        """Analyze content safety."""
        try:
            safety_analysis = {}
            
            # Hate speech detection
            try:
                hate_result = self.hate_speech_detector(content)
                if isinstance(hate_result, list):
                    hate_result = hate_result[0]
                
                safety_analysis['hate_speech'] = {
                    'detected': hate_result['label'] == 'HATE',
                    'confidence': hate_result['score']
                }
            except Exception as e:
                logger.warning(f"Hate speech detection failed: {e}")
                safety_analysis['hate_speech'] = {'detected': False, 'confidence': 0.0}
            
            # Violence detection patterns
            violence_patterns = [
                r'\b(kill|murder|attack|violence|assault|weapon|gun|knife|bomb)\b',
                r'\b(fight|battle|war|destroy|harm|hurt|damage)\b'
            ]
            
            violence_detected = False
            for pattern in violence_patterns:
                if re.search(pattern, content.lower()):
                    violence_detected = True
                    break
            
            safety_analysis['violence'] = {
                'detected': violence_detected,
                'confidence': 0.7 if violence_detected else 0.0
            }
            
            # Adult content detection
            adult_patterns = [
                r'\b(sex|sexual|nude|naked|explicit|adult|porn|erotic)\b',
                r'\b(intimate|arousal|orgasm|genitals|breast|penis|vagina)\b'
            ]
            
            adult_detected = False
            for pattern in adult_patterns:
                if re.search(pattern, content.lower()):
                    adult_detected = True
                    break
            
            safety_analysis['adult_content'] = {
                'detected': adult_detected,
                'confidence': 0.6 if adult_detected else 0.0
            }
            
            return safety_analysis
            
        except Exception as e:
            logger.error(f"Content safety analysis failed: {e}")
            return {}
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability."""
        try:
            readability_stats = self.readability_analyzer(content)
            
            # Assess readability level
            flesch_score = readability_stats['flesch_reading_ease']
            
            if flesch_score >= 90:
                readability_level = 'Very Easy'
            elif flesch_score >= 80:
                readability_level = 'Easy'
            elif flesch_score >= 70:
                readability_level = 'Fairly Easy'
            elif flesch_score >= 60:
                readability_level = 'Standard'
            elif flesch_score >= 50:
                readability_level = 'Fairly Difficult'
            elif flesch_score >= 30:
                readability_level = 'Difficult'
            else:
                readability_level = 'Very Difficult'
            
            readability_stats['level'] = readability_level
            readability_stats['recommendations'] = []
            
            # Generate recommendations
            if flesch_score < 60:
                readability_stats['recommendations'].append('Consider simplifying sentence structure')
            
            if readability_stats['word_count'] > 500:
                readability_stats['recommendations'].append('Consider breaking into smaller sections')
            
            return readability_stats
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return {}
    
    async def _analyze_privacy_concerns(self, content: str) -> Dict[str, Any]:
        """Analyze privacy concerns in content."""
        try:
            privacy_analysis = {}
            
            # NER for PII detection
            doc = self.nlp(content)
            
            pii_entities = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PHONE', 'EMAIL', 'MONEY', 'DATE']:
                    pii_entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            
            privacy_analysis['pii_detected'] = len(pii_entities) > 0
            privacy_analysis['pii_entities'] = pii_entities
            
            # Pattern-based privacy detection
            privacy_patterns = [
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', 'Credit Card'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email'),
                (r'\b\d{3}-\d{3}-\d{4}\b', 'Phone Number'),
                (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP Address')
            ]
            
            privacy_concerns = []
            for pattern, concern_type in privacy_patterns:
                if re.search(pattern, content):
                    privacy_concerns.append(concern_type)
            
            privacy_analysis['privacy_concerns'] = privacy_concerns
            privacy_analysis['recommendations'] = []
            
            if privacy_concerns:
                privacy_analysis['recommendations'].append('Review and potentially redact sensitive information')
            
            return privacy_analysis
            
        except Exception as e:
            logger.error(f"Privacy analysis failed: {e}")
            return {}
    
    async def _generate_insights(self, content: str, context: Dict[str, Any] = None) -> List[AIInsight]:
        """Generate AI insights for content."""
        try:
            insights = []
            
            # Zero-shot classification for general insights
            categories = [
                'requires immediate attention',
                'needs human review',
                'constitutional concern',
                'bias or discrimination',
                'positive contribution',
                'educational content',
                'controversial topic',
                'factual accuracy concern'
            ]
            
            try:
                classification_result = self.zero_shot_classifier(content, categories)
                
                for label, score in zip(classification_result['labels'], classification_result['scores']):
                    if score > 0.5:  # Threshold for insight generation
                        severity = 'high' if score > 0.8 else 'medium' if score > 0.6 else 'low'
                        
                        insight = AIInsight(
                            type=self._get_insight_type(label),
                            severity=severity,
                            title=f"Content classified as: {label}",
                            description=f"AI analysis suggests this content may be {label.lower()} (confidence: {score:.1%})",
                            confidence=score,
                            automated_action=self._get_automated_action(label, severity),
                            constitutional_implications=self._get_constitutional_implications(label),
                            constitutional_hash=self.constitutional_hash
                        )
                        
                        insights.append(insight)
                        
            except Exception as e:
                logger.warning(f"Zero-shot classification failed: {e}")
            
            # Length-based insights
            word_count = len(content.split())
            if word_count > 1000:
                insights.append(AIInsight(
                    type='suggestion',
                    severity='low',
                    title='Long content detected',
                    description=f'Content is {word_count} words long. Consider breaking into sections for better readability.',
                    confidence=0.9,
                    automated_action='suggest_sections',
                    constitutional_hash=self.constitutional_hash
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return []
    
    def _get_insight_type(self, label: str) -> str:
        """Map classification label to insight type."""
        type_mapping = {
            'requires immediate attention': 'warning',
            'needs human review': 'warning',
            'constitutional concern': 'compliance',
            'bias or discrimination': 'bias',
            'positive contribution': 'suggestion',
            'educational content': 'suggestion',
            'controversial topic': 'warning',
            'factual accuracy concern': 'warning'
        }
        return type_mapping.get(label, 'suggestion')
    
    def _get_automated_action(self, label: str, severity: str) -> str:
        """Get automated action for label."""
        if severity == 'high':
            return 'flag_for_review'
        elif 'constitutional' in label.lower():
            return 'constitutional_review'
        elif 'bias' in label.lower():
            return 'bias_review'
        else:
            return 'standard_review'
    
    def _get_constitutional_implications(self, label: str) -> List[str]:
        """Get constitutional implications for label."""
        implications = []
        
        if 'constitutional' in label.lower():
            implications.append('Potential constitutional violation')
        
        if 'bias' in label.lower() or 'discrimination' in label.lower():
            implications.append('Fairness and equality concerns')
        
        if 'accuracy' in label.lower():
            implications.append('Truth and transparency concerns')
        
        return implications
    
    def _calculate_overall_score(
        self,
        constitutional_compliance: ConstitutionalCompliance,
        bias_analysis: BiasAnalysis,
        sentiment_analysis: SentimentAnalysis,
        safety_analysis: Dict[str, Any],
        readability_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall content score."""
        try:
            scores = []
            
            # Constitutional compliance (40% weight)
            scores.append(constitutional_compliance.score * 0.4)
            
            # Bias analysis (30% weight)
            bias_score = 0.0 if bias_analysis.detected_bias else 1.0
            scores.append(bias_score * 0.3)
            
            # Sentiment analysis (10% weight)
            sentiment_score = sentiment_analysis.sentiment_score if sentiment_analysis.overall_sentiment == 'POSITIVE' else 1 - sentiment_analysis.sentiment_score
            scores.append(sentiment_score * 0.1)
            
            # Safety analysis (15% weight)
            safety_score = 1.0
            for safety_check in safety_analysis.values():
                if isinstance(safety_check, dict) and safety_check.get('detected', False):
                    safety_score *= (1 - safety_check.get('confidence', 0.5))
            scores.append(safety_score * 0.15)
            
            # Readability (5% weight)
            readability_score = min(readability_analysis.get('flesch_reading_ease', 50) / 100, 1.0)
            scores.append(readability_score * 0.05)
            
            return sum(scores)
            
        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return 0.5
    
    def _get_default_compliance(self) -> ConstitutionalCompliance:
        """Get default constitutional compliance."""
        return ConstitutionalCompliance(
            score=0.5,
            violations=[],
            recommendations=[],
            principle_scores={},
            constitutional_hash=self.constitutional_hash
        )
    
    def _get_default_bias(self) -> BiasAnalysis:
        """Get default bias analysis."""
        return BiasAnalysis(
            detected_bias=False,
            bias_types=[],
            mitigation_suggestions=[],
            bias_scores={},
            constitutional_hash=self.constitutional_hash
        )
    
    def _get_default_sentiment(self) -> SentimentAnalysis:
        """Get default sentiment analysis."""
        return SentimentAnalysis(
            overall_sentiment='NEUTRAL',
            sentiment_score=0.5,
            emotional_indicators=[],
            potential_impact='Unknown',
            constitutional_hash=self.constitutional_hash
        )
    
    async def _cache_analysis(self, content: str, analysis: AIAnalysis):
        """Cache analysis results."""
        try:
            if not self.redis_client:
                return
            
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            cache_key = f"ai_analysis:{content_hash}"
            
            cache_data = analysis.dict()
            await self.redis_client.setex(
                cache_key,
                1800,  # 30 minutes
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Analysis caching failed: {e}")
    
    async def health_check(self) -> bool:
        """Check if AI assistant is healthy."""
        try:
            # Test model inference
            test_content = "This is a test sentence for health check."
            
            # Test constitutional model
            self.constitutional_model.encode([test_content])
            
            # Test sentiment analyzer
            self.sentiment_analyzer(test_content)
            
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False