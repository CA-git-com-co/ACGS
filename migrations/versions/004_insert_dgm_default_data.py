"""Insert DGM default configuration data

Revision ID: 004_insert_dgm_default_data
Revises: 003_create_dgm_indexes
Create Date: 2025-01-20 12:03:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "004_insert_dgm_default_data"
down_revision: Union[str, None] = "003_create_dgm_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert default configuration data."""

    # Insert default system configurations
    default_configs = [
        {
            "key": "constitutional_hash",
            "value": "cdd01ef066bc6cf2",
            "value_type": "string",
            "description": "ACGS constitutional compliance hash for validation",
            "category": "compliance",
            "is_readonly": True,
            "is_sensitive": False,
        },
        {
            "key": "constitutional_version",
            "value": "1.0",
            "value_type": "string",
            "description": "Current constitutional version",
            "category": "compliance",
            "is_readonly": True,
            "is_sensitive": False,
        },
        {
            "key": "max_improvement_attempts",
            "value": "10",
            "value_type": "integer",
            "description": "Maximum improvement attempts per cycle",
            "category": "safety",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 1, "max": 100}',
        },
        {
            "key": "safety_threshold",
            "value": "0.8",
            "value_type": "float",
            "description": "Minimum safety threshold for improvements",
            "category": "safety",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 0.0, "max": 1.0}',
        },
        {
            "key": "constitutional_compliance_threshold",
            "value": "0.9",
            "value_type": "float",
            "description": "Minimum constitutional compliance score required",
            "category": "compliance",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 0.0, "max": 1.0}',
        },
        {
            "key": "bandit_exploration_rate",
            "value": "0.1",
            "value_type": "float",
            "description": "Exploration rate for bandit algorithms",
            "category": "learning",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 0.0, "max": 1.0}',
        },
        {
            "key": "conservative_bandit_enabled",
            "value": "true",
            "value_type": "boolean",
            "description": "Enable conservative bandit algorithms for safe exploration",
            "category": "safety",
            "is_readonly": False,
            "is_sensitive": False,
        },
        {
            "key": "max_concurrent_improvements",
            "value": "3",
            "value_type": "integer",
            "description": "Maximum number of concurrent improvement processes",
            "category": "performance",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 1, "max": 10}',
        },
        {
            "key": "improvement_timeout_minutes",
            "value": "30",
            "value_type": "integer",
            "description": "Timeout for improvement processes in minutes",
            "category": "performance",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 5, "max": 120}',
        },
        {
            "key": "rollback_retention_days",
            "value": "30",
            "value_type": "integer",
            "description": "Number of days to retain rollback data",
            "category": "storage",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 1, "max": 365}',
        },
        {
            "key": "metrics_aggregation_enabled",
            "value": "true",
            "value_type": "boolean",
            "description": "Enable automatic metrics aggregation",
            "category": "performance",
            "is_readonly": False,
            "is_sensitive": False,
        },
        {
            "key": "metrics_retention_days",
            "value": "90",
            "value_type": "integer",
            "description": "Number of days to retain detailed metrics",
            "category": "storage",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 7, "max": 365}',
        },
        {
            "key": "llm_model_primary",
            "value": "claude-3.5-sonnet",
            "value_type": "string",
            "description": "Primary LLM model for improvements",
            "category": "ai",
            "is_readonly": False,
            "is_sensitive": False,
        },
        {
            "key": "llm_model_secondary",
            "value": "o1-preview",
            "value_type": "string",
            "description": "Secondary LLM model for validation",
            "category": "ai",
            "is_readonly": False,
            "is_sensitive": False,
        },
        {
            "key": "workspace_cleanup_enabled",
            "value": "true",
            "value_type": "boolean",
            "description": "Enable automatic workspace cleanup",
            "category": "storage",
            "is_readonly": False,
            "is_sensitive": False,
        },
        {
            "key": "workspace_retention_hours",
            "value": "72",
            "value_type": "integer",
            "description": "Hours to retain completed workspaces",
            "category": "storage",
            "is_readonly": False,
            "is_sensitive": False,
            "validation_rules": '{"min": 1, "max": 720}',
        },
    ]

    # Insert configurations
    connection = op.get_bind()
    for config in default_configs:
        connection.execute(
            text(
                """
                INSERT INTO dgm.system_configurations 
                (key, value, value_type, description, category, is_readonly, is_sensitive, validation_rules, metadata)
                VALUES 
                (:key, :value, :value_type, :description, :category, :is_readonly, :is_sensitive, 
                 COALESCE(:validation_rules::jsonb, '{}'::jsonb), '{}'::jsonb)
                ON CONFLICT (key) DO NOTHING
            """
            ),
            {
                "key": config["key"],
                "value": config["value"],
                "value_type": config["value_type"],
                "description": config["description"],
                "category": config["category"],
                "is_readonly": config["is_readonly"],
                "is_sensitive": config["is_sensitive"],
                "validation_rules": config.get("validation_rules"),
            },
        )

    # Insert default bandit algorithm configurations
    default_bandit_configs = [
        {
            "algorithm_type": "conservative_bandit",
            "context_key": "default_improvement_context",
            "arm_id": "code_optimization",
            "safety_threshold": 0.9,
            "risk_tolerance": 0.05,
            "algorithm_state": '{"initialized": true, "version": "1.0"}',
        },
        {
            "algorithm_type": "conservative_bandit",
            "context_key": "default_improvement_context",
            "arm_id": "performance_tuning",
            "safety_threshold": 0.85,
            "risk_tolerance": 0.1,
            "algorithm_state": '{"initialized": true, "version": "1.0"}',
        },
        {
            "algorithm_type": "conservative_bandit",
            "context_key": "default_improvement_context",
            "arm_id": "security_enhancement",
            "safety_threshold": 0.95,
            "risk_tolerance": 0.02,
            "algorithm_state": '{"initialized": true, "version": "1.0"}',
        },
        {
            "algorithm_type": "epsilon_greedy",
            "context_key": "exploration_context",
            "arm_id": "new_algorithm_testing",
            "epsilon": 0.1,
            "safety_threshold": 0.8,
            "risk_tolerance": 0.15,
            "algorithm_state": '{"initialized": true, "version": "1.0"}',
        },
    ]

    # Insert bandit configurations
    for bandit_config in default_bandit_configs:
        connection.execute(
            text(
                """
                INSERT INTO dgm.bandit_states 
                (algorithm_type, context_key, arm_id, safety_threshold, risk_tolerance, 
                 epsilon, algorithm_state, exploration_data)
                VALUES 
                (:algorithm_type::dgm.bandit_algorithm_type, :context_key, :arm_id, 
                 :safety_threshold, :risk_tolerance, :epsilon, 
                 :algorithm_state::jsonb, '{}'::jsonb)
                ON CONFLICT (context_key, arm_id, algorithm_type) DO NOTHING
            """
            ),
            {
                "algorithm_type": bandit_config["algorithm_type"],
                "context_key": bandit_config["context_key"],
                "arm_id": bandit_config["arm_id"],
                "safety_threshold": bandit_config["safety_threshold"],
                "risk_tolerance": bandit_config["risk_tolerance"],
                "epsilon": bandit_config.get("epsilon"),
                "algorithm_state": bandit_config["algorithm_state"],
            },
        )

    # Create initial metric aggregation windows
    op.execute(
        """
        INSERT INTO dgm.metric_aggregations 
        (metric_name, aggregation_type, time_window, aggregated_value, sample_count, 
         window_start, window_end, metadata)
        VALUES 
        ('system_health', 'avg', 'hourly', 1.0, 0, 
         DATE_TRUNC('hour', NOW()), DATE_TRUNC('hour', NOW()) + INTERVAL '1 hour',
         '{"initialized": true}'::jsonb),
        ('improvement_success_rate', 'avg', 'daily', 0.0, 0,
         DATE_TRUNC('day', NOW()), DATE_TRUNC('day', NOW()) + INTERVAL '1 day',
         '{"initialized": true}'::jsonb),
        ('constitutional_compliance_rate', 'avg', 'daily', 1.0, 0,
         DATE_TRUNC('day', NOW()), DATE_TRUNC('day', NOW()) + INTERVAL '1 day',
         '{"initialized": true}'::jsonb)
        ON CONFLICT DO NOTHING
    """
    )


