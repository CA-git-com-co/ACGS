"""Create DGM schema and core tables

Revision ID: 001_create_dgm_schema
Revises: 
Create Date: 2025-01-20 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_dgm_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create DGM schema and core tables."""

    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Create DGM schema
    op.execute("CREATE SCHEMA IF NOT EXISTS dgm")

    # Create enum types
    improvement_status = postgresql.ENUM(
        "pending",
        "running",
        "completed",
        "failed",
        "rolled_back",
        name="improvement_status",
        schema="dgm",
    )
    improvement_status.create(op.get_bind())

    constitutional_compliance_level = postgresql.ENUM(
        "compliant",
        "warning",
        "violation",
        "critical",
        name="constitutional_compliance_level",
        schema="dgm",
    )
    constitutional_compliance_level.create(op.get_bind())

    bandit_algorithm_type = postgresql.ENUM(
        "epsilon_greedy",
        "ucb1",
        "thompson_sampling",
        "conservative_bandit",
        "safe_exploration",
        name="bandit_algorithm_type",
        schema="dgm",
    )
    bandit_algorithm_type.create(op.get_bind())

    # Create DGM Archive table
    op.create_table(
        "dgm_archive",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "improvement_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("algorithm_changes", postgresql.JSONB),
        sa.Column("performance_before", postgresql.JSONB),
        sa.Column("performance_after", postgresql.JSONB),
        sa.Column("constitutional_compliance_score", sa.Numeric(3, 2), nullable=False),
        sa.Column("compliance_details", postgresql.JSONB),
        sa.Column(
            "status", improvement_status, nullable=False, server_default="pending"
        ),
        sa.Column("rollback_data", postgresql.JSONB),
        sa.Column("metadata", postgresql.JSONB),
        sa.Column("created_by", sa.String(255)),
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

    # Add constraint for compliance score
    op.execute(
        """
        ALTER TABLE dgm.dgm_archive 
        ADD CONSTRAINT chk_compliance_score 
        CHECK (constitutional_compliance_score >= 0 AND constitutional_compliance_score <= 1)
    """
    )

    # Create Performance Metrics table
    op.create_table(
        "performance_metrics",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("metric_name", sa.String(255), nullable=False, index=True),
        sa.Column("metric_value", sa.Numeric(15, 6), nullable=False),
        sa.Column("metric_type", sa.String(50), nullable=False, index=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            index=True,
        ),
        sa.Column("service_name", sa.String(255), nullable=True, index=True),
        sa.Column(
            "improvement_id", postgresql.UUID(as_uuid=True), nullable=True, index=True
        ),
        sa.Column(
            "experiment_id", postgresql.UUID(as_uuid=True), nullable=True, index=True
        ),
        sa.Column("tags", postgresql.JSONB, server_default="{}"),
        sa.Column("dimensions", postgresql.JSONB, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default="cdd01ef066bc6cf2",
        ),
        sa.Column("constitutional_compliance_score", sa.Numeric(3, 2), nullable=True),
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

    # Create Constitutional Compliance Logs table
    op.create_table(
        "constitutional_compliance_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "improvement_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column(
            "compliance_level",
            constitutional_compliance_level,
            nullable=False,
            index=True,
        ),
        sa.Column("compliance_score", sa.Numeric(3, 2), nullable=False),
        sa.Column(
            "assessment_timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            index=True,
        ),
        sa.Column("principle_violations", postgresql.JSONB, server_default="[]"),
        sa.Column("governance_impact", sa.Text),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default="cdd01ef066bc6cf2",
        ),
        sa.Column(
            "constitutional_version",
            sa.String(50),
            nullable=False,
            server_default="1.0",
        ),
        sa.Column("violations", postgresql.JSONB, server_default="[]"),
        sa.Column("recommendations", postgresql.JSONB, server_default="[]"),
        sa.Column("evidence", postgresql.JSONB, server_default="{}"),
        sa.Column("assessment_method", sa.String(100), nullable=False),
        sa.Column("assessor_id", sa.String(255), nullable=True),
        sa.Column("review_required", sa.Boolean, server_default="false"),
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


def downgrade() -> None:
    """Drop DGM schema and all tables."""

    # Drop tables in reverse order
    op.drop_table("constitutional_compliance_logs", schema="dgm")
    op.drop_table("performance_metrics", schema="dgm")
    op.drop_table("dgm_archive", schema="dgm")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS dgm.bandit_algorithm_type")
    op.execute("DROP TYPE IF EXISTS dgm.constitutional_compliance_level")
    op.execute("DROP TYPE IF EXISTS dgm.improvement_status")

    # Drop schema (CASCADE will remove any remaining objects)
    op.execute("DROP SCHEMA IF EXISTS dgm CASCADE")
