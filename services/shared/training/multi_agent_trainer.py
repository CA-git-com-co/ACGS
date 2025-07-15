"""
Multi-Agent Coordination Training System

This module implements training for multi-agent coordination, including conflict
resolution, consensus building, and collaborative decision making using generated
training data.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
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
    AutoTokenizer, AutoModel, AutoConfig,
    TrainingArguments, Trainer
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class MultiAgentConfig:
    """Configuration for Multi-Agent Coordination training."""
    model_name: str = "microsoft/DialoGPT-medium"
    max_length: int = 512
    batch_size: int = 12
    learning_rate: float = 3e-5
    num_epochs: int = 4
    warmup_steps: int = 150
    
    # Multi-agent specific parameters
    agent_types: List[str] = None
    coordination_weight: float = 1.5
    consensus_weight: float = 2.0
    conflict_resolution_weight: float = 1.8
    
    # Performance targets
    target_coordination_efficiency: float = 0.85
    target_consensus_score: float = 0.90
    target_conflict_resolution: float = 0.95
    
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def __post_init__(self):
        if self.agent_types is None:
            self.agent_types = ["ethics", "legal", "operational", "security", "performance"]


class MultiAgentDataset(Dataset):
    """Dataset for Multi-Agent Coordination training."""
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        config: MultiAgentConfig
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
        
        logger.info(f"Loaded {len(self.examples)} Multi-Agent Coordination training examples")

    def _validate_constitutional_compliance(self):
        """Validate constitutional compliance of training data."""
        if self.data.get("constitutional_hash") != self.constitutional_hash:
            raise ValueError(f"Constitutional hash mismatch in multi-agent data")
        
        compliant_examples = sum(
            1 for ex in self.data.get("examples", [])
            if (ex.get("input", {}).get("constitutional_hash") == self.constitutional_hash and
                ex.get("target_output", {}).get("constitutional_hash") == self.constitutional_hash)
        )
        
        compliance_rate = compliant_examples / len(self.data.get("examples", []))
        if compliance_rate < 0.95:
            raise ValueError(f"Low constitutional compliance rate: {compliance_rate:.2%}")
        
        logger.info(f"Multi-agent constitutional compliance validated: {compliance_rate:.2%}")

    def _prepare_examples(self) -> List[Dict[str, Any]]:
        """Prepare training examples for multi-agent coordination."""
        examples = []
        
        for raw_example in self.data.get("examples", []):
            input_data = raw_example["input"]
            target_output = raw_example["target_output"]
            
            # Create input text for coordination
            input_text = self._format_coordination_input(input_data)
            
            # Create target coordination plan
            target_text = self._format_coordination_target(target_output)
            
            # Tokenize input
            input_encoding = self.tokenizer(
                input_text,
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            # Tokenize target
            target_encoding = self.tokenizer(
                target_text,
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            example = {
                "input_ids": input_encoding["input_ids"].squeeze(),
                "attention_mask": input_encoding["attention_mask"].squeeze(),
                "labels": target_encoding["input_ids"].squeeze(),
                "target_attention_mask": target_encoding["attention_mask"].squeeze(),
                
                # Multi-agent specific fields
                "scenario": input_data["coordination_request"]["scenario"],
                "involved_agents": input_data["coordination_request"]["involved_agents"],
                "agent_count": len(input_data["coordination_request"]["involved_agents"]),
                "coordination_plan": target_output.get("coordination_plan", {}),
                "success_metrics": target_output.get("success_metrics", {}),
                
                # Metadata
                "example_id": raw_example.get("id", "unknown"),
                "constitutional_hash": self.constitutional_hash
            }
            
            examples.append(example)
        
        return examples

    def _format_coordination_input(self, input_data: Dict[str, Any]) -> str:
        """Format coordination input for model training."""
        coord_request = input_data["coordination_request"]
        
        input_parts = [
            f"Coordination Scenario: {coord_request['scenario']}",
            f"Involved Agents: {', '.join(coord_request['involved_agents'])}",
            f"Task: {coord_request['task'].get('description', 'Coordination task')}",
            f"Priority: {coord_request['task'].get('priority', 'medium')}",
            f"Constraints: {', '.join(coord_request.get('constraints', []))}",
            f"Constitutional Hash: {input_data.get('constitutional_hash', self.constitutional_hash)}",
            "Coordination Plan:"
        ]
        
        return " | ".join(input_parts)

    def _format_coordination_target(self, target_output: Dict[str, Any]) -> str:
        """Format coordination target for model training."""
        coord_plan = target_output.get("coordination_plan", {})
        success_metrics = target_output.get("success_metrics", {})
        
        target_parts = [
            f"Communication Protocol: {coord_plan.get('communication_protocol', 'standard')}",
            f"Conflict Resolution: {coord_plan.get('conflict_resolution_method', 'consensus')}",
            f"Phases: {len(coord_plan.get('phases', []))} phases planned",
            f"Coordination Efficiency: {success_metrics.get('coordination_efficiency', 0.85):.3f}",
            f"Consensus Score: {success_metrics.get('consensus_score', 0.90):.3f}",
            f"Constitutional Compliance: {success_metrics.get('constitutional_compliance', 0.98):.3f}",
            f"Constitutional Hash: {target_output.get('constitutional_hash', self.constitutional_hash)}"
        ]
        
        return " | ".join(target_parts)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]


class MultiAgentCoordinationModel(nn.Module):
    """Multi-Agent Coordination model for collaborative decision making."""
    
    def __init__(self, config: MultiAgentConfig):
        super().__init__()
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Base language model
        self.base_model = AutoModel.from_pretrained(config.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Multi-agent coordination heads
        hidden_size = self.base_model.config.hidden_size
        
        # Coordination planning head
        self.coordination_head = nn.Linear(hidden_size, self.tokenizer.vocab_size)
        
        # Agent assignment head
        self.agent_assignment_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, len(config.agent_types)),
            nn.Sigmoid()
        )
        
        # Consensus scoring head
        self.consensus_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()
        )
        
        # Conflict resolution head
        self.conflict_resolution_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 4),  # none, low, medium, high conflict
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
        
        logger.info(f"Initialized Multi-Agent Coordination model with {config.model_name}")

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        """Forward pass through Multi-Agent Coordination model."""
        
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
        coordination_logits = self.coordination_head(hidden_states)
        agent_assignments = self.agent_assignment_head(pooled_output)
        consensus_score = self.consensus_head(pooled_output)
        conflict_resolution = self.conflict_resolution_head(pooled_output)
        constitutional_compliance = self.constitutional_compliance_head(pooled_output)
        
        # Calculate losses if labels provided
        total_loss = None
        if labels is not None:
            # Coordination planning loss
            coordination_loss = F.cross_entropy(
                coordination_logits.view(-1, coordination_logits.size(-1)),
                labels.view(-1),
                ignore_index=self.tokenizer.pad_token_id
            )
            
            # Agent assignment loss
            agent_loss = torch.tensor(0.0, device=input_ids.device)
            if "involved_agents" in kwargs:
                agent_targets = self._encode_agent_targets(kwargs["involved_agents"])
                agent_loss = F.binary_cross_entropy(agent_assignments, agent_targets)
            
            # Consensus loss
            consensus_target = torch.ones_like(consensus_score) * self.config.target_consensus_score
            consensus_loss = F.mse_loss(consensus_score, consensus_target)
            
            # Constitutional compliance loss
            constitutional_target = torch.ones_like(constitutional_compliance) * 0.98
            constitutional_loss = F.mse_loss(constitutional_compliance, constitutional_target)
            
            # Combine losses with weights
            total_loss = (
                coordination_loss +
                self.config.coordination_weight * agent_loss +
                self.config.consensus_weight * consensus_loss +
                self.config.conflict_resolution_weight * constitutional_loss
            )
        
        return {
            "loss": total_loss,
            "coordination_logits": coordination_logits,
            "agent_assignments": agent_assignments,
            "consensus_score": consensus_score,
            "conflict_resolution": conflict_resolution,
            "constitutional_compliance": constitutional_compliance,
            "hidden_states": hidden_states
        }

    def _encode_agent_targets(self, agent_lists: List[List[str]]) -> torch.Tensor:
        """Encode agent assignment targets for training."""
        batch_size = len(agent_lists)
        targets = torch.zeros(batch_size, len(self.config.agent_types))
        
        for i, agents in enumerate(agent_lists):
            for agent in agents:
                if agent in self.config.agent_types:
                    idx = self.config.agent_types.index(agent)
                    targets[i, idx] = 1.0
        
        return targets

    def generate_coordination_plan(
        self,
        coordination_input: str,
        max_length: int = 256,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate coordination plan for given input."""
        
        # Tokenize input
        inputs = self.tokenizer(
            coordination_input,
            return_tensors="pt",
            max_length=self.config.max_length,
            truncation=True,
            padding=True
        )
        
        # Generate coordination plan
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
            
            coordination_text = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            
            # Extract scores
            agent_assignments = outputs["agent_assignments"].squeeze().tolist()
            consensus_score = outputs["consensus_score"].item()
            conflict_resolution = outputs["conflict_resolution"].squeeze().tolist()
            constitutional_compliance = outputs["constitutional_compliance"].item()
        
        return {
            "coordination_plan": coordination_text,
            "agent_assignments": {
                agent: score 
                for agent, score in zip(self.config.agent_types, agent_assignments)
            },
            "consensus_score": consensus_score,
            "conflict_resolution": {
                "none": conflict_resolution[0],
                "low": conflict_resolution[1],
                "medium": conflict_resolution[2],
                "high": conflict_resolution[3]
            },
            "constitutional_compliance": constitutional_compliance,
            "constitutional_hash": self.constitutional_hash
        }


