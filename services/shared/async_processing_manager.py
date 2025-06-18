#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Async Processing Manager
Implements enterprise-grade asynchronous processing with job tracking and monitoring
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import redis.asyncio as redis
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AsyncJob:
    """Represents an asynchronous job."""
    job_id: str
    job_type: str
    payload: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AsyncProcessingManager:
    """Comprehensive async processing manager for ACGS-1."""
    
    def __init__(self, redis_url: str = "redis://localhost:6380"):
        self.redis_url = redis_url
        self.redis_client = None
        self.job_handlers: Dict[str, Callable] = {}
        self.worker_tasks: List[asyncio.Task] = []
        self.is_running = False
        self.worker_count = 4
        self.metrics = {
            "jobs_processed": 0,
            "jobs_failed": 0,
            "jobs_retried": 0,
            "average_processing_time": 0.0
        }
        
    async def initialize(self):
        """Initialize the async processing manager."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Async Processing Manager initialized")
            
            # Register default job handlers
            await self._register_default_handlers()
            
        except Exception as e:
            logger.error(f"Failed to initialize Async Processing Manager: {e}")
            raise
    
    async def _register_default_handlers(self):
        """Register default job handlers for common ACGS-1 operations."""
        
        # Constitutional compliance checking
        self.register_handler("constitutional_compliance_check", self._handle_constitutional_compliance)
        
        # Policy synthesis
        self.register_handler("policy_synthesis", self._handle_policy_synthesis)
        
        # Governance workflow processing
        self.register_handler("governance_workflow", self._handle_governance_workflow)
        
        # Performance monitoring
        self.register_handler("performance_monitoring", self._handle_performance_monitoring)
        
        # Data export/import
        self.register_handler("data_export", self._handle_data_export)
        self.register_handler("data_import", self._handle_data_import)
        
        # Notification processing
        self.register_handler("notification", self._handle_notification)
        
        logger.info("Default job handlers registered")
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register a job handler for a specific job type."""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    async def submit_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        callback_url: Optional[str] = None
    ) -> str:
        """Submit a job for asynchronous processing."""
        
        job_id = str(uuid.uuid4())
        job = AsyncJob(
            job_id=job_id,
            job_type=job_type,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            callback_url=callback_url
        )
        
        # Store job in Redis
        await self._store_job(job)
        
        # Add to appropriate queue based on priority
        queue_name = f"jobs:{priority.name.lower()}"
        await self.redis_client.lpush(queue_name, job_id)
        
        logger.info(f"Job submitted: {job_id} ({job_type}) with priority {priority.name}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[AsyncJob]:
        """Get the status of a job."""
        job_data = await self.redis_client.get(f"job:{job_id}")
        if job_data:
            job_dict = json.loads(job_data)
            return AsyncJob(**job_dict)
        return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        job = await self.get_job_status(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            await self._store_job(job)
            logger.info(f"Job cancelled: {job_id}")
            return True
        return False
    
    async def start_workers(self, worker_count: int = 4):
        """Start worker processes to handle jobs."""
        self.worker_count = worker_count
        self.is_running = True
        
        # Start workers for different priority queues
        for priority in JobPriority:
            for i in range(worker_count):
                task = asyncio.create_task(
                    self._worker_loop(f"jobs:{priority.name.lower()}", f"worker-{priority.name}-{i}")
                )
                self.worker_tasks.append(task)
        
        logger.info(f"Started {len(self.worker_tasks)} async workers")
    
    async def stop_workers(self):
        """Stop all worker processes."""
        self.is_running = False
        
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        logger.info("All async workers stopped")
    
    async def _worker_loop(self, queue_name: str, worker_name: str):
        """Main worker loop for processing jobs."""
        logger.info(f"Worker {worker_name} started for queue {queue_name}")
        
        while self.is_running:
            try:
                # Get next job from queue (blocking with timeout)
                result = await self.redis_client.brpop(queue_name, timeout=1)
                
                if not result:
                    continue
                
                _, job_id = result
                await self._process_job(job_id, worker_name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _process_job(self, job_id: str, worker_name: str):
        """Process a single job."""
        job = await self.get_job_status(job_id)
        if not job:
            logger.warning(f"Job not found: {job_id}")
            return
        
        if job.status != JobStatus.PENDING:
            logger.warning(f"Job {job_id} is not pending (status: {job.status})")
            return
        
        # Update job status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        await self._store_job(job)
        
        logger.info(f"Worker {worker_name} processing job {job_id} ({job.job_type})")
        
        try:
            # Get handler for job type
            handler = self.job_handlers.get(job.job_type)
            if not handler:
                raise ValueError(f"No handler registered for job type: {job.job_type}")
            
            # Execute job with timeout
            start_time = time.time()
            result = await asyncio.wait_for(
                handler(job.payload),
                timeout=job.timeout_seconds
            )
            processing_time = time.time() - start_time
            
            # Update job status to completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.metadata["result"] = result
            job.metadata["processing_time"] = processing_time
            await self._store_job(job)
            
            # Update metrics
            self.metrics["jobs_processed"] += 1
            self._update_average_processing_time(processing_time)
            
            # Send callback if configured
            if job.callback_url:
                await self._send_callback(job)
            
            logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s")
            
        except asyncio.TimeoutError:
            await self._handle_job_failure(job, "Job timed out")
        except Exception as e:
            await self._handle_job_failure(job, str(e))
    
    async def _handle_job_failure(self, job: AsyncJob, error_message: str):
        """Handle job failure with retry logic."""
        job.error_message = error_message
        job.retry_count += 1
        
        if job.retry_count <= job.max_retries:
            # Retry the job
            job.status = JobStatus.RETRYING
            await self._store_job(job)
            
            # Re-queue with exponential backoff
            delay = min(300, 2 ** job.retry_count)  # Max 5 minutes
            await asyncio.sleep(delay)
            
            job.status = JobStatus.PENDING
            await self._store_job(job)
            
            queue_name = f"jobs:{job.priority.name.lower()}"
            await self.redis_client.lpush(queue_name, job.job_id)
            
            self.metrics["jobs_retried"] += 1
            logger.info(f"Job {job.job_id} queued for retry {job.retry_count}/{job.max_retries}")
        else:
            # Mark as failed
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            await self._store_job(job)
            
            self.metrics["jobs_failed"] += 1
            logger.error(f"Job {job.job_id} failed permanently: {error_message}")
    
    async def _store_job(self, job: AsyncJob):
        """Store job data in Redis."""
        job_data = {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "payload": job.payload,
            "priority": job.priority.name,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "retry_count": job.retry_count,
            "max_retries": job.max_retries,
            "timeout_seconds": job.timeout_seconds,
            "callback_url": job.callback_url,
            "metadata": job.metadata
        }
        
        await self.redis_client.setex(
            f"job:{job.job_id}",
            86400,  # 24 hours TTL
            json.dumps(job_data, default=str)
        )
    
    async def _send_callback(self, job: AsyncJob):
        """Send callback notification for completed job."""
        try:
            async with aiohttp.ClientSession() as session:
                callback_data = {
                    "job_id": job.job_id,
                    "job_type": job.job_type,
                    "status": job.status.value,
                    "result": job.metadata.get("result"),
                    "processing_time": job.metadata.get("processing_time"),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
                
                async with session.post(
                    job.callback_url,
                    json=callback_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Callback sent successfully for job {job.job_id}")
                    else:
                        logger.warning(f"Callback failed for job {job.job_id}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send callback for job {job.job_id}: {e}")
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time metric."""
        current_avg = self.metrics["average_processing_time"]
        total_jobs = self.metrics["jobs_processed"]
        
        if total_jobs == 1:
            self.metrics["average_processing_time"] = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics["average_processing_time"] = (
                alpha * processing_time + (1 - alpha) * current_avg
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics."""
        # Get queue lengths
        queue_lengths = {}
        for priority in JobPriority:
            queue_name = f"jobs:{priority.name.lower()}"
            length = await self.redis_client.llen(queue_name)
            queue_lengths[priority.name.lower()] = length
        
        return {
            **self.metrics,
            "queue_lengths": queue_lengths,
            "active_workers": len(self.worker_tasks),
            "is_running": self.is_running
        }
    
    # Default job handlers
    async def _handle_constitutional_compliance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle constitutional compliance checking jobs."""
        # Simulate constitutional compliance check
        await asyncio.sleep(0.1)  # Simulate processing time
        return {
            "compliance_status": "compliant",
            "confidence": 0.95,
            "checked_principles": payload.get("principles", [])
        }
    
    async def _handle_policy_synthesis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle policy synthesis jobs."""
        # Simulate policy synthesis
        await asyncio.sleep(0.5)  # Simulate LLM processing time
        return {
            "synthesized_policy": f"Policy for {payload.get('topic', 'general')}",
            "confidence": 0.88,
            "synthesis_time": 0.5
        }
    
    async def _handle_governance_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle governance workflow processing jobs."""
        # Simulate workflow processing
        await asyncio.sleep(0.2)
        return {
            "workflow_status": "completed",
            "steps_executed": payload.get("steps", []),
            "execution_time": 0.2
        }
    
    async def _handle_performance_monitoring(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance monitoring jobs."""
        # Simulate performance monitoring
        await asyncio.sleep(0.1)
        return {
            "metrics_collected": True,
            "service": payload.get("service", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_data_export(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data export jobs."""
        # Simulate data export
        await asyncio.sleep(1.0)  # Simulate file generation
        return {
            "export_file": f"export_{int(time.time())}.json",
            "records_exported": payload.get("record_count", 100),
            "export_format": payload.get("format", "json")
        }
    
    async def _handle_data_import(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data import jobs."""
        # Simulate data import
        await asyncio.sleep(0.8)
        return {
            "import_status": "success",
            "records_imported": payload.get("record_count", 50),
            "import_file": payload.get("file_path", "unknown")
        }
    
    async def _handle_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification jobs."""
        # Simulate notification sending
        await asyncio.sleep(0.1)
        return {
            "notification_sent": True,
            "recipient": payload.get("recipient", "unknown"),
            "message_type": payload.get("type", "info")
        }

# Global async processing manager instance
_async_manager: Optional[AsyncProcessingManager] = None

async def get_async_manager() -> AsyncProcessingManager:
    """Get the global async processing manager instance."""
    global _async_manager
    if _async_manager is None:
        _async_manager = AsyncProcessingManager()
        await _async_manager.initialize()
    return _async_manager

async def submit_async_job(
    job_type: str,
    payload: Dict[str, Any],
    priority: JobPriority = JobPriority.NORMAL,
    **kwargs
) -> str:
    """Convenience function to submit an async job."""
    manager = await get_async_manager()
    return await manager.submit_job(job_type, payload, priority, **kwargs)

# Async job decorators for easy integration
def async_job(job_type: str, priority: JobPriority = JobPriority.NORMAL):
    """Decorator to mark a function as an async job handler."""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            manager = await get_async_manager()
            payload = {"args": args, "kwargs": kwargs}
            return await manager.submit_job(job_type, payload, priority)
        return wrapper
    return decorator

def background_task(priority: JobPriority = JobPriority.NORMAL):
    """Decorator to automatically submit function calls as background tasks."""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            job_type = f"{func.__module__}.{func.__name__}"
            payload = {"function": job_type, "args": args, "kwargs": kwargs}
            manager = await get_async_manager()
            return await manager.submit_job("function_execution", payload, priority)
        return wrapper
    return decorator
