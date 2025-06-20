"""
Unit tests for DGM Service database models.

Comprehensive test suite for database models including validation,
relationships, and data integrity constraints.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dgm_service.models import (
    DGMArchive, ImprovementStatus, PerformanceMetric, 
    ConstitutionalComplianceLog, ComplianceLevel,
    BanditState, BanditAlgorithmType, ImprovementWorkspace,
    SystemConfiguration
)


@pytest.mark.unit
@pytest.mark.database
class TestDGMModels:
    """Test suite for DGM database models."""
    
    async def test_dgm_archive_creation(self, test_db_session: AsyncSession):
        """Test DGM archive model creation and validation."""
        archive = DGMArchive(
            improvement_type="performance_optimization",
            status=ImprovementStatus.COMPLETED,
            strategy_used="gradient_descent",
            target_services=["gs-service", "ac-service"],
            performance_before={"response_time": 150.0, "throughput": 800.0},
            performance_after={"response_time": 125.0, "throughput": 950.0},
            constitutional_compliance_score=Decimal("0.95"),
            execution_time=Decimal("45.2"),
            improvement_metrics={"overall_improvement": 0.15},
            constitutional_hash="cdd01ef066bc6cf2"
        )
        
        test_db_session.add(archive)
        await test_db_session.commit()
        await test_db_session.refresh(archive)
        
        assert archive.id is not None
        assert archive.improvement_type == "performance_optimization"
        assert archive.status == ImprovementStatus.COMPLETED
        assert archive.constitutional_compliance_score == Decimal("0.95")
        assert archive.created_at is not None
        assert archive.updated_at is not None
    
    async def test_dgm_archive_status_transitions(self, test_db_session: AsyncSession):
        """Test DGM archive status transitions."""
        archive = DGMArchive(
            improvement_type="code_refactoring",
            status=ImprovementStatus.PENDING,
            strategy_used="evolutionary_algorithm"
        )
        
        test_db_session.add(archive)
        await test_db_session.commit()
        
        # Test status transition
        archive.status = ImprovementStatus.IN_PROGRESS
        await test_db_session.commit()
        
        assert archive.status == ImprovementStatus.IN_PROGRESS
        
        # Test completion
        archive.status = ImprovementStatus.COMPLETED
        archive.completed_at = datetime.utcnow()
        await test_db_session.commit()
        
        assert archive.status == ImprovementStatus.COMPLETED
        assert archive.completed_at is not None
    
    async def test_dgm_archive_required_fields(self, test_db_session: AsyncSession):
        """Test DGM archive required field validation."""
        # Test missing required fields
        with pytest.raises(IntegrityError):
            archive = DGMArchive()  # Missing required fields
            test_db_session.add(archive)
            await test_db_session.commit()
    
    async def test_performance_metric_creation(self, test_db_session: AsyncSession):
        """Test performance metric model creation."""
        metric = PerformanceMetric(
            metric_name="response_time",
            value=Decimal("125.5"),
            timestamp=datetime.utcnow(),
            service_name="dgm-service",
            improvement_id=uuid4(),
            experiment_id=uuid4(),
            tags={"endpoint": "/api/v1/dgm/improve", "method": "POST"},
            dimensions={"region": "us-east-1", "environment": "production"},
            constitutional_hash="cdd01ef066bc6cf2",
            constitutional_compliance_score=Decimal("0.95")
        )
        
        test_db_session.add(metric)
        await test_db_session.commit()
        await test_db_session.refresh(metric)
        
        assert metric.id is not None
        assert metric.metric_name == "response_time"
        assert metric.value == Decimal("125.5")
        assert metric.service_name == "dgm-service"
        assert metric.tags["endpoint"] == "/api/v1/dgm/improve"
        assert metric.constitutional_compliance_score == Decimal("0.95")
    
    async def test_performance_metric_indexing(self, test_db_session: AsyncSession):
        """Test performance metric indexing for queries."""
        # Create multiple metrics with different timestamps
        base_time = datetime.utcnow()
        metrics = []
        
        for i in range(5):
            metric = PerformanceMetric(
                metric_name="throughput",
                value=Decimal(str(800.0 + i * 10)),
                timestamp=base_time + timedelta(minutes=i),
                service_name="dgm-service"
            )
            metrics.append(metric)
            test_db_session.add(metric)
        
        await test_db_session.commit()
        
        # Query metrics by timestamp range
        from sqlalchemy import select
        
        start_time = base_time
        end_time = base_time + timedelta(minutes=3)
        
        stmt = select(PerformanceMetric).where(
            PerformanceMetric.timestamp.between(start_time, end_time)
        )
        result = await test_db_session.execute(stmt)
        queried_metrics = result.scalars().all()
        
        assert len(queried_metrics) == 4  # 0, 1, 2, 3 minute marks
    
    async def test_constitutional_compliance_log_creation(self, test_db_session: AsyncSession):
        """Test constitutional compliance log model."""
        compliance_log = ConstitutionalComplianceLog(
            improvement_id=uuid4(),
            compliance_level=ComplianceLevel.HIGH,
            compliance_score=Decimal("0.95"),
            constitutional_hash="cdd01ef066bc6cf2",
            validation_details={
                "checks_passed": 15,
                "checks_failed": 0,
                "warnings": 1,
                "recommendations": ["Consider additional safety checks"]
            },
            validator_version="1.0.0",
            validation_timestamp=datetime.utcnow()
        )
        
        test_db_session.add(compliance_log)
        await test_db_session.commit()
        await test_db_session.refresh(compliance_log)
        
        assert compliance_log.id is not None
        assert compliance_log.compliance_level == ComplianceLevel.HIGH
        assert compliance_log.compliance_score == Decimal("0.95")
        assert compliance_log.validation_details["checks_passed"] == 15
        assert compliance_log.validator_version == "1.0.0"
    
    async def test_compliance_level_enum(self, test_db_session: AsyncSession):
        """Test compliance level enumeration."""
        # Test all compliance levels
        levels = [
            (ComplianceLevel.CRITICAL, Decimal("0.25")),
            (ComplianceLevel.LOW, Decimal("0.45")),
            (ComplianceLevel.MEDIUM, Decimal("0.65")),
            (ComplianceLevel.HIGH, Decimal("0.85")),
            (ComplianceLevel.EXCELLENT, Decimal("0.98"))
        ]
        
        for level, score in levels:
            log = ConstitutionalComplianceLog(
                improvement_id=uuid4(),
                compliance_level=level,
                compliance_score=score,
                constitutional_hash="cdd01ef066bc6cf2"
            )
            test_db_session.add(log)
        
        await test_db_session.commit()
        
        # Query by compliance level
        from sqlalchemy import select
        
        stmt = select(ConstitutionalComplianceLog).where(
            ConstitutionalComplianceLog.compliance_level == ComplianceLevel.HIGH
        )
        result = await test_db_session.execute(stmt)
        high_compliance_logs = result.scalars().all()
        
        assert len(high_compliance_logs) == 1
        assert high_compliance_logs[0].compliance_score == Decimal("0.85")
    
    async def test_bandit_state_creation(self, test_db_session: AsyncSession):
        """Test bandit state model creation."""
        bandit_state = BanditState(
            algorithm_type=BanditAlgorithmType.UCB1,
            arm_name="performance_optimization",
            pulls=25,
            rewards=Decimal("18.5"),
            success_rate=Decimal("0.74"),
            confidence_bound=Decimal("0.85"),
            epsilon=None,  # Not used for UCB1
            alpha=None,    # Not used for UCB1
            beta=None,     # Not used for UCB1
            safety_threshold=Decimal("0.1"),
            last_updated=datetime.utcnow(),
            constitutional_hash="cdd01ef066bc6cf2"
        )
        
        test_db_session.add(bandit_state)
        await test_db_session.commit()
        await test_db_session.refresh(bandit_state)
        
        assert bandit_state.id is not None
        assert bandit_state.algorithm_type == BanditAlgorithmType.UCB1
        assert bandit_state.arm_name == "performance_optimization"
        assert bandit_state.pulls == 25
        assert bandit_state.rewards == Decimal("18.5")
        assert bandit_state.success_rate == Decimal("0.74")
    
    async def test_bandit_algorithm_types(self, test_db_session: AsyncSession):
        """Test different bandit algorithm types."""
        algorithms = [
            (BanditAlgorithmType.UCB1, {"confidence_bound": Decimal("1.414")}),
            (BanditAlgorithmType.EPSILON_GREEDY, {"epsilon": Decimal("0.1")}),
            (BanditAlgorithmType.THOMPSON_SAMPLING, {
                "alpha": Decimal("2.0"), 
                "beta": Decimal("3.0")
            })
        ]
        
        for algo_type, params in algorithms:
            state = BanditState(
                algorithm_type=algo_type,
                arm_name=f"test_arm_{algo_type.value}",
                pulls=10,
                rewards=Decimal("7.5"),
                **params
            )
            test_db_session.add(state)
        
        await test_db_session.commit()
        
        # Verify all algorithm types were stored
        from sqlalchemy import select
        
        stmt = select(BanditState)
        result = await test_db_session.execute(stmt)
        states = result.scalars().all()
        
        assert len(states) == 3
        algo_types = {state.algorithm_type for state in states}
        assert BanditAlgorithmType.UCB1 in algo_types
        assert BanditAlgorithmType.EPSILON_GREEDY in algo_types
        assert BanditAlgorithmType.THOMPSON_SAMPLING in algo_types
    
    async def test_improvement_workspace_creation(self, test_db_session: AsyncSession):
        """Test improvement workspace model."""
        workspace = ImprovementWorkspace(
            improvement_id=uuid4(),
            workspace_path="/tmp/dgm_workspace_123",
            status="active",
            created_files=["optimizer.py", "config.json", "test_results.txt"],
            modified_files=["main.py", "utils.py"],
            backup_location="/backups/workspace_123",
            cleanup_scheduled_at=datetime.utcnow() + timedelta(hours=24),
            constitutional_hash="cdd01ef066bc6cf2"
        )
        
        test_db_session.add(workspace)
        await test_db_session.commit()
        await test_db_session.refresh(workspace)
        
        assert workspace.id is not None
        assert workspace.status == "active"
        assert len(workspace.created_files) == 3
        assert len(workspace.modified_files) == 2
        assert workspace.cleanup_scheduled_at is not None
    
    async def test_system_configuration_creation(self, test_db_session: AsyncSession):
        """Test system configuration model."""
        config = SystemConfiguration(
            key="bandit_exploration_parameter",
            value="1.414",
            value_type="float",
            description="UCB1 exploration parameter for bandit algorithm",
            category="bandit_algorithm",
            is_sensitive=False,
            is_readonly=False,
            constitutional_hash="cdd01ef066bc6cf2"
        )
        
        test_db_session.add(config)
        await test_db_session.commit()
        await test_db_session.refresh(config)
        
        assert config.id is not None
        assert config.key == "bandit_exploration_parameter"
        assert config.value == "1.414"
        assert config.value_type == "float"
        assert config.category == "bandit_algorithm"
        assert config.is_sensitive is False
    
    async def test_system_configuration_unique_key(self, test_db_session: AsyncSession):
        """Test system configuration unique key constraint."""
        config1 = SystemConfiguration(
            key="test_config",
            value="value1",
            category="test"
        )
        
        config2 = SystemConfiguration(
            key="test_config",  # Same key
            value="value2",
            category="test"
        )
        
        test_db_session.add(config1)
        await test_db_session.commit()
        
        # Adding second config with same key should fail
        test_db_session.add(config2)
        with pytest.raises(IntegrityError):
            await test_db_session.commit()
    
    async def test_model_relationships(self, test_db_session: AsyncSession):
        """Test relationships between models."""
        improvement_id = uuid4()
        
        # Create archive entry
        archive = DGMArchive(
            improvement_type="performance_optimization",
            status=ImprovementStatus.COMPLETED,
            strategy_used="gradient_descent"
        )
        archive.id = improvement_id
        
        # Create related performance metrics
        metric1 = PerformanceMetric(
            metric_name="response_time",
            value=Decimal("125.0"),
            improvement_id=improvement_id,
            timestamp=datetime.utcnow()
        )
        
        metric2 = PerformanceMetric(
            metric_name="throughput",
            value=Decimal("850.0"),
            improvement_id=improvement_id,
            timestamp=datetime.utcnow()
        )
        
        # Create compliance log
        compliance_log = ConstitutionalComplianceLog(
            improvement_id=improvement_id,
            compliance_level=ComplianceLevel.HIGH,
            compliance_score=Decimal("0.95"),
            constitutional_hash="cdd01ef066bc6cf2"
        )
        
        test_db_session.add_all([archive, metric1, metric2, compliance_log])
        await test_db_session.commit()
        
        # Query related records
        from sqlalchemy import select
        
        # Find metrics for the improvement
        stmt = select(PerformanceMetric).where(
            PerformanceMetric.improvement_id == improvement_id
        )
        result = await test_db_session.execute(stmt)
        related_metrics = result.scalars().all()
        
        assert len(related_metrics) == 2
        
        # Find compliance logs for the improvement
        stmt = select(ConstitutionalComplianceLog).where(
            ConstitutionalComplianceLog.improvement_id == improvement_id
        )
        result = await test_db_session.execute(stmt)
        related_logs = result.scalars().all()
        
        assert len(related_logs) == 1
        assert related_logs[0].compliance_level == ComplianceLevel.HIGH
    
    async def test_model_timestamps(self, test_db_session: AsyncSession):
        """Test automatic timestamp handling."""
        archive = DGMArchive(
            improvement_type="test_improvement",
            status=ImprovementStatus.PENDING,
            strategy_used="test_strategy"
        )
        
        test_db_session.add(archive)
        await test_db_session.commit()
        await test_db_session.refresh(archive)
        
        created_at = archive.created_at
        updated_at = archive.updated_at
        
        assert created_at is not None
        assert updated_at is not None
        assert created_at == updated_at  # Should be same on creation
        
        # Update the record
        import asyncio
        await asyncio.sleep(0.01)  # Small delay to ensure different timestamp
        
        archive.status = ImprovementStatus.IN_PROGRESS
        await test_db_session.commit()
        await test_db_session.refresh(archive)
        
        assert archive.updated_at > updated_at  # Should be updated
        assert archive.created_at == created_at  # Should remain same
    
    async def test_constitutional_hash_consistency(self, test_db_session: AsyncSession):
        """Test constitutional hash consistency across models."""
        constitutional_hash = "cdd01ef066bc6cf2"
        improvement_id = uuid4()
        
        # Create records with same constitutional hash
        archive = DGMArchive(
            improvement_type="test",
            status=ImprovementStatus.PENDING,
            strategy_used="test",
            constitutional_hash=constitutional_hash
        )
        archive.id = improvement_id
        
        metric = PerformanceMetric(
            metric_name="test_metric",
            value=Decimal("100.0"),
            improvement_id=improvement_id,
            timestamp=datetime.utcnow(),
            constitutional_hash=constitutional_hash
        )
        
        compliance_log = ConstitutionalComplianceLog(
            improvement_id=improvement_id,
            compliance_level=ComplianceLevel.MEDIUM,
            compliance_score=Decimal("0.75"),
            constitutional_hash=constitutional_hash
        )
        
        test_db_session.add_all([archive, metric, compliance_log])
        await test_db_session.commit()
        
        # Verify all records have the same constitutional hash
        assert archive.constitutional_hash == constitutional_hash
        assert metric.constitutional_hash == constitutional_hash
        assert compliance_log.constitutional_hash == constitutional_hash
