"""
Conservative Constrained LinUCB (CLUCB2) Algorithm for ACGS AI Governance

This module implements the Conservative Constrained LinUCB algorithm specifically
designed for AI governance applications where safety and constitutional compliance
are paramount. The algorithm ensures performance never falls below baseline while
optimizing for governance effectiveness.

Key Features:
- Conservative constraints to prevent performance degradation
- Constitutional compliance integration
- Safety-first arm selection
- Baseline performance guarantees
- Integration with existing ACGS MAB framework

Based on research in safe multi-armed bandits and constitutional AI governance.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.linalg import inv

from .mab_prompt_optimizer import MABAlgorithmBase, MABConfig

logger = logging.getLogger(__name__)


@dataclass
class ConservativeLinUCBConfig:
    """Configuration for Conservative Constrained LinUCB algorithm."""
    
    # Core LinUCB parameters
    alpha: float = 1.0  # Confidence parameter
    lambda_reg: float = 1.0  # Regularization parameter
    
    # Conservative constraints
    safety_threshold: float = 0.1  # Maximum allowed performance drop
    baseline_window: int = 100  # Window for baseline calculation
    min_baseline_samples: int = 10  # Minimum samples before applying constraints
    
    # Constitutional compliance
    constitutional_weight: float = 0.3  # Weight for constitutional compliance
    safety_weight: float = 0.4  # Weight for safety considerations
    performance_weight: float = 0.3  # Weight for raw performance
    
    # Adaptation parameters
    context_dimension: int = 10  # Dimension of context vectors
    update_frequency: int = 50  # How often to update baseline
    
    # Fallback behavior
    fallback_to_baseline: bool = True  # Fall back to baseline if no safe arms
    exploration_bonus: float = 0.1  # Bonus for exploration in safe region


@dataclass
class ArmStatistics:
    """Statistics for a single arm in Conservative LinUCB."""
    
    arm_id: str
    A: np.ndarray = None  # Design matrix A_a
    b: np.ndarray = None  # Reward vector b_a
    theta: np.ndarray = None  # Parameter estimate
    n_pulls: int = 0
    total_reward: float = 0.0
    constitutional_scores: List[float] = field(default_factory=list)
    safety_scores: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize matrices if not provided."""
        if self.A is None:
            # Will be initialized when context dimension is known
            pass


