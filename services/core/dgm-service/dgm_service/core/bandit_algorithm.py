"""
Bandit Algorithm implementation for safe exploration in DGM.

Implements various multi-armed bandit algorithms for selecting
improvement strategies with conservative exploration.
"""

import asyncio
import logging
import math
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

import numpy as np

from ..config import settings
from ..database import get_db_session
from ..models.bandit import BanditState, BanditAlgorithmType

logger = logging.getLogger(__name__)


class BanditAlgorithmType(Enum):
    """Bandit algorithm types."""
    UCB = "ucb"
    EPSILON_GREEDY = "epsilon_greedy"
    THOMPSON_SAMPLING = "thompson_sampling"
    EXP3 = "exp3"


class BanditAlgorithm:
    """
    Multi-armed bandit algorithm for safe exploration.
    
    Implements conservative exploration strategies to safely
    select improvement approaches while minimizing risk.
    """
    
    def __init__(
        self,
        algorithm_type: str = "ucb",
        exploration_parameter: float = 2.0,
        decay_rate: float = 0.99
    ):
        self.algorithm_type = BanditAlgorithmType(algorithm_type)
        self.exploration_parameter = exploration_parameter
        self.decay_rate = decay_rate
        
        # Arm statistics
        self.arms: Dict[str, Dict[str, Any]] = {}
        self.total_pulls = 0
        
        # Algorithm-specific parameters
        self.epsilon = 0.1  # For epsilon-greedy
        self.temperature = 1.0  # For softmax
        
        # Safety parameters
        self.min_pulls_before_exploitation = 10
        self.safety_threshold = 0.5  # Minimum expected reward to consider
    
    async def add_arm(self, arm_id: str, description: str = ""):
        """Add a new arm to the bandit."""
        try:
            async with get_db_session() as session:
                # Check if arm already exists
                existing_arm = await session.get(BanditState, (self.algorithm_type, arm_id))
                
                if not existing_arm:
                    # Create new arm
                    new_arm = BanditState(
                        algorithm_type=self.algorithm_type,
                        arm_id=arm_id,
                        arm_description=description,
                        total_pulls=0,
                        total_reward=0.0,
                        average_reward=0.0,
                        confidence_bound=float('inf'),  # High initial confidence
                        metadata={}
                    )
                    
                    session.add(new_arm)
                    await session.commit()
                    
                    logger.info(f"Added new bandit arm: {arm_id}")
                
                # Load arm into memory
                await self._load_arm_stats(arm_id)
                
        except Exception as e:
            logger.error(f"Failed to add bandit arm {arm_id}: {e}")
            raise
    
    async def select_arm(self) -> str:
        """
        Select an arm using the configured bandit algorithm.
        
        Returns:
            Selected arm ID
        """
        try:
            # Ensure we have arms loaded
            if not self.arms:
                await self._load_all_arms()
            
            if not self.arms:
                raise ValueError("No arms available for selection")
            
            # Apply safety constraints
            safe_arms = await self._filter_safe_arms()
            
            if not safe_arms:
                # If no arms are considered safe, select the least risky
                safe_arms = [min(self.arms.keys(), key=lambda x: self.arms[x].get("risk_score", 1.0))]
                logger.warning("No safe arms available, selecting least risky")
            
            # Select arm based on algorithm
            if self.algorithm_type == BanditAlgorithmType.UCB:
                selected_arm = await self._select_ucb(safe_arms)
            elif self.algorithm_type == BanditAlgorithmType.EPSILON_GREEDY:
                selected_arm = await self._select_epsilon_greedy(safe_arms)
            elif self.algorithm_type == BanditAlgorithmType.THOMPSON_SAMPLING:
                selected_arm = await self._select_thompson_sampling(safe_arms)
            elif self.algorithm_type == BanditAlgorithmType.EXP3:
                selected_arm = await self._select_exp3(safe_arms)
            else:
                # Default to UCB
                selected_arm = await self._select_ucb(safe_arms)
            
            # Update selection count
            self.arms[selected_arm]["selections"] = self.arms[selected_arm].get("selections", 0) + 1
            
            logger.info(f"Selected arm: {selected_arm} using {self.algorithm_type.value}")
            return selected_arm
            
        except Exception as e:
            logger.error(f"Failed to select arm: {e}")
            # Fallback to random selection from available arms
            return random.choice(list(self.arms.keys())) if self.arms else "default"
    
    async def update_arm(self, arm_id: str, reward: float):
        """
        Update arm statistics with new reward.
        
        Args:
            arm_id: ID of the arm to update
            reward: Reward value (typically between -1 and 1)
        """
        try:
            async with get_db_session() as session:
                # Get existing arm state
                arm_state = await session.get(BanditState, (self.algorithm_type, arm_id))
                
                if not arm_state:
                    logger.warning(f"Arm {arm_id} not found, creating new one")
                    await self.add_arm(arm_id)
                    arm_state = await session.get(BanditState, (self.algorithm_type, arm_id))
                
                # Update statistics
                arm_state.total_pulls += 1
                arm_state.total_reward += reward
                arm_state.average_reward = arm_state.total_reward / arm_state.total_pulls
                arm_state.last_pulled_at = datetime.utcnow()
                
                # Update confidence bound for UCB
                if self.algorithm_type == BanditAlgorithmType.UCB:
                    arm_state.confidence_bound = self._calculate_ucb_bound(
                        arm_state.average_reward,
                        arm_state.total_pulls,
                        self.total_pulls + 1
                    )
                
                await session.commit()
                
                # Update in-memory statistics
                await self._load_arm_stats(arm_id)
                
                self.total_pulls += 1
                
                logger.info(
                    f"Updated arm {arm_id}: pulls={arm_state.total_pulls}, "
                    f"avg_reward={arm_state.average_reward:.4f}, reward={reward}"
                )
                
        except Exception as e:
            logger.error(f"Failed to update arm {arm_id}: {e}")
            raise
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        try:
            await self._load_all_arms()
            
            # Calculate statistics
            total_pulls = sum(arm["total_pulls"] for arm in self.arms.values())
            best_arm = max(self.arms.keys(), key=lambda x: self.arms[x]["average_reward"]) if self.arms else None
            
            # Calculate exploration rate
            if total_pulls > 0:
                recent_pulls = sum(
                    arm.get("selections", 0) for arm in self.arms.values()
                )
                exploration_rate = recent_pulls / max(total_pulls, 1)
            else:
                exploration_rate = 1.0
            
            # Prepare arm statistics
            arm_stats = []
            for arm_id, stats in self.arms.items():
                arm_stats.append({
                    "arm_id": arm_id,
                    "description": stats.get("description", ""),
                    "total_pulls": stats["total_pulls"],
                    "total_reward": stats["total_reward"],
                    "average_reward": stats["average_reward"],
                    "confidence_bound": stats.get("confidence_bound"),
                    "last_pulled": stats.get("last_pulled_at")
                })
            
            # Sort by average reward
            arm_stats.sort(key=lambda x: x["average_reward"], reverse=True)
            
            return {
                "algorithm_type": self.algorithm_type.value,
                "total_pulls": total_pulls,
                "best_arm": best_arm,
                "exploration_rate": exploration_rate,
                "arms": arm_stats,
                "performance_history": await self._get_performance_history()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {
                "algorithm_type": self.algorithm_type.value,
                "total_pulls": 0,
                "best_arm": None,
                "exploration_rate": 0.0,
                "arms": [],
                "performance_history": []
            }
    
    async def _select_ucb(self, safe_arms: List[str]) -> str:
        """Select arm using Upper Confidence Bound algorithm."""
        if self.total_pulls == 0:
            return random.choice(safe_arms)
        
        ucb_values = {}
        for arm_id in safe_arms:
            arm = self.arms[arm_id]
            if arm["total_pulls"] == 0:
                ucb_values[arm_id] = float('inf')
            else:
                confidence_bonus = math.sqrt(
                    (self.exploration_parameter * math.log(self.total_pulls)) / arm["total_pulls"]
                )
                ucb_values[arm_id] = arm["average_reward"] + confidence_bonus
        
        return max(ucb_values.keys(), key=lambda x: ucb_values[x])
    
    async def _select_epsilon_greedy(self, safe_arms: List[str]) -> str:
        """Select arm using epsilon-greedy algorithm."""
        if random.random() < self.epsilon:
            # Explore: random selection
            return random.choice(safe_arms)
        else:
            # Exploit: select best arm
            return max(safe_arms, key=lambda x: self.arms[x]["average_reward"])
    
    async def _select_thompson_sampling(self, safe_arms: List[str]) -> str:
        """Select arm using Thompson sampling."""
        # Simplified Thompson sampling using Beta distribution
        samples = {}
        for arm_id in safe_arms:
            arm = self.arms[arm_id]
            if arm["total_pulls"] == 0:
                samples[arm_id] = random.random()
            else:
                # Convert rewards to success/failure counts
                successes = max(1, arm["total_reward"] + arm["total_pulls"])
                failures = max(1, arm["total_pulls"] - successes + 1)
                samples[arm_id] = np.random.beta(successes, failures)
        
        return max(samples.keys(), key=lambda x: samples[x])
    
    async def _select_exp3(self, safe_arms: List[str]) -> str:
        """Select arm using EXP3 algorithm."""
        # Simplified EXP3 implementation
        weights = {}
        total_weight = 0
        
        for arm_id in safe_arms:
            arm = self.arms[arm_id]
            # Convert average reward to weight
            weight = math.exp(self.exploration_parameter * arm["average_reward"])
            weights[arm_id] = weight
            total_weight += weight
        
        # Normalize weights to probabilities
        probabilities = {arm_id: weight / total_weight for arm_id, weight in weights.items()}
        
        # Sample from the distribution
        rand = random.random()
        cumulative = 0
        for arm_id, prob in probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return arm_id
        
        return random.choice(safe_arms)
    
    async def _filter_safe_arms(self) -> List[str]:
        """Filter arms based on safety constraints."""
        safe_arms = []
        
        for arm_id, arm in self.arms.items():
            # Check if arm has minimum pulls for reliable statistics
            if arm["total_pulls"] < self.min_pulls_before_exploitation:
                safe_arms.append(arm_id)  # Include for exploration
                continue
            
            # Check if average reward meets safety threshold
            if arm["average_reward"] >= self.safety_threshold:
                safe_arms.append(arm_id)
            
            # Check risk score if available
            risk_score = arm.get("risk_score", 0.5)
            if risk_score <= 0.7:  # Low to medium risk
                safe_arms.append(arm_id)
        
        return list(set(safe_arms))  # Remove duplicates
    
    def _calculate_ucb_bound(self, avg_reward: float, arm_pulls: int, total_pulls: int) -> float:
        """Calculate UCB confidence bound."""
        if arm_pulls == 0 or total_pulls == 0:
            return float('inf')
        
        confidence_bonus = math.sqrt(
            (self.exploration_parameter * math.log(total_pulls)) / arm_pulls
        )
        return avg_reward + confidence_bonus
    
    async def _load_arm_stats(self, arm_id: str):
        """Load arm statistics from database."""
        try:
            async with get_db_session() as session:
                arm_state = await session.get(BanditState, (self.algorithm_type, arm_id))
                
                if arm_state:
                    self.arms[arm_id] = {
                        "total_pulls": arm_state.total_pulls,
                        "total_reward": float(arm_state.total_reward),
                        "average_reward": float(arm_state.average_reward),
                        "confidence_bound": float(arm_state.confidence_bound) if arm_state.confidence_bound else None,
                        "last_pulled_at": arm_state.last_pulled_at,
                        "description": arm_state.arm_description,
                        "metadata": arm_state.metadata or {}
                    }
                    
        except Exception as e:
            logger.error(f"Failed to load arm stats for {arm_id}: {e}")
    
    async def _load_all_arms(self):
        """Load all arm statistics from database."""
        try:
            async with get_db_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(BanditState).where(BanditState.algorithm_type == self.algorithm_type)
                )
                arm_states = result.scalars().all()
                
                self.arms = {}
                for arm_state in arm_states:
                    self.arms[arm_state.arm_id] = {
                        "total_pulls": arm_state.total_pulls,
                        "total_reward": float(arm_state.total_reward),
                        "average_reward": float(arm_state.average_reward),
                        "confidence_bound": float(arm_state.confidence_bound) if arm_state.confidence_bound else None,
                        "last_pulled_at": arm_state.last_pulled_at,
                        "description": arm_state.arm_description,
                        "metadata": arm_state.metadata or {}
                    }
                
                self.total_pulls = sum(arm["total_pulls"] for arm in self.arms.values())
                
        except Exception as e:
            logger.error(f"Failed to load all arms: {e}")
    
    async def _get_performance_history(self) -> List[Dict[str, Any]]:
        """Get performance history for visualization."""
        # This would typically query a separate performance history table
        # For now, return empty list
        return []
