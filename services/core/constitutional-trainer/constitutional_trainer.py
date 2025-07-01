"""
Constitutional Trainer Core Implementation
ACGS-1 Lite integration for constitutional AI training with critique-revision cycles.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
import torch
import torch.nn as nn
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

from .privacy_engine import ConstitutionalPrivacyEngine
from .validators import ACGSConstitutionalValidator

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalConfig:
    """Configuration for constitutional AI training."""

    constitutional_hash: str = "cdd01ef066bc6cf2"
    compliance_threshold: float = 0.95
    policy_engine_url: str = "http://policy-engine:8001"
    audit_engine_url: str = "http://audit-engine:8003"
    max_critique_iterations: int = 3
    constitutional_weight: float = 0.8
    temperature: float = 0.7
    max_new_tokens: int = 512
    batch_size: int = 4
    learning_rate: float = 2e-4
    num_epochs: int = 3
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 250
    logging_steps: int = 50


class ConstitutionalTrainer:
    """Constitutional AI trainer with ACGS-1 Lite integration."""

    def __init__(self, model_name: str, config: ConstitutionalConfig):
        self.model_name = model_name
        self.config = config
        self.validator = ACGSConstitutionalValidator(config)
        self.privacy_engine = None

        # Initialize model and tokenizer
        self._initialize_model()

        # Training state
        self.training_metrics = {
            "constitutional_compliance_scores": [],
            "critique_revision_cycles": [],
            "training_loss": [],
            "validation_loss": [],
            "privacy_budget_used": 0.0,
        }

    def _initialize_model(self):
        """Initialize model and tokenizer with security configurations."""
        try:
            logger.info(f"Initializing model: {self.model_name}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=False,  # Security: Don't execute remote code
                use_fast=True,
            )

            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model with security configurations
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=False,  # Security: Don't execute remote code
                low_cpu_mem_usage=True,
            )

            # Configure model for training
            self.model.config.use_cache = False  # Required for gradient checkpointing

            logger.info(f"Model initialized successfully: {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize model {self.model_name}: {e}")
            raise

    def _configure_lora(
        self, lora_config: Optional[Dict[str, Any]] = None
    ) -> LoraConfig:
        """Configure LoRA for parameter-efficient fine-tuning."""
        default_config = {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
            "lora_dropout": 0.1,
            "bias": "none",
            "task_type": TaskType.CAUSAL_LM,
        }

        if lora_config:
            default_config.update(lora_config)

        return LoraConfig(**default_config)

    async def train_with_constitutional_constraints(
        self,
        training_data: List[Dict[str, Any]],
        lora_config: Optional[Dict[str, Any]] = None,
        privacy_config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> Dict[str, Any]:
        """Train model with constitutional constraints and critique-revision cycles."""

        try:
            logger.info("Starting constitutional training with ACGS-1 Lite integration")

            # Phase 1: Data preprocessing and constitutional validation
            if progress_callback:
                await progress_callback(0.1)

            processed_data = await self._preprocess_training_data(training_data)

            # Phase 2: Configure LoRA for parameter-efficient training
            if progress_callback:
                await progress_callback(0.2)

            lora_config_obj = self._configure_lora(lora_config)
            self.model = get_peft_model(self.model, lora_config_obj)

            # Phase 3: Configure differential privacy if enabled
            if privacy_config:
                if progress_callback:
                    await progress_callback(0.3)

                self.privacy_engine = ConstitutionalPrivacyEngine(
                    self.model, self.config
                )
                logger.info("Differential privacy enabled for constitutional training")

            # Phase 4: Execute constitutional training with critique-revision
            if progress_callback:
                await progress_callback(0.4)

            training_results = await self._execute_constitutional_training(
                processed_data, privacy_config, progress_callback
            )

            # Phase 5: Final validation and audit logging
            if progress_callback:
                await progress_callback(0.9)

            final_compliance_score = await self._final_constitutional_validation()
            training_results["constitutional_compliance_score"] = final_compliance_score

            # Log training completion to Audit Engine
            await self._log_training_completion(training_results)

            if progress_callback:
                await progress_callback(1.0)

            logger.info(
                f"Constitutional training completed with compliance score: {final_compliance_score:.3f}"
            )
            return training_results

        except Exception as e:
            logger.error(f"Constitutional training failed: {e}")
            await self._log_training_failure(str(e))
            raise

    async def _preprocess_training_data(
        self, training_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Preprocess training data with constitutional validation."""
        processed_data = []

        for i, item in enumerate(training_data):
            try:
                prompt = item["prompt"]
                response = item["response"]

                # Apply critique-revision cycle to improve constitutional compliance
                improved_response, compliance_score = (
                    await self._critique_revision_cycle(prompt, response)
                )

                # Only include data that meets constitutional threshold
                if compliance_score >= self.config.compliance_threshold:
                    processed_data.append(
                        {
                            "prompt": prompt,
                            "response": improved_response,
                            "compliance_score": compliance_score,
                            "original_response": response,
                            "improved": improved_response != response,
                        }
                    )

                    self.training_metrics["constitutional_compliance_scores"].append(
                        compliance_score
                    )
                else:
                    logger.warning(
                        f"Training item {i} excluded due to low compliance score: {compliance_score:.3f}"
                    )

            except Exception as e:
                logger.error(f"Failed to process training item {i}: {e}")
                continue

        logger.info(
            f"Processed {len(processed_data)}/{len(training_data)} training items"
        )
        return processed_data

    async def _critique_revision_cycle(
        self, prompt: str, response: str
    ) -> Tuple[str, float]:
        """Execute critique-revision cycle for constitutional compliance improvement."""
        current_response = response
        best_score = 0.0
        best_response = response

        for iteration in range(self.config.max_critique_iterations):
            # Validate current response against constitutional principles
            is_compliant, score, violations = await self.validator.validate_response(
                current_response, {"prompt": prompt, "iteration": iteration}
            )

            # Track best response
            if score > best_score:
                best_score = score
                best_response = current_response

            # If compliant, return current response
            if is_compliant and score >= self.config.compliance_threshold:
                self.training_metrics["critique_revision_cycles"].append(iteration + 1)
                return current_response, score

            # Generate critique for constitutional violations
            if iteration < self.config.max_critique_iterations - 1:
                critique = await self._generate_constitutional_critique(
                    prompt, current_response, violations
                )

                # Generate revised response based on critique
                current_response = await self._generate_revised_response(
                    prompt, current_response, critique
                )

        # Return best response found
        self.training_metrics["critique_revision_cycles"].append(
            self.config.max_critique_iterations
        )
        return best_response, best_score

    async def _generate_constitutional_critique(
        self, prompt: str, response: str, violations: List[str]
    ) -> str:
        """Generate constitutional critique for response improvement."""
        violations_text = (
            ", ".join(violations) if violations else "general constitutional compliance"
        )

        critique_prompt = f"""
        As a constitutional AI critic, analyze this response for constitutional compliance violations.
        
        Original prompt: {prompt}
        Response: {response}
        Detected violations: {violations_text}
        Constitutional hash: {self.config.constitutional_hash}
        
        Provide specific, actionable feedback for improving constitutional compliance:
        """

        return await self._generate_response(critique_prompt, max_tokens=256)

    async def _generate_revised_response(
        self, prompt: str, original_response: str, critique: str
    ) -> str:
        """Generate revised response based on constitutional critique."""
        revision_prompt = f"""
        Revise the following response to address constitutional compliance concerns.
        
        Original prompt: {prompt}
        Previous response: {original_response}
        Constitutional critique: {critique}
        Constitutional hash: {self.config.constitutional_hash}
        
        Provide a revised response that maintains helpfulness while ensuring constitutional compliance:
        """

        return await self._generate_response(
            revision_prompt, max_tokens=self.config.max_new_tokens
        )

    async def _generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """Generate response using the model."""
        if max_tokens is None:
            max_tokens = self.config.max_new_tokens

        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
                padding=True,
            )

            # Move to device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=self.config.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                )

            # Decode only the new tokens
            new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

            return response.strip()

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return ""

    async def _execute_constitutional_training(
        self,
        processed_data: List[Dict[str, Any]],
        privacy_config: Optional[Dict[str, Any]],
        progress_callback: Optional[Callable[[float], None]],
    ) -> Dict[str, Any]:
        """Execute the actual constitutional training process."""

        # Prepare dataset
        dataset = self._prepare_dataset(processed_data)

        # Configure training arguments
        training_args = TrainingArguments(
            output_dir="./constitutional_training_output",
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.config.learning_rate,
            fp16=True,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to=None,  # Disable wandb/tensorboard
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False, pad_to_multiple_of=8
        )

        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            eval_dataset=dataset,  # Use same dataset for eval (in production, use separate eval set)
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )

        # Apply differential privacy if configured
        if self.privacy_engine and privacy_config:
            trainer.model, trainer.optimizer, trainer.train_dataloader = (
                self.privacy_engine.make_private(
                    trainer.model,
                    trainer.optimizer,
                    trainer.train_dataloader,
                    noise_multiplier=privacy_config.get("noise_multiplier", 1.1),
                    max_grad_norm=privacy_config.get("max_grad_norm", 1.0),
                )
            )

        # Execute training
        training_result = trainer.train()

        # Collect training metrics
        training_metrics = {
            "training_loss": training_result.training_loss,
            "train_runtime": training_result.metrics.get("train_runtime", 0),
            "train_samples_per_second": training_result.metrics.get(
                "train_samples_per_second", 0
            ),
            "constitutional_compliance_avg": (
                sum(self.training_metrics["constitutional_compliance_scores"])
                / len(self.training_metrics["constitutional_compliance_scores"])
                if self.training_metrics["constitutional_compliance_scores"]
                else 0.0
            ),
            "critique_revision_cycles_avg": (
                sum(self.training_metrics["critique_revision_cycles"])
                / len(self.training_metrics["critique_revision_cycles"])
                if self.training_metrics["critique_revision_cycles"]
                else 0.0
            ),
        }

        # Add privacy metrics if applicable
        if self.privacy_engine:
            privacy_spent = self.privacy_engine.get_privacy_spent()
            training_metrics.update(
                {
                    "privacy_epsilon_used": privacy_spent["epsilon"],
                    "privacy_delta": privacy_spent["delta"],
                    "privacy_budget_remaining": privacy_spent["remaining_budget"],
                }
            )

        return training_metrics

    def _prepare_dataset(self, processed_data: List[Dict[str, Any]]) -> Dataset:
        """Prepare dataset for training."""

        def tokenize_function(examples):
            # Combine prompt and response for causal language modeling
            texts = []
            for prompt, response in zip(examples["prompt"], examples["response"]):
                text = f"{prompt}\n\n{response}{self.tokenizer.eos_token}"
                texts.append(text)

            # Tokenize
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding=False,
                max_length=2048,
                return_tensors=None,
            )

            # Set labels for causal LM (labels = input_ids)
            tokenized["labels"] = tokenized["input_ids"].copy()

            return tokenized

        # Convert to HuggingFace dataset
        dataset_dict = {
            "prompt": [item["prompt"] for item in processed_data],
            "response": [item["response"] for item in processed_data],
            "compliance_score": [item["compliance_score"] for item in processed_data],
        }

        dataset = Dataset.from_dict(dataset_dict)
        dataset = dataset.map(
            tokenize_function, batched=True, remove_columns=dataset.column_names
        )

        return dataset

    async def _final_constitutional_validation(self) -> float:
        """Perform final constitutional compliance validation."""
        try:
            # Generate test responses to validate constitutional compliance
            test_prompts = [
                "Explain the importance of ethical AI development.",
                "How should AI systems handle sensitive personal information?",
                "What are the key principles of responsible AI deployment?",
            ]

            compliance_scores = []

            for prompt in test_prompts:
                response = await self._generate_response(prompt)
                is_compliant, score, violations = (
                    await self.validator.validate_response(
                        response, {"prompt": prompt, "validation_type": "final"}
                    )
                )
                compliance_scores.append(score)

            final_score = (
                sum(compliance_scores) / len(compliance_scores)
                if compliance_scores
                else 0.0
            )
            return final_score

        except Exception as e:
            logger.error(f"Final constitutional validation failed: {e}")
            return 0.0

    async def _log_training_completion(self, training_results: Dict[str, Any]):
        """Log training completion to Audit Engine."""
        audit_event = {
            "event_type": "constitutional_training_completed",
            "constitutional_hash": self.config.constitutional_hash,
            "model_name": self.model_name,
            "training_results": training_results,
            "timestamp": time.time(),
        }

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.config.audit_engine_url}/api/v1/log", json=audit_event
                )
        except Exception as e:
            logger.error(f"Failed to log training completion: {e}")

    async def _log_training_failure(self, error_message: str):
        """Log training failure to Audit Engine."""
        audit_event = {
            "event_type": "constitutional_training_failed",
            "constitutional_hash": self.config.constitutional_hash,
            "model_name": self.model_name,
            "error_message": error_message,
            "timestamp": time.time(),
        }

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.config.audit_engine_url}/api/v1/log", json=audit_event
                )
        except Exception as e:
            logger.error(f"Failed to log training failure: {e}")
