"""
Worker Agents Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for managing worker agents that execute tasks with
various capabilities including data processing, policy evaluation,
and computational workloads.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import os
import uuid

from .models import (
    WorkerProfile, WorkerType, TaskType, ExecutionStatus,
    TaskRequest, TaskResult, WorkerMetrics, HealthStatus,
    WorkerCommand, Skill, SkillLevel, ResourceRequirement,
    TaskExecution, CONSTITUTIONAL_HASH
)
from .services import (
    WorkerManager, WorkerRegistry, LoadBalancer, TaskExecutor
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize worker manager
worker_manager = WorkerManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Worker Agents Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize sample workers
    await initialize_sample_workers()
    
    # Start background task processor
    asyncio.create_task(worker_manager.process_tasks())
    asyncio.create_task(health_monitor())
    asyncio.create_task(metrics_collector())
    
    yield
    
    logger.info("Shutting down Worker Agents Service")

app = FastAPI(
    title="Worker Agents Service",
    description="Manage and coordinate worker agents for task execution",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_sample_workers():
    """Initialize sample worker agents"""
    sample_workers = [
        WorkerProfile(
            name="data-processor-alpha",
            worker_type=WorkerType.DATA_PROCESSOR,
            skills=[
                Skill(
                    name="data_analysis",
                    category="analytics",
                    level=SkillLevel.ADVANCED,
                    proficiency_score=0.90,
                    experience_hours=2000
                ),
                Skill(
                    name="data_transformation",
                    category="processing",
                    level=SkillLevel.EXPERT,
                    proficiency_score=0.95,
                    experience_hours=1500
                )
            ],
            capabilities=[{
                "name": "high_volume_processing",
                "description": "Process large datasets efficiently",
                "supported_task_types": [TaskType.DATA_ANALYSIS, TaskType.TRANSFORMATION, TaskType.AGGREGATION],
                "required_skills": ["data_analysis", "data_transformation"],
                "resource_requirements": [
                    ResourceRequirement(resource_type="memory", amount=4096, unit="MB"),
                    ResourceRequirement(resource_type="cpu", amount=2, unit="cores")
                ],
                "throughput_estimate": 5.0,
                "accuracy_rate": 0.98
            }],
            max_concurrent_tasks=5,
            available_resources={"cpu": 8, "memory": 16384, "storage": 100000}
        ),
        WorkerProfile(
            name="policy-evaluator-beta",
            worker_type=WorkerType.POLICY_EXECUTOR,
            skills=[
                Skill(
                    name="policy_analysis",
                    category="governance",
                    level=SkillLevel.EXPERT,
                    proficiency_score=0.93,
                    experience_hours=3000
                ),
                Skill(
                    name="constitutional_compliance",
                    category="compliance",
                    level=SkillLevel.MASTER,
                    proficiency_score=0.98,
                    experience_hours=2500
                )
            ],
            capabilities=[{
                "name": "policy_evaluation",
                "description": "Evaluate policies for compliance and effectiveness",
                "supported_task_types": [TaskType.POLICY_EVALUATION, TaskType.VALIDATION],
                "required_skills": ["policy_analysis", "constitutional_compliance"],
                "resource_requirements": [
                    ResourceRequirement(resource_type="cpu", amount=1, unit="cores"),
                    ResourceRequirement(resource_type="memory", amount=2048, unit="MB")
                ],
                "throughput_estimate": 3.0,
                "accuracy_rate": 0.97
            }],
            max_concurrent_tasks=3,
            available_resources={"cpu": 4, "memory": 8192, "storage": 50000}
        ),
        WorkerProfile(
            name="computational-gamma",
            worker_type=WorkerType.COMPUTATIONAL,
            skills=[
                Skill(
                    name="numerical_computation",
                    category="computation",
                    level=SkillLevel.ADVANCED,
                    proficiency_score=0.88,
                    experience_hours=1800
                ),
                Skill(
                    name="algorithm_optimization",
                    category="optimization",
                    level=SkillLevel.ADVANCED,
                    proficiency_score=0.85,
                    experience_hours=1200
                )
            ],
            capabilities=[{
                "name": "intensive_computation",
                "description": "Perform complex computational tasks",
                "supported_task_types": [TaskType.COMPUTATION, TaskType.AGGREGATION],
                "required_skills": ["numerical_computation"],
                "resource_requirements": [
                    ResourceRequirement(resource_type="cpu", amount=4, unit="cores"),
                    ResourceRequirement(resource_type="memory", amount=8192, unit="MB")
                ],
                "throughput_estimate": 2.0,
                "accuracy_rate": 0.94
            }],
            max_concurrent_tasks=4,
            available_resources={"cpu": 16, "memory": 32768, "storage": 200000}
        ),
        WorkerProfile(
            name="validator-delta",
            worker_type=WorkerType.VALIDATOR,
            skills=[
                Skill(
                    name="data_validation",
                    category="validation",
                    level=SkillLevel.EXPERT,
                    proficiency_score=0.96,
                    experience_hours=2200
                ),
                Skill(
                    name="quality_assurance",
                    category="quality",
                    level=SkillLevel.ADVANCED,
                    proficiency_score=0.91,
                    experience_hours=1600
                )
            ],
            capabilities=[{
                "name": "comprehensive_validation",
                "description": "Validate data and process quality",
                "supported_task_types": [TaskType.VALIDATION, TaskType.MONITORING],
                "required_skills": ["data_validation", "quality_assurance"],
                "resource_requirements": [
                    ResourceRequirement(resource_type="cpu", amount=1, unit="cores"),
                    ResourceRequirement(resource_type="memory", amount=1024, unit="MB")
                ],
                "throughput_estimate": 8.0,
                "accuracy_rate": 0.99
            }],
            max_concurrent_tasks=6,
            available_resources={"cpu": 2, "memory": 4096, "storage": 25000}
        ),
        WorkerProfile(
            name="monitor-epsilon",
            worker_type=WorkerType.GENERAL_PURPOSE,
            skills=[
                Skill(
                    name="system_monitoring",
                    category="observability",
                    level=SkillLevel.ADVANCED,
                    proficiency_score=0.87,
                    experience_hours=1400
                ),
                Skill(
                    name="report_generation",
                    category="reporting",
                    level=SkillLevel.INTERMEDIATE,
                    proficiency_score=0.82,
                    experience_hours=900
                )
            ],
            capabilities=[{
                "name": "monitoring_and_reporting",
                "description": "Monitor systems and generate reports",
                "supported_task_types": [TaskType.MONITORING, TaskType.REPORTING],
                "required_skills": ["system_monitoring"],
                "resource_requirements": [
                    ResourceRequirement(resource_type="cpu", amount=1, unit="cores"),
                    ResourceRequirement(resource_type="memory", amount="512", unit="MB")
                ],
                "throughput_estimate": 4.0,
                "accuracy_rate": 0.92
            }],
            max_concurrent_tasks=8,
            available_resources={"cpu": 2, "memory": 2048, "storage": 10000}
        )
    ]
    
    for worker in sample_workers:
        await worker_manager.registry.register_worker(worker)
    
    logger.info(f"Initialized {len(sample_workers)} sample workers")

async def health_monitor():
    """Monitor worker health in background"""
    while True:
        try:
            for worker_id, worker in worker_manager.registry.workers.items():
                # Update health status
                if worker_id in worker_manager.registry.worker_health:
                    health = worker_manager.registry.worker_health[worker_id]
                    
                    # Simulate health metrics
                    health.cpu_usage = min(worker.current_task_count * 20.0, 95.0)
                    health.memory_usage = min(worker.current_task_count * 15.0, 85.0)
                    health.active_tasks = worker.current_task_count
                    health.timestamp = datetime.utcnow()
                    
                    # Check if worker is overloaded
                    if worker.current_task_count >= worker.max_concurrent_tasks:
                        health.is_healthy = health.cpu_usage < 95.0
                    else:
                        health.is_healthy = True
                    
                    # Update worker status
                    if health.is_healthy:
                        if worker.current_task_count > 0:
                            worker.status = "busy"
                        else:
                            worker.status = "idle"
                    else:
                        worker.status = "overloaded"
                
                worker.last_active = datetime.utcnow()
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            await asyncio.sleep(30)

async def metrics_collector():
    """Collect and aggregate worker metrics"""
    while True:
        try:
            # Update throughput calculations for each worker
            for worker_id in worker_manager.registry.workers:
                if worker_id in worker_manager.metrics:
                    metrics = worker_manager.metrics[worker_id]
                    
                    # Calculate throughput (simplified)
                    if metrics.average_execution_time_ms > 0:
                        metrics.throughput_rps = 1000.0 / metrics.average_execution_time_ms
                    
                    # Update resource efficiency (placeholder)
                    metrics.resource_efficiency = {
                        "cpu": min(100.0, metrics.throughput_rps * 10),
                        "memory": min(100.0, metrics.success_rate * 100)
                    }
            
            await asyncio.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.error(f"Metrics collector error: {e}")
            await asyncio.sleep(60)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_workers = len(worker_manager.registry.workers)
    healthy_workers = sum(
        1 for health in worker_manager.registry.worker_health.values()
        if health.is_healthy
    )
    
    active_tasks = sum(
        worker.current_task_count 
        for worker in worker_manager.registry.workers.values()
    )
    
    queue_size = worker_manager.task_queue.qsize()
    
    return {
        "status": "healthy",
        "service": "worker-agents",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "workers": {
            "total": total_workers,
            "healthy": healthy_workers,
            "unhealthy": total_workers - healthy_workers
        },
        "tasks": {
            "active": active_tasks,
            "queued": queue_size
        }
    }

@app.post("/api/v1/workers/register", response_model=Dict[str, Any])
async def register_worker(worker: WorkerProfile):
    """Register a new worker"""
    success = await worker_manager.registry.register_worker(worker)
    
    if not success:
        raise HTTPException(status_code=409, detail="Worker already registered")
    
    return {
        "worker_id": worker.worker_id,
        "status": "registered",
        "constitutional_hash": CONSTITUTIONAL_HASH
    }

@app.get("/api/v1/workers", response_model=List[WorkerProfile])
async def list_workers(
    worker_type: Optional[str] = None,
    status: Optional[str] = None,
    skill: Optional[str] = None
):
    """List workers with optional filters"""
    workers = list(worker_manager.registry.workers.values())
    
    # Apply filters
    if worker_type:
        workers = [w for w in workers if w.worker_type == worker_type]
    
    if status:
        workers = [w for w in workers if w.status == status]
    
    if skill:
        skilled_workers = await worker_manager.registry.find_workers_by_skill(skill)
        workers = [w for w in workers if w in skilled_workers]
    
    return workers

@app.get("/api/v1/workers/{worker_id}", response_model=WorkerProfile)
async def get_worker(worker_id: str):
    """Get specific worker details"""
    if worker_id not in worker_manager.registry.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return worker_manager.registry.workers[worker_id]

@app.get("/api/v1/workers/{worker_id}/health", response_model=HealthStatus)
async def get_worker_health(worker_id: str):
    """Get worker health status"""
    if worker_id not in worker_manager.registry.worker_health:
        raise HTTPException(status_code=404, detail="Worker health data not found")
    
    return worker_manager.registry.worker_health[worker_id]

@app.get("/api/v1/workers/{worker_id}/metrics", response_model=WorkerMetrics)
async def get_worker_metrics(worker_id: str):
    """Get worker performance metrics"""
    metrics = await worker_manager.get_worker_metrics(worker_id)
    
    if not metrics:
        # Return empty metrics if none exist
        metrics = WorkerMetrics(worker_id=worker_id)
    
    return metrics

@app.post("/api/v1/tasks/submit", response_model=Dict[str, Any])
async def submit_task(task_request: TaskRequest):
    """Submit task for execution"""
    
    # Add constitutional hash to context
    task_request.context["constitutional_hash"] = CONSTITUTIONAL_HASH
    
    # Submit task
    task_id = await worker_manager.submit_task(task_request)
    
    return {
        "task_id": task_id,
        "status": "submitted",
        "queue_position": worker_manager.task_queue.qsize(),
        "constitutional_hash": CONSTITUTIONAL_HASH
    }

@app.get("/api/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get task execution status"""
    
    # Check if task is currently being processed
    if task_id in worker_manager.processing_tasks:
        return {
            "task_id": task_id,
            "status": "processing",
            "worker_id": worker_manager.processing_tasks[task_id]
        }
    
    # Check execution history across all workers
    for worker_id, executor in worker_manager.registry.worker_executors.items():
        # Check current executions
        for execution in executor.current_executions.values():
            if execution.task_id == task_id:
                return {
                    "task_id": task_id,
                    "execution_id": execution.execution_id,
                    "status": execution.status.value,
                    "worker_id": worker_id,
                    "progress": execution.progress_percentage,
                    "start_time": execution.start_time,
                    "constitutional_validation": execution.constitutional_validation
                }
        
        # Check execution history
        for execution in executor.execution_history:
            if execution.task_id == task_id:
                return {
                    "task_id": task_id,
                    "execution_id": execution.execution_id,
                    "status": execution.status.value,
                    "worker_id": worker_id,
                    "progress": execution.progress_percentage,
                    "start_time": execution.start_time,
                    "end_time": execution.end_time,
                    "duration_seconds": execution.duration_seconds,
                    "results": execution.results,
                    "constitutional_validation": execution.constitutional_validation
                }
    
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/api/v1/tasks/results")
async def get_task_results(limit: int = 10):
    """Get recent task results"""
    results = []
    
    # Collect results from result queue (non-blocking)
    for _ in range(min(limit, worker_manager.result_queue.qsize())):
        try:
            result = worker_manager.result_queue.get_nowait()
            results.append(result)
        except:
            break
    
    return {
        "results": results,
        "count": len(results)
    }