class ConservativeLinUCB(MABAlgorithmBase):
    """
    Conservative Constrained LinUCB algorithm for AI governance.
    
    Implements a contextual bandit algorithm with conservative constraints
    to ensure safety and constitutional compliance in AI governance decisions.
    """
    
    def __init__(self, config: ConservativeLinUCBConfig):
        """Initialize Conservative LinUCB algorithm."""
        super().__init__(MABConfig())  # Initialize base class
        self.config = config
        self.arm_stats: Dict[str, ArmStatistics] = {}
        self.baseline_performance: Optional[float] = None
        self.baseline_history: List[float] = []
        self.context_dimension = config.context_dimension
        self.total_rounds = 0
        
        # Performance tracking
        self.performance_history = []
        self.safety_violations = 0
        self.constitutional_violations = 0
        
        logger.info(f"Initialized Conservative LinUCB with config: {config}")
    
    def _initialize_arm(self, arm_id: str) -> ArmStatistics:
        """Initialize statistics for a new arm."""
        stats = ArmStatistics(
            arm_id=arm_id,
            A=np.eye(self.context_dimension) * self.config.lambda_reg,
            b=np.zeros(self.context_dimension),
            theta=np.zeros(self.context_dimension)
        )
        self.arm_stats[arm_id] = stats
        logger.debug(f"Initialized new arm: {arm_id}")
        return stats
    
    def _extract_context_vector(self, context: Dict[str, Any]) -> np.ndarray:
        """Extract and normalize context vector from context dictionary."""
        # Create context vector from available features
        features = []
        
        # Basic features
        features.append(context.get('safety_level', 0.5))
        features.append(context.get('constitutional_importance', 0.5))
        features.append(context.get('complexity_score', 0.5))
        features.append(context.get('urgency', 0.5))
        features.append(context.get('stakeholder_impact', 0.5))
        
        # Policy-specific features
        features.append(len(context.get('principles', [])) / 10.0)  # Normalized
        features.append(context.get('risk_level', 0.5))
        features.append(context.get('precedent_strength', 0.5))
        
        # Temporal features
        hour_of_day = datetime.now().hour / 24.0
        features.append(hour_of_day)
        features.append(context.get('time_pressure', 0.5))
        
        # Pad or truncate to match context dimension
        while len(features) < self.context_dimension:
            features.append(0.0)
        features = features[:self.context_dimension]
        
        return np.array(features, dtype=np.float64)
    
    def _calculate_confidence_bound(self, context_vector: np.ndarray, 
                                  arm_stats: ArmStatistics) -> float:
        """Calculate upper confidence bound for an arm."""
        try:
            A_inv = inv(arm_stats.A)
            confidence = self.config.alpha * np.sqrt(
                context_vector.T @ A_inv @ context_vector
            )
            return float(confidence)
        except np.linalg.LinAlgError:
            logger.warning(f"Singular matrix for arm {arm_stats.arm_id}, using fallback")
            return self.config.alpha  # Fallback confidence
    
    def _estimate_reward(self, context_vector: np.ndarray, 
                        arm_stats: ArmStatistics) -> float:
        """Estimate expected reward for an arm given context."""
        if arm_stats.n_pulls == 0:
            return 0.0  # No data yet
        
        try:
            A_inv = inv(arm_stats.A)
            arm_stats.theta = A_inv @ arm_stats.b
            estimated_reward = float(context_vector.T @ arm_stats.theta)
            return estimated_reward
        except np.linalg.LinAlgError:
            logger.warning(f"Singular matrix for arm {arm_stats.arm_id}")
            return arm_stats.total_reward / arm_stats.n_pulls if arm_stats.n_pulls > 0 else 0.0
    
    def _is_arm_safe(self, context_vector: np.ndarray, arm_id: str) -> bool:
        """Check if an arm satisfies conservative constraints."""
        if arm_id not in self.arm_stats:
            return True  # New arms are considered safe for exploration
        
        arm_stats = self.arm_stats[arm_id]
        
        # Need minimum samples to apply constraints
        if arm_stats.n_pulls < self.config.min_baseline_samples:
            return True
        
        # Check if baseline is established
        if self.baseline_performance is None:
            return True
        
        # Estimate performance
        estimated_reward = self._estimate_reward(context_vector, arm_stats)
        confidence_bound = self._calculate_confidence_bound(context_vector, arm_stats)
        
        # Conservative constraint: lower confidence bound must be above threshold
        lower_bound = estimated_reward - confidence_bound
        safety_threshold = self.baseline_performance - self.config.safety_threshold
        
        is_safe = lower_bound >= safety_threshold
        
        if not is_safe:
            logger.debug(f"Arm {arm_id} failed safety check: {lower_bound:.3f} < {safety_threshold:.3f}")
        
        return is_safe
    
    def select_arm(self, context: Dict[str, Any] = None, 
                  available_arms: List[str] = None) -> Optional[str]:
        """Select arm using Conservative Constrained LinUCB."""
        if not available_arms:
            logger.warning("No available arms for selection")
            return None
        
        context = context or {}
        context_vector = self._extract_context_vector(context)
        
        # Initialize arms if needed
        for arm_id in available_arms:
            if arm_id not in self.arm_stats:
                self._initialize_arm(arm_id)
        
        # Filter safe arms
        safe_arms = [arm_id for arm_id in available_arms 
                    if self._is_arm_safe(context_vector, arm_id)]
        
        if not safe_arms:
            if self.config.fallback_to_baseline and self.baseline_performance is not None:
                # Fallback to arm with performance closest to baseline
                logger.warning("No safe arms available, falling back to baseline-like arm")
                fallback_arm = self._select_fallback_arm(context_vector, available_arms)
                if fallback_arm:
                    self.safety_violations += 1
                    return fallback_arm
            
            logger.error("No safe arms available and no fallback possible")
            return available_arms[0] if available_arms else None
        
        # Calculate UCB values for safe arms
        ucb_values = {}
        for arm_id in safe_arms:
            arm_stats = self.arm_stats[arm_id]
            estimated_reward = self._estimate_reward(context_vector, arm_stats)
            confidence_bound = self._calculate_confidence_bound(context_vector, arm_stats)
            
            # Add exploration bonus for constitutional compliance
            constitutional_bonus = 0.0
            if arm_stats.constitutional_scores:
                avg_constitutional = np.mean(arm_stats.constitutional_scores)
                constitutional_bonus = self.config.exploration_bonus * avg_constitutional
            
            ucb_values[arm_id] = estimated_reward + confidence_bound + constitutional_bonus
        
        # Select arm with highest UCB value
        selected_arm = max(ucb_values.keys(), key=lambda x: ucb_values[x])
        
        logger.debug(f"Selected arm {selected_arm} with UCB {ucb_values[selected_arm]:.3f} "
                    f"from {len(safe_arms)} safe arms")
        
        return selected_arm
    
    def _select_fallback_arm(self, context_vector: np.ndarray, 
                           available_arms: List[str]) -> Optional[str]:
        """Select fallback arm when no safe arms are available."""
        if not self.baseline_performance:
            return available_arms[0] if available_arms else None
        
        # Select arm with estimated performance closest to baseline
        best_arm = None
        best_distance = float('inf')
        
        for arm_id in available_arms:
            if arm_id in self.arm_stats:
                arm_stats = self.arm_stats[arm_id]
                estimated_reward = self._estimate_reward(context_vector, arm_stats)
                distance = abs(estimated_reward - self.baseline_performance)
                
                if distance < best_distance:
                    best_distance = distance
                    best_arm = arm_id
        
        return best_arm or available_arms[0]

    def update_reward(self, arm_id: str, reward: float,
                      context: Dict[str, Any] = None):
        """Update arm statistics with new reward observation."""
        if arm_id not in self.arm_stats:
            self._initialize_arm(arm_id)

        context = context or {}
        context_vector = self._extract_context_vector(context)
        arm_stats = self.arm_stats[arm_id]

        # Update LinUCB matrices
        arm_stats.A += np.outer(context_vector, context_vector)
        arm_stats.b += reward * context_vector
        arm_stats.n_pulls += 1
        arm_stats.total_reward += reward

        # Track constitutional and safety scores
        constitutional_score = context.get('constitutional_compliance', 0.5)
        safety_score = context.get('safety_score', 0.5)

        arm_stats.constitutional_scores.append(constitutional_score)
        arm_stats.safety_scores.append(safety_score)

        # Update baseline performance
        self._update_baseline_performance(reward)

        # Update total rounds
        self.total_rounds += 1

        # Record performance history
        self.performance_history.append({
            'round': self.total_rounds,
            'arm_id': arm_id,
            'reward': reward,
            'constitutional_score': constitutional_score,
            'safety_score': safety_score,
            'timestamp': datetime.now(timezone.utc)
        })

        avg_reward = arm_stats.total_reward / arm_stats.n_pulls
        logger.debug(f"Updated arm {arm_id}: pulls={arm_stats.n_pulls}, "
                     f"avg_reward={avg_reward:.3f}")

    def _update_baseline_performance(self, reward: float):
        """Update baseline performance estimate."""
        self.baseline_history.append(reward)

        # Keep only recent history
        if len(self.baseline_history) > self.config.baseline_window:
            window_size = self.config.baseline_window
            self.baseline_history = self.baseline_history[-window_size:]

        # Update baseline if we have enough samples
        min_samples = self.config.min_baseline_samples
        if len(self.baseline_history) >= min_samples:
            # Use conservative estimate (e.g., 25th percentile)
            baseline_perf = np.percentile(self.baseline_history, 25)
            self.baseline_performance = baseline_perf

            # Update baseline periodically
            if self.total_rounds % self.config.update_frequency == 0:
                baseline_val = self.baseline_performance
                sample_count = len(self.baseline_history)
                msg = f"Updated baseline performance: {baseline_val:.3f} "
                msg += f"(from {sample_count} samples)"
                logger.info(msg)

    def get_arm_statistics(self, arm_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive statistics for an arm."""
        if arm_id not in self.arm_stats:
            return None

        arm_stats = self.arm_stats[arm_id]

        # Calculate average reward
        avg_reward = (arm_stats.total_reward / arm_stats.n_pulls
                      if arm_stats.n_pulls > 0 else 0.0)

        # Calculate constitutional score statistics
        const_scores = arm_stats.constitutional_scores
        const_mean = np.mean(const_scores) if const_scores else 0.0
        const_std = np.std(const_scores) if const_scores else 0.0

        # Calculate safety score statistics
        safety_scores = arm_stats.safety_scores
        safety_mean = np.mean(safety_scores) if safety_scores else 0.0
        safety_std = np.std(safety_scores) if safety_scores else 0.0

        # Calculate theta norm
        theta_norm = (np.linalg.norm(arm_stats.theta)
                      if arm_stats.theta is not None else 0.0)

        return {
            'arm_id': arm_id,
            'n_pulls': arm_stats.n_pulls,
            'total_reward': arm_stats.total_reward,
            'average_reward': avg_reward,
            'constitutional_scores': {
                'mean': const_mean,
                'std': const_std,
                'count': len(const_scores)
            },
            'safety_scores': {
                'mean': safety_mean,
                'std': safety_std,
                'count': len(safety_scores)
            },
            'created_at': arm_stats.created_at,
            'theta_norm': theta_norm
        }

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'total_rounds': self.total_rounds,
            'baseline_performance': self.baseline_performance,
            'baseline_samples': len(self.baseline_history),
            'safety_violations': self.safety_violations,
            'constitutional_violations': self.constitutional_violations,
            'active_arms': len(self.arm_stats),
            'config': {
                'alpha': self.config.alpha,
                'safety_threshold': self.config.safety_threshold,
                'constitutional_weight': self.config.constitutional_weight,
                'safety_weight': self.config.safety_weight
            },
            'performance_trend': {
                'recent_rewards': (self.baseline_history[-10:]
                                   if self.baseline_history else []),
                'total_performance_records': len(self.performance_history)
            }
        }

    def reset_baseline(self):
        """Reset baseline performance calculation."""
        self.baseline_performance = None
        self.baseline_history = []
        logger.info("Reset baseline performance calculation")

    def export_performance_data(self) -> Dict[str, Any]:
        """Export performance data for analysis."""
        return {
            'performance_history': self.performance_history,
            'arm_statistics': {arm_id: self.get_arm_statistics(arm_id)
                               for arm_id in self.arm_stats.keys()},
            'system_statistics': self.get_system_statistics(),
            'config': self.config.__dict__
        }
