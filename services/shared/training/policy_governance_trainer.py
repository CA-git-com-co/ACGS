"""
Policy Governance Fine-tuning System

This module implements fine-tuning for OPA rule generation, compliance assessment,
and multi-framework policy governance using generated training data.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForSeq2Seq, T5ForConditionalGeneration,
    TrainingArguments, Trainer
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class PolicyGovernanceConfig:
    """Configuration for Policy Governance training."""
    model_name: str = "t5-base"
    max_input_length: int = 512
    max_target_length: int = 256
    batch_size: int = 8
    learning_rate: float = 3e-4
    num_epochs: int = 5
    warmup_steps: int = 200
    
    # Policy-specific parameters
    opa_rule_weight: float = 2.0
    compliance_weight: float = 1.5
    framework_weight: float = 1.0
    
    # Supported frameworks
    supported_frameworks: List[str] = None
    
    # Performance targets
    target_rule_accuracy: float = 0.95
    target_compliance_score: float = 0.98
    
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def __post_init__(self):
        if self.supported_frameworks is None:
            self.supported_frameworks = ["GDPR", "HIPAA", "SOX", "PCI_DSS", "ACGS_Constitutional"]


class PolicyGovernanceDataset(Dataset):
    """Dataset for Policy Governance training."""
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        config: PolicyGovernanceConfig
    ):
        self.tokenizer = tokenizer
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Load training data
        with open(data_path, 'r') as f:
            self.data = json.load(f)
        
        # Validate constitutional compliance
        self._validate_constitutional_compliance()
        
        # Prepare examples
        self.examples = self._prepare_examples()
        
        logger.info(f"Loaded {len(self.examples)} Policy Governance training examples")

    def _validate_constitutional_compliance(self):
        """Validate constitutional compliance of training data."""
        if self.data.get("constitutional_hash") != self.constitutional_hash:
            raise ValueError(f"Constitutional hash mismatch in policy governance data")
        
        compliant_examples = sum(
            1 for ex in self.data.get("examples", [])
            if (ex.get("input", {}).get("constitutional_hash") == self.constitutional_hash and
                ex.get("target_output", {}).get("constitutional_hash") == self.constitutional_hash)
        )
        
        compliance_rate = compliant_examples / len(self.data.get("examples", []))
        if compliance_rate < 0.95:
            raise ValueError(f"Low constitutional compliance rate: {compliance_rate:.2%}")
        
        logger.info(f"Policy governance constitutional compliance validated: {compliance_rate:.2%}")

    def _prepare_examples(self) -> List[Dict[str, Any]]:
        """Prepare training examples for policy governance."""
        examples = []
        
        for raw_example in self.data.get("examples", []):
            input_data = raw_example["input"]
            target_output = raw_example["target_output"]
            
            # Create input text for OPA rule generation
            input_text = self._format_policy_input(input_data)
            
            # Create target OPA rule
            target_rule = target_output.get("opa_rule", "")
            
            # Tokenize input
            input_encoding = self.tokenizer(
                input_text,
                max_length=self.config.max_input_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            # Tokenize target
            target_encoding = self.tokenizer(
                target_rule,
                max_length=self.config.max_target_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            example = {
                "input_ids": input_encoding["input_ids"].squeeze(),
                "attention_mask": input_encoding["attention_mask"].squeeze(),
                "labels": target_encoding["input_ids"].squeeze(),
                
                # Policy-specific fields
                "policy_type": input_data["policy_request"]["type"],
                "framework": input_data["policy_request"]["framework"],
                "scope": input_data["policy_request"].get("scope", "system"),
                "governance_decision": target_output.get("governance_decision", {}),
                "compliance_assessment": target_output.get("compliance_assessment", {}),
                
                # Metadata
                "example_id": raw_example.get("id", "unknown"),
                "constitutional_hash": self.constitutional_hash
            }
            
            examples.append(example)
        
        return examples

    def _format_policy_input(self, input_data: Dict[str, Any]) -> str:
        """Format policy input for OPA rule generation."""
        policy_request = input_data["policy_request"]
        
        input_parts = [
            f"Generate OPA rule for policy type: {policy_request['type']}",
            f"Framework: {policy_request['framework']}",
            f"Scope: {policy_request.get('scope', 'system')}",
            f"Context: {policy_request.get('context', 'Standard policy implementation')}",
            f"Constitutional Hash: {input_data.get('constitutional_hash', self.constitutional_hash)}",
            "OPA Rule:"
        ]
        
        return " | ".join(input_parts)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]


class PolicyGovernanceModel(nn.Module):
    """Policy Governance model for OPA rule generation and compliance assessment."""
    
    def __init__(self, config: PolicyGovernanceConfig):
        super().__init__()
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Base T5 model for sequence-to-sequence generation
        self.base_model = T5ForConditionalGeneration.from_pretrained(config.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        
        # Policy-specific heads
        hidden_size = self.base_model.config.d_model
        
        # Framework compliance head
        self.framework_compliance_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, len(config.supported_frameworks)),
            nn.Sigmoid()
        )
        
        # Risk assessment head
        self.risk_assessment_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 3),  # low, medium, high risk
            nn.Softmax(dim=-1)
        )
        
        # Constitutional compliance head
        self.constitutional_compliance_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )
        
        logger.info(f"Initialized Policy Governance model with {config.model_name}")

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        """Forward pass through Policy Governance model."""
        
        # Get base model outputs
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            return_dict=True
        )
        
        # Extract encoder hidden states for additional heads
        encoder_outputs = self.base_model.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        
        # Pool encoder outputs
        pooled_output = encoder_outputs.last_hidden_state.mean(dim=1)
        
        # Generate additional predictions
        framework_compliance = self.framework_compliance_head(pooled_output)
        risk_assessment = self.risk_assessment_head(pooled_output)
        constitutional_compliance = self.constitutional_compliance_head(pooled_output)
        
        # Calculate additional losses if training
        additional_loss = torch.tensor(0.0, device=input_ids.device)
        if labels is not None:
            # Framework compliance loss
            if "framework" in kwargs:
                framework_targets = self._encode_framework_targets(kwargs["framework"])
                framework_loss = F.binary_cross_entropy(framework_compliance, framework_targets)
                additional_loss += self.config.framework_weight * framework_loss
            
            # Constitutional compliance loss
            constitutional_target = torch.ones_like(constitutional_compliance) * 0.98
            constitutional_loss = F.mse_loss(constitutional_compliance, constitutional_target)
            additional_loss += self.config.compliance_weight * constitutional_loss
        
        # Combine losses
        total_loss = outputs.loss
        if total_loss is not None:
            total_loss = total_loss + additional_loss
        
        return {
            "loss": total_loss,
            "logits": outputs.logits,
            "framework_compliance": framework_compliance,
            "risk_assessment": risk_assessment,
            "constitutional_compliance": constitutional_compliance,
            "encoder_hidden_states": encoder_outputs.last_hidden_state
        }

    def _encode_framework_targets(self, frameworks: List[str]) -> torch.Tensor:
        """Encode framework targets for training."""
        batch_size = len(frameworks)
        targets = torch.zeros(batch_size, len(self.config.supported_frameworks))
        
        for i, framework in enumerate(frameworks):
            if framework in self.config.supported_frameworks:
                idx = self.config.supported_frameworks.index(framework)
                targets[i, idx] = 1.0
        
        return targets

    def generate_opa_rule(
        self,
        policy_input: str,
        max_length: int = 256,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate OPA rule for given policy input."""
        
        # Tokenize input
        inputs = self.tokenizer(
            policy_input,
            return_tensors="pt",
            max_length=self.config.max_input_length,
            truncation=True,
            padding=True
        )
        
        # Generate OPA rule
        with torch.no_grad():
            # Get additional predictions
            outputs = self.forward(**inputs)
            
            # Generate rule text
            generated = self.base_model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
            
            opa_rule = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            
            # Extract compliance scores
            framework_compliance = outputs["framework_compliance"].squeeze().tolist()
            risk_assessment = outputs["risk_assessment"].squeeze().tolist()
            constitutional_compliance = outputs["constitutional_compliance"].item()
        
        return {
            "opa_rule": opa_rule,
            "framework_compliance": {
                framework: score 
                for framework, score in zip(self.config.supported_frameworks, framework_compliance)
            },
            "risk_assessment": {
                "low": risk_assessment[0],
                "medium": risk_assessment[1], 
                "high": risk_assessment[2]
            },
            "constitutional_compliance": constitutional_compliance,
            "constitutional_hash": self.constitutional_hash
        }

    def validate_opa_rule(self, opa_rule: str) -> Dict[str, Any]:
        """Validate generated OPA rule syntax and structure."""
        
        validation_results = {
            "is_valid": False,
            "syntax_score": 0.0,
            "structure_score": 0.0,
            "constitutional_compliance": False,
            "issues": []
        }
        
        # Basic syntax validation
        syntax_checks = [
            ("package declaration", r"package\s+[\w\.]+"),
            ("import statement", r"import\s+rego\.v1"),
            ("default rule", r"default\s+\w+\s*:=\s*\w+"),
            ("allow rule", r"allow\s+if\s*\{"),
            ("constitutional compliance", rf"constitutional_hash.*{self.constitutional_hash}")
        ]
        
        syntax_score = 0
        for check_name, pattern in syntax_checks:
            if re.search(pattern, opa_rule, re.IGNORECASE):
                syntax_score += 1
            else:
                validation_results["issues"].append(f"Missing {check_name}")
        
        validation_results["syntax_score"] = syntax_score / len(syntax_checks)
        
        # Structure validation
        structure_checks = [
            "package" in opa_rule.lower(),
            "default" in opa_rule.lower(),
            "allow" in opa_rule.lower(),
            "{" in opa_rule and "}" in opa_rule,
            len(opa_rule.strip()) > 50  # Minimum rule length
        ]
        
        structure_score = sum(structure_checks) / len(structure_checks)
        validation_results["structure_score"] = structure_score
        
        # Constitutional compliance check
        constitutional_compliance = self.constitutional_hash in opa_rule
        validation_results["constitutional_compliance"] = constitutional_compliance
        
        if not constitutional_compliance:
            validation_results["issues"].append("Missing constitutional hash")
        
        # Overall validity
        validation_results["is_valid"] = (
            validation_results["syntax_score"] >= 0.8 and
            validation_results["structure_score"] >= 0.8 and
            constitutional_compliance
        )
        
        return validation_results


