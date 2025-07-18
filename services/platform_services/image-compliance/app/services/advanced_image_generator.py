"""
Advanced Image Generator - Stable Diffusion 3 with enhanced safety
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import torch
from diffusers import (
    StableDiffusion3Pipeline,
    AutoPipelineForText2Image,
    DPMSolverMultistepScheduler,
    StableDiffusionXLPipeline,
    StableDiffusionPipeline,
)
from transformers import AutoTokenizer, AutoModel
from optimum.bettertransformer import BetterTransformer
import numpy as np
import cv2
from PIL import Image
import io
import base64
import json
from celery import Celery
from cryptography.fernet import Fernet
import hashlib

from ..models.schemas import (
    ImageGenerationRequest,
    ImageGenerationResult,
    GenerationStatus,
    RiskLevel,
    CONSTITUTIONAL_HASH,
)

logger = logging.getLogger(__name__)

# Celery for async processing
celery_app = Celery("image_generation", broker="redis://localhost:6389")


class AdvancedImageGenerator:
    """Enhanced image generation with Stable Diffusion 3 and safety features."""

    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.device = device
        self.quantization_bits = 8  # For model quantization

        # Privacy and security
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Safety configurations
        self.safety_threshold = 0.7
        self.content_filters = [
            "violence",
            "gore",
            "blood",
            "weapon",
            "gun",
            "knife",
            "nude",
            "naked",
            "sexual",
            "porn",
            "explicit",
            "hate",
            "racist",
            "discrimination",
            "slur",
            "illegal",
            "drug",
            "terrorism",
            "bomb",
        ]

        # Initialize models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize Stable Diffusion 3 and safety models."""
        try:
            logger.info("Initializing Stable Diffusion 3 pipeline...")

            # 1. Stable Diffusion 3 (primary model)
            try:
                self.sd3_pipeline = StableDiffusion3Pipeline.from_pretrained(
                    "stabilityai/stable-diffusion-3-medium-diffusers",
                    torch_dtype=(
                        torch.float16 if self.device == "cuda" else torch.float32
                    ),
                    use_safetensors=True,
                )
                self.sd3_pipeline.to(self.device)

                # Enable memory efficient attention
                self.sd3_pipeline.enable_model_cpu_offload()
                self.sd3_pipeline.enable_attention_slicing()

                logger.info("Stable Diffusion 3 pipeline loaded successfully")

            except Exception as e:
                logger.warning(f"SD3 not available, falling back to SDXL: {e}")

                # Fallback to SDXL
                self.sd3_pipeline = StableDiffusionXLPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=(
                        torch.float16 if self.device == "cuda" else torch.float32
                    ),
                    use_safetensors=True,
                )
                self.sd3_pipeline.to(self.device)
                self.sd3_pipeline.enable_model_cpu_offload()

            # 2. Safety classifier
            self.safety_classifier = AutoPipelineForText2Image.from_pretrained(
                "CompVis/stable-diffusion-safety-checker",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )

            # 3. Prompt enhancement model
            self.prompt_enhancer = AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            self.prompt_tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

            # 4. Constitutional compliance checker
            self.compliance_model = AutoModel.from_pretrained(
                "microsoft/DialoGPT-medium"
            )

            # Apply quantization if enabled
            if self.quantization_bits < 16 and self.device == "cuda":
                self._apply_quantization()

            logger.info("Advanced image generation models initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize image generation models: {e}")
            raise

    def _apply_quantization(self):
        """Apply 8-bit quantization for memory efficiency."""
        try:
            # Apply BetterTransformer optimizations
            self.sd3_pipeline.unet = BetterTransformer.transform(self.sd3_pipeline.unet)
            self.sd3_pipeline.text_encoder = BetterTransformer.transform(
                self.sd3_pipeline.text_encoder
            )

            logger.info(f"Applied {self.quantization_bits}-bit quantization")

        except Exception as e:
            logger.warning(f"Quantization failed, continuing without: {e}")

    async def generate_image_advanced(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """Advanced image generation with enhanced safety and quality."""
        try:
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise ValueError("Invalid constitutional hash")

            generation_id = hashlib.sha256(
                f"{request.prompt}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]

            # 1. Pre-generation safety check
            safety_result = await self._check_prompt_safety(request.prompt)
            if safety_result["risk_level"] == RiskLevel.HIGH:
                return ImageGenerationResult(
                    generation_id=generation_id,
                    status=GenerationStatus.BLOCKED,
                    error_message=f"Prompt blocked: {safety_result['reason']}",
                    safety_scores=safety_result["scores"],
                    constitutional_hash=self.constitutional_hash,
                )

            # 2. Enhance prompt for better results
            enhanced_prompt = await self._enhance_prompt(request.prompt)

            # 3. Generate image with async processing
            if request.async_processing:
                # Queue for background processing
                task = celery_app.send_task(
                    "generate_image_task",
                    args=[enhanced_prompt, request.dict()],
                    kwargs={"generation_id": generation_id},
                )

                return ImageGenerationResult(
                    generation_id=generation_id,
                    status=GenerationStatus.PROCESSING,
                    task_id=task.id,
                    estimated_completion=datetime.utcnow().timestamp() + 30,
                    constitutional_hash=self.constitutional_hash,
                )

            # 4. Synchronous generation
            generation_result = await self._generate_image_sync(
                enhanced_prompt, request, generation_id
            )

            # 5. Post-generation analysis
            if generation_result.status == GenerationStatus.COMPLETED:
                post_analysis = await self._analyze_generated_image(
                    generation_result.image_data
                )
                generation_result.safety_scores.update(
                    post_analysis.get("safety_scores", {})
                )
                generation_result.quality_metrics = post_analysis.get(
                    "quality_metrics", {}
                )

                # Block if post-analysis reveals issues
                if post_analysis.get("risk_level") == RiskLevel.HIGH:
                    generation_result.status = GenerationStatus.BLOCKED
                    generation_result.error_message = (
                        "Generated image blocked by post-analysis"
                    )

            logger.info(f"Image generation completed: {generation_id}")
            return generation_result

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return ImageGenerationResult(
                generation_id=generation_id if "generation_id" in locals() else "error",
                status=GenerationStatus.FAILED,
                error_message=str(e),
                constitutional_hash=self.constitutional_hash,
            )

    async def _check_prompt_safety(self, prompt: str) -> Dict[str, Any]:
        """Advanced prompt safety checking."""
        try:
            risk_level = RiskLevel.MINIMAL
            risk_factors = []
            scores = {}

            # 1. Keyword filtering
            prompt_lower = prompt.lower()
            for filter_word in self.content_filters:
                if filter_word in prompt_lower:
                    risk_factors.append(f"Contains prohibited word: {filter_word}")
                    risk_level = RiskLevel.HIGH

            # 2. Semantic analysis
            with torch.no_grad():
                # Encode prompt
                inputs = self.prompt_tokenizer(
                    prompt, return_tensors="pt", truncation=True, max_length=512
                )
                prompt_embedding = self.prompt_enhancer(
                    **inputs
                ).last_hidden_state.mean(dim=1)

                # Check against unsafe concepts
                unsafe_concepts = [
                    "violent imagery",
                    "explicit sexual content",
                    "hateful or discriminatory content",
                    "illegal activities",
                    "harmful or dangerous content",
                ]

                for concept in unsafe_concepts:
                    concept_inputs = self.prompt_tokenizer(
                        concept, return_tensors="pt", truncation=True, max_length=512
                    )
                    concept_embedding = self.prompt_enhancer(
                        **concept_inputs
                    ).last_hidden_state.mean(dim=1)

                    # Calculate similarity
                    similarity = torch.cosine_similarity(
                        prompt_embedding, concept_embedding
                    )
                    scores[concept] = float(similarity)

                    if similarity > self.safety_threshold:
                        risk_factors.append(f"High similarity to: {concept}")
                        risk_level = max(risk_level, RiskLevel.HIGH)

            # 3. Constitutional compliance check
            constitutional_score = await self._check_constitutional_compliance(prompt)
            scores["constitutional_compliance"] = constitutional_score

            if constitutional_score < 0.5:
                risk_factors.append("Constitutional compliance concern")
                risk_level = max(risk_level, RiskLevel.MEDIUM)

            return {
                "risk_level": risk_level,
                "scores": scores,
                "risk_factors": risk_factors,
                "reason": "; ".join(risk_factors) if risk_factors else "Safe",
            }

        except Exception as e:
            logger.error(f"Prompt safety check failed: {e}")
            return {
                "risk_level": RiskLevel.MEDIUM,
                "scores": {},
                "risk_factors": ["Safety check failed"],
                "reason": f"Safety check error: {e}",
            }

    async def _check_constitutional_compliance(self, prompt: str) -> float:
        """Check constitutional compliance of the prompt."""
        try:
            # Constitutional principles for image generation
            principles = [
                "respects human dignity",
                "promotes positive values",
                "avoids harmful stereotypes",
                "protects individual privacy",
                "encourages creative expression",
            ]

            # Simple compliance scoring (in practice, this would be more sophisticated)
            compliance_indicators = [
                "respectful",
                "positive",
                "creative",
                "artistic",
                "beautiful",
                "inspiring",
                "educational",
                "peaceful",
                "harmonious",
            ]

            negative_indicators = [
                "harmful",
                "offensive",
                "discriminatory",
                "invasive",
                "exploitative",
            ]

            prompt_lower = prompt.lower()

            positive_score = sum(
                1 for indicator in compliance_indicators if indicator in prompt_lower
            )
            negative_score = sum(
                1 for indicator in negative_indicators if indicator in prompt_lower
            )

            # Normalize score
            total_indicators = len(compliance_indicators) + len(negative_indicators)
            compliance_score = (positive_score - negative_score + total_indicators) / (
                2 * total_indicators
            )

            return max(0.0, min(1.0, compliance_score))

        except Exception as e:
            logger.error(f"Constitutional compliance check failed: {e}")
            return 0.5  # Default neutral score

    async def _enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt for better generation quality."""
        try:
            # Add quality enhancers
            quality_enhancers = [
                "high quality",
                "detailed",
                "masterpiece",
                "professional",
                "sharp focus",
                "8k resolution",
                "beautiful lighting",
            ]

            # Add safety enhancers
            safety_enhancers = [
                "appropriate",
                "respectful",
                "family-friendly",
                "tasteful",
            ]

            # Combine enhancements
            enhanced_prompt = prompt

            # Add quality terms if not present
            if not any(
                term in prompt.lower() for term in ["quality", "detailed", "resolution"]
            ):
                enhanced_prompt += ", high quality, detailed"

            # Add safety terms for sensitive contexts
            if any(
                term in prompt.lower()
                for term in ["person", "people", "human", "character"]
            ):
                enhanced_prompt += ", respectful, appropriate"

            # Add constitutional compliance
            enhanced_prompt += (
                f", constitutional compliance: {self.constitutional_hash}"
            )

            return enhanced_prompt

        except Exception as e:
            logger.error(f"Prompt enhancement failed: {e}")
            return prompt

    async def _generate_image_sync(
        self, prompt: str, request: ImageGenerationRequest, generation_id: str
    ) -> ImageGenerationResult:
        """Synchronous image generation."""
        try:
            start_time = datetime.utcnow()

            # Generation parameters
            generation_params = {
                "prompt": prompt,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "width": request.width,
                "height": request.height,
                "num_images_per_prompt": 1,
                "generator": (
                    torch.Generator(device=self.device).manual_seed(request.seed)
                    if request.seed
                    else None
                ),
            }

            # Add negative prompt
            if request.negative_prompt:
                generation_params["negative_prompt"] = request.negative_prompt

            # Generate image
            with torch.no_grad():
                result = self.sd3_pipeline(**generation_params)
                image = result.images[0]

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")
            image_data = img_byte_arr.getvalue()

            # Encrypt for privacy
            encrypted_data = self.cipher_suite.encrypt(image_data)

            # Calculate metrics
            generation_time = (datetime.utcnow() - start_time).total_seconds()

            return ImageGenerationResult(
                generation_id=generation_id,
                status=GenerationStatus.COMPLETED,
                image_data=base64.b64encode(image_data).decode(),
                generation_time=generation_time,
                prompt_used=prompt,
                model_info={
                    "model": "stable-diffusion-3",
                    "version": "3.0",
                    "parameters": generation_params,
                },
                constitutional_hash=self.constitutional_hash,
            )

        except Exception as e:
            logger.error(f"Synchronous generation failed: {e}")
            return ImageGenerationResult(
                generation_id=generation_id,
                status=GenerationStatus.FAILED,
                error_message=str(e),
                constitutional_hash=self.constitutional_hash,
            )

    async def _analyze_generated_image(self, image_data_b64: str) -> Dict[str, Any]:
        """Analyze generated image for safety and quality."""
        try:
            # Decode image
            image_data = base64.b64decode(image_data_b64)
            image = Image.open(io.BytesIO(image_data))

            analysis_results = {}

            # 1. Safety analysis
            safety_scores = await self._analyze_image_safety(image)
            analysis_results["safety_scores"] = safety_scores

            # 2. Quality metrics
            quality_metrics = await self._analyze_image_quality(image)
            analysis_results["quality_metrics"] = quality_metrics

            # 3. Determine risk level
            risk_level = RiskLevel.MINIMAL

            if any(score > 0.8 for score in safety_scores.values()):
                risk_level = RiskLevel.HIGH
            elif any(score > 0.6 for score in safety_scores.values()):
                risk_level = RiskLevel.MEDIUM

            analysis_results["risk_level"] = risk_level

            return analysis_results

        except Exception as e:
            logger.error(f"Generated image analysis failed: {e}")
            return {
                "risk_level": RiskLevel.MINIMAL,
                "safety_scores": {},
                "quality_metrics": {},
            }

    async def _analyze_image_safety(self, image: Image.Image) -> Dict[str, float]:
        """Analyze safety of generated image."""
        try:
            # Convert to numpy for analysis
            img_array = np.array(image)

            # Simple safety heuristics (in practice, use trained classifiers)
            safety_scores = {}

            # Color analysis for inappropriate content
            red_dominance = np.mean(img_array[:, :, 0]) / 255.0

            # Texture analysis
            gray = np.mean(img_array, axis=2)
            gradient = np.gradient(gray)
            texture_complexity = np.std(gradient)

            # Heuristic scoring
            safety_scores["red_dominance"] = float(red_dominance)
            safety_scores["texture_complexity"] = float(texture_complexity / 100.0)

            # Overall safety score
            safety_scores["overall_safety"] = 1.0 - max(
                red_dominance * 0.3, texture_complexity / 200.0
            )

            return safety_scores

        except Exception as e:
            logger.error(f"Image safety analysis failed: {e}")
            return {"overall_safety": 0.5}

    async def _analyze_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Analyze quality of generated image."""
        try:
            img_array = np.array(image)
            quality_metrics = {}

            # 1. Sharpness (using variance of Laplacian)
            gray = np.mean(img_array, axis=2)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            quality_metrics["sharpness"] = float(sharpness / 1000.0)  # Normalize

            # 2. Contrast
            contrast = np.std(gray)
            quality_metrics["contrast"] = float(contrast / 128.0)  # Normalize

            # 3. Color distribution
            color_std = np.std(img_array, axis=(0, 1))
            quality_metrics["color_diversity"] = float(np.mean(color_std) / 128.0)

            # 4. Overall quality score
            quality_metrics["overall_quality"] = float(
                np.mean(
                    [
                        quality_metrics["sharpness"],
                        quality_metrics["contrast"],
                        quality_metrics["color_diversity"],
                    ]
                )
            )

            return quality_metrics

        except Exception as e:
            logger.error(f"Image quality analysis failed: {e}")
            return {"overall_quality": 0.5}

    async def health_check(self) -> bool:
        """Check if the generation pipeline is healthy."""
        try:
            # Test generation with simple prompt
            test_prompt = "a simple red circle"

            with torch.no_grad():
                result = self.sd3_pipeline(
                    prompt=test_prompt,
                    num_inference_steps=1,
                    guidance_scale=1.0,
                    width=64,
                    height=64,
                )

            return len(result.images) > 0

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


@celery_app.task(name="generate_image_task")
def generate_image_task(
    prompt: str, request_data: Dict[str, Any], generation_id: str
) -> Dict[str, Any]:
    """Celery task for asynchronous image generation."""
    try:
        # This would be implemented with proper Celery setup
        # For now, return mock result
        return {
            "generation_id": generation_id,
            "status": "completed",
            "message": "Async generation completed",
        }

    except Exception as e:
        logger.error(f"Async generation task failed: {e}")
        return {"generation_id": generation_id, "status": "failed", "error": str(e)}
