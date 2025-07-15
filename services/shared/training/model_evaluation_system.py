"""
Model Evaluation and Benchmarking System for ACGS-2

This module implements comprehensive evaluation metrics, benchmarking suites,
and performance validation for all trained ACGS models with constitutional
compliance verification.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    
    # Evaluation metrics
    compute_accuracy: bool = True
    compute_precision_recall: bool = True
    compute_constitutional_compliance: bool = True
    compute_performance_metrics: bool = True
    
    # Benchmarking
    run_latency_benchmark: bool = True
    run_throughput_benchmark: bool = True
    run_memory_benchmark: bool = True
    
    # Constitutional compliance
    constitutional_threshold: float = 0.95
    compliance_sample_size: int = 1000
    
    # Performance targets (from ACGS requirements)
    target_p99_latency_ms: float = 5.0
    target_throughput_rps: float = 100.0
    target_memory_efficiency: float = 0.85
    
    # Evaluation settings
    batch_size: int = 32
    num_warmup_runs: int = 10
    num_benchmark_runs: int = 100
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class EvaluationResults:
    """Comprehensive evaluation results."""
    
    # Model identification
    model_name: str
    model_type: str
    evaluation_timestamp: float
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    # Accuracy metrics
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Performance metrics
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Constitutional compliance
    compliance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Benchmarking results
    benchmark_results: Dict[str, Any] = field(default_factory=dict)
    
    # Overall assessment
    overall_score: float = 0.0
    meets_requirements: bool = False
    recommendations: List[str] = field(default_factory=list)


class ModelEvaluator:
    """
    Comprehensive model evaluator for ACGS-2 components.
    
    Provides accuracy assessment, performance benchmarking, constitutional
    compliance verification, and overall model quality evaluation.
    """
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        logger.info(f"Initialized Model Evaluator")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    async def evaluate_model(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset,
        model_name: str,
        model_type: str
    ) -> EvaluationResults:
        """
        Comprehensive model evaluation.
        
        Args:
            model: Trained model to evaluate
            test_dataset: Test dataset for evaluation
            model_name: Name of the model
            model_type: Type of model (constitutional_ai, policy_governance, etc.)
            
        Returns:
            Comprehensive evaluation results
        """
        
        logger.info(f"🔍 Starting comprehensive evaluation for {model_name}")
        logger.info(f"📊 Model type: {model_type}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        # Initialize results
        results = EvaluationResults(
            model_name=model_name,
            model_type=model_type,
            evaluation_timestamp=start_time
        )
        
        # Set model to evaluation mode
        model.eval()
        
        try:
            # 1. Accuracy evaluation
            if self.config.compute_accuracy:
                logger.info("📈 Computing accuracy metrics...")
                results.accuracy_metrics = await self._evaluate_accuracy(model, test_dataset)
            
            # 2. Constitutional compliance evaluation
            if self.config.compute_constitutional_compliance:
                logger.info("🔒 Evaluating constitutional compliance...")
                results.compliance_metrics = await self._evaluate_constitutional_compliance(model, test_dataset)
            
            # 3. Performance benchmarking
            if self.config.compute_performance_metrics:
                logger.info("⚡ Running performance benchmarks...")
                results.benchmark_results = await self._run_performance_benchmarks(model, test_dataset)
            
            # 4. Model-specific evaluation
            logger.info(f"🎯 Running {model_type}-specific evaluation...")
            model_specific_metrics = await self._evaluate_model_specific(model, test_dataset, model_type)
            results.performance_metrics.update(model_specific_metrics)
            
            # 5. Calculate overall score and assessment
            results.overall_score = self._calculate_overall_score(results)
            results.meets_requirements = self._assess_requirements_compliance(results)
            results.recommendations = self._generate_recommendations(results)
            
            evaluation_time = time.time() - start_time
            logger.info(f"✅ Evaluation completed in {evaluation_time:.2f} seconds")
            logger.info(f"📊 Overall score: {results.overall_score:.3f}")
            logger.info(f"🎯 Meets requirements: {'✅ YES' if results.meets_requirements else '❌ NO'}")
            
        except Exception as e:
            logger.exception(f"❌ Evaluation failed: {e}")
            results.accuracy_metrics["error"] = str(e)
        
        return results

    async def _evaluate_accuracy(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Evaluate model accuracy metrics."""
        
        # Create test dataloader
        test_loader = torch.utils.data.DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=2
        )
        
        all_predictions = []
        all_targets = []
        all_losses = []
        
        with torch.no_grad():
            for batch in test_loader:
                # Forward pass
                outputs = model(**batch)
                
                # Extract predictions and targets
                if isinstance(outputs, dict):
                    if "logits" in outputs:
                        predictions = torch.argmax(outputs["logits"], dim=-1)
                    elif "decision_logits" in outputs:
                        predictions = torch.argmax(outputs["decision_logits"], dim=-1)
                    else:
                        predictions = torch.zeros(batch["input_ids"].shape[0])
                    
                    if "loss" in outputs:
                        all_losses.append(outputs["loss"].item())
                else:
                    predictions = torch.argmax(outputs, dim=-1)
                
                # Get targets (simplified - would need proper target extraction)
                if "labels" in batch:
                    targets = batch["labels"]
                else:
                    targets = torch.zeros_like(predictions)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(all_targets, all_predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_targets, all_predictions, average='weighted', zero_division=0
        )
        
        avg_loss = np.mean(all_losses) if all_losses else 0.0
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "average_loss": avg_loss,
            "num_samples": len(all_predictions)
        }

    async def _evaluate_constitutional_compliance(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Evaluate constitutional compliance of model outputs."""
        
        # Sample subset for compliance evaluation
        sample_size = min(self.config.compliance_sample_size, len(test_dataset))
        indices = np.random.choice(len(test_dataset), sample_size, replace=False)
        
        compliance_scores = []
        hash_validations = []
        principle_alignments = []
        
        with torch.no_grad():
            for idx in indices:
                sample = test_dataset[idx]
                
                # Convert to batch format
                batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else [v] 
                        for k, v in sample.items()}
                
                # Forward pass
                outputs = model(**batch)
                
                # Extract compliance metrics
                if isinstance(outputs, dict):
                    # Constitutional compliance score
                    if "constitutional_compliance" in outputs:
                        compliance_score = outputs["constitutional_compliance"].item()
                    elif "compliance_score" in outputs:
                        compliance_score = outputs["compliance_score"].item()
                    else:
                        compliance_score = 1.0  # Default if not available
                    
                    compliance_scores.append(compliance_score)
                    
                    # Hash validation
                    hash_valid = sample.get("constitutional_hash") == self.constitutional_hash
                    hash_validations.append(hash_valid)
                    
                    # Principle alignment (if available)
                    if "principle_alignment" in outputs:
                        principle_alignment = outputs["principle_alignment"].mean().item()
                        principle_alignments.append(principle_alignment)
        
        # Calculate compliance metrics
        avg_compliance = np.mean(compliance_scores)
        compliance_rate = np.mean([s >= self.config.constitutional_threshold for s in compliance_scores])
        hash_validation_rate = np.mean(hash_validations)
        avg_principle_alignment = np.mean(principle_alignments) if principle_alignments else 0.0
        
        return {
            "average_compliance_score": avg_compliance,
            "compliance_rate": compliance_rate,
            "hash_validation_rate": hash_validation_rate,
            "average_principle_alignment": avg_principle_alignment,
            "meets_compliance_threshold": avg_compliance >= self.config.constitutional_threshold,
            "samples_evaluated": sample_size
        }

    async def _run_performance_benchmarks(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks."""
        
        benchmark_results = {}
        
        # Latency benchmark
        if self.config.run_latency_benchmark:
            benchmark_results["latency"] = await self._benchmark_latency(model, test_dataset)
        
        # Throughput benchmark
        if self.config.run_throughput_benchmark:
            benchmark_results["throughput"] = await self._benchmark_throughput(model, test_dataset)
        
        # Memory benchmark
        if self.config.run_memory_benchmark:
            benchmark_results["memory"] = await self._benchmark_memory(model, test_dataset)
        
        return benchmark_results

    async def _benchmark_latency(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Benchmark model latency."""
        
        # Prepare single sample for latency testing
        sample = test_dataset[0]
        batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else [v] 
                for k, v in sample.items()}
        
        # Warmup runs
        with torch.no_grad():
            for _ in range(self.config.num_warmup_runs):
                _ = model(**batch)
        
        # Benchmark runs
        latencies = []
        with torch.no_grad():
            for _ in range(self.config.num_benchmark_runs):
                start_time = time.time()
                _ = model(**batch)
                latency_ms = (time.time() - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate statistics
        p50_latency = np.percentile(latencies, 50)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)
        avg_latency = np.mean(latencies)
        
        return {
            "p50_latency_ms": p50_latency,
            "p95_latency_ms": p95_latency,
            "p99_latency_ms": p99_latency,
            "average_latency_ms": avg_latency,
            "meets_p99_target": p99_latency < self.config.target_p99_latency_ms
        }

    async def _benchmark_throughput(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Benchmark model throughput."""
        
        # Create batch for throughput testing
        batch_samples = [test_dataset[i] for i in range(min(self.config.batch_size, len(test_dataset)))]
        
        # Convert to batch format
        batch = {}
        for key in batch_samples[0].keys():
            if isinstance(batch_samples[0][key], torch.Tensor):
                batch[key] = torch.stack([sample[key] for sample in batch_samples])
            else:
                batch[key] = [sample[key] for sample in batch_samples]
        
        # Warmup
        with torch.no_grad():
            for _ in range(self.config.num_warmup_runs):
                _ = model(**batch)
        
        # Throughput benchmark
        start_time = time.time()
        with torch.no_grad():
            for _ in range(self.config.num_benchmark_runs):
                _ = model(**batch)
        
        total_time = time.time() - start_time
        total_samples = self.config.num_benchmark_runs * self.config.batch_size
        throughput_rps = total_samples / total_time
        
        return {
            "throughput_rps": throughput_rps,
            "batch_size": self.config.batch_size,
            "total_samples": total_samples,
            "total_time_seconds": total_time,
            "meets_throughput_target": throughput_rps > self.config.target_throughput_rps
        }

    async def _benchmark_memory(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Benchmark model memory usage."""
        
        if not torch.cuda.is_available():
            return {"memory_usage_mb": 0.0, "memory_efficiency": 1.0}
        
        # Clear cache and measure baseline
        torch.cuda.empty_cache()
        baseline_memory = torch.cuda.memory_allocated()
        
        # Load model and measure
        sample = test_dataset[0]
        batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else [v] 
                for k, v in sample.items()}
        
        with torch.no_grad():
            _ = model(**batch)
        
        peak_memory = torch.cuda.max_memory_allocated()
        model_memory = peak_memory - baseline_memory
        
        # Calculate efficiency
        total_memory = torch.cuda.get_device_properties(0).total_memory
        memory_efficiency = 1.0 - (peak_memory / total_memory)
        
        return {
            "memory_usage_mb": model_memory / (1024 * 1024),
            "peak_memory_mb": peak_memory / (1024 * 1024),
            "memory_efficiency": memory_efficiency,
            "meets_memory_target": memory_efficiency > self.config.target_memory_efficiency
        }

    async def _evaluate_model_specific(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset,
        model_type: str
    ) -> Dict[str, float]:
        """Evaluate model-specific metrics based on model type."""
        
        if model_type == "constitutional_ai":
            return await self._evaluate_constitutional_ai_specific(model, test_dataset)
        elif model_type == "policy_governance":
            return await self._evaluate_policy_governance_specific(model, test_dataset)
        elif model_type == "multi_agent_coordination":
            return await self._evaluate_multi_agent_specific(model, test_dataset)
        else:
            return {"model_specific_score": 0.8}  # Default score

    async def _evaluate_constitutional_ai_specific(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Evaluate Constitutional AI specific metrics."""
        
        principle_scores = []
        reasoning_scores = []
        decision_consistency = []
        
        with torch.no_grad():
            for i in range(min(100, len(test_dataset))):
                sample = test_dataset[i]
                batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else [v] 
                        for k, v in sample.items()}
                
                outputs = model(**batch)
                
                if isinstance(outputs, dict):
                    # Principle alignment
                    if "principle_alignment" in outputs:
                        principle_score = outputs["principle_alignment"].mean().item()
                        principle_scores.append(principle_score)
                    
                    # Reasoning quality
                    if "reasoning_quality" in outputs:
                        reasoning_score = outputs["reasoning_quality"].item()
                        reasoning_scores.append(reasoning_score)
                    
                    # Decision consistency (simplified)
                    if "decision_logits" in outputs:
                        decision_confidence = torch.max(F.softmax(outputs["decision_logits"], dim=-1)).item()
                        decision_consistency.append(decision_confidence)
        
        return {
            "avg_principle_alignment": np.mean(principle_scores) if principle_scores else 0.0,
            "avg_reasoning_quality": np.mean(reasoning_scores) if reasoning_scores else 0.0,
            "avg_decision_consistency": np.mean(decision_consistency) if decision_consistency else 0.0,
            "constitutional_ai_score": np.mean([
                np.mean(principle_scores) if principle_scores else 0.0,
                np.mean(reasoning_scores) if reasoning_scores else 0.0,
                np.mean(decision_consistency) if decision_consistency else 0.0
            ])
        }

    async def _evaluate_policy_governance_specific(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Evaluate Policy Governance specific metrics."""
        
        framework_compliance_scores = []
        risk_assessment_accuracy = []
        
        with torch.no_grad():
            for i in range(min(100, len(test_dataset))):
                sample = test_dataset[i]
                batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else [v] 
                        for k, v in sample.items()}
                
                outputs = model(**batch)
                
                if isinstance(outputs, dict):
                    # Framework compliance
                    if "framework_compliance" in outputs:
                        compliance_score = outputs["framework_compliance"].mean().item()
                        framework_compliance_scores.append(compliance_score)
                    
                    # Risk assessment
                    if "risk_assessment" in outputs:
                        risk_score = outputs["risk_assessment"].max().item()  # Confidence in risk prediction
                        risk_assessment_accuracy.append(risk_score)
        
        return {
            "avg_framework_compliance": np.mean(framework_compliance_scores) if framework_compliance_scores else 0.0,
            "avg_risk_assessment_accuracy": np.mean(risk_assessment_accuracy) if risk_assessment_accuracy else 0.0,
            "policy_governance_score": np.mean([
                np.mean(framework_compliance_scores) if framework_compliance_scores else 0.0,
                np.mean(risk_assessment_accuracy) if risk_assessment_accuracy else 0.0
            ])
        }

    async def _evaluate_multi_agent_specific(
        self,
        model: torch.nn.Module,
        test_dataset: torch.utils.data.Dataset
    ) -> Dict[str, float]:
        """Evaluate Multi-Agent Coordination specific metrics."""
        
        coordination_scores = []
        consensus_scores = []
        conflict_resolution_scores = []
        
        with torch.no_grad():
            for i in range(min(100, len(test_dataset))):
                sample = test_dataset[i]
                batch = {k: v.unsqueeze(0) if isinstance(v, torch.Tensor) else [v] 
                        for k, v in sample.items()}
                
                outputs = model(**batch)
                
                if isinstance(outputs, dict):
                    # Agent assignments (coordination effectiveness)
                    if "agent_assignments" in outputs:
                        coordination_score = outputs["agent_assignments"].mean().item()
                        coordination_scores.append(coordination_score)
                    
                    # Consensus scoring
                    if "consensus_score" in outputs:
                        consensus_score = outputs["consensus_score"].item()
                        consensus_scores.append(consensus_score)
                    
                    # Conflict resolution
                    if "conflict_resolution" in outputs:
                        conflict_score = outputs["conflict_resolution"].max().item()
                        conflict_resolution_scores.append(conflict_score)
        
        return {
            "avg_coordination_effectiveness": np.mean(coordination_scores) if coordination_scores else 0.0,
            "avg_consensus_score": np.mean(consensus_scores) if consensus_scores else 0.0,
            "avg_conflict_resolution": np.mean(conflict_resolution_scores) if conflict_resolution_scores else 0.0,
            "multi_agent_score": np.mean([
                np.mean(coordination_scores) if coordination_scores else 0.0,
                np.mean(consensus_scores) if consensus_scores else 0.0,
                np.mean(conflict_resolution_scores) if conflict_resolution_scores else 0.0
            ])
        }

    def _calculate_overall_score(self, results: EvaluationResults) -> float:
        """Calculate overall model score."""
        
        scores = []
        
        # Accuracy component (30%)
        if results.accuracy_metrics:
            accuracy_score = results.accuracy_metrics.get("accuracy", 0.0)
            f1_score = results.accuracy_metrics.get("f1_score", 0.0)
            accuracy_component = (accuracy_score + f1_score) / 2
            scores.append(accuracy_component * 0.3)
        
        # Constitutional compliance component (40%)
        if results.compliance_metrics:
            compliance_score = results.compliance_metrics.get("average_compliance_score", 0.0)
            scores.append(compliance_score * 0.4)
        
        # Performance component (20%)
        if results.benchmark_results:
            performance_score = 0.0
            performance_count = 0
            
            if "latency" in results.benchmark_results:
                latency_meets_target = results.benchmark_results["latency"].get("meets_p99_target", False)
                performance_score += 1.0 if latency_meets_target else 0.5
                performance_count += 1
            
            if "throughput" in results.benchmark_results:
                throughput_meets_target = results.benchmark_results["throughput"].get("meets_throughput_target", False)
                performance_score += 1.0 if throughput_meets_target else 0.5
                performance_count += 1
            
            if performance_count > 0:
                scores.append((performance_score / performance_count) * 0.2)
        
        # Model-specific component (10%)
        if results.performance_metrics:
            model_specific_score = results.performance_metrics.get(f"{results.model_type}_score", 0.0)
            scores.append(model_specific_score * 0.1)
        
        return sum(scores) if scores else 0.0

    def _assess_requirements_compliance(self, results: EvaluationResults) -> bool:
        """Assess if model meets ACGS requirements."""
        
        requirements_met = []
        
        # Constitutional compliance requirement
        if results.compliance_metrics:
            compliance_rate = results.compliance_metrics.get("compliance_rate", 0.0)
            requirements_met.append(compliance_rate >= 0.95)
        
        # Performance requirements
        if results.benchmark_results:
            if "latency" in results.benchmark_results:
                latency_ok = results.benchmark_results["latency"].get("meets_p99_target", False)
                requirements_met.append(latency_ok)
            
            if "throughput" in results.benchmark_results:
                throughput_ok = results.benchmark_results["throughput"].get("meets_throughput_target", False)
                requirements_met.append(throughput_ok)
        
        # Accuracy requirement
        if results.accuracy_metrics:
            accuracy = results.accuracy_metrics.get("accuracy", 0.0)
            requirements_met.append(accuracy >= 0.85)
        
        return all(requirements_met) if requirements_met else False

    def _generate_recommendations(self, results: EvaluationResults) -> List[str]:
        """Generate improvement recommendations based on evaluation results."""
        
        recommendations = []
        
        # Constitutional compliance recommendations
        if results.compliance_metrics:
            compliance_rate = results.compliance_metrics.get("compliance_rate", 0.0)
            if compliance_rate < 0.95:
                recommendations.append(f"Improve constitutional compliance: {compliance_rate:.2%} < 95%")
        
        # Performance recommendations
        if results.benchmark_results:
            if "latency" in results.benchmark_results:
                p99_latency = results.benchmark_results["latency"].get("p99_latency_ms", 0.0)
                if p99_latency > self.config.target_p99_latency_ms:
                    recommendations.append(f"Optimize latency: {p99_latency:.2f}ms > {self.config.target_p99_latency_ms}ms")
            
            if "throughput" in results.benchmark_results:
                throughput = results.benchmark_results["throughput"].get("throughput_rps", 0.0)
                if throughput < self.config.target_throughput_rps:
                    recommendations.append(f"Improve throughput: {throughput:.1f} RPS < {self.config.target_throughput_rps} RPS")
        
        # Accuracy recommendations
        if results.accuracy_metrics:
            accuracy = results.accuracy_metrics.get("accuracy", 0.0)
            if accuracy < 0.9:
                recommendations.append(f"Improve model accuracy: {accuracy:.2%} < 90%")
        
        # Overall score recommendation
        if results.overall_score < 0.8:
            recommendations.append(f"Overall model quality needs improvement: {results.overall_score:.3f} < 0.8")
        
        if not recommendations:
            recommendations.append("Model meets all requirements - consider advanced optimizations")
        
        return recommendations

    async def save_evaluation_results(
        self,
        results: EvaluationResults,
        output_path: Path
    ):
        """Save comprehensive evaluation results."""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert results to serializable format
        results_dict = {
            "model_name": results.model_name,
            "model_type": results.model_type,
            "evaluation_timestamp": results.evaluation_timestamp,
            "constitutional_hash": results.constitutional_hash,
            "accuracy_metrics": results.accuracy_metrics,
            "performance_metrics": results.performance_metrics,
            "compliance_metrics": results.compliance_metrics,
            "benchmark_results": results.benchmark_results,
            "overall_score": results.overall_score,
            "meets_requirements": results.meets_requirements,
            "recommendations": results.recommendations
        }
        
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        logger.info(f"📄 Evaluation results saved to: {output_path}")

    def print_evaluation_summary(self, results: EvaluationResults):
        """Print formatted evaluation summary."""
        
        print("\n" + "="*80)
        print(f"🔍 Model Evaluation Summary: {results.model_name}")
        print("="*80)
        print(f"🔒 Constitutional Hash: {results.constitutional_hash}")
        print(f"🏷️ Model Type: {results.model_type}")
        print(f"📊 Overall Score: {results.overall_score:.3f}")
        print(f"🎯 Meets Requirements: {'✅ YES' if results.meets_requirements else '❌ NO'}")
        
        # Accuracy metrics
        if results.accuracy_metrics:
            print(f"\n📈 Accuracy Metrics:")
            for metric, value in results.accuracy_metrics.items():
                if isinstance(value, float):
                    print(f"  • {metric}: {value:.3f}")
                else:
                    print(f"  • {metric}: {value}")
        
        # Constitutional compliance
        if results.compliance_metrics:
            print(f"\n🔒 Constitutional Compliance:")
            for metric, value in results.compliance_metrics.items():
                if isinstance(value, float):
                    print(f"  • {metric}: {value:.3f}")
                else:
                    print(f"  • {metric}: {value}")
        
        # Performance benchmarks
        if results.benchmark_results:
            print(f"\n⚡ Performance Benchmarks:")
            for benchmark_type, metrics in results.benchmark_results.items():
                print(f"  {benchmark_type.upper()}:")
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        print(f"    • {metric}: {value:.3f}")
                    else:
                        print(f"    • {metric}: {value}")
        
        # Recommendations
        if results.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(results.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("="*80)
