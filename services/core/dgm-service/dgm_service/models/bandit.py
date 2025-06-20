"""
Bandit algorithm state model for DGM service.
"""

import enum
from typing import Dict, Any

from sqlalchemy import Column, String, DateTime, Enum, Numeric, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BanditAlgorithmType(enum.Enum):
    """Type of bandit algorithm."""
    EPSILON_GREEDY = "epsilon_greedy"
    UCB1 = "ucb1"
    THOMPSON_SAMPLING = "thompson_sampling"
    CONSERVATIVE_BANDIT = "conservative_bandit"
    SAFE_EXPLORATION = "safe_exploration"


class BanditState(Base):
    """State tracking for bandit algorithms in DGM."""

    __tablename__ = "bandit_states"
    __table_args__ = {"schema": "dgm"}

    id = Column(PG_UUID(as_uuid=True), primary_key=True,
                server_default=func.uuid_generate_v4())

    # Bandit configuration
    algorithm_type = Column(Enum(BanditAlgorithmType), nullable=False, index=True)
    context_key = Column(String(255), nullable=False, index=True)  # Context identifier
    arm_id = Column(String(255), nullable=False, index=True)  # Action/arm identifier

    # Bandit statistics
    total_pulls = Column(Integer, nullable=False, default=0)
    total_reward = Column(Numeric(15, 6), nullable=False, default=0.0)
    average_reward = Column(Numeric(15, 6), nullable=False, default=0.0)

    # Algorithm-specific parameters
    confidence_bound = Column(Numeric(15, 6), nullable=True)  # For UCB
    epsilon = Column(Numeric(5, 4), nullable=True)  # For epsilon-greedy
    alpha = Column(Numeric(15, 6), nullable=True)  # For Thompson sampling
    beta = Column(Numeric(15, 6), nullable=True)  # For Thompson sampling

    # Safety constraints
    safety_threshold = Column(Numeric(3, 2), nullable=False, default=0.8)
    risk_tolerance = Column(Numeric(3, 2), nullable=False, default=0.1)

    # State metadata
    algorithm_state = Column(JSON, default=dict)  # Algorithm-specific state
    exploration_data = Column(JSON, default=dict)  # Exploration history

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False,
                                default="cdd01ef066bc6cf2")

    # Timestamps
    last_updated = Column(DateTime(timezone=True), nullable=False,
                         server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False,
                       server_default=func.now())

    def __repr__(self):
        return (f"<BanditState(algorithm={self.algorithm_type}, "
                f"context={self.context_key}, arm={self.arm_id})>")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "algorithm_type": self.algorithm_type.value if self.algorithm_type else None,
            "context_key": self.context_key,
            "arm_id": self.arm_id,
            "total_pulls": self.total_pulls,
            "total_reward": float(self.total_reward),
            "average_reward": float(self.average_reward),
            "confidence_bound": float(self.confidence_bound) if self.confidence_bound else None,
            "epsilon": float(self.epsilon) if self.epsilon else None,
            "alpha": float(self.alpha) if self.alpha else None,
            "beta": float(self.beta) if self.beta else None,
            "safety_threshold": float(self.safety_threshold),
            "risk_tolerance": float(self.risk_tolerance),
            "algorithm_state": self.algorithm_state,
            "exploration_data": self.exploration_data,
            "constitutional_hash": self.constitutional_hash,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }