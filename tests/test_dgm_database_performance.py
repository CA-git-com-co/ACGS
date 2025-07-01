"""
Test suite for DGM database performance optimization.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.core.dgm_service.dgm_service.database.monitoring import (
    DatabaseAlert,
    DGMDatabaseMonitor,
    MonitoringConfig,
    initialize_database_monitor,
)
from services.core.dgm_service.dgm_service.database.performance_optimizer import (
    DGMPerformanceOptimizer,
    OptimizationConfig,
    PerformanceMetrics,
    initialize_performance_optimizer,
)


class TestDGMPerformanceOptimizer:
    """Test suite for DGM performance optimizer."""

    @pytest.fixture
    def optimization_config(self):
        """Create optimization configuration for testing."""
        return OptimizationConfig(
            slow_query_threshold_ms=100.0,
            index_usage_threshold=0.8,
            cache_hit_ratio_threshold=0.9,
            auto_vacuum_enabled=True,
            auto_index_creation=True,
        )

    @pytest.fixture
    def performance_optimizer(self, optimization_config):
        """Create performance optimizer instance."""
        return DGMPerformanceOptimizer(optimization_config)

    @pytest.fixture
    async def mock_db_manager(self):
        """Create mock database manager."""
        mock_manager = MagicMock()
        mock_session = AsyncMock()
        mock_manager.get_session.return_value.__aenter__.return_value = mock_session
        mock_manager.get_session.return_value.__aexit__.return_value = None

        # Mock query results
        mock_session.execute.return_value.fetchone.return_value = (100, 5, 150.0, 500.0)
        mock_session.execute.return_value.fetchall.return_value = [
            ("dgm_archive", 1000, 50),
            ("performance_metrics", 5000, 100),
        ]
        mock_session.execute.return_value.scalar.return_value = 1

        return mock_manager

    def test_optimization_config_defaults(self):
        """Test optimization configuration defaults."""
        config = OptimizationConfig()

        assert config.slow_query_threshold_ms == 200.0
        assert config.index_usage_threshold == 0.8
        assert config.cache_hit_ratio_threshold == 0.9
        assert config.auto_vacuum_enabled is True
        assert config.auto_index_creation is True
        assert config.partition_by_time is True
        assert config.partition_interval_days == 30

    def test_performance_metrics_initialization(self):
        """Test performance metrics initialization."""
        metrics = PerformanceMetrics()

        assert metrics.query_count == 0
        assert metrics.slow_query_count == 0
        assert metrics.avg_query_time == 0.0
        assert metrics.max_query_time == 0.0
        assert metrics.index_hit_ratio == 0.0
        assert metrics.cache_hit_ratio == 0.0
        assert metrics.connection_count == 0
        assert metrics.active_connections == 0

    @pytest.mark.asyncio
    async def test_optimizer_initialization(
        self, performance_optimizer, mock_db_manager
    ):
        """Test performance optimizer initialization."""
        with patch(
            "services.core.dgm_service.dgm_service.database.performance_optimizer.get_database_manager",
            return_value=mock_db_manager,
        ):
            await performance_optimizer.initialize()

            assert performance_optimizer.db_manager is not None
            assert isinstance(performance_optimizer.metrics, PerformanceMetrics)
            assert isinstance(performance_optimizer.optimization_history, list)

    @pytest.mark.asyncio
    async def test_collect_performance_metrics(
        self, performance_optimizer, mock_db_manager
    ):
        """Test performance metrics collection."""
        performance_optimizer.db_manager = mock_db_manager

        metrics = await performance_optimizer._collect_performance_metrics()

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.query_count >= 0
        assert metrics.avg_query_time >= 0.0

        # Verify database queries were made
        mock_db_manager.get_session.assert_called()

    @pytest.mark.asyncio
    async def test_optimize_indexes(self, performance_optimizer, mock_db_manager):
        """Test index optimization."""
        performance_optimizer.db_manager = mock_db_manager

        await performance_optimizer._optimize_indexes()

        # Verify that index creation queries were executed
        mock_session = mock_db_manager.get_session.return_value.__aenter__.return_value
        assert mock_session.execute.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_optimize_queries(self, performance_optimizer, mock_db_manager):
        """Test query optimization."""
        performance_optimizer.db_manager = mock_db_manager

        await performance_optimizer._optimize_queries()

        # Verify that ANALYZE commands were executed
        mock_session = mock_db_manager.get_session.return_value.__aenter__.return_value
        assert mock_session.execute.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_optimize_vacuum_settings(
        self, performance_optimizer, mock_db_manager
    ):
        """Test vacuum settings optimization."""
        performance_optimizer.db_manager = mock_db_manager

        await performance_optimizer._optimize_vacuum_settings()

        # Verify that vacuum configuration was applied
        mock_session = mock_db_manager.get_session.return_value.__aenter__.return_value
        assert mock_session.execute.called
        assert mock_session.commit.called

    def test_calculate_improvement(self, performance_optimizer):
        """Test performance improvement calculation."""
        before_metrics = PerformanceMetrics(
            query_count=1000,
            slow_query_count=50,
            avg_query_time=200.0,
            cache_hit_ratio=0.8,
        )

        after_metrics = PerformanceMetrics(
            query_count=1000,
            slow_query_count=30,
            avg_query_time=150.0,
            cache_hit_ratio=0.9,
        )

        improvements = performance_optimizer._calculate_improvement(
            before_metrics, after_metrics
        )

        assert "avg_query_time_improvement" in improvements
        assert "slow_query_reduction" in improvements
        assert "cache_hit_ratio_change" in improvements

        assert improvements["avg_query_time_improvement"] == 25.0  # 25% improvement
        assert improvements["slow_query_reduction"] == 40.0  # 40% reduction
        assert improvements["cache_hit_ratio_change"] == 0.1  # 0.1 increase

    @pytest.mark.asyncio
    async def test_generate_recommendations(
        self, performance_optimizer, mock_db_manager
    ):
        """Test recommendation generation."""
        performance_optimizer.db_manager = mock_db_manager

        # Set up metrics that would trigger recommendations
        performance_optimizer.metrics = PerformanceMetrics(
            avg_query_time=300.0,  # Above threshold
            slow_query_count=15,  # Above threshold
            cache_hit_ratio=0.7,  # Below threshold
            connection_count=100,
            active_connections=90,  # High utilization
        )

        recommendations = await performance_optimizer._generate_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Check that recommendations address the issues
        recommendation_text = " ".join(recommendations)
        assert (
            "query time" in recommendation_text.lower()
            or "slow queries" in recommendation_text.lower()
        )

    @pytest.mark.asyncio
    async def test_full_optimization_cycle(
        self, performance_optimizer, mock_db_manager
    ):
        """Test complete optimization cycle."""
        with patch(
            "services.core.dgm_service.dgm_service.database.performance_optimizer.get_database_manager",
            return_value=mock_db_manager,
        ):
            await performance_optimizer.initialize()

            result = await performance_optimizer.optimize_database()

            assert isinstance(result, dict)
            assert "started_at" in result
            assert "optimizations_applied" in result
            assert "recommendations" in result
            assert "performance_improvement" in result
            assert "status" in result

            # Verify optimization was recorded in history
            assert len(performance_optimizer.optimization_history) > 0

    @pytest.mark.asyncio
    async def test_performance_report_generation(
        self, performance_optimizer, mock_db_manager
    ):
        """Test performance report generation."""
        performance_optimizer.db_manager = mock_db_manager

        report = await performance_optimizer.get_performance_report()

        assert isinstance(report, dict)
        assert "generated_at" in report
        assert "performance_metrics" in report
        assert "table_statistics" in report
        assert "index_usage" in report
        assert "slow_queries" in report
        assert "recommendations" in report
        assert "constitutional_compliance" in report

        # Verify constitutional compliance
        assert report["constitutional_compliance"]["hash"] == "cdd01ef066bc6cf2"
        assert report["constitutional_compliance"]["validated"] is True


class TestDGMDatabaseMonitor:
    """Test suite for DGM database monitor."""

    @pytest.fixture
    def monitoring_config(self):
        """Create monitoring configuration for testing."""
        return MonitoringConfig(
            slow_query_threshold_ms=100.0,
            connection_utilization_threshold=0.8,
            cache_hit_ratio_threshold=0.9,
            metrics_collection_interval=10,
            alert_check_interval=5,
        )

    @pytest.fixture
    def database_monitor(self, monitoring_config):
        """Create database monitor instance."""
        return DGMDatabaseMonitor(monitoring_config)

    @pytest.fixture
    async def mock_db_manager(self):
        """Create mock database manager for monitoring tests."""
        mock_manager = MagicMock()
        mock_session = AsyncMock()
        mock_manager.get_session.return_value.__aenter__.return_value = mock_session
        mock_manager.get_session.return_value.__aexit__.return_value = None

        # Mock monitoring query results
        mock_session.execute.return_value.fetchall.return_value = [
            ("active", 10),
            ("idle", 5),
        ]
        mock_session.execute.return_value.fetchone.return_value = (50, 5, 150.0)
        mock_session.execute.return_value.scalar.return_value = 1

        return mock_manager

    def test_monitoring_config_defaults(self):
        """Test monitoring configuration defaults."""
        config = MonitoringConfig()

        assert config.slow_query_threshold_ms == 200.0
        assert config.connection_utilization_threshold == 0.8
        assert config.cache_hit_ratio_threshold == 0.9
        assert config.metrics_collection_interval == 60
        assert config.alert_check_interval == 30
        assert config.alert_cooldown_minutes == 15

    def test_database_alert_creation(self):
        """Test database alert creation."""
        alert = DatabaseAlert(
            name="test_alert",
            severity="warning",
            message="Test alert message",
            metric_value=0.95,
            threshold=0.9,
            timestamp=datetime.utcnow(),
        )

        assert alert.name == "test_alert"
        assert alert.severity == "warning"
        assert alert.message == "Test alert message"
        assert alert.metric_value == 0.95
        assert alert.threshold == 0.9
        assert alert.resolved is False

    @pytest.mark.asyncio
    async def test_monitor_initialization(self, database_monitor, mock_db_manager):
        """Test database monitor initialization."""
        with patch(
            "services.core.dgm_service.dgm_service.database.monitoring.get_database_manager",
            return_value=mock_db_manager,
        ):
            await database_monitor.initialize()

            assert database_monitor.db_manager is not None
            assert database_monitor.monitoring_active is True
            assert isinstance(database_monitor.active_alerts, list)
            assert isinstance(database_monitor.alert_history, list)

    @pytest.mark.asyncio
    async def test_metrics_collection(self, database_monitor, mock_db_manager):
        """Test database metrics collection."""
        database_monitor.db_manager = mock_db_manager

        await database_monitor._collect_database_metrics()

        # Verify database queries were made
        mock_session = mock_db_manager.get_session.return_value.__aenter__.return_value
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_alert_processing(self, database_monitor, mock_db_manager):
        """Test alert processing."""
        database_monitor.db_manager = mock_db_manager

        alert = DatabaseAlert(
            name="test_alert",
            severity="warning",
            message="Test alert",
            metric_value=0.95,
            threshold=0.9,
            timestamp=datetime.utcnow(),
        )

        await database_monitor._process_alert(alert)

        # Verify alert was added to active alerts
        assert len(database_monitor.active_alerts) > 0
        assert len(database_monitor.alert_history) > 0

        # Verify alert was logged to database
        mock_session = mock_db_manager.get_session.return_value.__aenter__.return_value
        assert mock_session.execute.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_health_check(self, database_monitor, mock_db_manager):
        """Test database health check."""
        database_monitor.db_manager = mock_db_manager

        await database_monitor._perform_health_check()

        # Verify health check queries were executed
        mock_session = mock_db_manager.get_session.return_value.__aenter__.return_value
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_monitoring_report_generation(self, database_monitor):
        """Test monitoring report generation."""
        # Add some test alerts
        test_alert = DatabaseAlert(
            name="test_alert",
            severity="warning",
            message="Test alert",
            metric_value=0.95,
            threshold=0.9,
            timestamp=datetime.utcnow(),
        )
        database_monitor.active_alerts.append(test_alert)
        database_monitor.alert_history.append(test_alert)

        report = await database_monitor.get_monitoring_report()

        assert isinstance(report, dict)
        assert "generated_at" in report
        assert "monitoring_status" in report
        assert "active_alerts" in report
        assert "alert_summary" in report
        assert "constitutional_compliance" in report

        # Verify alert information
        assert len(report["active_alerts"]) > 0
        assert report["alert_summary"]["total_alerts"] > 0
        assert report["alert_summary"]["active_alerts"] > 0

        # Verify constitutional compliance
        assert report["constitutional_compliance"]["hash"] == "cdd01ef066bc6cf2"
        assert report["constitutional_compliance"]["monitoring_enabled"] is True

    @pytest.mark.asyncio
    async def test_alert_deduplication(self, database_monitor, mock_db_manager):
        """Test alert deduplication."""
        database_monitor.db_manager = mock_db_manager

        # Create identical alerts
        alert1 = DatabaseAlert(
            name="duplicate_alert",
            severity="warning",
            message="Duplicate alert",
            metric_value=0.95,
            threshold=0.9,
            timestamp=datetime.utcnow(),
        )

        alert2 = DatabaseAlert(
            name="duplicate_alert",
            severity="warning",
            message="Duplicate alert updated",
            metric_value=0.96,
            threshold=0.9,
            timestamp=datetime.utcnow(),
        )

        # Process both alerts
        await database_monitor._process_alert(alert1)
        await database_monitor._process_alert(alert2)

        # Verify only one active alert exists
        active_alerts = [a for a in database_monitor.active_alerts if not a.resolved]
        duplicate_alerts = [a for a in active_alerts if a.name == "duplicate_alert"]
        assert len(duplicate_alerts) == 1

        # Verify the alert was updated with new metric value
        assert duplicate_alerts[0].metric_value == 0.96


@pytest.mark.integration
class TestDatabasePerformanceIntegration:
    """Integration tests for database performance optimization."""

    @pytest.mark.asyncio
    async def test_optimizer_monitor_integration(self):
        """Test integration between optimizer and monitor."""
        # This test would require a real database connection
        # For now, we'll test the initialization flow

        with patch(
            "services.core.dgm_service.dgm_service.database.performance_optimizer.get_database_manager"
        ) as mock_db:
            mock_manager = MagicMock()
            mock_session = AsyncMock()
            mock_manager.get_session.return_value.__aenter__.return_value = mock_session
            mock_manager.get_session.return_value.__aexit__.return_value = None
            mock_db.return_value = mock_manager

            # Initialize optimizer
            optimizer = await initialize_performance_optimizer()
            assert optimizer is not None

            # Initialize monitor
            monitor = await initialize_database_monitor()
            assert monitor is not None

            # Test that both can generate reports
            optimizer_report = await optimizer.get_performance_report()
            monitor_report = await monitor.get_monitoring_report()

            assert isinstance(optimizer_report, dict)
            assert isinstance(monitor_report, dict)

            # Verify constitutional compliance in both reports
            assert (
                optimizer_report["constitutional_compliance"]["hash"]
                == "cdd01ef066bc6cf2"
            )
            assert (
                monitor_report["constitutional_compliance"]["hash"]
                == "cdd01ef066bc6cf2"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