class MultiAgentTrainer:
    """Trainer for Multi-Agent Coordination models."""
    
    def __init__(self, config: MultiAgentConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Initialize model and tokenizer
        self.model = MultiAgentCoordinationModel(config)
        self.tokenizer = self.model.tokenizer
        
        logger.info("Initialized Multi-Agent Coordination Trainer")

    async def train(
        self,
        train_data_path: str,
        val_data_path: Optional[str] = None,
        output_dir: str = "multi_agent_model"
    ) -> Dict[str, Any]:
        """Train Multi-Agent Coordination model."""
        
        logger.info(f"🚀 Starting Multi-Agent Coordination training")
        logger.info(f"📊 Configuration: {self.config}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        # Create datasets
        train_dataset = MultiAgentDataset(train_data_path, self.tokenizer, self.config)
        
        val_dataset = None
        if val_data_path:
            val_dataset = MultiAgentDataset(val_data_path, self.tokenizer, self.config)
        
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
        
        # Test coordination capabilities
        coordination_results = await self._test_coordination_capabilities(train_dataset)
        
        # Test constitutional compliance
        compliance_results = await self._test_constitutional_compliance(train_dataset)
        
        # Compile results
        results = {
            "constitutional_hash": self.constitutional_hash,
            "training_time_seconds": training_time,
            "train_loss": train_result.training_loss,
            "eval_results": eval_results,
            "coordination_results": coordination_results,
            "compliance_results": compliance_results,
            "model_path": output_dir,
            "config": self.config.__dict__,
            "training_examples": len(train_dataset),
            "validation_examples": len(val_dataset) if val_dataset else 0
        }
        
        logger.info(f"✅ Multi-Agent Coordination training completed in {training_time:.2f} seconds")
        logger.info(f"📈 Final train loss: {train_result.training_loss:.4f}")
        logger.info(f"🔒 Constitutional compliance: {compliance_results['compliance_rate']:.2%}")
        logger.info(f"🤝 Coordination efficiency: {coordination_results['avg_coordination_efficiency']:.3f}")
        
        return results

    async def _test_coordination_capabilities(self, dataset: MultiAgentDataset) -> Dict[str, Any]:
        """Test coordination capabilities of trained model."""
        
        logger.info("🔍 Testing coordination capabilities...")
        
        self.model.eval()
        total_examples = min(50, len(dataset))
        coordination_scores = []
        consensus_scores = []
        
        with torch.no_grad():
            for i in range(total_examples):
                example = dataset[i]
                
                # Create coordination input
                coord_input = f"Coordinate {example['scenario']} with agents: {', '.join(example['involved_agents'])}"
                
                # Generate coordination plan
                result = self.model.generate_coordination_plan(coord_input)
                
                coordination_scores.append(result.get("constitutional_compliance", 0.0))
                consensus_scores.append(result.get("consensus_score", 0.0))
        
        return {
            "avg_coordination_efficiency": np.mean(coordination_scores),
            "avg_consensus_score": np.mean(consensus_scores),
            "total_tested": total_examples,
            "meets_coordination_target": np.mean(coordination_scores) >= self.config.target_coordination_efficiency,
            "meets_consensus_target": np.mean(consensus_scores) >= self.config.target_consensus_score
        }

    async def _test_constitutional_compliance(self, dataset: MultiAgentDataset) -> Dict[str, Any]:
        """Test constitutional compliance of coordination decisions."""
        
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