@app.get("/api/v1/workers/available")
async def get_available_workers(
    task_type: Optional[str] = None,
    required_skills: Optional[List[str]] = None
):
    """Get workers available for new tasks"""
    available = await worker_manager.registry.get_available_workers()
    
    # Filter by task type capability
    if task_type:
        try:
            task_type_enum = TaskType(task_type)
            capable_workers = []
            
            for worker in available:
                for capability in worker.capabilities:
                    if task_type_enum in capability.supported_task_types:
                        capable_workers.append(worker)
                        break
            
            available = capable_workers
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task type")
    
    # Filter by required skills
    if required_skills:
        skilled_workers = []
        for worker in available:
            worker_skills = {skill.name for skill in worker.skills}
            if all(skill in worker_skills for skill in required_skills):
                skilled_workers.append(worker)
        available = skilled_workers
    
    return {
        "available_workers": available,
        "count": len(available)
    }

@app.get("/api/v1/skills")
async def list_skills():
    """List all available skills across workers"""
    skills = {}
    
    for worker in worker_manager.registry.workers.values():
        for skill in worker.skills:
            if skill.name not in skills:
                skills[skill.name] = {
                    "name": skill.name,
                    "category": skill.category,
                    "workers": [],
                    "average_proficiency": 0.0
                }
            
            skills[skill.name]["workers"].append({
                "worker_id": worker.worker_id,
                "worker_name": worker.name,
                "level": skill.level,
                "proficiency": skill.proficiency_score
            })
    
    # Calculate average proficiency
    for skill_data in skills.values():
        if skill_data["workers"]:
            avg_prof = sum(w["proficiency"] for w in skill_data["workers"]) / len(skill_data["workers"])
            skill_data["average_proficiency"] = avg_prof
    
    return {
        "skills": list(skills.values()),
        "total_skills": len(skills)
    }