def downgrade() -> None:
    """Remove default configuration data."""

    # Remove default configurations
    default_config_keys = [
        "constitutional_hash",
        "constitutional_version",
        "max_improvement_attempts",
        "safety_threshold",
        "constitutional_compliance_threshold",
        "bandit_exploration_rate",
        "conservative_bandit_enabled",
        "max_concurrent_improvements",
        "improvement_timeout_minutes",
        "rollback_retention_days",
        "metrics_aggregation_enabled",
        "metrics_retention_days",
        "llm_model_primary",
        "llm_model_secondary",
        "workspace_cleanup_enabled",
        "workspace_retention_hours",
    ]

    connection = op.get_bind()
    for key in default_config_keys:
        connection.execute(
            text("DELETE FROM dgm.system_configurations WHERE key = :key"), {"key": key}
        )

    # Remove default bandit states
    connection.execute(
        text(
            """
            DELETE FROM dgm.bandit_states 
            WHERE context_key IN ('default_improvement_context', 'exploration_context')
        """
        )
    )

    # Remove initial metric aggregations
    connection.execute(
        text(
            """
            DELETE FROM dgm.metric_aggregations 
            WHERE metric_name IN ('system_health', 'improvement_success_rate', 'constitutional_compliance_rate')
            AND metadata->>'initialized' = 'true'
        """
        )
    )
