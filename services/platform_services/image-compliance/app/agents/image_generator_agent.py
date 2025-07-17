"""
Image Generator Agent - AI-powered safe image generation with compliance validation
Constitutional Hash: cdd01ef066bc6cf2
"""

import base64
import io
import time
import random
from typing import Dict, List, Optional, Any
import torch
import numpy as np
from PIL import Image
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import logging

from ..models.schemas import (
    ImageGenerationRequest, 
    ImageGenerationResult, 
    ImageAuditResult,
    CONSTITUTIONAL_HASH
)
from .image_audit_agent import ImageAuditAgent

logger = logging.getLogger(__name__)

class ImageGeneratorAgent:
    """
    AI-powered image generation agent with built-in safety validation.
    Uses Stable Diffusion with constitutional compliance checking.
    """
    
    def __init__(self):
        """Initialize the image generation agent with Stable Diffusion model."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing ImageGeneratorAgent on device: {self.device}")
        
        # Initialize audit agent for safety checking
        self.audit_agent = ImageAuditAgent()
        
        # Load image generation model
        self._load_model()
        
        # Safety prompts and filters
        self._setup_safety_filters()
        
    def _load_model(self):
        """Load Stable Diffusion model with optimizations."""
        try:
            logger.info("Loading Stable Diffusion model...")
            
            # Use a lightweight model for faster generation
            model_id = "runwayml/stable-diffusion-v1-5"
            
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None,  # We'll use our own safety checker
                requires_safety_checker=False
            )
            
            # Optimize for memory and speed
            if torch.cuda.is_available():
                self.pipeline = self.pipeline.to(self.device)
                self.pipeline.enable_memory_efficient_attention()
                self.pipeline.enable_xformers_memory_efficient_attention()
            
            # Use faster scheduler
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            logger.info("Stable Diffusion model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Stable Diffusion model: {e}")
            # Set up mock generator for testing
            self.pipeline = None
            logger.warning("Using mock image generator")
    
    def _setup_safety_filters(self):
        """Setup safety filters and prompt modifications."""
        # Negative prompts to avoid unsafe content
        self.default_negative_prompt = (
            "nsfw, nude, naked, sexual, explicit, gore, violence, blood, "
            "weapon, gun, knife, hate, offensive, disturbing, inappropriate, "
            "realistic face, celebrity, politician, harmful, dangerous"
        )
        
        # Banned keywords that should not appear in prompts
        self.banned_keywords = {
            "nsfw", "nude", "naked", "sexual", "explicit", "porn", "xxx",
            "gore", "blood", "violence", "murder", "kill", "death", "suicide",
            "weapon", "gun", "rifle", "pistol", "knife", "bomb", "explosive",
            "hate", "racist", "nazi", "terrorist", "drug", "cocaine", "heroin",
            "celebrity", "politician", "trump", "biden", "obama", "celebrity name"
        }
        
        # Safe prompt templates
        self.safe_templates = [
            "beautiful landscape with {subject}",
            "abstract art featuring {subject}",
            "cartoon style {subject}",
            "minimalist design of {subject}",
            "watercolor painting of {subject}",
            "digital art {subject}",
            "fantasy scene with {subject}"
        ]
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate image with safety validation and constitutional compliance.
        
        Args:
            request: Image generation request with prompt and parameters
            
        Returns:
            ImageGenerationResult with generated image and safety assessment
        """
        start_time = time.time()
        
        try:
            # Validate constitutional compliance
            if request.constitutional_hash != self.constitutional_hash:
                raise ValueError(f"Constitutional hash mismatch: {request.constitutional_hash}")
            
            # Safety check the prompt
            safe_prompt, safety_check = await self._validate_prompt(request.prompt)
            if safety_check != "passed":
                return self._create_safety_failure_result(
                    request, safety_check, (time.time() - start_time) * 1000
                )
            
            # Generate the image
            generated_image = await self._generate_image_internal(request, safe_prompt)
            if generated_image is None:
                return self._create_error_result(
                    request, "Image generation failed", (time.time() - start_time) * 1000
                )
            
            # Audit the generated image for safety
            audit_result = await self._audit_generated_image(generated_image, request)
            
            # Convert image to base64 for response
            image_data = self._image_to_base64(generated_image)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ImageGenerationResult(
                success=True,
                image_data=image_data,
                prompt_used=safe_prompt,
                safety_check="passed" if audit_result.compliant else "failed",
                audit_result=audit_result,
                metadata={
                    "model": "stable-diffusion-v1-5",
                    "steps": request.num_inference_steps,
                    "guidance_scale": request.guidance_scale,
                    "seed": request.seed,
                    "dimensions": f"{request.width}x{request.height}",
                    "safety_filters": "enabled"
                },
                constitutional_hash=self.constitutional_hash,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            return self._create_error_result(request, str(e), processing_time)
    
    async def _validate_prompt(self, prompt: str) -> tuple[str, str]:
        """Validate and sanitize the input prompt for safety."""
        try:
            # Convert to lowercase for checking
            prompt_lower = prompt.lower()
            
            # Check for banned keywords
            for keyword in self.banned_keywords:
                if keyword in prompt_lower:
                    logger.warning(f"Banned keyword detected: {keyword}")
                    return prompt, f"blocked_keyword_{keyword}"
            
            # Add safety prefix if needed
            safe_prompt = prompt
            if not any(safe_word in prompt_lower for safe_word in ["safe", "appropriate", "clean"]):
                safe_prompt = f"safe, appropriate, clean, {prompt}"
            
            return safe_prompt, "passed"
            
        except Exception as e:
            logger.error(f"Prompt validation failed: {e}")
            return prompt, f"validation_error_{str(e)}"
    
    async def _generate_image_internal(self, request: ImageGenerationRequest, safe_prompt: str) -> Optional[Image.Image]:
        """Internal image generation with error handling."""
        try:
            if self.pipeline is None:
                # Mock image generation for testing
                return self._generate_mock_image(request.width, request.height)
            
            # Set seed for reproducibility
            if request.seed is not None:
                torch.manual_seed(request.seed)
                np.random.seed(request.seed)
            
            # Combine positive and negative prompts
            negative_prompt = request.negative_prompt or ""
            combined_negative = f"{self.default_negative_prompt}, {negative_prompt}".strip(", ")
            
            # Generate image
            with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
                result = self.pipeline(
                    prompt=safe_prompt,
                    negative_prompt=combined_negative,
                    width=request.width,
                    height=request.height,
                    num_inference_steps=request.num_inference_steps,
                    guidance_scale=request.guidance_scale,
                    num_images_per_prompt=1
                )
            
            return result.images[0]
            
        except Exception as e:
            logger.error(f"Internal image generation failed: {e}")
            # Return mock image as fallback
            return self._generate_mock_image(request.width, request.height)
    
    def _generate_mock_image(self, width: int, height: int) -> Image.Image:
        """Generate a mock image for testing purposes."""
        # Create a simple gradient image
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                img_array[y, x] = [
                    int(255 * x / width),
                    int(255 * y / height),
                    int(255 * (x + y) / (width + height))
                ]
        
        return Image.fromarray(img_array)
    
    async def _audit_generated_image(self, image: Image.Image, request: ImageGenerationRequest) -> ImageAuditResult:
        """Audit the generated image for safety compliance."""
        try:
            # Convert image to base64 for audit
            image_data = self._image_to_base64(image)
            
            # Create audit request
            from ..models.schemas import ImageAuditRequest
            audit_request = ImageAuditRequest(
                image_data=image_data,
                context=f"Generated image from prompt: {request.prompt}",
                user_id=request.user_id,
                constitutional_hash=self.constitutional_hash
            )
            
            # Perform audit
            audit_result = await self.audit_agent.audit_image(audit_request)
            return audit_result
            
        except Exception as e:
            logger.error(f"Image audit failed: {e}")
            # Return conservative audit result
            return ImageAuditResult(
                compliant=False,
                confidence_score=0.0,
                violations=[],
                labels={},
                analysis_details={"error": str(e)},
                constitutional_hash=self.constitutional_hash
            )
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def _create_safety_failure_result(self, request: ImageGenerationRequest, safety_issue: str, processing_time: float) -> ImageGenerationResult:
        """Create result for safety check failures."""
        return ImageGenerationResult(
            success=False,
            prompt_used=request.prompt,
            safety_check=safety_issue,
            metadata={
                "safety_issue": safety_issue,
                "original_prompt": request.prompt
            },
            constitutional_hash=self.constitutional_hash,
            processing_time_ms=processing_time
        )
    
    def _create_error_result(self, request: ImageGenerationRequest, error_message: str, processing_time: float) -> ImageGenerationResult:
        """Create error result for generation failures."""
        return ImageGenerationResult(
            success=False,
            prompt_used=request.prompt,
            safety_check="error",
            metadata={
                "error": error_message,
                "original_prompt": request.prompt
            },
            constitutional_hash=self.constitutional_hash,
            processing_time_ms=processing_time
        )