@app.get("/api/v1/task-types")
async def list_task_types():
    """List supported task types"""
    task_types = []
    
    for task_type in TaskType:
        # Find workers that support this task type
        supporting_workers = 0
        for worker in worker_manager.registry.workers.values():
            for capability in worker.capabilities:
                if task_type in capability.supported_task_types:
                    supporting_workers += 1
                    break
        
        task_types.append({
            "name": task_type.value,
            "supporting_workers": supporting_workers,
            "description": get_task_type_description(task_type)
        })
    
    return {
        "task_types": task_types
    }

@app.post("/api/v1/workers/{worker_id}/command")
async def send_worker_command(worker_id: str, command: WorkerCommand):
    """Send command to specific worker"""
    if worker_id not in worker_manager.registry.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Process command (simplified implementation)
    if command.command_type == "pause":
        # Mark worker as paused (would implement actual pause logic)
        worker = worker_manager.registry.workers[worker_id]
        worker.status = "paused"
        command.status = "completed"
    elif command.command_type == "resume":
        worker = worker_manager.registry.workers[worker_id]
        worker.status = "idle" if worker.current_task_count == 0 else "busy"
        command.status = "completed"
    elif command.command_type == "restart":
        # Restart worker (would implement actual restart logic)
        command.status = "completed"
    else:
        command.status = "failed"
        raise HTTPException(status_code=400, detail="Unknown command type")
    
    return {
        "command_id": command.command_id,
        "status": command.status,
        "message": f"Command {command.command_type} executed on worker {worker_id}"
    }

