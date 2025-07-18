"""
Worker Agents Services
Constitutional Hash: cdd01ef066bc6cf2

Core business logic for worker agent management including task execution,
load balancing, skill development, and performance optimization.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import random
import logging
import json
from asyncio import Queue, Lock
import uuid

from .models import (
    WorkerProfile, WorkerType, TaskType, ExecutionStatus,
    TaskExecution, TaskRequest, TaskResult, WorkerMetrics,
    WorkerPool, LoadBalancingStrategy, ScalingPolicy,
    TaskQueue, HealthStatus, WorkerCommand, Skill,
    SkillLevel, ResourceRequirement, ResourceType,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Execute tasks on worker agents"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.current_executions: Dict[str, TaskExecution] = {}
        self.execution_history: List[TaskExecution] = []
        self.resource_monitor = ResourceMonitor()
        
    async def execute_task(
        self,
        task_request: TaskRequest
    ) -> TaskExecution:
        """Execute a single task"""
        
        # Create execution record
        execution = TaskExecution(
            task_id=task_request.request_id,
            worker_id=self.worker_id,
            task_type=task_request.task_type,
            status=ExecutionStatus.STARTING,
            constitutional_validation=task_request.constitutional_validation_required
        )
        
        self.current_executions[execution.execution_id] = execution
        
        try:
            # Validate constitutional compliance
            if task_request.constitutional_validation_required:
                if not await self._validate_constitutional_compliance(task_request):
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = "Constitutional validation failed"
                    return execution
                execution.constitutional_validation = True
            
            # Start execution
            execution.start_time = datetime.utcnow()
            execution.status = ExecutionStatus.RUNNING
            
            # Execute based on task type
            result = await self._execute_by_type(task_request, execution)
            
            # Complete execution
            execution.end_time = datetime.utcnow()
            execution.duration_seconds = (
                execution.end_time - execution.start_time
            ).total_seconds()
            execution.results = result
            execution.status = ExecutionStatus.COMPLETED
            execution.progress_percentage = 100.0
            
            logger.info(
                f"Task {execution.task_id} completed in "
                f"{execution.duration_seconds:.2f}s"
            )
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
            
            # Retry logic
            if execution.retry_count < execution.max_retries:
                execution.retry_count += 1
                logger.warning(
                    f"Task {execution.task_id} failed, retry {execution.retry_count}"
                )
                await asyncio.sleep(2 ** execution.retry_count)  # Exponential backoff
                return await self.execute_task(task_request)
            
            logger.error(f"Task {execution.task_id} failed: {e}")
        
        finally:
            # Move to history
            if execution.execution_id in self.current_executions:
                del self.current_executions[execution.execution_id]
            self.execution_history.append(execution)
            
            # Keep history limited
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
        
        return execution
    
    async def _validate_constitutional_compliance(
        self,
        task_request: TaskRequest
    ) -> bool:
        """Validate task against constitutional requirements"""
        
        # Check constitutional hash in context
        if task_request.context.get("constitutional_hash") != CONSTITUTIONAL_HASH:
            return False
        
        # Validate performance requirements
        if "performance_requirements" in task_request.payload:
            perf_reqs = task_request.payload["performance_requirements"]
            
            # Check latency requirement
            if perf_reqs.get("max_latency_ms", float('inf')) < 5.0:
                return False  # Must allow at least 5ms for constitutional requirement
            
            # Check throughput requirement
            if perf_reqs.get("min_throughput", 0) > 100:
                # Validate we can meet throughput requirement
                pass
        
        # Check for prohibited operations
        prohibited_operations = [
            "data_deletion_without_backup",
            "unauthorized_access",
            "security_bypass",
            "constitutional_override"
        ]
        
        task_operations = task_request.payload.get("operations", [])
        if any(op in prohibited_operations for op in task_operations):
            return False
        
        return True
    
    async def _execute_by_type(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute task based on its type"""
        
        if task_request.task_type == TaskType.DATA_ANALYSIS:
            return await self._execute_data_analysis(task_request, execution)
        elif task_request.task_type == TaskType.POLICY_EVALUATION:
            return await self._execute_policy_evaluation(task_request, execution)
        elif task_request.task_type == TaskType.COMPUTATION:
            return await self._execute_computation(task_request, execution)
        elif task_request.task_type == TaskType.VALIDATION:
            return await self._execute_validation(task_request, execution)
        elif task_request.task_type == TaskType.TRANSFORMATION:
            return await self._execute_transformation(task_request, execution)
        elif task_request.task_type == TaskType.AGGREGATION:
            return await self._execute_aggregation(task_request, execution)
        elif task_request.task_type == TaskType.MONITORING:
            return await self._execute_monitoring(task_request, execution)
        elif task_request.task_type == TaskType.REPORTING:
            return await self._execute_reporting(task_request, execution)
        else:
            raise ValueError(f"Unknown task type: {task_request.task_type}")
    
    async def _execute_data_analysis(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute data analysis task"""
        data = task_request.payload.get("data", [])
        analysis_type = task_request.payload.get("analysis_type", "summary")
        
        # Simulate processing time based on data size
        processing_time = min(len(data) * 0.001, 2.0)  # Max 2 seconds
        await asyncio.sleep(processing_time)
        
        # Update progress
        execution.progress_percentage = 50.0
        
        # Perform analysis
        if analysis_type == "summary":
            result = {
                "type": "summary",
                "record_count": len(data),
                "fields": list(data[0].keys()) if data else [],
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        elif analysis_type == "aggregation":
            result = {
                "type": "aggregation",
                "total_records": len(data),
                "aggregations": {
                    "count": len(data),
                    "groups": {}
                },
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        else:
            result = {
                "type": "custom",
                "analysis_type": analysis_type,
                "processed_records": len(data),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
        
        execution.progress_percentage = 100.0
        return result
    
    async def _execute_policy_evaluation(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute policy evaluation task"""
        policy = task_request.payload.get("policy", {})
        context = task_request.payload.get("context", {})
        
        # Simulate policy evaluation
        await asyncio.sleep(0.5)
        execution.progress_percentage = 25.0
        
        # Check constitutional compliance
        constitutional_score = 1.0
        if policy.get("constitutional_hash") != CONSTITUTIONAL_HASH:
            constitutional_score = 0.0
        
        execution.progress_percentage = 50.0
        
        # Evaluate policy effectiveness
        effectiveness_score = random.uniform(0.7, 0.95)
        
        execution.progress_percentage = 75.0
        
        # Generate recommendations
        recommendations = [
            "Maintain current constitutional compliance",
            "Monitor performance metrics continuously",
            "Consider policy optimization opportunities"
        ]
        
        execution.progress_percentage = 100.0
        
        return {
            "policy_id": policy.get("id", "unknown"),
            "constitutional_compliance": constitutional_score,
            "effectiveness_score": effectiveness_score,
            "recommendations": recommendations,
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def _execute_computation(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute computational task"""
        computation_type = task_request.payload.get("type", "general")
        parameters = task_request.payload.get("parameters", {})
        
        # Simulate computation
        complexity = parameters.get("complexity", 1)
        processing_time = min(complexity * 0.1, 3.0)  # Max 3 seconds
        
        steps = 10
        for i in range(steps):
            await asyncio.sleep(processing_time / steps)
            execution.progress_percentage = ((i + 1) / steps) * 100
        
        # Generate computational result
        result = {
            "computation_type": computation_type,
            "parameters": parameters,
            "result": {
                "value": random.uniform(0, 1000),
                "confidence": random.uniform(0.8, 0.99),
                "iterations": complexity * 100
            },
            "computational_cost": processing_time,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        return result
    
    async def _execute_validation(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute validation task"""
        validation_type = task_request.payload.get("type", "data")
        subject = task_request.payload.get("subject", {})
        
        await asyncio.sleep(0.3)
        execution.progress_percentage = 30.0
        
        # Perform validation
        is_valid = True
        validation_errors = []
        
        # Constitutional validation
        if subject.get("constitutional_hash") != CONSTITUTIONAL_HASH:
            is_valid = False
            validation_errors.append("Invalid constitutional hash")
        
        execution.progress_percentage = 70.0
        
        # Data validation
        if validation_type == "data" and "data" in subject:
            data = subject["data"]
            if not isinstance(data, (list, dict)):
                is_valid = False
                validation_errors.append("Invalid data format")
        
        execution.progress_percentage = 100.0
        
        return {
            "validation_type": validation_type,
            "is_valid": is_valid,
            "errors": validation_errors,
            "validation_score": 1.0 if is_valid else 0.0,
            "validated_at": datetime.utcnow().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def _execute_transformation(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute data transformation task"""
        source_data = task_request.payload.get("source_data", [])
        transformation_rules = task_request.payload.get("rules", [])
        
        execution.progress_percentage = 10.0
        
        # Apply transformations
        transformed_data = []
        total_records = len(source_data)
        
        for i, record in enumerate(source_data):
            # Apply transformation rules
            transformed_record = record.copy()
            
            for rule in transformation_rules:
                if rule.get("type") == "field_mapping":
                    old_field = rule.get("from")
                    new_field = rule.get("to")
                    if old_field in transformed_record:
                        transformed_record[new_field] = transformed_record.pop(old_field)
                elif rule.get("type") == "value_transformation":
                    field = rule.get("field")
                    if field in transformed_record:
                        # Apply transformation (simplified)
                        if rule.get("operation") == "uppercase":
                            transformed_record[field] = str(transformed_record[field]).upper()
            
            transformed_data.append(transformed_record)
            
            # Update progress
            execution.progress_percentage = 10.0 + (i / total_records) * 80.0
            
            if i % 100 == 0:  # Yield control periodically
                await asyncio.sleep(0.001)
        
        execution.progress_percentage = 95.0
        
        # Add constitutional hash to each record
        for record in transformed_data:
            record["constitutional_hash"] = CONSTITUTIONAL_HASH
        
        execution.progress_percentage = 100.0
        
        return {
            "source_record_count": len(source_data),
            "transformed_record_count": len(transformed_data),
            "transformation_rules_applied": len(transformation_rules),
            "transformed_data": transformed_data,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def _execute_aggregation(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute data aggregation task"""
        data = task_request.payload.get("data", [])
        group_by = task_request.payload.get("group_by", [])
        aggregations = task_request.payload.get("aggregations", [])
        
        execution.progress_percentage = 20.0
        
        # Group data
        groups = defaultdict(list)
        for record in data:
            group_key = tuple(record.get(field, None) for field in group_by)
            groups[group_key].append(record)
        
        execution.progress_percentage = 60.0
        
        # Calculate aggregations
        result_groups = {}
        for group_key, group_records in groups.items():
            group_result = {}
            
            for agg in aggregations:
                field = agg.get("field")
                operation = agg.get("operation", "count")
                
                if operation == "count":
                    group_result[f"{field}_count"] = len(group_records)
                elif operation == "sum" and field:
                    values = [r.get(field, 0) for r in group_records if isinstance(r.get(field), (int, float))]
                    group_result[f"{field}_sum"] = sum(values)
                elif operation == "avg" and field:
                    values = [r.get(field, 0) for r in group_records if isinstance(r.get(field), (int, float))]
                    group_result[f"{field}_avg"] = sum(values) / len(values) if values else 0
            
            result_groups[str(group_key)] = group_result
        
        execution.progress_percentage = 100.0
        
        return {
            "total_records": len(data),
            "group_count": len(groups),
            "group_by_fields": group_by,
            "aggregations": result_groups,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def _execute_monitoring(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute monitoring task"""
        target = task_request.payload.get("target", {})
        metrics = task_request.payload.get("metrics", [])
        duration = task_request.payload.get("duration_seconds", 30)
        
        # Simulate monitoring
        monitoring_data = []
        samples = min(duration, 10)  # Max 10 samples
        
        for i in range(samples):
            sample = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {}
            }
            
            for metric in metrics:
                if metric == "cpu_usage":
                    sample["metrics"]["cpu_usage"] = random.uniform(10, 90)
                elif metric == "memory_usage":
                    sample["metrics"]["memory_usage"] = random.uniform(30, 80)
                elif metric == "response_time":
                    sample["metrics"]["response_time"] = random.uniform(1, 50)
                elif metric == "throughput":
                    sample["metrics"]["throughput"] = random.uniform(50, 200)
            
            monitoring_data.append(sample)
            execution.progress_percentage = ((i + 1) / samples) * 100
            
            await asyncio.sleep(0.1)  # Brief interval between samples
        
        return {
            "target": target,
            "monitoring_duration": duration,
            "sample_count": len(monitoring_data),
            "data": monitoring_data,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def _execute_reporting(
        self,
        task_request: TaskRequest,
        execution: TaskExecution
    ) -> Dict[str, Any]:
        """Execute reporting task"""
        report_type = task_request.payload.get("type", "summary")
        data_sources = task_request.payload.get("data_sources", [])
        format_type = task_request.payload.get("format", "json")
        
        execution.progress_percentage = 25.0
        
        # Generate report content
        report_content = {
            "report_id": str(uuid.uuid4()),
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "data_sources": data_sources,
            "summary": {
                "total_data_sources": len(data_sources),
                "report_format": format_type,
                "constitutional_compliance": True
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        execution.progress_percentage = 75.0
        
        # Add detailed sections based on report type
        if report_type == "performance":
            report_content["performance_metrics"] = {
                "avg_response_time": random.uniform(1, 10),
                "throughput": random.uniform(100, 500),
                "error_rate": random.uniform(0, 0.05),
                "constitutional_compliance_rate": random.uniform(0.95, 1.0)
            }
        elif report_type == "constitutional":
            report_content["constitutional_analysis"] = {
                "compliance_score": random.uniform(0.95, 1.0),
                "violations_detected": 0,
                "recommendations": [
                    "Maintain current compliance standards",
                    "Continue regular monitoring"
                ]
            }
        
        execution.progress_percentage = 100.0
        
        return report_content

class ResourceMonitor:
    """Monitor and manage worker resources"""
    
    def __init__(self):
        self.resource_usage: Dict[str, float] = {}
        self.usage_history: List[Dict[str, Any]] = []
        
    async def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        # Simulate resource monitoring
        usage = {
            "cpu": random.uniform(10, 80),
            "memory": random.uniform(20, 70),
            "disk": random.uniform(5, 50),
            "network": random.uniform(0, 100)
        }
        
        self.resource_usage = usage
        self.usage_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "usage": usage.copy()
        })
        
        # Keep history limited
        if len(self.usage_history) > 100:
            self.usage_history = self.usage_history[-100:]
        
        return usage

class WorkerRegistry:
    """Registry for managing worker agents"""
    
    def __init__(self):
        self.workers: Dict[str, WorkerProfile] = {}
        self.worker_health: Dict[str, HealthStatus] = {}
        self.worker_executors: Dict[str, TaskExecutor] = {}
        self.skill_index: Dict[str, List[str]] = defaultdict(list)
        
    async def register_worker(self, worker: WorkerProfile) -> bool:
        """Register a new worker"""
        if worker.worker_id in self.workers:
            logger.warning(f"Worker {worker.worker_id} already registered")
            return False
        
        self.workers[worker.worker_id] = worker
        self.worker_executors[worker.worker_id] = TaskExecutor(worker.worker_id)
        
        # Index skills
        for skill in worker.skills:
            self.skill_index[skill.name].append(worker.worker_id)
        
        # Initialize health status
        self.worker_health[worker.worker_id] = HealthStatus(
            worker_id=worker.worker_id,
            is_healthy=True
        )
        
        logger.info(f"Registered worker {worker.worker_id} ({worker.worker_type})")
        return True
    
    async def find_workers_by_skill(
        self,
        skill_name: str,
        min_level: SkillLevel = SkillLevel.NOVICE
    ) -> List[WorkerProfile]:
        """Find workers with specific skill"""
        worker_ids = self.skill_index.get(skill_name, [])
        qualified_workers = []
        
        for worker_id in worker_ids:
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                for skill in worker.skills:
                    if skill.name == skill_name:
                        # Check skill level meets minimum
                        level_order = [e.value for e in SkillLevel]
                        if level_order.index(skill.level.value) >= level_order.index(min_level.value):
                            qualified_workers.append(worker)
                        break
        
        return qualified_workers
    
    async def get_available_workers(
        self,
        worker_type: Optional[WorkerType] = None
    ) -> List[WorkerProfile]:
        """Get available workers"""
        available = []
        
        for worker in self.workers.values():
            if worker.current_task_count < worker.max_concurrent_tasks:
                if worker_type is None or worker.worker_type == worker_type:
                    health = self.worker_health.get(worker.worker_id)
                    if health and health.is_healthy:
                        available.append(worker)
        
        return available

class LoadBalancer:
    """Load balancer for distributing tasks among workers"""
    
    def __init__(self, registry: WorkerRegistry):
        self.registry = registry
        self.strategy = "least_loaded"  # round_robin, least_loaded, weighted
        self.round_robin_index = 0
        
    async def select_worker(
        self,
        task_request: TaskRequest,
        required_skills: List[str] = None
    ) -> Optional[WorkerProfile]:
        """Select best worker for task"""
        
        # Get candidates
        candidates = await self._get_candidates(task_request, required_skills)
        
        if not candidates:
            return None
        
        # Apply selection strategy
        if self.strategy == "round_robin":
            return self._round_robin_selection(candidates)
        elif self.strategy == "least_loaded":
            return self._least_loaded_selection(candidates)
        elif self.strategy == "weighted":
            return self._weighted_selection(candidates)
        else:
            return candidates[0]
    
    async def _get_candidates(
        self,
        task_request: TaskRequest,
        required_skills: List[str]
    ) -> List[WorkerProfile]:
        """Get candidate workers for task"""
        candidates = await self.registry.get_available_workers()
        
        # Filter by required skills
        if required_skills:
            qualified_candidates = []
            for candidate in candidates:
                worker_skills = {skill.name for skill in candidate.skills}
                if all(skill in worker_skills for skill in required_skills):
                    qualified_candidates.append(candidate)
            candidates = qualified_candidates
        
        # Filter by task type capability
        capable_candidates = []
        for candidate in candidates:
            for capability in candidate.capabilities:
                if task_request.task_type in capability.supported_task_types:
                    capable_candidates.append(candidate)
                    break
        
        return capable_candidates
    
    def _round_robin_selection(self, candidates: List[WorkerProfile]) -> WorkerProfile:
        """Round-robin worker selection"""
        if not candidates:
            return None
        
        selected = candidates[self.round_robin_index % len(candidates)]
        self.round_robin_index += 1
        return selected
    
    def _least_loaded_selection(self, candidates: List[WorkerProfile]) -> WorkerProfile:
        """Select worker with least load"""
        return min(candidates, key=lambda w: w.current_task_count)
    
    def _weighted_selection(self, candidates: List[WorkerProfile]) -> WorkerProfile:
        """Weighted selection based on performance"""
        if not candidates:
            return None
        
        # Calculate weights based on performance and availability
        weights = []
        for worker in candidates:
            load_factor = 1.0 - (worker.current_task_count / worker.max_concurrent_tasks)
            
            # Average skill proficiency
            if worker.skills:
                skill_factor = sum(skill.proficiency_score for skill in worker.skills) / len(worker.skills)
            else:
                skill_factor = 0.5
            
            weight = load_factor * 0.7 + skill_factor * 0.3
            weights.append(weight)
        
        # Select based on weights
        total_weight = sum(weights)
        if total_weight == 0:
            return candidates[0]
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return candidates[i]
        
        return candidates[-1]

class WorkerManager:
    """Main manager for worker agents"""
    
    def __init__(self):
        self.registry = WorkerRegistry()
        self.load_balancer = LoadBalancer(self.registry)
        self.task_queue: Queue[TaskRequest] = Queue()
        self.result_queue: Queue[TaskResult] = Queue()
        self.metrics: Dict[str, WorkerMetrics] = {}
        self.processing_tasks = {}
        
    async def submit_task(self, task_request: TaskRequest) -> str:
        """Submit task for execution"""
        await self.task_queue.put(task_request)
        return task_request.request_id
    
    async def process_tasks(self):
        """Process tasks from queue"""
        while True:
            try:
                # Get task from queue
                task_request = await self.task_queue.get()
                
                # Select worker
                worker = await self.load_balancer.select_worker(task_request)
                
                if not worker:
                    # No available workers, put back in queue
                    await asyncio.sleep(1)
                    await self.task_queue.put(task_request)
                    continue
                
                # Execute task
                executor = self.registry.worker_executors[worker.worker_id]
                asyncio.create_task(self._execute_and_track(executor, task_request, worker))
                
            except Exception as e:
                logger.error(f"Task processing error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_and_track(
        self,
        executor: TaskExecutor,
        task_request: TaskRequest,
        worker: WorkerProfile
    ):
        """Execute task and track results"""
        try:
            # Update worker load
            worker.current_task_count += 1
            
            # Execute task
            execution = await executor.execute_task(task_request)
            
            # Create result
            result = TaskResult(
                execution_id=execution.execution_id,
                task_id=execution.task_id,
                worker_id=worker.worker_id,
                status=execution.status,
                results=execution.results,
                performance_metrics={
                    "execution_time_ms": (execution.duration_seconds or 0) * 1000,
                    "constitutional_compliance": execution.constitutional_validation
                },
                constitutional_compliance=execution.constitutional_validation,
                execution_time_ms=(execution.duration_seconds or 0) * 1000
            )
            
            # Put result in queue
            await self.result_queue.put(result)
            
            # Update metrics
            await self._update_worker_metrics(worker.worker_id, execution)
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
        
        finally:
            # Decrease worker load
            worker.current_task_count = max(0, worker.current_task_count - 1)
    
    async def _update_worker_metrics(
        self,
        worker_id: str,
        execution: TaskExecution
    ):
        """Update worker performance metrics"""
        if worker_id not in self.metrics:
            self.metrics[worker_id] = WorkerMetrics(worker_id=worker_id)
        
        metrics = self.metrics[worker_id]
        
        if execution.status == ExecutionStatus.COMPLETED:
            metrics.total_tasks_completed += 1
            
            # Update execution time
            if execution.duration_seconds:
                exec_time_ms = execution.duration_seconds * 1000
                if metrics.average_execution_time_ms == 0:
                    metrics.average_execution_time_ms = exec_time_ms
                else:
                    # Moving average
                    metrics.average_execution_time_ms = (
                        metrics.average_execution_time_ms * 0.9 + exec_time_ms * 0.1
                    )
                
                # Update P95 latency (simplified)
                if exec_time_ms > metrics.p95_latency_ms:
                    metrics.p95_latency_ms = exec_time_ms * 0.95 + metrics.p95_latency_ms * 0.05
        else:
            metrics.total_tasks_failed += 1
        
        # Update success rate
        total_tasks = metrics.total_tasks_completed + metrics.total_tasks_failed
        if total_tasks > 0:
            metrics.success_rate = metrics.total_tasks_completed / total_tasks
        
        # Update constitutional compliance rate
        if execution.constitutional_validation:
            # This would be calculated properly based on all executions
            metrics.constitutional_compliance_rate = min(1.0, metrics.constitutional_compliance_rate + 0.01)
    
    async def get_worker_metrics(self, worker_id: str) -> Optional[WorkerMetrics]:
        """Get metrics for specific worker"""
        return self.metrics.get(worker_id)
    
    async def get_all_metrics(self) -> Dict[str, WorkerMetrics]:
        """Get metrics for all workers"""
        return self.metrics.copy()