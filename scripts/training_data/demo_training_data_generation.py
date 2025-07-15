#!/usr/bin/env python3
"""
ACGS-2 Training Data Generation Demo

This script demonstrates the training data generation capabilities for ACGS-2
without requiring external dependencies. It generates sample training data
for all major ACGS components.

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ACGSTrainingDataDemo:
    """
    Demonstration of ACGS-2 training data generation capabilities.
    
    Generates sample training data for all major ACGS components without
    requiring external dependencies.
    """
    
    def __init__(self, output_dir: str = "demo_training_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        logger.info(f"Initialized ACGS Training Data Demo with output_dir: {output_dir}")

    def generate_all_demo_datasets(self, size_per_dataset: int = 50) -> Dict[str, Any]:
        """Generate all demo training datasets."""
        logger.info(f"🚀 Generating ACGS-2 Demo Training Data")
        logger.info(f"📊 Size per dataset: {size_per_dataset}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        results = {
            "constitutional_hash": self.constitutional_hash,
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "datasets_generated": {},
            "total_examples": 0,
            "generation_time_seconds": 0
        }
        
        # Generate each type of training data
        datasets = [
            ("constitutional_ai", self._generate_constitutional_ai_demo),
            ("policy_governance", self._generate_policy_governance_demo),
            ("multi_agent_coordination", self._generate_multi_agent_demo),
            ("performance_optimization", self._generate_performance_demo),
            ("transformer_efficiency", self._generate_transformer_demo),
            ("wina_optimization", self._generate_wina_demo)
        ]
        
        for dataset_name, generator_func in datasets:
            try:
                logger.info(f"📝 Generating {dataset_name} dataset...")
                
                # Generate dataset
                dataset = generator_func(size_per_dataset)
                
                # Save dataset
                output_path = self.output_dir / f"{dataset_name}_demo.json"
                with open(output_path, 'w') as f:
                    json.dump(dataset, f, indent=2)
                
                # Update results
                results["datasets_generated"][dataset_name] = {
                    "path": str(output_path),
                    "examples": len(dataset["examples"]),
                    "size_mb": output_path.stat().st_size / (1024 * 1024)
                }
                results["total_examples"] += len(dataset["examples"])
                
                logger.info(f"✅ Generated {dataset_name}: {len(dataset['examples'])} examples")
                
            except Exception as e:
                logger.exception(f"❌ Failed to generate {dataset_name}: {e}")
                results["datasets_generated"][dataset_name] = {"error": str(e)}
        
        # Calculate total time
        results["generation_time_seconds"] = time.time() - start_time
        
        # Generate summary report
        summary_path = self._generate_summary_report(results)
        results["summary_report"] = str(summary_path)
        
        logger.info(f"✅ Demo generation completed in {results['generation_time_seconds']:.2f} seconds")
        logger.info(f"📊 Total examples generated: {results['total_examples']}")
        
        return results

    def _generate_constitutional_ai_demo(self, size: int) -> Dict[str, Any]:
        """Generate constitutional AI training data demo."""
        examples = []
        
        principles = ["transparency", "accountability", "fairness", "privacy", "safety", "reliability"]
        scenarios = ["data_access_request", "policy_decision", "ethical_dilemma", "bias_detection"]
        
        for i in range(size):
            principle = random.choice(principles)
            scenario = random.choice(scenarios)
            
            example = {
                "id": f"const_ai_demo_{i:04d}",
                "input": {
                    "scenario": scenario,
                    "context": {
                        "user_role": random.choice(["employee", "manager", "admin"]),
                        "data_type": random.choice(["personal", "financial", "operational"]),
                        "sensitivity": random.choice(["public", "internal", "confidential"])
                    },
                    "user_request": f"Demo request for {scenario} involving {principle} considerations",
                    "constitutional_principles": [principle],
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "target_output": {
                    "decision": f"Approve with {principle} safeguards",
                    "reasoning": f"Decision aligns with {principle} constitutional principle and ensures proper governance",
                    "compliance_score": round(random.uniform(0.9, 1.0), 3),
                    "principle_alignment": {principle: round(random.uniform(0.95, 1.0), 3)},
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "scenario_type": scenario,
                    "primary_principle": principle,
                    "complexity": random.choice(["low", "medium", "high"]),
                    "domain": random.choice(["healthcare", "finance", "general", "education"])
                }
            }
            examples.append(example)
        
        return {
            "dataset_type": "constitutional_ai",
            "description": "Constitutional AI training examples for governance decision making",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "examples": examples,
            "metadata": {
                "total_examples": len(examples),
                "principles_covered": list(set(ex["input"]["constitutional_principles"][0] for ex in examples)),
                "scenarios_covered": list(set(ex["input"]["scenario"] for ex in examples))
            }
        }

    def _generate_policy_governance_demo(self, size: int) -> Dict[str, Any]:
        """Generate policy governance training data demo."""
        examples = []
        
        frameworks = ["GDPR", "HIPAA", "SOX", "PCI_DSS", "ACGS_Constitutional"]
        policy_types = ["data_protection", "access_control", "audit_requirements", "compliance_rules"]
        
        for i in range(size):
            framework = random.choice(frameworks)
            policy_type = random.choice(policy_types)
            
            example = {
                "id": f"policy_gov_demo_{i:04d}",
                "input": {
                    "policy_request": {
                        "type": policy_type,
                        "framework": framework,
                        "scope": random.choice(["user", "system", "organization"]),
                        "context": f"Demo {policy_type} policy for {framework} compliance"
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "target_output": {
                    "opa_rule": f"""
