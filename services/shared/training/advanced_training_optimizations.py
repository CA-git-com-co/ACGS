"""
Advanced Training Optimizations for ACGS-2

This module implements advanced training techniques including distributed training,
mixed precision, gradient accumulation, learning rate scheduling, and other
optimizations for improved training efficiency and model performance.

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
from torch.utils.data import Dataset, DataLoader, DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.cuda.amp import GradScaler, autocast
from transformers import (
    get_linear_schedule_with_warmup,
    get_cosine_schedule_with_warmup,
    get_polynomial_decay_schedule_with_warmup
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class AdvancedTrainingConfig:
    """Configuration for advanced training optimizations."""
    
    # Mixed precision training
    use_mixed_precision: bool = True
    fp16_opt_level: str = "O1"  # O0, O1, O2, O3
    
    # Gradient optimization
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0
    gradient_checkpointing: bool = True
    
    # Learning rate scheduling
    lr_scheduler_type: str = "cosine"  # linear, cosine, polynomial
    warmup_ratio: float = 0.1
    lr_decay_factor: float = 0.95
    min_lr_ratio: float = 0.01
    
    # Distributed training
    use_distributed: bool = False
    world_size: int = 1
    local_rank: int = 0
    
    # Memory optimization
    dataloader_num_workers: int = 4
    pin_memory: bool = True
    prefetch_factor: int = 2
    
    # Training stability
    loss_scaling: float = 1.0
    early_stopping_patience: int = 3
    save_steps: int = 500
    eval_steps: int = 100
    
    # Performance monitoring
    log_training_dynamics: bool = True
    track_gradient_norms: bool = True
    monitor_memory_usage: bool = True
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class TrainingMetrics:
    """Advanced training metrics tracking."""
    epoch: int
    step: int
    loss: float
    learning_rate: float
    gradient_norm: float
    memory_usage_mb: float
    throughput_samples_per_sec: float
    constitutional_compliance: float
    training_time_seconds: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


class AdvancedTrainingOptimizer:
    """
    Advanced training optimizer with state-of-the-art techniques.
    
    Implements mixed precision, gradient accumulation, advanced scheduling,
    and distributed training for optimal performance.
    """
    
    def __init__(self, config: AdvancedTrainingConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Initialize components
        self.scaler = None
        self.scheduler = None
        self.metrics_history: List[TrainingMetrics] = []
        
        # Setup mixed precision
        if config.use_mixed_precision and torch.cuda.is_available():
            self.scaler = GradScaler()
            logger.info("✅ Mixed precision training enabled")
        
        # Setup distributed training
        if config.use_distributed:
            self._setup_distributed_training()
        
        logger.info(f"Initialized Advanced Training Optimizer")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    def _setup_distributed_training(self):
        """Setup distributed training environment."""
        try:
            import torch.distributed as dist
            
            # Initialize process group
            dist.init_process_group(
                backend='nccl' if torch.cuda.is_available() else 'gloo',
                world_size=self.config.world_size,
                rank=self.config.local_rank
            )
            
            # Set device
            if torch.cuda.is_available():
                torch.cuda.set_device(self.config.local_rank)
            
            logger.info(f"✅ Distributed training initialized: rank {self.config.local_rank}/{self.config.world_size}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup distributed training: {e}")
            self.config.use_distributed = False

    def setup_model_for_training(self, model: nn.Module) -> nn.Module:
        """Setup model with advanced optimizations."""
        
        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing and hasattr(model, 'gradient_checkpointing_enable'):
            model.gradient_checkpointing_enable()
            logger.info("✅ Gradient checkpointing enabled")
        
        # Setup distributed training
        if self.config.use_distributed:
            model = DDP(
                model,
                device_ids=[self.config.local_rank] if torch.cuda.is_available() else None,
                find_unused_parameters=True
            )
            logger.info("✅ Distributed Data Parallel enabled")
        
        return model

    def create_optimized_dataloader(
        self,
        dataset: Dataset,
        batch_size: int,
        shuffle: bool = True,
        drop_last: bool = True
    ) -> DataLoader:
        """Create optimized DataLoader with advanced settings."""
        
        # Setup sampler for distributed training
        sampler = None
        if self.config.use_distributed:
            sampler = DistributedSampler(
                dataset,
                num_replicas=self.config.world_size,
                rank=self.config.local_rank,
                shuffle=shuffle
            )
            shuffle = False  # Sampler handles shuffling
        
        # Create optimized DataLoader
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=self.config.dataloader_num_workers,
            pin_memory=self.config.pin_memory,
            drop_last=drop_last,
            prefetch_factor=self.config.prefetch_factor,
            persistent_workers=True if self.config.dataloader_num_workers > 0 else False
        )
        
        logger.info(f"✅ Optimized DataLoader created: {len(dataloader)} batches")
        return dataloader

    def create_advanced_scheduler(
        self,
        optimizer: torch.optim.Optimizer,
        num_training_steps: int
    ) -> torch.optim.lr_scheduler._LRScheduler:
        """Create advanced learning rate scheduler."""
        
        num_warmup_steps = int(num_training_steps * self.config.warmup_ratio)
        
        if self.config.lr_scheduler_type == "linear":
            scheduler = get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=num_warmup_steps,
                num_training_steps=num_training_steps
            )
        elif self.config.lr_scheduler_type == "cosine":
            scheduler = get_cosine_schedule_with_warmup(
                optimizer,
                num_warmup_steps=num_warmup_steps,
                num_training_steps=num_training_steps,
                num_cycles=0.5
            )
        elif self.config.lr_scheduler_type == "polynomial":
            scheduler = get_polynomial_decay_schedule_with_warmup(
                optimizer,
                num_warmup_steps=num_warmup_steps,
                num_training_steps=num_training_steps,
                lr_end=optimizer.param_groups[0]['lr'] * self.config.min_lr_ratio,
                power=2.0
            )
        else:
            # Fallback to simple step scheduler
            scheduler = torch.optim.lr_scheduler.StepLR(
                optimizer,
                step_size=num_training_steps // 3,
                gamma=self.config.lr_decay_factor
            )
        
        self.scheduler = scheduler
        logger.info(f"✅ Advanced scheduler created: {self.config.lr_scheduler_type}")
        return scheduler

    def training_step(
        self,
        model: nn.Module,
        batch: Dict[str, torch.Tensor],
        optimizer: torch.optim.Optimizer,
        step: int
    ) -> Dict[str, float]:
        """Execute optimized training step with advanced techniques."""
        
        step_start_time = time.time()
        
        # Mixed precision forward pass
        if self.config.use_mixed_precision and self.scaler is not None:
            with autocast():
                outputs = model(**batch)
                loss = outputs.get("loss", outputs.get("logits", torch.tensor(0.0)))
        else:
            outputs = model(**batch)
            loss = outputs.get("loss", outputs.get("logits", torch.tensor(0.0)))
        
        # Scale loss for gradient accumulation
        if self.config.gradient_accumulation_steps > 1:
            loss = loss / self.config.gradient_accumulation_steps
        
        # Backward pass with mixed precision
        if self.config.use_mixed_precision and self.scaler is not None:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        
        # Gradient accumulation and optimization
        if (step + 1) % self.config.gradient_accumulation_steps == 0:
            # Gradient clipping
            if self.config.max_grad_norm > 0:
                if self.config.use_mixed_precision and self.scaler is not None:
                    self.scaler.unscale_(optimizer)
                    grad_norm = torch.nn.utils.clip_grad_norm_(
                        model.parameters(), 
                        self.config.max_grad_norm
                    )
                else:
                    grad_norm = torch.nn.utils.clip_grad_norm_(
                        model.parameters(), 
                        self.config.max_grad_norm
                    )
            else:
                grad_norm = self._calculate_grad_norm(model)
            
            # Optimizer step
            if self.config.use_mixed_precision and self.scaler is not None:
                self.scaler.step(optimizer)
                self.scaler.update()
            else:
                optimizer.step()
            
            # Scheduler step
            if self.scheduler is not None:
                self.scheduler.step()
            
            # Zero gradients
            optimizer.zero_grad()
        else:
            grad_norm = 0.0
        
        # Calculate metrics
        step_time = time.time() - step_start_time
        memory_usage = self._get_memory_usage()
        learning_rate = optimizer.param_groups[0]['lr']
        
        # Extract constitutional compliance if available
        constitutional_compliance = 0.0
        if isinstance(outputs, dict):
            if "constitutional_compliance" in outputs:
                constitutional_compliance = outputs["constitutional_compliance"].mean().item()
            elif "compliance_score" in outputs:
                constitutional_compliance = outputs["compliance_score"].mean().item()
        
        return {
            "loss": loss.item() * self.config.gradient_accumulation_steps,
            "learning_rate": learning_rate,
            "gradient_norm": grad_norm,
            "memory_usage_mb": memory_usage,
            "step_time_seconds": step_time,
            "constitutional_compliance": constitutional_compliance
        }

    def _calculate_grad_norm(self, model: nn.Module) -> float:
        """Calculate gradient norm for monitoring."""
        if not self.config.track_gradient_norms:
            return 0.0
        
        total_norm = 0.0
        param_count = 0
        
        for p in model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
                param_count += 1
        
        return math.sqrt(total_norm) if param_count > 0 else 0.0

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if not self.config.monitor_memory_usage:
            return 0.0
        
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024 * 1024)
        else:
            # Fallback to system memory (simplified)
            import psutil
            return psutil.virtual_memory().used / (1024 * 1024)

    def log_training_metrics(
        self,
        epoch: int,
        step: int,
        step_metrics: Dict[str, float],
        throughput_samples_per_sec: float = 0.0
    ):
        """Log comprehensive training metrics."""
        
        metrics = TrainingMetrics(
            epoch=epoch,
            step=step,
            loss=step_metrics.get("loss", 0.0),
            learning_rate=step_metrics.get("learning_rate", 0.0),
            gradient_norm=step_metrics.get("gradient_norm", 0.0),
            memory_usage_mb=step_metrics.get("memory_usage_mb", 0.0),
            throughput_samples_per_sec=throughput_samples_per_sec,
            constitutional_compliance=step_metrics.get("constitutional_compliance", 0.0),
            training_time_seconds=step_metrics.get("step_time_seconds", 0.0)
        )
        
        self.metrics_history.append(metrics)
        
        # Log every N steps
        if step % self.config.eval_steps == 0:
            logger.info(
                f"Step {step} | Loss: {metrics.loss:.4f} | "
                f"LR: {metrics.learning_rate:.2e} | "
                f"Grad Norm: {metrics.gradient_norm:.3f} | "
                f"Memory: {metrics.memory_usage_mb:.1f}MB | "
                f"Compliance: {metrics.constitutional_compliance:.3f}"
            )

    def save_training_state(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        step: int,
        output_dir: Path
    ):
        """Save comprehensive training state."""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare state dict
        model_state = model.module.state_dict() if hasattr(model, 'module') else model.state_dict()
        
        checkpoint = {
            "epoch": epoch,
            "step": step,
            "model_state_dict": model_state,
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict() if self.scheduler else None,
            "scaler_state_dict": self.scaler.state_dict() if self.scaler else None,
            "config": self.config.__dict__,
            "metrics_history": [m.__dict__ for m in self.metrics_history[-100:]],  # Last 100 metrics
            "constitutional_hash": self.constitutional_hash
        }
        
        # Save checkpoint
        checkpoint_path = output_dir / f"checkpoint_step_{step}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        # Save latest checkpoint link
        latest_path = output_dir / "checkpoint_latest.pt"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(checkpoint_path.name)
        
        logger.info(f"💾 Training state saved: {checkpoint_path}")

    def load_training_state(
        self,
        checkpoint_path: Path,
        model: nn.Module,
        optimizer: torch.optim.Optimizer
    ) -> Tuple[int, int]:
        """Load training state from checkpoint."""
        
        if not checkpoint_path.exists():
            logger.warning(f"⚠️ Checkpoint not found: {checkpoint_path}")
            return 0, 0
        
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        # Validate constitutional hash
        if checkpoint.get("constitutional_hash") != self.constitutional_hash:
            raise ValueError(f"Constitutional hash mismatch in checkpoint")
        
        # Load model state
        if hasattr(model, 'module'):
            model.module.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint["model_state_dict"])
        
        # Load optimizer state
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        # Load scheduler state
        if self.scheduler and checkpoint.get("scheduler_state_dict"):
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
        # Load scaler state
        if self.scaler and checkpoint.get("scaler_state_dict"):
            self.scaler.load_state_dict(checkpoint["scaler_state_dict"])
        
        # Load metrics history
        if "metrics_history" in checkpoint:
            self.metrics_history = [
                TrainingMetrics(**m) for m in checkpoint["metrics_history"]
            ]
        
        epoch = checkpoint.get("epoch", 0)
        step = checkpoint.get("step", 0)
        
        logger.info(f"📂 Training state loaded from: {checkpoint_path}")
        logger.info(f"   Resumed from epoch {epoch}, step {step}")
        
        return epoch, step

    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary."""
        
        if not self.metrics_history:
            return {"status": "no_training_data"}
        
        # Calculate averages from recent metrics
        recent_metrics = self.metrics_history[-100:]  # Last 100 steps
        
        avg_loss = np.mean([m.loss for m in recent_metrics])
        avg_grad_norm = np.mean([m.gradient_norm for m in recent_metrics])
        avg_memory = np.mean([m.memory_usage_mb for m in recent_metrics])
        avg_compliance = np.mean([m.constitutional_compliance for m in recent_metrics])
        avg_throughput = np.mean([m.throughput_samples_per_sec for m in recent_metrics])
        
        # Calculate training stability metrics
        loss_std = np.std([m.loss for m in recent_metrics])
        loss_trend = self._calculate_trend([m.loss for m in recent_metrics])
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "total_steps": len(self.metrics_history),
            "recent_performance": {
                "avg_loss": avg_loss,
                "avg_gradient_norm": avg_grad_norm,
                "avg_memory_usage_mb": avg_memory,
                "avg_constitutional_compliance": avg_compliance,
                "avg_throughput_samples_per_sec": avg_throughput
            },
            "training_stability": {
                "loss_std": loss_std,
                "loss_trend": loss_trend,
                "is_stable": loss_std < 0.1 and abs(loss_trend) < 0.01
            },
            "optimization_config": {
                "mixed_precision": self.config.use_mixed_precision,
                "gradient_accumulation": self.config.gradient_accumulation_steps,
                "distributed_training": self.config.use_distributed,
                "scheduler_type": self.config.lr_scheduler_type
            },
            "constitutional_compliance": {
                "avg_compliance": avg_compliance,
                "meets_threshold": avg_compliance >= 0.95,
                "hash_validated": True
            }
        }

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope) of values."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        return slope

    def cleanup(self):
        """Cleanup resources and finalize training."""
        
        if self.config.use_distributed:
            try:
                import torch.distributed as dist
                dist.destroy_process_group()
                logger.info("✅ Distributed training cleanup completed")
            except Exception as e:
                logger.warning(f"⚠️ Distributed cleanup warning: {e}")
        
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("🧹 Training optimization cleanup completed")
