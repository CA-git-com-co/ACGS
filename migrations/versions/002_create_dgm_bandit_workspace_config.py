"""Create DGM bandit states, workspaces, and configuration tables

Revision ID: 002_create_dgm_bandit_workspace_config
Revises: 001_create_dgm_schema
Create Date: 2025-01-20 12:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_create_dgm_bandit_workspace_config"
down_revision: Union[str, None] = "001_create_dgm_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create bandit states, workspaces, and configuration tables."""

    # Create Bandit States table
    op.create_table(
        "bandit_states",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "algorithm_type",
            sa.Enum(
                "epsilon_greedy",
                "ucb1",
                "thompson_sampling",
                "conservative_bandit",
                "safe_exploration",
                name="bandit_algorithm_type",
                schema="dgm",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column("context_key", sa.String(255), nullable=False, index=True),
        sa.Column("arm_id", sa.String(255), nullable=False, index=True),
        sa.Column("total_pulls", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "total_reward", sa.Numeric(15, 6), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "average_reward", sa.Numeric(15, 6), nullable=False, server_default="0.0"
        ),
        sa.Column("confidence_bound", sa.Numeric(15, 6), nullable=True),
        sa.Column("epsilon", sa.Numeric(5, 4), nullable=True),
        sa.Column("alpha", sa.Numeric(15, 6), nullable=True),
        sa.Column("beta", sa.Numeric(15, 6), nullable=True),
        sa.Column(
            "safety_threshold", sa.Numeric(3, 2), nullable=False, server_default="0.8"
        ),
        sa.Column(
            "risk_tolerance", sa.Numeric(3, 2), nullable=False, server_default="0.1"
        ),
        sa.Column("algorithm_state", postgresql.JSONB, server_default="{}"),
        sa.Column("exploration_data", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default="cdd01ef066bc6cf2",
        ),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        schema="dgm",
    )

    # Create Improvement Workspaces table
    op.create_table(
        "improvement_workspaces",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("workspace_name", sa.String(255), nullable=False, index=True),
        sa.Column(
            "improvement_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column(
            "status", sa.String(50), nullable=False, index=True, server_default="active"
        ),
        sa.Column("description", sa.Text),
        sa.Column("target_service", sa.String(255), nullable=False, index=True),
        sa.Column("improvement_type", sa.String(100), nullable=False, index=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("source_code", postgresql.JSONB, server_default="{}"),
        sa.Column("configuration", postgresql.JSONB, server_default="{}"),
        sa.Column("test_results", postgresql.JSONB, server_default="[]"),
        sa.Column("validation_results", postgresql.JSONB, server_default="{}"),
        sa.Column("environment_snapshot", postgresql.JSONB, server_default="{}"),
        sa.Column("dependencies", postgresql.JSONB, server_default="[]"),
        sa.Column("rollback_plan", postgresql.JSONB, server_default="{}"),
        sa.Column("safety_checks", postgresql.JSONB, server_default="[]"),
        sa.Column("risk_assessment", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default="cdd01ef066bc6cf2",
        ),
        sa.Column("created_by", sa.String(255)),
        sa.Column("assigned_to", sa.String(255)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        schema="dgm",
    )

    # Create System Configurations table
    op.create_table(
        "system_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("key", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("value_type", sa.String(50), nullable=False, server_default="string"),
        sa.Column("description", sa.Text),
        sa.Column(
            "category",
            sa.String(100),
            nullable=False,
            index=True,
            server_default="general",
        ),
        sa.Column("is_readonly", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_sensitive", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("validation_rules", postgresql.JSONB, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default="cdd01ef066bc6cf2",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        schema="dgm",
    )

    # Create Metric Aggregations table (for performance optimization)
    op.create_table(
        "metric_aggregations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("metric_name", sa.String(255), nullable=False, index=True),
        sa.Column("aggregation_type", sa.String(50), nullable=False, index=True),
        sa.Column("time_window", sa.String(50), nullable=False, index=True),
        sa.Column("aggregated_value", sa.Numeric(15, 6), nullable=False),
        sa.Column("sample_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "window_start", sa.DateTime(timezone=True), nullable=False, index=True
        ),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("service_name", sa.String(255), nullable=True, index=True),
        sa.Column("tags", postgresql.JSONB, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default="cdd01ef066bc6cf2",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        schema="dgm",
    )

    # Add constraints
    op.execute(
        """
        ALTER TABLE dgm.bandit_states 
        ADD CONSTRAINT chk_safety_threshold 
        CHECK (safety_threshold >= 0 AND safety_threshold <= 1)
    """
    )

    op.execute(
        """
        ALTER TABLE dgm.bandit_states 
        ADD CONSTRAINT chk_risk_tolerance 
        CHECK (risk_tolerance >= 0 AND risk_tolerance <= 1)
    """
    )

    # Create unique constraint for bandit context
    op.create_unique_constraint(
        "uq_bandit_context_arm",
        "bandit_states",
        ["context_key", "arm_id", "algorithm_type"],
        schema="dgm",
    )


def downgrade() -> None:
    """Drop bandit states, workspaces, and configuration tables."""

    # Drop tables in reverse order
    op.drop_table("metric_aggregations", schema="dgm")
    op.drop_table("system_configurations", schema="dgm")
    op.drop_table("improvement_workspaces", schema="dgm")
    op.drop_table("bandit_states", schema="dgm")