class PolicyGovernanceTrainer:
    """Trainer for Policy Governance models."""
    
    def __init__(self, config: PolicyGovernanceConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Initialize model and tokenizer
        self.model = PolicyGovernanceModel(config)
        self.tokenizer = self.model.tokenizer
        
        logger.info("Initialized Policy Governance Trainer")

    async def train(
        self,
        train_data_path: str,
        val_data_path: Optional[str] = None,
        output_dir: str = "policy_governance_model"
    ) -> Dict[str, Any]:
        """Train Policy Governance model."""
        
        logger.info(f"🚀 Starting Policy Governance training")
        logger.info(f"📊 Configuration: {self.config}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        # Create datasets
        train_dataset = PolicyGovernanceDataset(train_data_path, self.tokenizer, self.config)
        
        val_dataset = None
        if val_data_path:
            val_dataset = PolicyGovernanceDataset(val_data_path, self.tokenizer, self.config)
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=10,
            evaluation_strategy="epoch" if val_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if val_dataset else False,
            metric_for_best_model="eval_loss" if val_dataset else None,
            save_total_limit=3,
            report_to=None,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
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
        
        # Test OPA rule generation
        rule_generation_results = await self._test_opa_rule_generation(train_dataset)
        
        # Test constitutional compliance
        compliance_results = await self._test_constitutional_compliance(train_dataset)
        
        # Compile results
        results = {
            "constitutional_hash": self.constitutional_hash,
            "training_time_seconds": training_time,
            "train_loss": train_result.training_loss,
            "eval_results": eval_results,
            "rule_generation_results": rule_generation_results,
            "compliance_results": compliance_results,
            "model_path": output_dir,
            "config": self.config.__dict__,
            "training_examples": len(train_dataset),
            "validation_examples": len(val_dataset) if val_dataset else 0
        }
        
        logger.info(f"✅ Policy Governance training completed in {training_time:.2f} seconds")
        logger.info(f"📈 Final train loss: {train_result.training_loss:.4f}")
        logger.info(f"🔒 Constitutional compliance: {compliance_results['compliance_rate']:.2%}")
        logger.info(f"📋 OPA rule validity: {rule_generation_results['valid_rules_rate']:.2%}")
        
        return results

    async def _test_opa_rule_generation(self, dataset: PolicyGovernanceDataset) -> Dict[str, Any]:
        """Test OPA rule generation quality."""
        
        logger.info("🔍 Testing OPA rule generation...")
        
        self.model.eval()
        total_examples = min(50, len(dataset))  # Test on subset
        valid_rules = 0
        syntax_scores = []
        structure_scores = []
        
        with torch.no_grad():
            for i in range(total_examples):
                example = dataset[i]
                
                # Create input text
                policy_input = f"Generate OPA rule for {example['policy_type']} under {example['framework']}"
                
                # Generate rule
                result = self.model.generate_opa_rule(policy_input)
                opa_rule = result["opa_rule"]
                
                # Validate rule
                validation = self.model.validate_opa_rule(opa_rule)
                
                if validation["is_valid"]:
                    valid_rules += 1
                
                syntax_scores.append(validation["syntax_score"])
                structure_scores.append(validation["structure_score"])
        
        return {
            "valid_rules_rate": valid_rules / total_examples,
            "avg_syntax_score": np.mean(syntax_scores),
            "avg_structure_score": np.mean(structure_scores),
            "total_tested": total_examples,
            "valid_rules": valid_rules
        }

    async def _test_constitutional_compliance(self, dataset: PolicyGovernanceDataset) -> Dict[str, Any]:
        """Test constitutional compliance of generated policies."""
        
        logger.info("🔍 Testing constitutional compliance...")
        
        self.model.eval()
        total_examples = min(100, len(dataset))
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
                
                # Check compliance
                compliance_score = outputs["constitutional_compliance"].item()
                compliance_scores.append(compliance_score)
                
                if compliance_score >= 0.95:
                    compliant_examples += 1
        
        compliance_rate = compliant_examples / total_examples
        avg_compliance_score = np.mean(compliance_scores)
        
        return {
            "compliance_rate": compliance_rate,
            "avg_compliance_score": avg_compliance_score,
            "total_tested": total_examples,
            "compliant_examples": compliant_examples,
            "constitutional_hash": self.constitutional_hash
        }
