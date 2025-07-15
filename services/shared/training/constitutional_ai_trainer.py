"""
Constitutional AI Model Training System

This module implements training and fine-tuning for Constitutional AI models
using governance scenarios, principle-based decision making, and compliance
scoring from the generated training data.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModel, AutoConfig,
    TrainingArguments, Trainer, EarlyStoppingCallback
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalAIConfig:
    """Configuration for Constitutional AI training."""
    model_name: str = "microsoft/DialoGPT-medium"
    max_length: int = 512
    batch_size: int = 16
    learning_rate: float = 5e-5
    num_epochs: int = 3
    warmup_steps: int = 100
    weight_decay: float = 0.01
    
    # Constitutional AI specific parameters
    principle_weight: float = 1.0
    compliance_weight: float = 2.0
    reasoning_weight: float = 1.5
    constitutional_threshold: float = 0.95
    
    # Performance targets
    target_accuracy: float = 0.95
    target_compliance: float = 0.98
    target_latency_ms: float = 5.0
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class TrainingMetrics:
    """Training metrics for Constitutional AI."""
    epoch: int
    loss: float
    accuracy: float
    compliance_score: float
    principle_alignment: float
    reasoning_quality: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ConstitutionalAIDataset(Dataset):
    """Dataset for Constitutional AI training."""
    
    def __init__(
        self, 
        data_path: str, 
        tokenizer, 
        max_length: int = 512,
        constitutional_hash: str = CONSTITUTIONAL_HASH
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.constitutional_hash = constitutional_hash
        
        # Load training data
        with open(data_path, 'r') as f:
            self.data = json.load(f)
        
        # Validate constitutional compliance
        self._validate_constitutional_compliance()
        
        # Prepare examples
        self.examples = self._prepare_examples()
        
        logger.info(f"Loaded {len(self.examples)} Constitutional AI training examples")

    def _validate_constitutional_compliance(self):
        """Validate constitutional compliance of training data."""
        if "constitutional_hash" not in self.data:
            raise ValueError("Training data missing constitutional hash")
        
        if self.data["constitutional_hash"] != self.constitutional_hash:
            raise ValueError(f"Constitutional hash mismatch: {self.data['constitutional_hash']} != {self.constitutional_hash}")
        
        # Validate examples
        compliant_examples = 0
        for example in self.data.get("examples", []):
            if (example.get("input", {}).get("constitutional_hash") == self.constitutional_hash and
                example.get("target_output", {}).get("constitutional_hash") == self.constitutional_hash):
                compliant_examples += 1
        
        compliance_rate = compliant_examples / len(self.data.get("examples", []))
        if compliance_rate < 0.95:
            raise ValueError(f"Low constitutional compliance rate: {compliance_rate:.2%}")
        
        logger.info(f"Constitutional compliance validated: {compliance_rate:.2%}")

    def _prepare_examples(self) -> List[Dict[str, Any]]:
        """Prepare training examples from raw data."""
        examples = []
        
        for raw_example in self.data.get("examples", []):
            # Extract input components
            input_data = raw_example["input"]
            target_output = raw_example["target_output"]
            
            # Create input text
            input_text = self._format_input(input_data)
            
            # Create target text
            target_text = self._format_target(target_output)
            
            # Tokenize
            input_encoding = self.tokenizer(
                input_text,
                max_length=self.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            target_encoding = self.tokenizer(
                target_text,
                max_length=self.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            example = {
                "input_ids": input_encoding["input_ids"].squeeze(),
                "attention_mask": input_encoding["attention_mask"].squeeze(),
                "labels": target_encoding["input_ids"].squeeze(),
                "target_attention_mask": target_encoding["attention_mask"].squeeze(),
                
                # Constitutional AI specific fields
                "principle": input_data.get("constitutional_principles", ["transparency"])[0],
                "scenario": input_data.get("scenario", "general"),
                "compliance_score": target_output.get("compliance_score", 1.0),
                "principle_alignment": target_output.get("principle_alignment", {}),
                
                # Metadata
                "example_id": raw_example.get("id", "unknown"),
                "constitutional_hash": self.constitutional_hash
            }
            
            examples.append(example)
        
        return examples

    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """Format input data into text for model training."""
        scenario = input_data.get("scenario", "general")
        context = input_data.get("context", {})
        user_request = input_data.get("user_request", "")
        principles = input_data.get("constitutional_principles", ["transparency"])
        
        # Create structured input
        input_parts = [
            f"Scenario: {scenario}",
            f"Context: {json.dumps(context)}",
            f"Request: {user_request}",
            f"Constitutional Principles: {', '.join(principles)}",
            f"Constitutional Hash: {input_data.get('constitutional_hash', self.constitutional_hash)}",
            "Decision:"
        ]
        
        return " | ".join(input_parts)

    def _format_target(self, target_output: Dict[str, Any]) -> str:
        """Format target output into text for model training."""
        decision = target_output.get("decision", "")
        reasoning = target_output.get("reasoning", "")
        compliance_score = target_output.get("compliance_score", 1.0)
        
        # Create structured output
        target_parts = [
            f"Decision: {decision}",
            f"Reasoning: {reasoning}",
            f"Compliance Score: {compliance_score:.3f}",
            f"Constitutional Hash: {target_output.get('constitutional_hash', self.constitutional_hash)}"
        ]
        
        return " | ".join(target_parts)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]


class ConstitutionalAIModel(nn.Module):
    """Constitutional AI model with principle-based decision making."""
    
    def __init__(self, config: ConstitutionalAIConfig):
        super().__init__()
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Base language model
        self.base_model = AutoModel.from_pretrained(config.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        
        # Add special tokens if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Constitutional AI heads
        hidden_size = self.base_model.config.hidden_size
        
        # Decision generation head
        self.decision_head = nn.Linear(hidden_size, self.tokenizer.vocab_size)
        
        # Compliance scoring head
        self.compliance_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
        # Principle alignment head
        self.principle_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 8),  # Support for 8 constitutional principles
            nn.Sigmoid()
        )
        
        # Reasoning quality head
        self.reasoning_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
        logger.info(f"Initialized Constitutional AI model with {config.model_name}")

    def forward(
        self, 
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        """Forward pass through Constitutional AI model."""
        
        # Get base model outputs
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        
        # Extract hidden states
        hidden_states = outputs.last_hidden_state
        pooled_output = hidden_states.mean(dim=1)  # Simple pooling
        
        # Generate predictions
        decision_logits = self.decision_head(hidden_states)
        compliance_score = self.compliance_head(pooled_output)
        principle_alignment = self.principle_head(pooled_output)
        reasoning_quality = self.reasoning_head(pooled_output)
        
        # Calculate losses if labels provided
        total_loss = None
        if labels is not None:
            # Decision generation loss
            decision_loss = F.cross_entropy(
                decision_logits.view(-1, decision_logits.size(-1)),
                labels.view(-1),
                ignore_index=self.tokenizer.pad_token_id
            )
            
            # Compliance loss (if compliance scores provided)
            compliance_loss = torch.tensor(0.0, device=input_ids.device)
            if "compliance_score" in kwargs:
                target_compliance = kwargs["compliance_score"].float()
                compliance_loss = F.mse_loss(compliance_score.squeeze(), target_compliance)
            
            # Principle alignment loss
            principle_loss = torch.tensor(0.0, device=input_ids.device)
            if "principle_alignment" in kwargs:
                # Simplified principle loss - would need more sophisticated implementation
                principle_loss = F.mse_loss(principle_alignment.mean(dim=1), torch.ones_like(principle_alignment.mean(dim=1)) * 0.9)
            
            # Reasoning quality loss
            reasoning_loss = F.mse_loss(reasoning_quality.squeeze(), torch.ones_like(reasoning_quality.squeeze()) * 0.9)
            
            # Combine losses with weights
            total_loss = (
                decision_loss +
                self.config.compliance_weight * compliance_loss +
                self.config.principle_weight * principle_loss +
                self.config.reasoning_weight * reasoning_loss
            )
        
        return {
            "loss": total_loss,
            "decision_logits": decision_logits,
            "compliance_score": compliance_score,
            "principle_alignment": principle_alignment,
            "reasoning_quality": reasoning_quality,
            "hidden_states": hidden_states
        }

    def generate_constitutional_decision(
        self, 
        input_text: str,
        max_length: int = 256,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate constitutional decision for given input."""
        
        # Tokenize input
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=self.config.max_length,
            truncation=True,
            padding=True
        )
        
        # Generate decision
        with torch.no_grad():
            outputs = self.forward(**inputs)
            
            # Generate text response
            generated = self.tokenizer.generate(
                inputs["input_ids"],
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
            
            decision_text = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            
            # Extract scores
            compliance_score = outputs["compliance_score"].item()
            principle_alignment = outputs["principle_alignment"].squeeze().tolist()
            reasoning_quality = outputs["reasoning_quality"].item()
        
        return {
            "decision": decision_text,
            "compliance_score": compliance_score,
            "principle_alignment": principle_alignment,
            "reasoning_quality": reasoning_quality,
            "constitutional_hash": self.constitutional_hash
        }


class ConstitutionalAITrainer:
    """Trainer for Constitutional AI models."""
    
    def __init__(self, config: ConstitutionalAIConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Initialize model and tokenizer
        self.model = ConstitutionalAIModel(config)
        self.tokenizer = self.model.tokenizer
        
        # Training metrics
        self.training_history: List[TrainingMetrics] = []
        
        logger.info("Initialized Constitutional AI Trainer")

    async def train(
        self, 
        train_data_path: str,
        val_data_path: Optional[str] = None,
        output_dir: str = "constitutional_ai_model"
    ) -> Dict[str, Any]:
        """Train Constitutional AI model."""
        
        logger.info(f"🚀 Starting Constitutional AI training")
        logger.info(f"📊 Configuration: {self.config}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        # Create datasets
        train_dataset = ConstitutionalAIDataset(
            train_data_path, 
            self.tokenizer, 
            self.config.max_length
        )
        
        val_dataset = None
        if val_data_path:
            val_dataset = ConstitutionalAIDataset(
                val_data_path,
                self.tokenizer,
                self.config.max_length
            )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=2
        )
        
        val_loader = None
        if val_dataset:
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=2
            )
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            warmup_steps=self.config.warmup_steps,
            logging_steps=10,
            evaluation_strategy="epoch" if val_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if val_dataset else False,
            metric_for_best_model="eval_loss" if val_dataset else None,
            greater_is_better=False,
            save_total_limit=3,
            report_to=None,  # Disable wandb/tensorboard
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)] if val_dataset else None,
        )
        
        # Train model
        logger.info("🔥 Starting training...")
        train_result = trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # Calculate training time
        training_time = time.time() - start_time
        
        # Evaluate model
        eval_results = {}
        if val_dataset:
            logger.info("📊 Evaluating model...")
            eval_results = trainer.evaluate()
        
        # Test constitutional compliance
        compliance_results = await self._test_constitutional_compliance(train_dataset)
        
        # Compile results
        results = {
            "constitutional_hash": self.constitutional_hash,
            "training_time_seconds": training_time,
            "train_loss": train_result.training_loss,
            "eval_results": eval_results,
            "compliance_results": compliance_results,
            "model_path": output_dir,
            "config": self.config.__dict__,
            "training_examples": len(train_dataset),
            "validation_examples": len(val_dataset) if val_dataset else 0
        }
        
        logger.info(f"✅ Training completed in {training_time:.2f} seconds")
        logger.info(f"📈 Final train loss: {train_result.training_loss:.4f}")
        logger.info(f"🔒 Constitutional compliance: {compliance_results['compliance_rate']:.2%}")
        
        return results

    async def _test_constitutional_compliance(self, dataset: ConstitutionalAIDataset) -> Dict[str, Any]:
        """Test constitutional compliance of trained model."""
        
        logger.info("🔍 Testing constitutional compliance...")
        
        self.model.eval()
        total_examples = min(100, len(dataset))  # Test on subset
        compliant_examples = 0
        compliance_scores = []
        
        with torch.no_grad():
            for i in range(total_examples):
                example = dataset[i]
                
                # Forward pass
                outputs = self.model(
                    input_ids=example["input_ids"].unsqueeze(0),
                    attention_mask=example["attention_mask"].unsqueeze(0)
                )
                
                # Check compliance score
                compliance_score = outputs["compliance_score"].item()
                compliance_scores.append(compliance_score)
                
                if compliance_score >= self.config.constitutional_threshold:
                    compliant_examples += 1
        
        compliance_rate = compliant_examples / total_examples
        avg_compliance_score = np.mean(compliance_scores)
        
        return {
            "compliance_rate": compliance_rate,
            "avg_compliance_score": avg_compliance_score,
            "total_tested": total_examples,
            "compliant_examples": compliant_examples,
            "constitutional_threshold": self.config.constitutional_threshold,
            "constitutional_hash": self.constitutional_hash
        }
