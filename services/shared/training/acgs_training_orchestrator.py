"""
ACGS-2 Training Orchestrator

This module orchestrates training across all ACGS-2 components, including
Constitutional AI, Policy Governance, Multi-Agent Coordination, Performance
Optimization, Transformer Efficiency, and WINA Optimization.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch

from .constitutional_ai_trainer import ConstitutionalAITrainer, ConstitutionalAIConfig
from .policy_governance_trainer import PolicyGovernanceTrainer, PolicyGovernanceConfig
from .multi_agent_trainer import MultiAgentTrainer, MultiAgentConfig

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ACGSTrainingConfig:
    """Configuration for ACGS-2 training orchestration."""
    
    # Data paths
    training_data_dir: str = "demo_training_data"
    output_models_dir: str = "trained_models"
    
    # Training components to include
    train_constitutional_ai: bool = True
    train_policy_governance: bool = True
    train_multi_agent_coordination: bool = True
    train_performance_optimization: bool = True
    train_transformer_efficiency: bool = True
    train_wina_optimization: bool = True
    
    # Training modes
    parallel_training: bool = False  # Set to True for parallel training (requires more resources)
    use_validation_split: bool = True
    validation_split_ratio: float = 0.2
    
    # Performance targets
    target_overall_accuracy: float = 0.95
    target_constitutional_compliance: float = 0.98
    max_training_time_hours: float = 24.0
    
    # Resource management
    max_gpu_memory_gb: float = 8.0
    max_cpu_cores: int = 4
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class TrainingResults:
    """Results from ACGS-2 training orchestration."""
    constitutional_hash: str = CONSTITUTIONAL_HASH
    total_training_time_seconds: float = 0.0
    successful_components: List[str] = field(default_factory=list)
    failed_components: List[str] = field(default_factory=list)
    component_results: Dict[str, Any] = field(default_factory=dict)
    overall_metrics: Dict[str, float] = field(default_factory=dict)
    model_paths: Dict[str, str] = field(default_factory=dict)


class ACGSTrainingOrchestrator:
    """
    Orchestrates training across all ACGS-2 components.
    
    Manages resource allocation, training sequencing, and result aggregation
    for comprehensive ACGS-2 system training.
    """
    
    def __init__(self, config: ACGSTrainingConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Create output directories
        self.training_data_dir = Path(config.training_data_dir)
        self.output_models_dir = Path(config.output_models_dir)
        self.output_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize component trainers
        self.trainers = {}
        self._initialize_trainers()
        
        # Training results
        self.results = TrainingResults()
        
        logger.info(f"Initialized ACGS Training Orchestrator")
        logger.info(f"📊 Training data directory: {self.training_data_dir}")
        logger.info(f"📁 Output models directory: {self.output_models_dir}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

    def _initialize_trainers(self):
        """Initialize all component trainers."""
        
        if self.config.train_constitutional_ai:
            const_ai_config = ConstitutionalAIConfig(
                batch_size=8,  # Reduced for resource management
                num_epochs=3,
                learning_rate=5e-5
            )
            self.trainers["constitutional_ai"] = ConstitutionalAITrainer(const_ai_config)
        
        if self.config.train_policy_governance:
            policy_config = PolicyGovernanceConfig(
                batch_size=6,  # Reduced for resource management
                num_epochs=4,
                learning_rate=3e-4
            )
            self.trainers["policy_governance"] = PolicyGovernanceTrainer(policy_config)
        
        if self.config.train_multi_agent_coordination:
            multi_agent_config = MultiAgentConfig(
                batch_size=8,  # Reduced for resource management
                num_epochs=3,
                learning_rate=3e-5
            )
            self.trainers["multi_agent_coordination"] = MultiAgentTrainer(multi_agent_config)
        
        # Additional trainers would be initialized here for:
        # - Performance Optimization
        # - Transformer Efficiency  
        # - WINA Optimization
        
        logger.info(f"Initialized {len(self.trainers)} component trainers")

    async def train_all_components(self) -> TrainingResults:
        """Train all ACGS-2 components."""
        
        logger.info(f"🚀 Starting ACGS-2 comprehensive training")
        logger.info(f"📊 Components to train: {list(self.trainers.keys())}")
        logger.info(f"⚡ Parallel training: {self.config.parallel_training}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        # Validate training data availability
        await self._validate_training_data()
        
        # Train components
        if self.config.parallel_training:
            await self._train_components_parallel()
        else:
            await self._train_components_sequential()
        
        # Calculate total training time
        self.results.total_training_time_seconds = time.time() - start_time
        
        # Generate overall metrics
        await self._calculate_overall_metrics()
        
        # Save training summary
        await self._save_training_summary()
        
        logger.info(f"✅ ACGS-2 training completed in {self.results.total_training_time_seconds:.2f} seconds")
        logger.info(f"📈 Successful components: {len(self.results.successful_components)}")
        logger.info(f"❌ Failed components: {len(self.results.failed_components)}")
        
        return self.results

    async def _validate_training_data(self):
        """Validate availability and quality of training data."""
        
        logger.info("🔍 Validating training data...")
        
        required_datasets = {
            "constitutional_ai": "constitutional_ai_demo.json",
            "policy_governance": "policy_governance_demo.json", 
            "multi_agent_coordination": "multi_agent_coordination_demo.json",
            "performance_optimization": "performance_optimization_demo.json",
            "transformer_efficiency": "transformer_efficiency_demo.json",
            "wina_optimization": "wina_optimization_demo.json"
        }
        
        missing_datasets = []
        for component, filename in required_datasets.items():
            dataset_path = self.training_data_dir / filename
            if not dataset_path.exists():
                missing_datasets.append(filename)
                logger.warning(f"⚠️ Missing training data: {filename}")
            else:
                # Validate constitutional compliance
                with open(dataset_path, 'r') as f:
                    data = json.load(f)
                
                if data.get("constitutional_hash") != self.constitutional_hash:
                    raise ValueError(f"Constitutional hash mismatch in {filename}")
                
                logger.info(f"✅ Validated {filename}: {len(data.get('examples', []))} examples")
        
        if missing_datasets:
            logger.warning(f"⚠️ Missing {len(missing_datasets)} datasets, but continuing with available data")

    async def _train_components_sequential(self):
        """Train components sequentially."""
        
        logger.info("🔄 Training components sequentially...")
        
        for component_name, trainer in self.trainers.items():
            try:
                logger.info(f"🎯 Training {component_name}...")
                
                # Determine data paths
                train_data_path = self._get_training_data_path(component_name)
                val_data_path = self._get_validation_data_path(component_name) if self.config.use_validation_split else None
                output_dir = self.output_models_dir / component_name
                
                # Train component
                component_start_time = time.time()
                
                if hasattr(trainer, 'train'):
                    results = await trainer.train(
                        train_data_path=str(train_data_path),
                        val_data_path=str(val_data_path) if val_data_path else None,
                        output_dir=str(output_dir)
                    )
                else:
                    # For components without async train method
                    results = await self._train_component_sync(trainer, train_data_path, val_data_path, output_dir)
                
                component_time = time.time() - component_start_time
                
                # Store results
                self.results.successful_components.append(component_name)
                self.results.component_results[component_name] = results
                self.results.model_paths[component_name] = str(output_dir)
                
                logger.info(f"✅ {component_name} training completed in {component_time:.2f} seconds")
                
                # Clear GPU memory if using CUDA
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
            except Exception as e:
                logger.exception(f"❌ Failed to train {component_name}: {e}")
                self.results.failed_components.append(component_name)
                self.results.component_results[component_name] = {"error": str(e)}

    async def _train_components_parallel(self):
        """Train components in parallel (requires more resources)."""
        
        logger.info("⚡ Training components in parallel...")
        
        # Create training tasks
        training_tasks = []
        
        for component_name, trainer in self.trainers.items():
            train_data_path = self._get_training_data_path(component_name)
            val_data_path = self._get_validation_data_path(component_name) if self.config.use_validation_split else None
            output_dir = self.output_models_dir / component_name
            
            task = asyncio.create_task(
                self._train_component_async(
                    component_name, trainer, train_data_path, val_data_path, output_dir
                )
            )
            training_tasks.append(task)
        
        # Wait for all training tasks to complete
        results = await asyncio.gather(*training_tasks, return_exceptions=True)
        
        # Process results
        for i, (component_name, result) in enumerate(zip(self.trainers.keys(), results)):
            if isinstance(result, Exception):
                logger.exception(f"❌ Failed to train {component_name}: {result}")
                self.results.failed_components.append(component_name)
                self.results.component_results[component_name] = {"error": str(result)}
            else:
                logger.info(f"✅ {component_name} training completed")
                self.results.successful_components.append(component_name)
                self.results.component_results[component_name] = result
                self.results.model_paths[component_name] = str(self.output_models_dir / component_name)

    async def _train_component_async(
        self, 
        component_name: str, 
        trainer, 
        train_data_path: Path, 
        val_data_path: Optional[Path], 
        output_dir: Path
    ) -> Dict[str, Any]:
        """Train a single component asynchronously."""
        
        try:
            if hasattr(trainer, 'train'):
                return await trainer.train(
                    train_data_path=str(train_data_path),
                    val_data_path=str(val_data_path) if val_data_path else None,
                    output_dir=str(output_dir)
                )
            else:
                return await self._train_component_sync(trainer, train_data_path, val_data_path, output_dir)
        
        except Exception as e:
            logger.exception(f"Error training {component_name}: {e}")
            raise

    async def _train_component_sync(self, trainer, train_data_path: Path, val_data_path: Optional[Path], output_dir: Path) -> Dict[str, Any]:
        """Train component with synchronous trainer (placeholder for future implementations)."""
        
        # This would be implemented for components that don't have async training yet
        # For now, return a placeholder result
        return {
            "status": "placeholder",
            "message": "Synchronous training not yet implemented",
            "constitutional_hash": self.constitutional_hash
        }

    def _get_training_data_path(self, component_name: str) -> Path:
        """Get training data path for component."""
        filename_map = {
            "constitutional_ai": "constitutional_ai_demo.json",
            "policy_governance": "policy_governance_demo.json",
            "multi_agent_coordination": "multi_agent_coordination_demo.json",
            "performance_optimization": "performance_optimization_demo.json",
            "transformer_efficiency": "transformer_efficiency_demo.json",
            "wina_optimization": "wina_optimization_demo.json"
        }
        
        filename = filename_map.get(component_name, f"{component_name}_demo.json")
        return self.training_data_dir / filename

    def _get_validation_data_path(self, component_name: str) -> Optional[Path]:
        """Get validation data path for component (if using validation split)."""
        # For now, use the same data file (trainer will handle splitting)
        # In production, you might have separate validation files
        return self._get_training_data_path(component_name)

    async def _calculate_overall_metrics(self):
        """Calculate overall training metrics across all components."""
        
        logger.info("📊 Calculating overall metrics...")
        
        # Aggregate metrics from successful components
        total_accuracy = 0.0
        total_compliance = 0.0
        total_examples = 0
        successful_count = len(self.results.successful_components)
        
        for component_name in self.results.successful_components:
            component_results = self.results.component_results[component_name]
            
            # Extract metrics (these would vary by component)
            if "compliance_results" in component_results:
                compliance_rate = component_results["compliance_results"].get("compliance_rate", 0.0)
                total_compliance += compliance_rate
            
            if "training_examples" in component_results:
                total_examples += component_results["training_examples"]
        
        # Calculate averages
        if successful_count > 0:
            avg_compliance = total_compliance / successful_count
            
            self.results.overall_metrics = {
                "overall_constitutional_compliance": avg_compliance,
                "successful_components_ratio": successful_count / len(self.trainers),
                "total_training_examples": total_examples,
                "training_time_hours": self.results.total_training_time_seconds / 3600,
                "meets_compliance_target": avg_compliance >= self.config.target_constitutional_compliance,
                "constitutional_hash": self.constitutional_hash
            }
        
        logger.info(f"📈 Overall constitutional compliance: {self.results.overall_metrics.get('overall_constitutional_compliance', 0.0):.2%}")

    async def _save_training_summary(self):
        """Save comprehensive training summary."""
        
        summary_path = self.output_models_dir / "training_summary.json"
        
        summary = {
            "acgs_training_summary": {
                "constitutional_hash": self.constitutional_hash,
                "training_config": self.config.__dict__,
                "results": {
                    "total_training_time_seconds": self.results.total_training_time_seconds,
                    "successful_components": self.results.successful_components,
                    "failed_components": self.results.failed_components,
                    "overall_metrics": self.results.overall_metrics,
                    "model_paths": self.results.model_paths
                },
                "component_details": self.results.component_results
            }
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Training summary saved to: {summary_path}")

    def print_training_summary(self):
        """Print formatted training summary."""
        
        print("\n" + "="*80)
        print("🎯 ACGS-2 Comprehensive Training Summary")
        print("="*80)
        print(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        print(f"⏱️ Total Training Time: {self.results.total_training_time_seconds:.2f} seconds ({self.results.total_training_time_seconds/3600:.2f} hours)")
        print(f"📊 Training Mode: {'Parallel' if self.config.parallel_training else 'Sequential'}")
        
        print(f"\n📈 Component Results:")
        print(f"  ✅ Successful: {len(self.results.successful_components)} components")
        for component in self.results.successful_components:
            model_path = self.results.model_paths.get(component, "N/A")
            print(f"    • {component}: {model_path}")
        
        if self.results.failed_components:
            print(f"  ❌ Failed: {len(self.results.failed_components)} components")
            for component in self.results.failed_components:
                error = self.results.component_results.get(component, {}).get("error", "Unknown error")
                print(f"    • {component}: {error}")
        
        print(f"\n🎯 Overall Metrics:")
        for metric, value in self.results.overall_metrics.items():
            if isinstance(value, float):
                if "compliance" in metric or "ratio" in metric:
                    print(f"  • {metric}: {value:.2%}")
                else:
                    print(f"  • {metric}: {value:.3f}")
            else:
                print(f"  • {metric}: {value}")
        
        print(f"\n📁 Models Directory: {self.output_models_dir}")
        print("="*80)


async def main():
    """Main function for ACGS-2 training orchestration."""
    
    # Configure training
    config = ACGSTrainingConfig(
        training_data_dir="demo_training_data",
        output_models_dir="trained_models",
        parallel_training=False,  # Set to True if you have sufficient resources
        use_validation_split=True
    )
    
    # Initialize orchestrator
    orchestrator = ACGSTrainingOrchestrator(config)
    
    # Train all components
    results = await orchestrator.train_all_components()
    
    # Print summary
    orchestrator.print_training_summary()
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
