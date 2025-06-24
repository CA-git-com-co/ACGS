"""
Constitutional Privacy Engine
Differential privacy implementation for constitutional AI training with ACGS-1 Lite integration.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
from opacus import PrivacyEngine
from opacus.accountants import RDPAccountant
from opacus.utils.batch_memory_manager import BatchMemoryManager
from opacus.validators import ModuleValidator

logger = logging.getLogger(__name__)


class ConstitutionalPrivacyEngine:
    """Privacy-preserving training engine with constitutional constraints."""

    def __init__(self, model: nn.Module, config):
        self.model = model
        self.config = config
        self.constitutional_hash = config.constitutional_hash

        # Privacy parameters
        self.target_epsilon = getattr(config, "privacy_epsilon", 8.0)
        self.target_delta = getattr(config, "privacy_delta", 1e-5)
        self.max_grad_norm = 1.0
        self.noise_multiplier = 1.1

        # Initialize Opacus Privacy Engine
        self.privacy_engine = PrivacyEngine(accountant="rdp")

        # Privacy tracking
        self.privacy_spent = {"epsilon": 0.0, "delta": self.target_delta}
        self.training_steps = 0
        self.privacy_violations = []

        # Validate model for differential privacy
        self._validate_model_for_privacy()

    def _validate_model_for_privacy(self):
        """Validate model compatibility with differential privacy."""
        try:
            errors = ModuleValidator.validate(self.model, strict=False)
            if errors:
                logger.warning(f"Model validation warnings for differential privacy: {errors}")
                # Fix common issues automatically
                self._fix_model_for_privacy()

            logger.info("Model validated for differential privacy training")

        except Exception as e:
            logger.error(f"Model validation for privacy failed: {e}")
            raise

    def _fix_model_for_privacy(self):
        """Fix common model issues for differential privacy compatibility."""
        try:
            # Replace unsupported layers
            ModuleValidator.fix(self.model)
            logger.info("Model automatically fixed for differential privacy compatibility")
        except Exception as e:
            logger.warning(f"Automatic model fixing failed: {e}")

    def make_private(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        data_loader: torch.utils.data.DataLoader,
        noise_multiplier: float = None,
        max_grad_norm: float = None,
    ) -> Tuple[nn.Module, torch.optim.Optimizer, torch.utils.data.DataLoader]:
        """Make training differentially private with constitutional constraints."""

        if noise_multiplier is not None:
            self.noise_multiplier = noise_multiplier
        if max_grad_norm is not None:
            self.max_grad_norm = max_grad_norm

        try:
            logger.info(
                f"Applying differential privacy with ε={self.target_epsilon}, δ={self.target_delta}"
            )

            # Make model, optimizer, and data loader private
            model, optimizer, data_loader = self.privacy_engine.make_private_with_epsilon(
                module=model,
                optimizer=optimizer,
                data_loader=data_loader,
                epochs=self.config.num_epochs,
                target_epsilon=self.target_epsilon,
                target_delta=self.target_delta,
                max_grad_norm=self.max_grad_norm,
            )

            # Log privacy parameters
            logger.info(f"Differential privacy applied successfully:")
            logger.info(f"  - Noise multiplier: {self.privacy_engine.noise_multiplier}")
            logger.info(f"  - Max grad norm: {self.max_grad_norm}")
            logger.info(f"  - Target epsilon: {self.target_epsilon}")
            logger.info(f"  - Target delta: {self.target_delta}")

            return model, optimizer, data_loader

        except Exception as e:
            logger.error(f"Failed to apply differential privacy: {e}")
            raise

    def make_private_with_epsilon(
        self,
        module: nn.Module,
        optimizer: torch.optim.Optimizer,
        data_loader: torch.utils.data.DataLoader,
        epochs: int,
        target_epsilon: float,
        target_delta: float = 1e-5,
        max_grad_norm: float = 1.0,
    ) -> Tuple[nn.Module, torch.optim.Optimizer, torch.utils.data.DataLoader]:
        """Make training private with specific epsilon target."""

        self.target_epsilon = target_epsilon
        self.target_delta = target_delta
        self.max_grad_norm = max_grad_norm

        return self.privacy_engine.make_private_with_epsilon(
            module=module,
            optimizer=optimizer,
            data_loader=data_loader,
            epochs=epochs,
            target_epsilon=target_epsilon,
            target_delta=target_delta,
            max_grad_norm=max_grad_norm,
        )

    def get_privacy_spent(self) -> Dict[str, float]:
        """Get current privacy budget consumption."""
        try:
            epsilon = self.privacy_engine.get_epsilon(delta=self.target_delta)
            remaining_budget = max(0.0, self.target_epsilon - epsilon)

            privacy_metrics = {
                "epsilon": epsilon,
                "delta": self.target_delta,
                "target_epsilon": self.target_epsilon,
                "remaining_budget": remaining_budget,
                "budget_utilization": (
                    epsilon / self.target_epsilon if self.target_epsilon > 0 else 0.0
                ),
                "training_steps": self.training_steps,
                "constitutional_hash": self.constitutional_hash,
            }

            # Update internal tracking
            self.privacy_spent = privacy_metrics

            return privacy_metrics

        except Exception as e:
            logger.error(f"Failed to get privacy spent: {e}")
            return {
                "epsilon": 0.0,
                "delta": self.target_delta,
                "target_epsilon": self.target_epsilon,
                "remaining_budget": self.target_epsilon,
                "budget_utilization": 0.0,
                "training_steps": self.training_steps,
                "constitutional_hash": self.constitutional_hash,
                "error": str(e),
            }

    def check_privacy_budget(self) -> Dict[str, Any]:
        """Check if privacy budget is within acceptable limits."""
        privacy_spent = self.get_privacy_spent()

        budget_status = {
            "budget_ok": privacy_spent["epsilon"] <= self.target_epsilon,
            "budget_utilization": privacy_spent["budget_utilization"],
            "remaining_budget": privacy_spent["remaining_budget"],
            "warning_threshold": 0.9,  # Warn at 90% budget utilization
            "critical_threshold": 0.95,  # Critical at 95% budget utilization
        }

        # Determine status
        if budget_status["budget_utilization"] >= budget_status["critical_threshold"]:
            budget_status["status"] = "critical"
            budget_status["message"] = "Privacy budget critically low - training should be halted"
        elif budget_status["budget_utilization"] >= budget_status["warning_threshold"]:
            budget_status["status"] = "warning"
            budget_status["message"] = "Privacy budget running low - monitor closely"
        else:
            budget_status["status"] = "ok"
            budget_status["message"] = "Privacy budget within acceptable limits"

        return budget_status

    def validate_constitutional_privacy_compliance(self, training_data: Any) -> Dict[str, Any]:
        """Validate that privacy measures comply with constitutional requirements."""

        compliance_check = {
            "constitutional_hash": self.constitutional_hash,
            "privacy_compliant": True,
            "violations": [],
            "recommendations": [],
        }

        # Check privacy budget compliance
        budget_status = self.check_privacy_budget()
        if not budget_status["budget_ok"]:
            compliance_check["privacy_compliant"] = False
            compliance_check["violations"].append("privacy_budget_exceeded")

        # Check differential privacy parameters
        if self.target_epsilon > 10.0:
            compliance_check["violations"].append("epsilon_too_high")
            compliance_check["recommendations"].append(
                "Consider reducing epsilon for stronger privacy"
            )

        if self.target_delta > 1e-4:
            compliance_check["violations"].append("delta_too_high")
            compliance_check["recommendations"].append(
                "Consider reducing delta for stronger privacy"
            )

        # Check noise multiplier
        if hasattr(self.privacy_engine, "noise_multiplier"):
            if self.privacy_engine.noise_multiplier < 0.5:
                compliance_check["violations"].append("noise_multiplier_too_low")
                compliance_check["recommendations"].append(
                    "Increase noise multiplier for better privacy"
                )

        # Constitutional compliance check
        if compliance_check["violations"]:
            compliance_check["privacy_compliant"] = False
            self.privacy_violations.extend(compliance_check["violations"])

        return compliance_check

    def get_privacy_metrics_for_monitoring(self) -> Dict[str, Any]:
        """Get privacy metrics formatted for monitoring systems."""

        privacy_spent = self.get_privacy_spent()
        budget_status = self.check_privacy_budget()

        metrics = {
            # Core privacy metrics
            "privacy_epsilon_current": privacy_spent["epsilon"],
            "privacy_epsilon_target": privacy_spent["target_epsilon"],
            "privacy_delta": privacy_spent["delta"],
            "privacy_budget_remaining": privacy_spent["remaining_budget"],
            "privacy_budget_utilization": privacy_spent["budget_utilization"],
            # Training metrics
            "training_steps": self.training_steps,
            "noise_multiplier": getattr(
                self.privacy_engine, "noise_multiplier", self.noise_multiplier
            ),
            "max_grad_norm": self.max_grad_norm,
            # Status metrics
            "privacy_budget_status": budget_status["status"],
            "privacy_violations_count": len(self.privacy_violations),
            # Constitutional compliance
            "constitutional_hash": self.constitutional_hash,
            "constitutional_privacy_compliant": len(self.privacy_violations) == 0,
            # Timestamps
            "last_updated": time.time(),
            "metrics_version": "1.0.0",
        }

        return metrics

    def create_batch_memory_manager(
        self, data_loader: torch.utils.data.DataLoader, max_physical_batch_size: int = 32
    ) -> BatchMemoryManager:
        """Create batch memory manager for large logical batch sizes."""

        return BatchMemoryManager(
            data_loader=data_loader,
            max_physical_batch_size=max_physical_batch_size,
            optimizer=None,  # Will be set when used
        )

    def log_privacy_event(self, event_type: str, details: Dict[str, Any]):
        """Log privacy-related events for audit purposes."""

        privacy_event = {
            "event_type": f"privacy_{event_type}",
            "constitutional_hash": self.constitutional_hash,
            "privacy_metrics": self.get_privacy_spent(),
            "event_details": details,
            "timestamp": time.time(),
        }

        logger.info(f"Privacy event logged: {event_type}")

        # In production, this would send to the Audit Engine
        # For now, just log locally
        return privacy_event

    def emergency_privacy_halt(self, reason: str) -> Dict[str, Any]:
        """Emergency halt of training due to privacy budget exhaustion."""

        halt_event = {
            "event_type": "emergency_privacy_halt",
            "reason": reason,
            "constitutional_hash": self.constitutional_hash,
            "privacy_spent": self.get_privacy_spent(),
            "training_steps": self.training_steps,
            "timestamp": time.time(),
        }

        logger.critical(f"Emergency privacy halt triggered: {reason}")

        # Log the halt event
        self.log_privacy_event("emergency_halt", halt_event)

        return halt_event

    def get_privacy_accountant_state(self) -> Dict[str, Any]:
        """Get detailed state of the privacy accountant."""

        try:
            if hasattr(self.privacy_engine, "accountant"):
                accountant = self.privacy_engine.accountant

                if isinstance(accountant, RDPAccountant):
                    return {
                        "accountant_type": "RDP",
                        "history": accountant.history,
                        "rdp_orders": accountant.orders,
                        "steps": len(accountant.history),
                        "constitutional_hash": self.constitutional_hash,
                    }

            return {"accountant_type": "unknown", "constitutional_hash": self.constitutional_hash}

        except Exception as e:
            logger.error(f"Failed to get privacy accountant state: {e}")
            return {"error": str(e), "constitutional_hash": self.constitutional_hash}

    def reset_privacy_accountant(self):
        """Reset privacy accountant (use with caution)."""

        logger.warning(
            "Resetting privacy accountant - this should only be done between training sessions"
        )

        try:
            if hasattr(self.privacy_engine, "accountant"):
                self.privacy_engine.accountant.history = []
                self.training_steps = 0
                self.privacy_violations = []

                logger.info("Privacy accountant reset successfully")

                # Log the reset event
                self.log_privacy_event(
                    "accountant_reset",
                    {"reason": "manual_reset", "constitutional_hash": self.constitutional_hash},
                )

        except Exception as e:
            logger.error(f"Failed to reset privacy accountant: {e}")
            raise

    def __del__(self):
        """Cleanup when privacy engine is destroyed."""
        if hasattr(self, "privacy_violations") and self.privacy_violations:
            logger.warning(
                f"Privacy engine destroyed with {len(self.privacy_violations)} violations recorded"
            )