@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get summary of all worker metrics"""
    all_metrics = await worker_manager.get_all_metrics()
    
    summary = {
        "total_workers": len(worker_manager.registry.workers),
        "total_tasks_completed": sum(m.total_tasks_completed for m in all_metrics.values()),
        "total_tasks_failed": sum(m.total_tasks_failed for m in all_metrics.values()),
        "average_success_rate": 0.0,
        "average_execution_time_ms": 0.0,
        "constitutional_compliance_rate": 0.0,
        "workers": all_metrics
    }
    
    if all_metrics:
        summary["average_success_rate"] = sum(m.success_rate for m in all_metrics.values()) / len(all_metrics)
        summary["average_execution_time_ms"] = sum(m.average_execution_time_ms for m in all_metrics.values()) / len(all_metrics)
        summary["constitutional_compliance_rate"] = sum(m.constitutional_compliance_rate for m in all_metrics.values()) / len(all_metrics)
    
    return summary

def get_task_type_description(task_type: TaskType) -> str:
    """Get description for task type"""
    descriptions = {
        TaskType.DATA_ANALYSIS: "Analyze and extract insights from data",
        TaskType.POLICY_EVALUATION: "Evaluate policies for compliance and effectiveness",
        TaskType.COMPUTATION: "Perform computational and mathematical operations",
        TaskType.VALIDATION: "Validate data integrity and compliance",
        TaskType.TRANSFORMATION: "Transform data from one format to another",
        TaskType.AGGREGATION: "Aggregate and summarize data",
        TaskType.MONITORING: "Monitor system performance and health",
        TaskType.REPORTING: "Generate reports and documentation"
    }
    return descriptions.get(task_type, "Unknown task type")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8009))
    uvicorn.run(app, host="0.0.0.0", port=port)