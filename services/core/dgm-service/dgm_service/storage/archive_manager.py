"""
Archive Manager for DGM Service.

Manages the storage and retrieval of improvement archives,
including performance data, constitutional compliance records,
and rollback information.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

import asyncpg
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..models.archive import DGMArchive, ImprovementStatus
from ..config import settings

logger = logging.getLogger(__name__)


class ArchiveManager:
    """Manages DGM improvement archives."""
    
    def __init__(self):
        self.retention_days = settings.ARCHIVE_RETENTION_DAYS
    
    async def store_improvement(
        self,
        improvement_id: UUID,
        description: str,
        algorithm_changes: Dict[str, Any],
        performance_before: Dict[str, Any],
        performance_after: Dict[str, Any],
        constitutional_compliance_score: float,
        compliance_details: Dict[str, Any],
        rollback_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> UUID:
        """Store a new improvement in the archive."""
        try:
            async with get_db_session() as session:
                archive_entry = DGMArchive(
                    improvement_id=improvement_id,
                    description=description,
                    algorithm_changes=algorithm_changes,
                    performance_before=performance_before,
                    performance_after=performance_after,
                    constitutional_compliance_score=constitutional_compliance_score,
                    compliance_details=compliance_details,
                    status=ImprovementStatus.COMPLETED,
                    rollback_data=rollback_data,
                    metadata=metadata or {},
                    created_by=created_by
                )
                
                session.add(archive_entry)
                await session.commit()
                await session.refresh(archive_entry)
                
                logger.info(f"Stored improvement {improvement_id} in archive")
                return archive_entry.id
                
        except Exception as e:
            logger.error(f"Failed to store improvement {improvement_id}: {e}")
            raise
    
    async def get_improvement(self, improvement_id: UUID) -> Optional[DGMArchive]:
        """Retrieve a specific improvement from the archive."""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(DGMArchive).where(DGMArchive.improvement_id == improvement_id)
                )
                return result.scalar_one_or_none()
                
        except Exception as e:
            logger.error(f"Failed to retrieve improvement {improvement_id}: {e}")
            return None
    
    async def list_improvements(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[ImprovementStatus] = None,
        min_compliance_score: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[DGMArchive]:
        """List improvements with optional filtering."""
        try:
            async with get_db_session() as session:
                query = select(DGMArchive)
                
                # Apply filters
                if status:
                    query = query.where(DGMArchive.status == status)
                
                if min_compliance_score is not None:
                    query = query.where(
                        DGMArchive.constitutional_compliance_score >= min_compliance_score
                    )
                
                if start_date:
                    query = query.where(DGMArchive.timestamp >= start_date)
                
                if end_date:
                    query = query.where(DGMArchive.timestamp <= end_date)
                
                # Order by timestamp descending
                query = query.order_by(DGMArchive.timestamp.desc())
                
                # Apply pagination
                query = query.offset(offset).limit(limit)
                
                result = await session.execute(query)
                return result.scalars().all()
                
        except Exception as e:
            logger.error(f"Failed to list improvements: {e}")
            return []
    
    async def update_improvement_status(
        self,
        improvement_id: UUID,
        status: ImprovementStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update the status of an improvement."""
        try:
            async with get_db_session() as session:
                update_data = {"status": status}
                if metadata:
                    update_data["metadata"] = metadata
                
                result = await session.execute(
                    update(DGMArchive)
                    .where(DGMArchive.improvement_id == improvement_id)
                    .values(**update_data)
                )
                
                await session.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Updated improvement {improvement_id} status to {status}")
                    return True
                else:
                    logger.warning(f"No improvement found with ID {improvement_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update improvement {improvement_id} status: {e}")
            return False
    
    async def get_performance_trends(
        self,
        days: int = 30,
        metric_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance trends over time."""
        try:
            async with get_db_session() as session:
                start_date = datetime.utcnow() - timedelta(days=days)
                
                query = select(DGMArchive).where(
                    DGMArchive.timestamp >= start_date
                ).order_by(DGMArchive.timestamp.asc())
                
                result = await session.execute(query)
                improvements = result.scalars().all()
                
                trends = {
                    "timeline": [],
                    "compliance_scores": [],
                    "performance_improvements": [],
                    "total_improvements": len(improvements)
                }
                
                for improvement in improvements:
                    trends["timeline"].append(improvement.timestamp.isoformat())
                    trends["compliance_scores"].append(
                        float(improvement.constitutional_compliance_score)
                    )
                    
                    # Calculate performance improvement
                    before = improvement.performance_before.get("overall_score", 0)
                    after = improvement.performance_after.get("overall_score", 0)
                    improvement_pct = ((after - before) / before * 100) if before > 0 else 0
                    trends["performance_improvements"].append(improvement_pct)
                
                return trends
                
        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            return {}
    
    async def cleanup_old_archives(self) -> int:
        """Clean up old archive entries based on retention policy."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            async with get_db_session() as session:
                result = await session.execute(
                    delete(DGMArchive).where(DGMArchive.timestamp < cutoff_date)
                )
                
                await session.commit()
                deleted_count = result.rowcount
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old archive entries")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old archives: {e}")
            return 0
    
    async def export_archive(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """Export archive data for backup or analysis."""
        try:
            improvements = await self.list_improvements(
                limit=10000,  # Large limit for export
                start_date=start_date,
                end_date=end_date
            )
            
            if format.lower() == "json":
                export_data = []
                for improvement in improvements:
                    export_data.append({
                        "improvement_id": str(improvement.improvement_id),
                        "timestamp": improvement.timestamp.isoformat(),
                        "description": improvement.description,
                        "algorithm_changes": improvement.algorithm_changes,
                        "performance_before": improvement.performance_before,
                        "performance_after": improvement.performance_after,
                        "constitutional_compliance_score": float(improvement.constitutional_compliance_score),
                        "compliance_details": improvement.compliance_details,
                        "status": improvement.status.value,
                        "metadata": improvement.metadata,
                        "created_by": improvement.created_by
                    })
                
                return json.dumps(export_data, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export archive: {e}")
            raise
