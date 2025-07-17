"""
Image Audit Agent - AI-powered image content analysis and compliance checking
Constitutional Hash: cdd01ef066bc6cf2
"""

import base64
import io
import time
from typing import Dict, List, Optional, Union
import torch
import numpy as np
from PIL import Image
import cv2
from transformers import pipeline, AutoImageProcessor, AutoModelForImageClassification
from sentence_transformers import SentenceTransformer
import logging

from ..models.schemas import (
    ImageAuditRequest, 
    ImageAuditResult, 
    ImageContentType, 
    ComplianceViolation,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class ImageAuditAgent:
    """
    AI-powered image audit agent for content compliance checking.
    Implements multi-model analysis for comprehensive content moderation.
    """
    
    def __init__(self):
        """Initialize the image audit agent with pre-trained models."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing ImageAuditAgent on device: {self.device}")
        
        # Load content moderation models
        self._load_models()
        
        # Confidence thresholds for different content types
        self.thresholds = {
            ImageContentType.NSFW: 0.7,
            ImageContentType.VIOLENCE: 0.8,
            ImageContentType.HATE_SPEECH: 0.75,
            ImageContentType.POLITICAL_SENSITIVE: 0.6,
        }
        
    def _load_models(self):
        """Load all required AI models for image analysis."""
        try:
            # NSFW detection model
            logger.info("Loading NSFW detection model...")
            self.nsfw_classifier = pipeline(
                "image-classification",
                model="Falconsai/nsfw_image_detection",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Violence detection model
            logger.info("Loading violence detection model...")
            self.violence_classifier = pipeline(
                "image-classification", 
                model="nateraw/vit-base-patch16-224-violence",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # General content classification
            logger.info("Loading general content classifier...")
            self.general_classifier = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Text embedding model for context analysis
            logger.info("Loading text embedding model...")
            self.text_embedder = SentenceTransformer("all-MiniLM-L6-v2")
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            # Fallback to CPU if GPU fails
            self.device = torch.device("cpu")
            self._load_fallback_models()
    
    def _load_fallback_models(self):
        """Load simpler fallback models if main models fail."""
        logger.warning("Loading fallback models on CPU...")
        try:
            self.nsfw_classifier = pipeline(
                "image-classification",
                model="Falconsai/nsfw_image_detection",
                device=-1
            )
            self.violence_classifier = None  # Skip if loading fails
            self.general_classifier = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224",
                device=-1
            )
            self.text_embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Fallback model loading failed: {e}")
            raise
    
    async def audit_image(self, request: ImageAuditRequest) -> ImageAuditResult:
        """
        Perform comprehensive image audit for compliance violations.
        
        Args:
            request: Image audit request with image data or URL
            
        Returns:
            ImageAuditResult with compliance assessment and details
        """
        start_time = time.time()
        
        try:
            # Validate constitutional compliance
            if request.constitutional_hash != self.constitutional_hash:
                raise ValueError(f"Constitutional hash mismatch: {request.constitutional_hash}")
            
            # Load and preprocess image
            image = await self._load_image(request)
            if image is None:
                return self._create_error_result("Failed to load image")
            
            # Perform multi-model analysis
            analysis_results = await self._analyze_image(image, request.context)
            
            # Determine overall compliance
            violations, compliant = self._assess_compliance(analysis_results)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(analysis_results)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ImageAuditResult(
                compliant=compliant,
                confidence_score=confidence_score,
                violations=violations,
                labels=analysis_results,
                analysis_details={
                    "model_versions": self._get_model_info(),
                    "processing_device": str(self.device),
                    "analysis_methods": ["nsfw_detection", "violence_detection", "content_classification"]
                },
                constitutional_hash=self.constitutional_hash,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Image audit failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return self._create_error_result(str(e), processing_time)
    
    async def _load_image(self, request: ImageAuditRequest) -> Optional[Image.Image]:
        """Load image from base64 data or URL."""
        try:
            if request.image_data:
                # Decode base64 image
                image_bytes = base64.b64decode(request.image_data)
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                return image
            elif request.image_url:
                # Download image from URL
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(request.image_url)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content)).convert("RGB")
                    return image
            else:
                logger.error("No image data or URL provided")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    async def _analyze_image(self, image: Image.Image, context: Optional[str]) -> Dict[ImageContentType, float]:
        """Perform comprehensive image analysis using multiple models."""
        results = {}
        
        try:
            # NSFW detection
            nsfw_result = self.nsfw_classifier(image)
            nsfw_score = self._extract_score(nsfw_result, ["nsfw", "porn", "sexual"])
            results[ImageContentType.NSFW] = nsfw_score
            
            # Violence detection
            if self.violence_classifier:
                violence_result = self.violence_classifier(image)
                violence_score = self._extract_score(violence_result, ["violence", "violent", "weapon"])
                results[ImageContentType.VIOLENCE] = violence_score
            else:
                results[ImageContentType.VIOLENCE] = 0.0
            
            # General content analysis
            general_result = self.general_classifier(image)
            
            # Analyze context if provided
            if context:
                context_analysis = await self._analyze_context(context)
                # Adjust scores based on context
                for content_type in results:
                    if content_type.value in context_analysis:
                        results[content_type] = min(1.0, results[content_type] + 0.1)
            
            # Set default scores for unanalyzed types
            for content_type in ImageContentType:
                if content_type not in results:
                    results[content_type] = 0.0
            
            # Ensure safe content has high score
            max_violation_score = max(results[ct] for ct in results if ct != ImageContentType.SAFE)
            results[ImageContentType.SAFE] = 1.0 - max_violation_score
            
            return results
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            # Return conservative scores
            return {
                ImageContentType.SAFE: 0.3,
                ImageContentType.NSFW: 0.5,
                ImageContentType.VIOLENCE: 0.5,
                ImageContentType.HATE_SPEECH: 0.3,
                ImageContentType.POLITICAL_SENSITIVE: 0.3,
                ImageContentType.UNKNOWN: 0.8
            }
    
    def _extract_score(self, model_result: List[Dict], target_labels: List[str]) -> float:
        """Extract confidence score for target labels from model results."""
        if not model_result:
            return 0.0
        
        max_score = 0.0
        for result in model_result:
            label = result.get("label", "").lower()
            score = result.get("score", 0.0)
            
            for target in target_labels:
                if target in label:
                    max_score = max(max_score, score)
        
        return max_score
    
    async def _analyze_context(self, context: str) -> Dict[str, float]:
        """Analyze textual context for content type indicators."""
        try:
            # Embed context text
            context_embedding = self.text_embedder.encode([context])
            
            # Define reference embeddings for different content types
            reference_texts = {
                "nsfw": "sexual explicit adult content pornography",
                "violence": "violence weapons fighting aggression",
                "hate_speech": "hate speech discrimination offensive",
                "political": "political sensitive government controversial"
            }
            
            results = {}
            for content_type, ref_text in reference_texts.items():
                ref_embedding = self.text_embedder.encode([ref_text])
                similarity = np.dot(context_embedding[0], ref_embedding[0])
                results[content_type] = max(0.0, similarity)
            
            return results
            
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")
            return {}
    
    def _assess_compliance(self, analysis_results: Dict[ImageContentType, float]) -> tuple[List[ComplianceViolation], bool]:
        """Assess overall compliance based on analysis results."""
        violations = []
        
        # Check each content type against thresholds
        if analysis_results[ImageContentType.NSFW] > self.thresholds[ImageContentType.NSFW]:
            violations.append(ComplianceViolation.NSFW_CONTENT)
        
        if analysis_results[ImageContentType.VIOLENCE] > self.thresholds[ImageContentType.VIOLENCE]:
            violations.append(ComplianceViolation.VIOLENT_CONTENT)
        
        if analysis_results[ImageContentType.HATE_SPEECH] > self.thresholds[ImageContentType.HATE_SPEECH]:
            violations.append(ComplianceViolation.HATE_SPEECH_CONTENT)
        
        if analysis_results[ImageContentType.POLITICAL_SENSITIVE] > self.thresholds[ImageContentType.POLITICAL_SENSITIVE]:
            violations.append(ComplianceViolation.POLITICAL_CONTENT)
        
        # Compliant if no violations found
        compliant = len(violations) == 0
        
        return violations, compliant
    
    def _calculate_confidence(self, analysis_results: Dict[ImageContentType, float]) -> float:
        """Calculate overall confidence score for the analysis."""
        # Use the maximum confidence across all models as overall confidence
        confidence_scores = [
            analysis_results.get(ImageContentType.SAFE, 0.0),
            1.0 - analysis_results.get(ImageContentType.NSFW, 0.0),
            1.0 - analysis_results.get(ImageContentType.VIOLENCE, 0.0),
            1.0 - analysis_results.get(ImageContentType.HATE_SPEECH, 0.0)
        ]
        
        # Return average confidence, clamped between 0 and 1
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        return max(0.0, min(1.0, avg_confidence))
    
    def _get_model_info(self) -> Dict[str, str]:
        """Get information about loaded models."""
        return {
            "nsfw_model": "Falconsai/nsfw_image_detection",
            "violence_model": "nateraw/vit-base-patch16-224-violence" if self.violence_classifier else "disabled",
            "general_model": "google/vit-base-patch16-224",
            "text_embedder": "all-MiniLM-L6-v2",
            "device": str(self.device)
        }
    
    def _create_error_result(self, error_message: str, processing_time: float = 0.0) -> ImageAuditResult:
        """Create an error result with conservative compliance assessment."""
        return ImageAuditResult(
            compliant=False,
            confidence_score=0.0,
            violations=[ComplianceViolation.NSFW_CONTENT],  # Conservative assumption
            labels={
                ImageContentType.SAFE: 0.0,
                ImageContentType.UNKNOWN: 1.0
            },
            analysis_details={
                "error": error_message,
                "model_versions": self._get_model_info()
            },
            constitutional_hash=self.constitutional_hash,
            processing_time_ms=processing_time
        )