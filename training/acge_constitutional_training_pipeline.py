"""
ACGE Constitutional AI Training Pipeline

This module implements the constitutional AI training pipeline for ACGE
(Adaptive Constitutional Governance Engine) with RLHF methodology and
constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
Target Compliance: >95%
Response Time Target: ≤2s
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
import wandb
from datasets import load_dataset

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ACGETrainingConfig:
    """Configuration for ACGE constitutional AI training."""

    # Model configuration
    model_name: str = "constitutional-ai-foundation"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    max_sequence_length: int = 4096

    # Training configuration
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    num_epochs: int = 3
    warmup_steps: int = 500

    # Constitutional AI configuration
    constitutional_compliance_threshold: float = 0.95
    rlhf_iterations: int = 1000
    constitutional_principles_weight: float = 2.0

    # Performance targets
    response_time_target_ms: int = 2000
    throughput_target_rps: int = 1000

    # Infrastructure configuration
    use_deepspeed: bool = True
    mixed_precision: bool = True
    gradient_checkpointing: bool = True

    # Monitoring configuration
    wandb_project: str = "acge-constitutional-training"
    log_interval: int = 100
    eval_interval: int = 500
    save_interval: int = 1000


class ConstitutionalDataset(Dataset):
    """Dataset for constitutional AI training with ACGE principles."""

    def __init__(
        self,
        data_path: str,
        tokenizer: AutoTokenizer,
        constitutional_hash: str = "cdd01ef066bc6cf2",
        max_length: int = 4096,
    ):
        self.tokenizer = tokenizer
        self.constitutional_hash = constitutional_hash
        self.max_length = max_length

        # Load constitutional training data
        self.data = self._load_constitutional_data(data_path)
        logger.info(f"Loaded {len(self.data)} constitutional training examples")

    def _load_constitutional_data(self, data_path: str) -> List[Dict[str, Any]]:
        """Load and validate constitutional training data."""

        constitutional_data = []

        # Load constitutional principles corpus
        with open(f"{data_path}/constitutional_principles.json", "r") as f:
            principles_data = json.load(f)

        # Load governance decision precedents
        with open(f"{data_path}/governance_precedents.json", "r") as f:
            precedents_data = json.load(f)

        # Load constitutional violation examples
        with open(f"{data_path}/constitutional_violations.json", "r") as f:
            violations_data = json.load(f)

        # Combine and validate data
        for example in principles_data + precedents_data + violations_data:
            if self._validate_constitutional_example(example):
                constitutional_data.append(example)

        return constitutional_data

    def _validate_constitutional_example(self, example: Dict[str, Any]) -> bool:
        """Validate constitutional training example."""

        required_fields = [
            "constitutional_context",
            "governance_scenario",
            "constitutional_compliance_score",
            "constitutional_reasoning",
            "constitutional_hash",
        ]

        # Check required fields
        for field in required_fields:
            if field not in example:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate constitutional hash
        if example["constitutional_hash"] != self.constitutional_hash:
            logger.warning(
                f"Constitutional hash mismatch: {example['constitutional_hash']}"
            )
            return False

        # Validate compliance score
        compliance_score = example["constitutional_compliance_score"]
        if not (0.0 <= compliance_score <= 1.0):
            logger.warning(f"Invalid compliance score: {compliance_score}")
            return False

        return True

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get constitutional training example."""

        example = self.data[idx]

        # Format constitutional training prompt
        prompt = self._format_constitutional_prompt(example)

        # Tokenize
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "constitutional_compliance_score": torch.tensor(
                example["constitutional_compliance_score"], dtype=torch.float32
            ),
            "constitutional_hash": example["constitutional_hash"],
        }

    def _format_constitutional_prompt(self, example: Dict[str, Any]) -> str:
        """Format constitutional training prompt."""

        prompt = f"""Constitutional Governance Analysis

Constitutional Hash: {example['constitutional_hash']}

Governance Scenario:
{example['governance_scenario']}

Constitutional Context:
{example['constitutional_context']}

Constitutional Analysis:
{example['constitutional_reasoning']}

Constitutional Compliance Score: {example['constitutional_compliance_score']:.3f}

Constitutional Decision: {"COMPLIANT" if example['constitutional_compliance_score'] >= 0.95 else "NON-COMPLIANT"}
"""

        return prompt


