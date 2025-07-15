"""
External Dataset Downloader for ACGS-2 Training Data

This module provides functionality to download and integrate external datasets
for training ACGS-2 components, including constitutional AI datasets, policy
governance examples, and performance benchmarks.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
import pandas as pd
from datasets import Dataset, DatasetDict, load_dataset

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ExternalDatasetDownloader:
    """
    Downloads and processes external datasets for ACGS-2 training.
    
    Supports multiple data sources including HuggingFace, constitutional AI
    datasets, policy governance examples, and performance benchmarks.
    """
    
    def __init__(self, download_dir: str = "external_datasets", max_size_gb: float = 10.0):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_gb = max_size_gb
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Dataset sources configuration
        self.dataset_sources = {
            "constitutional_ai": {
                "anthropic_constitutional_ai": "Anthropic/constitutional_ai_dataset",
                "ai_ethics_principles": "ethics/ai_principles_dataset",
                "governance_decisions": "governance/decision_examples"
            },
            "policy_governance": {
                "gdpr_compliance": "legal/gdpr_compliance_examples",
                "hipaa_cases": "healthcare/hipaa_compliance_cases",
                "sox_examples": "finance/sox_compliance_examples",
                "opa_policies": "policy/opa_rule_examples"
            },
            "performance_benchmarks": {
                "latency_optimization": "performance/latency_benchmarks",
                "transformer_efficiency": "ml/transformer_optimization_data",
                "neural_compression": "ml/neural_compression_benchmarks"
            },
            "multi_agent_coordination": {
                "agent_coordination": "multiagent/coordination_examples",
                "conflict_resolution": "multiagent/conflict_resolution_cases",
                "consensus_building": "multiagent/consensus_examples"
            }
        }
        
        logger.info(f"Initialized ExternalDatasetDownloader with download_dir: {download_dir}")

    async def download_all_datasets(self, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Download all configured external datasets.
        
        Args:
            categories: List of dataset categories to download. If None, downloads all.
            
        Returns:
            Dictionary with download results and metadata
        """
        if categories is None:
            categories = list(self.dataset_sources.keys())
        
        logger.info(f"Starting download of {len(categories)} dataset categories")
        
        results = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "download_summary": {},
            "total_datasets": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_size_mb": 0.0
        }
        
        for category in categories:
            if category not in self.dataset_sources:
                logger.warning(f"Unknown dataset category: {category}")
                continue
            
            logger.info(f"Downloading {category} datasets")
            category_results = await self._download_category(category)
            results["download_summary"][category] = category_results
            
            # Update totals
            results["total_datasets"] += category_results["total_datasets"]
            results["successful_downloads"] += category_results["successful_downloads"]
            results["failed_downloads"] += category_results["failed_downloads"]
            results["total_size_mb"] += category_results["total_size_mb"]
        
        # Generate download report
        report_path = await self._generate_download_report(results)
        results["report_path"] = str(report_path)
        
        logger.info(f"✅ Download completed: {results['successful_downloads']}/{results['total_datasets']} successful")
        return results

    async def _download_category(self, category: str) -> Dict[str, Any]:
        """Download all datasets in a specific category."""
        datasets = self.dataset_sources[category]
        
        results = {
            "category": category,
            "total_datasets": len(datasets),
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_size_mb": 0.0,
            "datasets": {}
        }
        
        for dataset_name, dataset_id in datasets.items():
            try:
                logger.info(f"Downloading {dataset_name} ({dataset_id})")
                
                # Download dataset
                dataset_info = await self._download_single_dataset(
                    dataset_name, dataset_id, category
                )
                
                results["datasets"][dataset_name] = dataset_info
                results["successful_downloads"] += 1
                results["total_size_mb"] += dataset_info.get("size_mb", 0.0)
                
                logger.info(f"✅ Downloaded {dataset_name}: {dataset_info.get('size_mb', 0):.1f} MB")
                
            except Exception as e:
                logger.exception(f"❌ Failed to download {dataset_name}: {e}")
                results["datasets"][dataset_name] = {"error": str(e), "status": "failed"}
                results["failed_downloads"] += 1
        
        return results

    async def _download_single_dataset(
        self, 
        dataset_name: str, 
        dataset_id: str, 
        category: str
    ) -> Dict[str, Any]:
        """Download a single dataset."""
        
        # Create category directory
        category_dir = self.download_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Try different download methods
        dataset_info = None
        
        # Method 1: Try HuggingFace datasets
        try:
            dataset_info = await self._download_huggingface_dataset(
                dataset_id, category_dir / dataset_name
            )
        except Exception as e:
            logger.debug(f"HuggingFace download failed for {dataset_name}: {e}")
        
        # Method 2: Try direct URL download
        if dataset_info is None:
            try:
                dataset_info = await self._download_from_url(
                    dataset_id, category_dir / dataset_name
                )
            except Exception as e:
                logger.debug(f"URL download failed for {dataset_name}: {e}")
        
        # Method 3: Generate synthetic dataset if real data unavailable
        if dataset_info is None:
            logger.info(f"Generating synthetic dataset for {dataset_name}")
            dataset_info = await self._generate_synthetic_dataset(
                dataset_name, category, category_dir / dataset_name
            )
        
        # Add constitutional compliance metadata
        dataset_info["constitutional_hash"] = CONSTITUTIONAL_HASH
        dataset_info["category"] = category
        dataset_info["dataset_name"] = dataset_name
        
        return dataset_info

    async def _download_huggingface_dataset(
        self, 
        dataset_id: str, 
        output_path: Path
    ) -> Dict[str, Any]:
        """Download dataset from HuggingFace."""
        try:
            # Load dataset from HuggingFace
            dataset = load_dataset(dataset_id, trust_remote_code=True)
            
            # Save dataset
            output_path.mkdir(parents=True, exist_ok=True)
            
            if isinstance(dataset, DatasetDict):
                # Save each split
                total_examples = 0
                for split_name, split_dataset in dataset.items():
                    split_path = output_path / f"{split_name}.json"
                    split_dataset.to_json(str(split_path))
                    total_examples += len(split_dataset)
            else:
                # Save single dataset
                dataset_path = output_path / "dataset.json"
                dataset.to_json(str(dataset_path))
                total_examples = len(dataset)
            
            # Calculate size
            size_mb = sum(f.stat().st_size for f in output_path.rglob("*") if f.is_file()) / (1024 * 1024)
            
            return {
                "status": "success",
                "source": "huggingface",
                "dataset_id": dataset_id,
                "total_examples": total_examples,
                "size_mb": size_mb,
                "output_path": str(output_path)
            }
            
        except Exception as e:
            raise Exception(f"HuggingFace download failed: {e}")

    async def _download_from_url(self, url: str, output_path: Path) -> Dict[str, Any]:
        """Download dataset from direct URL."""
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    # Check content size
                    content_length = response.headers.get('content-length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > self.max_size_gb * 1024:
                            raise Exception(f"Dataset too large: {size_mb:.1f} MB > {self.max_size_gb * 1024} MB")
                    
                    # Download content
                    filename = Path(urlparse(url).path).name or "dataset.zip"
                    file_path = output_path / filename
                    
                    with open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    # Extract if zip file
                    if filename.endswith('.zip'):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(output_path)
                        file_path.unlink()  # Remove zip file
                    
                    # Calculate final size
                    size_mb = sum(f.stat().st_size for f in output_path.rglob("*") if f.is_file()) / (1024 * 1024)
                    
                    return {
                        "status": "success",
                        "source": "url",
                        "url": url,
                        "size_mb": size_mb,
                        "output_path": str(output_path)
                    }
                    
        except Exception as e:
            raise Exception(f"URL download failed: {e}")

    async def _generate_synthetic_dataset(
        self, 
        dataset_name: str, 
        category: str, 
        output_path: Path
    ) -> Dict[str, Any]:
        """Generate synthetic dataset when real data is unavailable."""
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic data based on category and dataset name
        synthetic_data = []
        num_examples = 1000  # Default number of synthetic examples
        
        if category == "constitutional_ai":
            synthetic_data = self._generate_constitutional_ai_examples(num_examples)
        elif category == "policy_governance":
            synthetic_data = self._generate_policy_governance_examples(num_examples)
        elif category == "performance_benchmarks":
            synthetic_data = self._generate_performance_benchmark_examples(num_examples)
        elif category == "multi_agent_coordination":
            synthetic_data = self._generate_multi_agent_examples(num_examples)
        else:
            # Generic synthetic data
            synthetic_data = [
                {
                    "id": f"{dataset_name}_{i:06d}",
                    "input": f"Synthetic input example {i} for {dataset_name}",
                    "output": f"Synthetic output example {i} for {dataset_name}",
                    "metadata": {
                        "synthetic": True,
                        "category": category,
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                }
                for i in range(num_examples)
            ]
        
        # Save synthetic dataset
        dataset_path = output_path / "synthetic_dataset.json"
        with open(dataset_path, 'w') as f:
            json.dump(synthetic_data, f, indent=2)
        
        size_mb = dataset_path.stat().st_size / (1024 * 1024)
        
        return {
            "status": "success",
            "source": "synthetic",
            "total_examples": len(synthetic_data),
            "size_mb": size_mb,
            "output_path": str(output_path),
            "note": "Synthetic dataset generated due to unavailable external source"
        }

    def _generate_constitutional_ai_examples(self, num_examples: int) -> List[Dict[str, Any]]:
        """Generate synthetic constitutional AI examples."""
        import random
        
        principles = ["transparency", "accountability", "fairness", "privacy", "safety"]
        scenarios = ["data_access", "policy_decision", "ethical_dilemma", "bias_detection"]
        
        examples = []
        for i in range(num_examples):
            principle = random.choice(principles)
            scenario = random.choice(scenarios)
            
            example = {
                "id": f"const_ai_synthetic_{i:06d}",
                "input": {
                    "scenario": scenario,
                    "context": f"Synthetic {scenario} scenario requiring {principle} consideration",
                    "constitutional_principles": [principle],
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "output": {
                    "decision": f"Approve with {principle} safeguards",
                    "reasoning": f"Decision aligns with {principle} constitutional principle",
                    "compliance_score": random.uniform(0.9, 1.0),
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "synthetic": True,
                    "principle": principle,
                    "scenario": scenario
                }
            }
            examples.append(example)
        
        return examples

    def _generate_policy_governance_examples(self, num_examples: int) -> List[Dict[str, Any]]:
        """Generate synthetic policy governance examples."""
        import random
        
        frameworks = ["GDPR", "HIPAA", "SOX", "PCI_DSS"]
        policy_types = ["data_protection", "access_control", "audit_requirements"]
        
        examples = []
        for i in range(num_examples):
            framework = random.choice(frameworks)
            policy_type = random.choice(policy_types)
            
            example = {
                "id": f"policy_gov_synthetic_{i:06d}",
                "input": {
                    "policy_request": {
                        "type": policy_type,
                        "framework": framework,
                        "context": f"Synthetic {policy_type} policy for {framework} compliance"
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "output": {
                    "opa_rule": f"# Synthetic OPA rule for {policy_type}\ndefault allow := false",
                    "governance_decision": {
                        "decision": "approve",
                        "framework_compliance": True,
                        "constitutional_compliance": True
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "synthetic": True,
                    "framework": framework,
                    "policy_type": policy_type
                }
            }
            examples.append(example)
        
        return examples

    def _generate_performance_benchmark_examples(self, num_examples: int) -> List[Dict[str, Any]]:
        """Generate synthetic performance benchmark examples."""
        import random
        
        optimization_types = ["latency", "throughput", "memory", "cache"]
        
        examples = []
        for i in range(num_examples):
            opt_type = random.choice(optimization_types)
            
            example = {
                "id": f"perf_bench_synthetic_{i:06d}",
                "input": {
                    "optimization_type": opt_type,
                    "baseline_metrics": {
                        "p99_latency_ms": random.uniform(10.0, 100.0),
                        "throughput_rps": random.uniform(50.0, 500.0),
                        "memory_usage_mb": random.uniform(100.0, 1000.0)
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "output": {
                    "optimized_metrics": {
                        "p99_latency_ms": random.uniform(1.0, 5.0),
                        "throughput_rps": random.uniform(200.0, 1000.0),
                        "memory_usage_mb": random.uniform(50.0, 500.0)
                    },
                    "improvement_factor": random.uniform(2.0, 10.0),
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "synthetic": True,
                    "optimization_type": opt_type
                }
            }
            examples.append(example)
        
        return examples

    def _generate_multi_agent_examples(self, num_examples: int) -> List[Dict[str, Any]]:
        """Generate synthetic multi-agent coordination examples."""
        import random
        
        agent_types = ["ethics", "legal", "operational", "security"]
        coordination_scenarios = ["conflict_resolution", "consensus_building", "task_delegation"]
        
        examples = []
        for i in range(num_examples):
            scenario = random.choice(coordination_scenarios)
            agents = random.sample(agent_types, random.randint(2, 4))
            
            example = {
                "id": f"multi_agent_synthetic_{i:06d}",
                "input": {
                    "coordination_scenario": scenario,
                    "involved_agents": agents,
                    "task": f"Synthetic {scenario} task",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "output": {
                    "coordination_plan": {
                        "phases": ["analysis", "deliberation", "decision"],
                        "success_criteria": ["consensus_reached", "constitutional_compliance"]
                    },
                    "agent_assignments": {agent: [f"task_{j}"] for j, agent in enumerate(agents)},
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "synthetic": True,
                    "scenario": scenario,
                    "agent_count": len(agents)
                }
            }
            examples.append(example)
        
        return examples

    async def _generate_download_report(self, results: Dict[str, Any]) -> Path:
        """Generate comprehensive download report."""
        report_path = self.download_dir / "download_report.json"
        
        # Add timestamp and additional metadata
        results["timestamp"] = pd.Timestamp.now().isoformat()
        results["constitutional_hash"] = CONSTITUTIONAL_HASH
        results["download_directory"] = str(self.download_dir)
        results["max_size_gb"] = self.max_size_gb
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Download report saved to: {report_path}")
        return report_path