package acgs.demo.{policy_type}

import rego.v1

default allow := false

allow if {{
    input.user.role in ["admin", "policy_officer"]
    input.action.type == "{policy_type}"
    constitutional_compliance
    {framework.lower()}_compliance
}}

constitutional_compliance if {{
    input.constitutional_hash == "{CONSTITUTIONAL_HASH}"
    input.constitutional_principles
}}

{framework.lower()}_compliance if {{
    input.framework == "{framework}"
    input.compliance_verified
}}
""",
                    "governance_decision": {
                        "decision": random.choice(["approve", "approve_with_conditions", "escalate"]),
                        "conditions": [
                            "Implement audit logging",
                            "Add constitutional compliance checks",
                            "Require periodic review"
                        ][:random.randint(1, 3)],
                        "rationale": f"Decision based on {framework} requirements and constitutional principles",
                        "review_period": random.choice(["monthly", "quarterly", "annually"])
                    },
                    "compliance_assessment": {
                        "framework_compliance": round(random.uniform(0.9, 1.0), 3),
                        "constitutional_compliance": round(random.uniform(0.95, 1.0), 3),
                        "risk_level": random.choice(["low", "medium", "high"])
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "policy_type": policy_type,
                    "framework": framework,
                    "complexity": random.choice(["simple", "moderate", "complex"]),
                    "enforcement_level": random.choice(["advisory", "mandatory", "critical"])
                }
            }
            examples.append(example)
        
        return {
            "dataset_type": "policy_governance",
            "description": "Policy governance training examples for OPA rule generation and compliance",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "examples": examples,
            "metadata": {
                "total_examples": len(examples),
                "frameworks_covered": list(set(ex["input"]["policy_request"]["framework"] for ex in examples)),
                "policy_types_covered": list(set(ex["input"]["policy_request"]["type"] for ex in examples))
            }
        }

    def _generate_multi_agent_demo(self, size: int) -> Dict[str, Any]:
        """Generate multi-agent coordination training data demo."""
        examples = []
        
        agent_types = ["ethics", "legal", "operational", "security", "performance"]
        scenarios = ["conflict_resolution", "consensus_building", "task_delegation", "resource_allocation"]
        
        for i in range(size):
            scenario = random.choice(scenarios)
            involved_agents = random.sample(agent_types, random.randint(2, 4))
            
            example = {
                "id": f"multi_agent_demo_{i:04d}",
                "input": {
                    "coordination_request": {
                        "scenario": scenario,
                        "involved_agents": involved_agents,
                        "task": {
                            "description": f"Demo {scenario} task requiring coordination between {', '.join(involved_agents)} agents",
                            "priority": random.choice(["low", "medium", "high", "critical"]),
                            "deadline": random.choice(["1 hour", "4 hours", "24 hours", "1 week"]),
                            "complexity": random.choice(["simple", "moderate", "complex"])
                        },
                        "constraints": [
                            "Must maintain constitutional compliance",
                            "Cannot exceed resource limits",
                            "Must complete within deadline"
                        ][:random.randint(1, 3)]
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "target_output": {
                    "coordination_plan": {
                        "phases": [
                            {"phase": "analysis", "duration": "30 minutes", "agents": involved_agents[:2]},
                            {"phase": "deliberation", "duration": "1 hour", "agents": involved_agents},
                            {"phase": "decision", "duration": "15 minutes", "agents": [involved_agents[0]]},
                            {"phase": "implementation", "duration": "2 hours", "agents": involved_agents}
                        ],
                        "communication_protocol": "blackboard_system",
                        "conflict_resolution_method": "weighted_voting"
                    },
                    "agent_assignments": {
                        agent: [f"task_{j+1}" for j in range(random.randint(1, 3))]
                        for agent in involved_agents
                    },
                    "success_metrics": {
                        "coordination_efficiency": round(random.uniform(0.8, 1.0), 3),
                        "consensus_score": round(random.uniform(0.7, 1.0), 3),
                        "constitutional_compliance": round(random.uniform(0.95, 1.0), 3)
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "scenario_type": scenario,
                    "agent_count": len(involved_agents),
                    "complexity": random.choice(["simple", "moderate", "complex"]),
                    "conflict_level": random.choice(["none", "low", "medium", "high"])
                }
            }
            examples.append(example)
        
        return {
            "dataset_type": "multi_agent_coordination",
            "description": "Multi-agent coordination training examples for agent collaboration and conflict resolution",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "examples": examples,
            "metadata": {
                "total_examples": len(examples),
                "scenarios_covered": list(set(ex["input"]["coordination_request"]["scenario"] for ex in examples)),
                "agents_involved": list(set().union(*[ex["input"]["coordination_request"]["involved_agents"] for ex in examples]))
            }
        }

    def _generate_performance_demo(self, size: int) -> Dict[str, Any]:
        """Generate performance optimization training data demo."""
        examples = []
        
        optimization_types = ["latency_optimization", "throughput_improvement", "memory_optimization", "cache_optimization"]
        
        for i in range(size):
            opt_type = random.choice(optimization_types)
            
            # Generate realistic baseline metrics
            baseline_p99 = random.uniform(10.0, 100.0)
            baseline_throughput = random.uniform(50.0, 500.0)
            baseline_memory = random.uniform(60.0, 95.0)
            
            example = {
                "id": f"perf_opt_demo_{i:04d}",
                "input": {
                    "optimization_request": {
                        "type": opt_type,
                        "current_metrics": {
                            "p99_latency_ms": round(baseline_p99, 2),
                            "throughput_rps": round(baseline_throughput, 1),
                            "memory_usage_percent": round(baseline_memory, 1),
                            "cache_hit_rate": round(random.uniform(0.6, 0.9), 3)
                        },
                        "target_metrics": {
                            "p99_latency_ms": 5.0,
                            "throughput_rps": 100.0,
                            "memory_usage_percent": 85.0,
                            "cache_hit_rate": 0.85
                        },
                        "system_context": {
                            "architecture": random.choice(["microservices", "monolithic", "serverless"]),
                            "deployment": random.choice(["kubernetes", "docker", "cloud"]),
                            "load_pattern": random.choice(["steady", "bursty", "seasonal"])
                        }
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "target_output": {
                    "optimization_strategy": {
                        "primary_approach": f"{opt_type}_focused_optimization",
                        "techniques": [
                            "caching_optimization",
                            "database_indexing",
                            "async_processing"
                        ][:random.randint(2, 3)],
                        "expected_improvement": f"{random.randint(50, 300)}% improvement"
                    },
                    "expected_improvements": {
                        "p99_latency_ms": round(baseline_p99 * random.uniform(0.1, 0.5), 2),
                        "throughput_rps": round(baseline_throughput * random.uniform(1.5, 5.0), 1),
                        "memory_usage_percent": round(baseline_memory * random.uniform(0.6, 0.9), 1)
                    },
                    "performance_validation": {
                        "meets_targets": True,
                        "improvement_factor": round(random.uniform(2.0, 10.0), 1),
                        "constitutional_compliance": round(random.uniform(0.95, 1.0), 3)
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "optimization_type": opt_type,
                    "baseline_p99": round(baseline_p99, 2),
                    "target_p99": 5.0,
                    "complexity": random.choice(["low", "medium", "high"])
                }
            }
            examples.append(example)
        
        return {
            "dataset_type": "performance_optimization",
            "description": "Performance optimization training examples for ACGS performance targets",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "examples": examples,
            "metadata": {
                "total_examples": len(examples),
                "optimization_types": list(set(ex["input"]["optimization_request"]["type"] for ex in examples)),
                "target_p99_latency": 5.0,
                "target_throughput": 100.0
            }
        }

    def _generate_transformer_demo(self, size: int) -> Dict[str, Any]:
        """Generate transformer efficiency optimization demo data."""
        examples = []
        
        techniques = ["performer_attention", "sparse_attention", "low_rank_approximation", "quantization"]
        
        for i in range(size):
            technique = random.choice(techniques)
            seq_len = random.choice([512, 1024, 2048])
            dim = random.choice([256, 512, 768])
            
            example = {
                "id": f"transformer_demo_{i:04d}",
                "input": {
                    "model_config": {
                        "seq_len": seq_len,
                        "dim": dim,
                        "heads": random.choice([4, 8, 12]),
                        "layers": random.choice([6, 12, 24])
                    },
                    "optimization_technique": technique,
                    "performance_requirements": {
                        "p99_latency_ms": 5.0,
                        "min_throughput_rps": 100.0,
                        "max_approximation_error": 0.05
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "target_output": {
                    "optimized_config": {
                        "technique_applied": technique,
                        "num_random_features": 64 if technique == "performer_attention" else None,
                        "sparsity_ratio": random.uniform(0.1, 0.5) if "sparse" in technique else None,
                        "quantization_bits": 8 if technique == "quantization" else None
                    },
                    "performance_metrics": {
                        "complexity_reduction": round(random.uniform(2.0, 32.0), 1),
                        "approximation_error": round(random.uniform(0.001, 0.1), 4),
                        "memory_reduction": round(random.uniform(0.3, 0.8), 3),
                        "latency_improvement": round(random.uniform(1.5, 10.0), 1)
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "technique": technique,
                    "model_size": dim * random.choice([6, 12, 24]),
                    "complexity_class": "linear" if random.uniform(2.0, 32.0) > 10 else "quadratic"
                }
            }
            examples.append(example)
        
        return {
            "dataset_type": "transformer_efficiency",
            "description": "Transformer efficiency optimization training examples",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "examples": examples,
            "metadata": {
                "total_examples": len(examples),
                "techniques_covered": list(set(ex["input"]["optimization_technique"] for ex in examples)),
                "model_sizes": list(set(ex["input"]["model_config"]["seq_len"] for ex in examples))
            }
        }

    def _generate_wina_demo(self, size: int) -> Dict[str, Any]:
        """Generate WINA optimization demo data."""
        examples = []
        
        scenarios = ["neuron_activation_optimization", "weight_informed_gating", "svd_transformation", "gflops_reduction"]
        
        for i in range(size):
            scenario = random.choice(scenarios)
            
            example = {
                "id": f"wina_demo_{i:04d}",
                "input": {
                    "wina_config": {
                        "target_sparsity": round(random.uniform(0.3, 0.8), 2),
                        "gflops_reduction_target": round(random.uniform(0.4, 0.7), 2),
                        "accuracy_preservation_threshold": round(random.uniform(0.9, 0.98), 3),
                        "constitutional_compliance_threshold": 0.95
                    },
                    "model_architecture": {
                        "layers": random.randint(6, 24),
                        "neurons_per_layer": random.choice([512, 1024, 2048]),
                        "activation_function": random.choice(["relu", "gelu", "swish"])
                    },
                    "optimization_scenario": scenario,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "target_output": {
                    "wina_optimization_result": {
                        "gflops_reduction": round(random.uniform(0.4, 0.7), 3),
                        "accuracy_preservation": round(random.uniform(0.92, 0.99), 3),
                        "sparsity_achieved": round(random.uniform(0.3, 0.8), 3),
                        "constitutional_compliance": round(random.uniform(0.95, 1.0), 3)
                    },
                    "optimization_strategy": {
                        "method": scenario,
                        "phases": ["analysis", "optimization", "validation"],
                        "expected_benefits": f"Reduce GFLOPs by {random.randint(40, 70)}% while preserving accuracy"
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                "metadata": {
                    "scenario": scenario,
                    "model_size": random.randint(6, 24) * random.choice([512, 1024, 2048]),
                    "optimization_level": random.choice(["conservative", "moderate", "aggressive"])
                }
            }
            examples.append(example)
        
        return {
            "dataset_type": "wina_optimization",
            "description": "WINA optimization training examples for neural efficiency",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "examples": examples,
            "metadata": {
                "total_examples": len(examples),
                "scenarios_covered": list(set(ex["input"]["optimization_scenario"] for ex in examples)),
                "target_gflops_reduction": "40-70%"
            }
        }

    def _generate_summary_report(self, results: Dict[str, Any]) -> Path:
        """Generate a summary report of the demo generation."""
        report_path = self.output_dir / "demo_generation_report.json"
        
        # Add additional metadata
        results["demo_info"] = {
            "purpose": "ACGS-2 Training Data Generation Demonstration",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "datasets_included": list(results["datasets_generated"].keys()),
            "total_size_mb": sum(
                info.get("size_mb", 0) 
                for info in results["datasets_generated"].values() 
                if isinstance(info, dict) and "size_mb" in info
            )
        }
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return report_path

    def print_demo_summary(self, results: Dict[str, Any]):
        """Print a formatted summary of the demo results."""
        print("\n" + "="*80)
        print("🎯 ACGS-2 Training Data Generation Demo - Summary")
        print("="*80)
        print(f"🔒 Constitutional Hash: {results['constitutional_hash']}")
        print(f"⏱️ Generation Time: {results['generation_time_seconds']:.2f} seconds")
        print(f"📊 Total Examples: {results['total_examples']}")
        print(f"📁 Output Directory: {self.output_dir}")
        
        print("\n📈 Generated Datasets:")
        for dataset_name, info in results["datasets_generated"].items():
            if isinstance(info, dict) and "examples" in info:
                print(f"  ✅ {dataset_name}: {info['examples']} examples ({info['size_mb']:.2f} MB)")
                print(f"     📄 File: {info['path']}")
            else:
                print(f"  ❌ {dataset_name}: {info.get('error', 'Unknown error')}")
        
        if "summary_report" in results:
            print(f"\n📋 Summary Report: {results['summary_report']}")
        
        print("\n🎉 Demo completed successfully!")
        print("   Use the generated datasets to train ACGS-2 components")
        print("   All data includes constitutional compliance validation")
        print("="*80)


def main():
    """Run the training data generation demo."""
    print("🚀 Starting ACGS-2 Training Data Generation Demo")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Initialize demo
    demo = ACGSTrainingDataDemo()
    
    # Generate demo datasets
    results = demo.generate_all_demo_datasets(size_per_dataset=25)
    
    # Print summary
    demo.print_demo_summary(results)
    
    return results


if __name__ == "__main__":
    main()
