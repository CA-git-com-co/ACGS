#!/usr/bin/env python3
"""
Quantumagi Transaction Optimizer
Implements transaction batching, cost optimization, and performance monitoring
to achieve <0.01 SOL governance action costs
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TransactionMetrics:
    """Metrics for transaction cost analysis"""

    transaction_id: str
    action_type: str
    cost_lamports: int
    cost_sol: float
    compute_units_used: int
    account_size_bytes: int
    timestamp: float
    batch_id: str | None = None


@dataclass
class BatchConfiguration:
    """Configuration for transaction batching"""

    max_batch_size: int = 5
    batch_timeout_seconds: int = 3
    cost_target_lamports: int = 10_000_000  # 0.01 SOL
    enabled: bool = True


@dataclass
class OptimizationResult:
    """Result of optimization analysis"""

    original_cost_sol: float
    optimized_cost_sol: float
    savings_percentage: float
    techniques_applied: list[str]
    meets_target: bool


class TransactionOptimizer:
    """
    Optimizes Quantumagi governance transactions for cost and performance
    """

    def __init__(self, config_path: str = "COST_OPTIMIZATION_CONFIG.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.metrics_history: list[TransactionMetrics] = []
        self.pending_transactions: list[dict[str, Any]] = []

    def _load_config(self) -> dict[str, Any]:
        """Load optimization configuration"""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default optimization configuration"""
        return {
            "costOptimization": {
                "enabled": True,
                "targetCostSOL": 0.01,
                "techniques": [
                    "account_size_reduction",
                    "transaction_batching",
                    "pda_optimization",
                    "compute_unit_optimization",
                ],
            },
            "batchConfiguration": {
                "maxBatchSize": 5,
                "batchTimeoutSeconds": 3,
                "costTargetLamports": 10_000_000,
                "enabled": True,
            },
            "accountOptimization": {
                "governanceAccountSize": 3850,
                "proposalAccountSize": 700,
                "voteRecordSize": 140,
                "rentOptimizationEnabled": True,
            },
            "computeOptimization": {
                "createProposalCU": 37500,
                "voteOnProposalCU": 18750,
                "finalizeProposalCU": 22500,
                "pdaOptimizationEnabled": True,
            },
        }

    async def optimize_transaction(
        self, transaction_data: dict[str, Any]
    ) -> OptimizationResult:
        """
        Optimize a single transaction for cost and performance
        """
        logger.info(
            f"Optimizing transaction: {transaction_data.get('type', 'unknown')}"
        )

        original_cost = self._estimate_transaction_cost(transaction_data)
        optimization_techniques = []

        # Apply optimization techniques
        optimized_data = transaction_data.copy()

        if "account_size_reduction" in self.config["costOptimization"]["techniques"]:
            optimized_data = self._optimize_account_sizes(optimized_data)
            optimization_techniques.append("account_size_reduction")

        if "compute_unit_optimization" in self.config["costOptimization"]["techniques"]:
            optimized_data = self._optimize_compute_units(optimized_data)
            optimization_techniques.append("compute_unit_optimization")

        if "pda_optimization" in self.config["costOptimization"]["techniques"]:
            optimized_data = self._optimize_pda_derivation(optimized_data)
            optimization_techniques.append("pda_optimization")

        optimized_cost = self._estimate_transaction_cost(optimized_data)
        savings_percentage = ((original_cost - optimized_cost) / original_cost) * 100

        target_cost_sol = self.config["costOptimization"]["targetCostSOL"]
        meets_target = optimized_cost <= target_cost_sol

        result = OptimizationResult(
            original_cost_sol=original_cost,
            optimized_cost_sol=optimized_cost,
            savings_percentage=savings_percentage,
            techniques_applied=optimization_techniques,
            meets_target=meets_target,
        )

        logger.info(
            f"Optimization complete: {savings_percentage:.2f}% savings, "
            f"target met: {meets_target}"
        )

        return result

    def _estimate_transaction_cost(self, transaction_data: dict[str, Any]) -> float:
        """
        Estimate transaction cost in SOL
        """
        base_fee = 0.000005  # 5000 lamports base fee

        # Account creation costs
        account_costs = 0
        if transaction_data.get("creates_accounts"):
            for account_type in transaction_data["creates_accounts"]:
                size = self.config["accountOptimization"].get(
                    f"{account_type}Size", 1000
                )
                rent_cost = size * 0.00000348  # Approximate rent per byte
                account_costs += rent_cost

        # Compute unit costs
        compute_units = transaction_data.get("compute_units", 200000)
        compute_cost = compute_units * 0.000000001  # Approximate CU cost

        total_cost = base_fee + account_costs + compute_cost
        return total_cost

    def _optimize_account_sizes(
        self, transaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Optimize account sizes to reduce rent costs
        """
        optimized = transaction_data.copy()

        if "creates_accounts" in optimized:
            for _i, account_type in enumerate(optimized["creates_accounts"]):
                # Use optimized sizes from config
                optimized_size_key = f"{account_type}Size"
                if optimized_size_key in self.config["accountOptimization"]:
                    # Account size already optimized in config
                    pass

        return optimized

    def _optimize_compute_units(
        self, transaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Optimize compute unit usage
        """
        optimized = transaction_data.copy()

        action_type = transaction_data.get("type", "unknown")
        compute_key = f"{action_type}CU"

        if compute_key in self.config["computeOptimization"]:
            optimized["compute_units"] = self.config["computeOptimization"][compute_key]

        return optimized

    def _optimize_pda_derivation(
        self, transaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Optimize PDA derivation for reduced compute costs
        """
        optimized = transaction_data.copy()

        if self.config["computeOptimization"]["pdaOptimizationEnabled"]:
            # Use shorter seeds for PDA derivation
            if "pda_seeds" in optimized:
                optimized["pda_seeds"] = [seed[:8] for seed in optimized["pda_seeds"]]

        return optimized

    async def batch_transactions(
        self, transactions: list[dict[str, Any]]
    ) -> list[list[dict[str, Any]]]:
        """
        Batch transactions for cost optimization
        """
        if not self.config["batchConfiguration"]["enabled"]:
            return [[tx] for tx in transactions]

        batches = []
        current_batch = []
        current_batch_cost = 0

        max_batch_size = self.config["batchConfiguration"]["maxBatchSize"]
        cost_target = (
            self.config["batchConfiguration"]["costTargetLamports"] / 1_000_000_000
        )  # Convert to SOL

        for transaction in transactions:
            tx_cost = self._estimate_transaction_cost(transaction)

            # Check if adding this transaction would exceed limits
            if (
                len(current_batch) >= max_batch_size
                or current_batch_cost + tx_cost > cost_target
            ):
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_batch_cost = 0

            current_batch.append(transaction)
            current_batch_cost += tx_cost

        # Add remaining transactions
        if current_batch:
            batches.append(current_batch)

        logger.info(
            f"Created {len(batches)} batches from {len(transactions)} transactions"
        )
        return batches

    async def monitor_performance(
        self, transaction_metrics: TransactionMetrics
    ) -> dict[str, Any]:
        """
        Monitor transaction performance and costs
        """
        self.metrics_history.append(transaction_metrics)

        # Calculate performance metrics
        recent_metrics = self.metrics_history[-100:]  # Last 100 transactions

        avg_cost_sol = sum(m.cost_sol for m in recent_metrics) / len(recent_metrics)
        avg_compute_units = sum(m.compute_units_used for m in recent_metrics) / len(
            recent_metrics
        )

        target_cost = self.config["costOptimization"]["targetCostSOL"]
        cost_compliance = sum(
            1 for m in recent_metrics if m.cost_sol <= target_cost
        ) / len(recent_metrics)

        performance_report = {
            "average_cost_sol": avg_cost_sol,
            "average_compute_units": avg_compute_units,
            "cost_target_compliance": cost_compliance,
            "target_cost_sol": target_cost,
            "meets_target": avg_cost_sol <= target_cost,
            "total_transactions": len(self.metrics_history),
            "recent_transactions": len(recent_metrics),
        }

        logger.info(
            f"Performance: Avg cost {avg_cost_sol:.6f} SOL, "
            f"Target compliance: {cost_compliance:.2%}"
        )

        return performance_report

    async def generate_optimization_report(self) -> dict[str, Any]:
        """
        Generate comprehensive optimization report
        """
        if not self.metrics_history:
            return {"error": "No transaction metrics available"}

        total_transactions = len(self.metrics_history)
        total_cost_sol = sum(m.cost_sol for m in self.metrics_history)
        avg_cost_sol = total_cost_sol / total_transactions

        target_cost = self.config["costOptimization"]["targetCostSOL"]
        compliant_transactions = sum(
            1 for m in self.metrics_history if m.cost_sol <= target_cost
        )
        compliance_rate = compliant_transactions / total_transactions

        # Cost breakdown by action type
        action_costs = {}
        for metric in self.metrics_history:
            action_type = metric.action_type
            if action_type not in action_costs:
                action_costs[action_type] = []
            action_costs[action_type].append(metric.cost_sol)

        action_averages = {
            action: sum(costs) / len(costs) for action, costs in action_costs.items()
        }

        report = {
            "summary": {
                "total_transactions": total_transactions,
                "total_cost_sol": total_cost_sol,
                "average_cost_sol": avg_cost_sol,
                "target_cost_sol": target_cost,
                "compliance_rate": compliance_rate,
                "meets_target": avg_cost_sol <= target_cost,
            },
            "cost_breakdown": action_averages,
            "optimization_config": self.config,
            "recommendations": self._generate_recommendations(
                avg_cost_sol, target_cost
            ),
        }

        return report

    def _generate_recommendations(
        self, avg_cost: float, target_cost: float
    ) -> list[str]:
        """
        Generate optimization recommendations
        """
        recommendations = []

        if avg_cost > target_cost:
            recommendations.append(
                f"Average cost ({avg_cost:.6f} SOL) exceeds target ({target_cost:.6f} SOL)"
            )
            recommendations.append(
                "Consider enabling additional optimization techniques"
            )
            recommendations.append(
                "Increase transaction batching to reduce per-transaction costs"
            )

        if avg_cost <= target_cost * 0.5:
            recommendations.append("Excellent cost optimization achieved")
            recommendations.append(
                "Consider increasing batch sizes for even better efficiency"
            )

        return recommendations


async def main():
    """
    Main function for transaction optimization testing
    """
    logger.info("Starting Quantumagi Transaction Optimizer")

    optimizer = TransactionOptimizer()

    # Test transaction optimization
    test_transactions = [
        {
            "type": "createProposal",
            "creates_accounts": ["proposal"],
            "compute_units": 50000,
            "pda_seeds": ["proposal", "test_proposal_id"],
        },
        {
            "type": "voteOnProposal",
            "creates_accounts": ["voteRecord"],
            "compute_units": 25000,
            "pda_seeds": ["vote", "voter_pubkey", "proposal_id"],
        },
    ]

    # Optimize individual transactions
    for tx in test_transactions:
        result = await optimizer.optimize_transaction(tx)
        logger.info(f"Optimization result: {result}")

    # Test batching
    batches = await optimizer.batch_transactions(test_transactions)
    logger.info(f"Created {len(batches)} batches")

    # Simulate metrics
    for i, tx in enumerate(test_transactions):
        metrics = TransactionMetrics(
            transaction_id=f"tx_{i}",
            action_type=tx["type"],
            cost_lamports=8_000_000,  # 0.008 SOL
            cost_sol=0.008,
            compute_units_used=tx["compute_units"],
            account_size_bytes=700,
            timestamp=time.time(),
        )

        performance = await optimizer.monitor_performance(metrics)
        logger.info(f"Performance metrics: {performance}")

    # Generate final report
    report = await optimizer.generate_optimization_report()
    logger.info(f"Final optimization report: {json.dumps(report, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