class ACGEConstitutionalTrainer:
    """Constitutional AI trainer for ACGE model."""

    def __init__(self, config: ACGETrainingConfig):
        self.config = config
        self.constitutional_hash = config.constitutional_hash

        # Initialize model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(config.model_name)

        # Add special tokens for constitutional AI
        special_tokens = [
            "<constitutional>",
            "</constitutional>",
            "<compliance>",
            "</compliance>",
            "<violation>",
            "</violation>",
        ]
        self.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})
        self.model.resize_token_embeddings(len(self.tokenizer))

        # Initialize training components
        self.constitutional_compliance_head = nn.Linear(
            self.model.config.hidden_size, 1
        )

        # Initialize monitoring
        if config.wandb_project:
            wandb.init(
                project=config.wandb_project,
                config=config.__dict__,
                tags=["constitutional-ai", "acge", "rlhf"],
            )

    async def train_constitutional_model(
        self, train_data_path: str, val_data_path: str
    ) -> Dict[str, Any]:
        """Train ACGE constitutional model with RLHF."""

        training_start = time.time()
        logger.info("Starting ACGE constitutional AI training...")

        # Load datasets
        train_dataset = ConstitutionalDataset(
            train_data_path,
            self.tokenizer,
            self.constitutional_hash,
            self.config.max_sequence_length,
        )

        val_dataset = ConstitutionalDataset(
            val_data_path,
            self.tokenizer,
            self.constitutional_hash,
            self.config.max_sequence_length,
        )

        # Configure training arguments
        training_args = TrainingArguments(
            output_dir=f"./acge_constitutional_model_{self.constitutional_hash}",
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.log_interval,
            eval_steps=self.config.eval_interval,
            save_steps=self.config.save_interval,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="constitutional_compliance",
            greater_is_better=True,
            fp16=self.config.mixed_precision,
            gradient_checkpointing=self.config.gradient_checkpointing,
            dataloader_num_workers=4,
            remove_unused_columns=False,
            report_to="wandb" if self.config.wandb_project else None,
        )

        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self._compute_constitutional_metrics,
            callbacks=[ConstitutionalComplianceCallback(self.config)],
        )

        # Train model
        training_result = trainer.train()

        # Evaluate final model
        eval_result = await self._evaluate_constitutional_compliance(val_dataset)

        training_duration = time.time() - training_start

        training_summary = {
            "training_duration_seconds": training_duration,
            "constitutional_hash": self.constitutional_hash,
            "final_constitutional_compliance": eval_result["constitutional_compliance"],
            "final_response_time_ms": eval_result["avg_response_time_ms"],
            "model_path": training_args.output_dir,
            "training_loss": training_result.training_loss,
            "eval_loss": training_result.log_history[-1].get("eval_loss", 0.0),
        }

        logger.info(f"ACGE constitutional training completed: {training_summary}")
        return training_summary

    def _compute_constitutional_metrics(self, eval_pred) -> Dict[str, float]:
        """Compute constitutional compliance metrics."""

        predictions, labels = eval_pred

        # Calculate constitutional compliance accuracy
        compliance_predictions = torch.sigmoid(torch.tensor(predictions))
        compliance_labels = torch.tensor(labels)

        compliance_accuracy = (
            ((compliance_predictions >= 0.95) == (compliance_labels >= 0.95))
            .float()
            .mean()
            .item()
        )

        return {
            "constitutional_compliance": compliance_accuracy,
            "avg_compliance_score": compliance_predictions.mean().item(),
        }

    async def _evaluate_constitutional_compliance(
        self, dataset: ConstitutionalDataset
    ) -> Dict[str, Any]:
        """Evaluate constitutional compliance on validation set."""

        self.model.eval()
        total_compliance = 0.0
        total_response_time = 0.0
        num_samples = min(1000, len(dataset))  # Sample for evaluation

        with torch.no_grad():
            for i in range(num_samples):
                start_time = time.time()

                sample = dataset[i]
                input_ids = sample["input_ids"].unsqueeze(0)
                attention_mask = sample["attention_mask"].unsqueeze(0)

                # Generate constitutional response
                outputs = self.model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

                response_time = (time.time() - start_time) * 1000
                total_response_time += response_time

                # Evaluate constitutional compliance
                compliance_score = await self._evaluate_response_compliance(
                    outputs[0], sample["constitutional_compliance_score"]
                )
                total_compliance += compliance_score

        return {
            "constitutional_compliance": total_compliance / num_samples,
            "avg_response_time_ms": total_response_time / num_samples,
        }

    async def _evaluate_response_compliance(
        self, generated_tokens: torch.Tensor, target_compliance: torch.Tensor
    ) -> float:
        """Evaluate constitutional compliance of generated response."""

        # Decode generated response
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        # Simple compliance evaluation (would be more sophisticated in practice)
        compliance_indicators = [
            "constitutional",
            "compliant",
            "governance",
            "principle",
            "democratic",
        ]

        compliance_score = sum(
            1
            for indicator in compliance_indicators
            if indicator.lower() in response.lower()
        ) / len(compliance_indicators)

        return compliance_score


class ConstitutionalComplianceCallback:
    """Callback for monitoring constitutional compliance during training."""

    def __init__(self, config: ACGETrainingConfig):
        self.config = config
        self.constitutional_hash = config.constitutional_hash

    def on_evaluate(self, args, state, control, model, logs=None, **kwargs):
        """Monitor constitutional compliance during evaluation."""

        if logs and "eval_constitutional_compliance" in logs:
            compliance = logs["eval_constitutional_compliance"]

            if compliance < self.config.constitutional_compliance_threshold:
                logger.warning(
                    f"Constitutional compliance below threshold: "
                    f"{compliance:.3f} < {self.config.constitutional_compliance_threshold}"
                )

            # Log to wandb if available
            if wandb.run:
                wandb.log(
                    {
                        "constitutional_compliance": compliance,
                        "constitutional_hash": self.constitutional_hash,
                        "step": state.global_step,
                    }
                )


# Training execution
async def main():
    """Main training execution."""

    config = ACGETrainingConfig()
    trainer = ACGEConstitutionalTrainer(config)

    # Train constitutional model
    training_result = await trainer.train_constitutional_model(
        train_data_path="./data/constitutional_training",
        val_data_path="./data/constitutional_validation",
    )

    logger.info(f"ACGE constitutional training completed: {training_result}")


if __name__ == "__main__":
    asyncio.run(main())
