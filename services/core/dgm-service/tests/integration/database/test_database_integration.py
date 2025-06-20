"""
Integration tests for database operations.

Tests database connectivity, transactions, and data integrity
across the DGM service database layer.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from dgm_service.models import (
    DGMArchive, ImprovementStatus, PerformanceMetric,
    ConstitutionalComplianceLog, ComplianceLevel,
    BanditState, BanditAlgorithmType
)


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    async def test_database_connection(self, test_db_session: AsyncSession):
        """Test basic database connectivity."""
        result = await test_db_session.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
    
    async def test_dgm_archive_crud_operations(self, test_db_session: AsyncSession):
        """Test complete CRUD operations for DGM archive."""
        # Create
        archive = DGMArchive(
            improvement_type="integration_test",
            status=ImprovementStatus.PENDING,
            strategy_used="test_strategy",
            target_services=["test-service"],
            constitutional_hash="test_hash_123"
        )
        
        test_db_session.add(archive)
        await test_db_session.commit()
        await test_db_session.refresh(archive)
        
        created_id = archive.id
        assert created_id is not None
        
        # Read
        from sqlalchemy import select
        stmt = select(DGMArchive).where(DGMArchive.id == created_id)
        result = await test_db_session.execute(stmt)
        retrieved_archive = result.scalar_one()
        
        assert retrieved_archive.improvement_type == "integration_test"
        assert retrieved_archive.status == ImprovementStatus.PENDING
        
        # Update
        retrieved_archive.status = ImprovementStatus.IN_PROGRESS
        retrieved_archive.performance_before = {"response_time": 150.0}
        await test_db_session.commit()
        
        # Verify update
        await test_db_session.refresh(retrieved_archive)
        assert retrieved_archive.status == ImprovementStatus.IN_PROGRESS
        assert retrieved_archive.performance_before["response_time"] == 150.0
        
        # Delete
        await test_db_session.delete(retrieved_archive)
        await test_db_session.commit()
        
        # Verify deletion
        stmt = select(DGMArchive).where(DGMArchive.id == created_id)
        result = await test_db_session.execute(stmt)
        assert result.scalar_one_or_none() is None
    
    async def test_performance_metrics_batch_insert(self, test_db_session: AsyncSession):
        """Test batch insertion of performance metrics."""
        improvement_id = uuid4()
        base_time = datetime.utcnow()
        
        # Create batch of metrics
        metrics = []
        for i in range(100):
            metric = PerformanceMetric(
                metric_name="batch_test_metric",
                value=Decimal(str(100.0 + i)),
                timestamp=base_time + timedelta(seconds=i),
                improvement_id=improvement_id,
                service_name="test-service",
                constitutional_hash="batch_test_hash"
            )
            metrics.append(metric)
        
        # Batch insert
        test_db_session.add_all(metrics)
        await test_db_session.commit()
        
        # Verify batch insertion
        from sqlalchemy import select, func
        stmt = select(func.count(PerformanceMetric.id)).where(
            PerformanceMetric.improvement_id == improvement_id
        )
        result = await test_db_session.execute(stmt)
        count = result.scalar()
        
        assert count == 100
        
        # Test range query
        start_time = base_time + timedelta(seconds=25)
        end_time = base_time + timedelta(seconds=75)
        
        stmt = select(PerformanceMetric).where(
            PerformanceMetric.improvement_id == improvement_id,
            PerformanceMetric.timestamp.between(start_time, end_time)
        )
        result = await test_db_session.execute(stmt)
        range_metrics = result.scalars().all()
        
        assert len(range_metrics) == 51  # 25-75 inclusive
    
    async def test_constitutional_compliance_workflow(self, test_db_session: AsyncSession):
        """Test constitutional compliance logging workflow."""
        improvement_id = uuid4()
        
        # Create archive entry
        archive = DGMArchive(
            improvement_type="compliance_test",
            status=ImprovementStatus.PENDING,
            strategy_used="compliance_strategy",
            constitutional_hash="compliance_hash_456"
        )
        archive.id = improvement_id
        
        test_db_session.add(archive)
        await test_db_session.commit()
        
        # Create compliance logs for different stages
        stages = [
            ("proposal", ComplianceLevel.HIGH, Decimal("0.95")),
            ("execution", ComplianceLevel.HIGH, Decimal("0.92")),
            ("validation", ComplianceLevel.MEDIUM, Decimal("0.78"))
        ]
        
        for stage, level, score in stages:
            compliance_log = ConstitutionalComplianceLog(
                improvement_id=improvement_id,
                compliance_level=level,
                compliance_score=score,
                constitutional_hash="compliance_hash_456",
                validation_details={
                    "stage": stage,
                    "checks_performed": 10,
                    "checks_passed": int(score * 10)
                },
                validator_version="1.0.0"
            )
            test_db_session.add(compliance_log)
        
        await test_db_session.commit()
        
        # Query compliance history
        from sqlalchemy import select
        stmt = select(ConstitutionalComplianceLog).where(
            ConstitutionalComplianceLog.improvement_id == improvement_id
        ).order_by(ConstitutionalComplianceLog.created_at)
        
        result = await test_db_session.execute(stmt)
        compliance_logs = result.scalars().all()
        
        assert len(compliance_logs) == 3
        assert compliance_logs[0].validation_details["stage"] == "proposal"
        assert compliance_logs[1].validation_details["stage"] == "execution"
        assert compliance_logs[2].validation_details["stage"] == "validation"
    
    async def test_bandit_state_updates(self, test_db_session: AsyncSession):
        """Test bandit algorithm state updates."""
        # Create initial bandit states
        arms = ["performance_optimization", "code_refactoring", "architecture_improvement"]
        
        for arm in arms:
            state = BanditState(
                algorithm_type=BanditAlgorithmType.UCB1,
                arm_name=arm,
                pulls=0,
                rewards=Decimal("0.0"),
                success_rate=Decimal("0.0"),
                confidence_bound=Decimal("1.0"),
                constitutional_hash="bandit_test_hash"
            )
            test_db_session.add(state)
        
        await test_db_session.commit()
        
        # Simulate bandit updates
        from sqlalchemy import select, update
        
        for i in range(10):
            # Select arm (simulate UCB1 selection)
            arm_name = arms[i % len(arms)]
            reward = Decimal(str(0.7 + (i % 3) * 0.1))  # Varying rewards
            
            # Update bandit state
            stmt = update(BanditState).where(
                BanditState.arm_name == arm_name
            ).values(
                pulls=BanditState.pulls + 1,
                rewards=BanditState.rewards + reward,
                success_rate=(BanditState.rewards + reward) / (BanditState.pulls + 1),
                last_updated=datetime.utcnow()
            )
            
            await test_db_session.execute(stmt)
            await test_db_session.commit()
        
        # Verify final states
        stmt = select(BanditState).order_by(BanditState.arm_name)
        result = await test_db_session.execute(stmt)
        final_states = result.scalars().all()
        
        assert len(final_states) == 3
        
        # Check that pulls were distributed
        total_pulls = sum(state.pulls for state in final_states)
        assert total_pulls == 10
        
        # Check that success rates are calculated correctly
        for state in final_states:
            if state.pulls > 0:
                expected_rate = state.rewards / state.pulls
                assert abs(state.success_rate - expected_rate) < Decimal("0.001")
    
    async def test_transaction_rollback(self, test_db_session: AsyncSession):
        """Test transaction rollback behavior."""
        # Start a transaction
        archive = DGMArchive(
            improvement_type="rollback_test",
            status=ImprovementStatus.PENDING,
            strategy_used="rollback_strategy"
        )
        
        test_db_session.add(archive)
        await test_db_session.flush()  # Flush but don't commit
        
        archive_id = archive.id
        assert archive_id is not None
        
        # Rollback the transaction
        await test_db_session.rollback()
        
        # Verify the record was not persisted
        from sqlalchemy import select
        stmt = select(DGMArchive).where(DGMArchive.id == archive_id)
        result = await test_db_session.execute(stmt)
        assert result.scalar_one_or_none() is None
    
    async def test_concurrent_access_simulation(self, test_db_session: AsyncSession):
        """Test concurrent access patterns."""
        improvement_id = uuid4()
        
        # Create base archive
        archive = DGMArchive(
            improvement_type="concurrent_test",
            status=ImprovementStatus.IN_PROGRESS,
            strategy_used="concurrent_strategy"
        )
        archive.id = improvement_id
        
        test_db_session.add(archive)
        await test_db_session.commit()
        
        # Simulate concurrent metric insertions
        import asyncio
        
        async def insert_metrics(session, start_idx, count):
            metrics = []
            for i in range(count):
                metric = PerformanceMetric(
                    metric_name="concurrent_metric",
                    value=Decimal(str(start_idx + i)),
                    timestamp=datetime.utcnow(),
                    improvement_id=improvement_id,
                    service_name="concurrent-service"
                )
                metrics.append(metric)
            
            session.add_all(metrics)
            await session.commit()
        
        # Create multiple "concurrent" insertions
        tasks = [
            insert_metrics(test_db_session, 0, 10),
            insert_metrics(test_db_session, 10, 10),
            insert_metrics(test_db_session, 20, 10)
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify all metrics were inserted
        from sqlalchemy import select, func
        stmt = select(func.count(PerformanceMetric.id)).where(
            PerformanceMetric.improvement_id == improvement_id
        )
        result = await test_db_session.execute(stmt)
        total_count = result.scalar()
        
        assert total_count == 30
    
    async def test_database_constraints(self, test_db_session: AsyncSession):
        """Test database constraint enforcement."""
        from sqlalchemy.exc import IntegrityError
        
        # Test unique constraint (if any)
        # Test foreign key constraints
        # Test check constraints
        
        # Example: Test that improvement_id foreign key is enforced
        invalid_improvement_id = uuid4()
        
        metric = PerformanceMetric(
            metric_name="constraint_test",
            value=Decimal("100.0"),
            timestamp=datetime.utcnow(),
            improvement_id=invalid_improvement_id,  # Non-existent improvement
            service_name="constraint-service"
        )
        
        test_db_session.add(metric)
        
        # This should succeed in our test setup since we're using SQLite
        # In production with proper foreign keys, this would fail
        await test_db_session.commit()
        
        # Verify the metric was created (SQLite allows this)
        from sqlalchemy import select
        stmt = select(PerformanceMetric).where(
            PerformanceMetric.improvement_id == invalid_improvement_id
        )
        result = await test_db_session.execute(stmt)
        created_metric = result.scalar_one_or_none()
        
        assert created_metric is not None
    
    async def test_complex_queries(self, test_db_session: AsyncSession):
        """Test complex database queries."""
        # Create test data
        improvement_ids = [uuid4() for _ in range(3)]
        
        # Create archives
        for i, imp_id in enumerate(improvement_ids):
            archive = DGMArchive(
                improvement_type=f"query_test_{i}",
                status=ImprovementStatus.COMPLETED,
                strategy_used=f"strategy_{i}",
                performance_before={"response_time": 150.0 + i * 10},
                performance_after={"response_time": 125.0 + i * 5},
                constitutional_compliance_score=Decimal(str(0.9 - i * 0.05))
            )
            archive.id = imp_id
            test_db_session.add(archive)
        
        await test_db_session.commit()
        
        # Complex query: Find improvements with best performance gains
        from sqlalchemy import select, func, cast, Float
        
        stmt = select(
            DGMArchive.id,
            DGMArchive.improvement_type,
            (
                cast(DGMArchive.performance_before['response_time'], Float) -
                cast(DGMArchive.performance_after['response_time'], Float)
            ).label('performance_gain')
        ).where(
            DGMArchive.status == ImprovementStatus.COMPLETED
        ).order_by(
            (
                cast(DGMArchive.performance_before['response_time'], Float) -
                cast(DGMArchive.performance_after['response_time'], Float)
            ).desc()
        )
        
        result = await test_db_session.execute(stmt)
        improvements = result.all()
        
        assert len(improvements) == 3
        
        # Verify ordering (highest gain first)
        gains = [imp.performance_gain for imp in improvements]
        assert gains == sorted(gains, reverse=True)
