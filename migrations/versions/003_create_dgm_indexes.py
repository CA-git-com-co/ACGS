"""Create DGM performance indexes and triggers

Revision ID: 003_create_dgm_indexes
Revises: 002_create_dgm_bandit_workspace_config
Create Date: 2025-01-20 12:02:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003_create_dgm_indexes"
down_revision: Union[str, None] = "002_create_dgm_bandit_workspace_config"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create performance indexes and triggers."""

    # Archive table indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_status_timestamp
        ON dgm.dgm_archive (status, timestamp DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_compliance_score
        ON dgm.dgm_archive (constitutional_compliance_score DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_created_by
        ON dgm.dgm_archive (created_by, created_at DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_improvement_id
        ON dgm.dgm_archive (improvement_id)
    """
    )

    # Performance metrics indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_name_timestamp
        ON dgm.performance_metrics (metric_name, timestamp DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_service_type
        ON dgm.performance_metrics (service_name, metric_type, timestamp DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_improvement
        ON dgm.performance_metrics (improvement_id, timestamp DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_experiment
        ON dgm.performance_metrics (experiment_id, timestamp DESC)
    """
    )

    # GIN indexes for JSONB columns
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_tags_gin
        ON dgm.performance_metrics USING GIN (tags)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_dimensions_gin
        ON dgm.performance_metrics USING GIN (dimensions)
    """
    )

    # Constitutional compliance logs indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_level_timestamp
        ON dgm.constitutional_compliance_logs (compliance_level, assessment_timestamp DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_improvement
        ON dgm.constitutional_compliance_logs (improvement_id, assessment_timestamp DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_score
        ON dgm.constitutional_compliance_logs (compliance_score DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_review_required
        ON dgm.constitutional_compliance_logs (review_required, assessment_timestamp DESC)
        WHERE review_required = true
    """
    )

    # Bandit states indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bandit_states_context_arm
        ON dgm.bandit_states (context_key, arm_id, last_updated DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bandit_states_algorithm_type
        ON dgm.bandit_states (algorithm_type, last_updated DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bandit_states_reward
        ON dgm.bandit_states (average_reward DESC, total_pulls DESC)
    """
    )

    # Workspace indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_status_created
        ON dgm.improvement_workspaces (status, created_at DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_service_type
        ON dgm.improvement_workspaces (target_service, improvement_type, created_at DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_priority
        ON dgm.improvement_workspaces (priority, created_at DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_assigned
        ON dgm.improvement_workspaces (assigned_to, status, created_at DESC)
        WHERE assigned_to IS NOT NULL
    """
    )

    # System configurations indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_configs_category
        ON dgm.system_configurations (category, key)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_configs_readonly
        ON dgm.system_configurations (is_readonly, key)
    """
    )

    # Metric aggregations indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metric_aggregations_name_window
        ON dgm.metric_aggregations (metric_name, time_window, window_start DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metric_aggregations_service_window
        ON dgm.metric_aggregations (service_name, time_window, window_start DESC)
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metric_aggregations_type_window
        ON dgm.metric_aggregations (aggregation_type, window_start DESC)
    """
    )

    # Create updated_at triggers for automatic timestamp updates
    op.execute(
        """
        CREATE OR REPLACE FUNCTION dgm.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """
    )

    # Apply triggers to all tables with updated_at columns
    tables_with_updated_at = [
        "dgm_archive",
        "performance_metrics",
        "constitutional_compliance_logs",
        "bandit_states",
        "improvement_workspaces",
        "system_configurations",
        "metric_aggregations",
    ]

    for table in tables_with_updated_at:
        op.execute(
            f"""
            CREATE TRIGGER trigger_update_{table}_updated_at
            BEFORE UPDATE ON dgm.{table}
            FOR EACH ROW
            EXECUTE FUNCTION dgm.update_updated_at_column()
        """
        )

    # Create function for constitutional compliance validation
    op.execute(
        """
        CREATE OR REPLACE FUNCTION dgm.validate_constitutional_compliance()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Ensure compliance score is within valid range
            IF NEW.constitutional_compliance_score < 0 OR NEW.constitutional_compliance_score > 1 THEN
                RAISE EXCEPTION 'Constitutional compliance score must be between 0 and 1';
            END IF;
            
            -- Ensure constitutional hash is not empty
            IF NEW.constitutional_hash IS NULL OR LENGTH(NEW.constitutional_hash) = 0 THEN
                RAISE EXCEPTION 'Constitutional hash cannot be empty';
            END IF;
            
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """
    )

    # Apply constitutional compliance validation to relevant tables
    op.execute(
        """
        CREATE TRIGGER trigger_validate_dgm_archive_compliance
        BEFORE INSERT OR UPDATE ON dgm.dgm_archive
        FOR EACH ROW
        EXECUTE FUNCTION dgm.validate_constitutional_compliance()
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_validate_compliance_logs_compliance
        BEFORE INSERT OR UPDATE ON dgm.constitutional_compliance_logs
        FOR EACH ROW
        EXECUTE FUNCTION dgm.validate_constitutional_compliance()
    """
    )


def downgrade() -> None:
    """Drop indexes and triggers."""

    # Drop triggers
    tables_with_updated_at = [
        "dgm_archive",
        "performance_metrics",
        "constitutional_compliance_logs",
        "bandit_states",
        "improvement_workspaces",
        "system_configurations",
        "metric_aggregations",
    ]

    for table in tables_with_updated_at:
        op.execute(
            f"DROP TRIGGER IF EXISTS trigger_update_{table}_updated_at ON dgm.{table}"
        )

    op.execute(
        "DROP TRIGGER IF EXISTS trigger_validate_dgm_archive_compliance ON dgm.dgm_archive"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trigger_validate_compliance_logs_compliance ON dgm.constitutional_compliance_logs"
    )

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS dgm.update_updated_at_column()")
    op.execute("DROP FUNCTION IF EXISTS dgm.validate_constitutional_compliance()")

    # Drop indexes (PostgreSQL will handle CONCURRENTLY automatically)
    indexes_to_drop = [
        "idx_dgm_archive_status_timestamp",
        "idx_dgm_archive_compliance_score",
        "idx_dgm_archive_created_by",
        "idx_dgm_archive_improvement_id",
        "idx_performance_metrics_name_timestamp",
        "idx_performance_metrics_service_type",
        "idx_performance_metrics_improvement",
        "idx_performance_metrics_experiment",
        "idx_performance_metrics_tags_gin",
        "idx_performance_metrics_dimensions_gin",
        "idx_compliance_logs_level_timestamp",
        "idx_compliance_logs_improvement",
        "idx_compliance_logs_score",
        "idx_compliance_logs_review_required",
        "idx_bandit_states_context_arm",
        "idx_bandit_states_algorithm_type",
        "idx_bandit_states_reward",
        "idx_workspaces_status_created",
        "idx_workspaces_service_type",
        "idx_workspaces_priority",
        "idx_workspaces_assigned",
        "idx_system_configs_category",
        "idx_system_configs_readonly",
        "idx_metric_aggregations_name_window",
        "idx_metric_aggregations_service_window",
        "idx_metric_aggregations_type_window",
    ]

    for index in indexes_to_drop:
        op.execute(f"DROP INDEX IF EXISTS dgm.{index}")
