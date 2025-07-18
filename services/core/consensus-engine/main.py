"""
Consensus Engine Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service for distributed consensus mechanisms including PBFT, Raft,
constitutional governance, and multi-agent decision making.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import os
import uuid

from .models import (
    ConsensusAlgorithm,
    NodeIdentity,
    NodeRole,
    Proposal,
    ProposalType,
    Vote,
    VoteType,
    ConsensusResult,
    ConsensusStatus,
    ConsensusMetrics,
    ConstitutionalRule,
    ReputationScore,
    ConsensusAuditTrail,
    CONSTITUTIONAL_HASH,
)
from .services import ConsensusEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize consensus engine
consensus_engine = ConsensusEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Consensus Engine Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Initialize sample nodes
    await initialize_sample_nodes()

    # Start background tasks
    asyncio.create_task(monitor_active_proposals())
    asyncio.create_task(reputation_maintenance())

    yield

    logger.info("Shutting down Consensus Engine Service")


app = FastAPI(
    title="Consensus Engine Service",
    description="Distributed consensus for multi-agent governance",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def initialize_sample_nodes():
    """Initialize sample consensus nodes"""
    sample_nodes = [
        NodeIdentity(
            name="constitutional-guardian-alpha",
            role=NodeRole.CONSTITUTIONAL_GUARDIAN,
            public_key="guardian_alpha_key",
            stake_amount=10000.0,
            reputation_score=0.95,
            constitutional_compliance=1.0,
            voting_power=1.0,
        ),
        NodeIdentity(
            name="validator-beta",
            role=NodeRole.VALIDATOR,
            public_key="validator_beta_key",
            stake_amount=5000.0,
            reputation_score=0.88,
            constitutional_compliance=0.98,
            voting_power=0.8,
        ),
        NodeIdentity(
            name="delegate-gamma",
            role=NodeRole.DELEGATE,
            public_key="delegate_gamma_key",
            stake_amount=3000.0,
            reputation_score=0.82,
            constitutional_compliance=0.95,
            voting_power=0.7,
        ),
        NodeIdentity(
            name="validator-delta",
            role=NodeRole.VALIDATOR,
            public_key="validator_delta_key",
            stake_amount=4500.0,
            reputation_score=0.90,
            constitutional_compliance=0.97,
            voting_power=0.85,
        ),
        NodeIdentity(
            name="observer-epsilon",
            role=NodeRole.OBSERVER,
            public_key="observer_epsilon_key",
            stake_amount=1000.0,
            reputation_score=0.75,
            constitutional_compliance=0.92,
            voting_power=0.5,
        ),
        NodeIdentity(
            name="leader-zeta",
            role=NodeRole.LEADER,
            public_key="leader_zeta_key",
            stake_amount=8000.0,
            reputation_score=0.93,
            constitutional_compliance=0.99,
            voting_power=1.2,
        ),
    ]

    for node in sample_nodes:
        await consensus_engine.register_node(node)

    logger.info(f"Initialized {len(sample_nodes)} sample consensus nodes")


async def monitor_active_proposals():
    """Monitor and timeout stale proposals"""
    while True:
        try:
            current_time = datetime.utcnow()

            # Check for expired proposals
            expired_proposals = []
            for proposal_id, proposal in consensus_engine.active_proposals.items():
                if proposal.expires_at and proposal.expires_at <= current_time:
                    expired_proposals.append(proposal_id)

            # Handle expired proposals
            for proposal_id in expired_proposals:
                logger.warning(f"Proposal {proposal_id} expired")
                # Would implement timeout handling

            await asyncio.sleep(30)  # Check every 30 seconds

        except Exception as e:
            logger.error(f"Proposal monitor error: {e}")
            await asyncio.sleep(60)


async def reputation_maintenance():
    """Maintain and decay reputation scores"""
    while True:
        try:
            # Gradual reputation decay for inactive nodes
            for node_id, node in consensus_engine.nodes.items():
                time_since_activity = datetime.utcnow() - node.last_activity

                if time_since_activity > timedelta(days=7):
                    # Gradual reputation decay
                    reputation = await consensus_engine.reputation.get_reputation(
                        node_id
                    )
                    decay_factor = 0.99  # 1% decay per week
                    reputation.current_score *= decay_factor
                    reputation.last_updated = datetime.utcnow()

            await asyncio.sleep(3600)  # Run every hour

        except Exception as e:
            logger.error(f"Reputation maintenance error: {e}")
            await asyncio.sleep(3600)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_nodes = len(consensus_engine.nodes)
    active_nodes = sum(1 for node in consensus_engine.nodes.values() if node.is_active)
    active_proposals = len(consensus_engine.active_proposals)

    return {
        "status": "healthy",
        "service": "consensus-engine",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "consensus": {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "active_proposals": active_proposals,
            "supported_algorithms": [algo.value for algo in ConsensusAlgorithm],
        },
    }


# Node Management
@app.post("/api/v1/nodes/register", response_model=Dict[str, Any])
async def register_node(node: NodeIdentity):
    """Register a new consensus node"""
    success = await consensus_engine.register_node(node)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Node registration failed - constitutional validation error",
        )

    return {
        "node_id": node.node_id,
        "status": "registered",
        "role": node.role.value,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@app.get("/api/v1/nodes", response_model=List[NodeIdentity])
async def list_nodes(
    role: Optional[str] = None,
    active_only: bool = Query(True, description="Return only active nodes"),
):
    """List consensus nodes"""
    nodes = list(consensus_engine.nodes.values())

    if role:
        try:
            role_enum = NodeRole(role)
            nodes = [n for n in nodes if n.role == role_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid node role")

    if active_only:
        nodes = [n for n in nodes if n.is_active]

    return nodes


@app.get("/api/v1/nodes/{node_id}", response_model=NodeIdentity)
async def get_node(node_id: str):
    """Get specific node details"""
    if node_id not in consensus_engine.nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    return consensus_engine.nodes[node_id]


@app.get("/api/v1/nodes/{node_id}/reputation", response_model=ReputationScore)
async def get_node_reputation(node_id: str):
    """Get node reputation score"""
    reputation = await consensus_engine.get_node_reputation(node_id)

    if not reputation:
        raise HTTPException(status_code=404, detail="Node not found")

    return reputation


@app.put("/api/v1/nodes/{node_id}/status")
async def update_node_status(node_id: str, active: bool):
    """Update node active status"""
    if node_id not in consensus_engine.nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node = consensus_engine.nodes[node_id]
    node.is_active = active
    node.last_activity = datetime.utcnow()

    return {
        "node_id": node_id,
        "active": active,
        "updated_at": node.last_activity.isoformat(),
    }


# Proposal Management
@app.post("/api/v1/proposals/submit", response_model=Dict[str, Any])
async def submit_proposal(proposal: Proposal):
    """Submit a proposal for consensus"""
    try:
        proposal_id = await consensus_engine.submit_proposal(proposal)

        return {
            "proposal_id": proposal_id,
            "status": "submitted",
            "algorithm": proposal.algorithm.value,
            "required_threshold": proposal.required_threshold,
            "expires_at": (
                proposal.expires_at.isoformat() if proposal.expires_at else None
            ),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/proposals/{proposal_id}/consensus", response_model=ConsensusResult)
async def run_proposal_consensus(proposal_id: str, algorithm: Optional[str] = None):
    """Run consensus for a proposal"""

    # Validate algorithm if provided
    consensus_algorithm = None
    if algorithm:
        try:
            consensus_algorithm = ConsensusAlgorithm(algorithm)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid consensus algorithm")

    try:
        result = await consensus_engine.run_consensus(proposal_id, consensus_algorithm)
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consensus failed: {str(e)}")


@app.get("/api/v1/proposals/active", response_model=List[Proposal])
async def list_active_proposals():
    """List active proposals"""
    return list(consensus_engine.active_proposals.values())


@app.get("/api/v1/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get proposal details"""
    if proposal_id not in consensus_engine.active_proposals:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = consensus_engine.active_proposals[proposal_id]

    return {
        "proposal": proposal,
        "status": "active",
        "time_remaining_seconds": (
            (proposal.expires_at - datetime.utcnow()).total_seconds()
            if proposal.expires_at
            else None
        ),
    }


# Consensus Algorithms
@app.get("/api/v1/algorithms")
async def list_consensus_algorithms():
    """List supported consensus algorithms"""
    algorithms = []

    for algo in ConsensusAlgorithm:
        description = get_algorithm_description(algo)
        use_cases = get_algorithm_use_cases(algo)

        algorithms.append(
            {
                "name": algo.value,
                "description": description,
                "use_cases": use_cases,
                "byzantine_fault_tolerant": algo
                in [ConsensusAlgorithm.PBFT, ConsensusAlgorithm.CONSTITUTIONAL],
            }
        )

    return {
        "algorithms": algorithms,
        "default": ConsensusAlgorithm.CONSTITUTIONAL.value,
    }


@app.post("/api/v1/consensus/test")
async def test_consensus_algorithm(
    algorithm: str,
    participants: int = Query(5, ge=3, le=20),
    threshold: float = Query(0.67, ge=0.51, le=1.0),
):
    """Test consensus algorithm with dummy proposal"""

    try:
        algo_enum = ConsensusAlgorithm(algorithm)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid algorithm")

    # Create test proposal
    test_proposal = Proposal(
        proposer_id="test_proposer",
        proposal_type=ProposalType.PARAMETER_ADJUSTMENT,
        title="Test Consensus Proposal",
        description="Testing consensus algorithm performance",
        content={
            "test": True,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "implementation_plan": "Test implementation",
            "risk_assessment": "Low risk test",
            "rollback_plan": "Immediate rollback",
        },
        algorithm=algo_enum,
        required_threshold=threshold,
        timeout_seconds=60,
    )

    # Get active nodes (limit to requested participants)
    active_nodes = [n for n in consensus_engine.nodes.values() if n.is_active]
    test_nodes = active_nodes[:participants]

    if len(test_nodes) < 3:
        raise HTTPException(
            status_code=400,
            detail="Insufficient active nodes for test (minimum 3 required)",
        )

    # Run test consensus
    start_time = datetime.utcnow()

    try:
        result = await consensus_engine.algorithm_engine.run_consensus(
            test_proposal, test_nodes, algo_enum
        )

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return {
            "test_result": result,
            "duration_ms": duration_ms,
            "participants": len(test_nodes),
            "algorithm": algorithm,
            "threshold": threshold,
            "constitutional_compliance": result.constitutional_compliance,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


# Constitutional Rules
@app.get("/api/v1/constitutional/rules", response_model=List[ConstitutionalRule])
async def list_constitutional_rules():
    """List constitutional rules"""
    return list(consensus_engine.validator.rules.values())


@app.post("/api/v1/constitutional/validate")
async def validate_proposal_constitutional(proposal: Proposal):
    """Validate proposal against constitutional rules"""

    is_valid, violations, applicable_rules = (
        await consensus_engine.validator.validate_proposal(proposal)
    )

    return {
        "is_valid": is_valid,
        "violations": violations,
        "applicable_rules": [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "category": rule.category,
                "priority": rule.priority,
            }
            for rule in applicable_rules
        ],
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


# Metrics and Analytics
@app.get("/api/v1/metrics", response_model=ConsensusMetrics)
async def get_consensus_metrics():
    """Get consensus performance metrics"""
    return await consensus_engine.get_metrics()


@app.get("/api/v1/audit-trail", response_model=List[ConsensusAuditTrail])
async def get_audit_trail(
    proposal_id: Optional[str] = None, limit: int = Query(50, ge=1, le=200)
):
    """Get consensus audit trail"""
    return await consensus_engine.get_audit_trail(proposal_id, limit)


@app.get("/api/v1/analytics/participation")
async def get_participation_analytics():
    """Get participation analytics"""

    total_nodes = len(consensus_engine.nodes)
    active_nodes = sum(1 for n in consensus_engine.nodes.values() if n.is_active)

    # Analyze node roles
    role_distribution = {}
    for node in consensus_engine.nodes.values():
        role = node.role.value
        role_distribution[role] = role_distribution.get(role, 0) + 1

    # Analyze reputation distribution
    reputation_scores = []
    for node in consensus_engine.nodes.values():
        reputation_scores.append(node.reputation_score)

    avg_reputation = (
        sum(reputation_scores) / len(reputation_scores) if reputation_scores else 0
    )

    return {
        "total_nodes": total_nodes,
        "active_nodes": active_nodes,
        "participation_rate": active_nodes / total_nodes if total_nodes > 0 else 0,
        "role_distribution": role_distribution,
        "average_reputation": avg_reputation,
        "reputation_distribution": {
            "min": min(reputation_scores) if reputation_scores else 0,
            "max": max(reputation_scores) if reputation_scores else 0,
            "avg": avg_reputation,
        },
    }


@app.get("/api/v1/analytics/algorithms")
async def get_algorithm_analytics():
    """Get algorithm performance analytics"""

    # This would analyze historical performance of different algorithms
    # For now, return theoretical performance characteristics

    algorithm_performance = {}

    for algo in ConsensusAlgorithm:
        performance = {
            "name": algo.value,
            "theoretical_latency_ms": get_algorithm_latency(algo),
            "byzantine_fault_tolerance": algo
            in [ConsensusAlgorithm.PBFT, ConsensusAlgorithm.CONSTITUTIONAL],
            "scalability": get_algorithm_scalability(algo),
            "constitutional_compliance": algo == ConsensusAlgorithm.CONSTITUTIONAL,
        }

        algorithm_performance[algo.value] = performance

    return {
        "algorithm_performance": algorithm_performance,
        "recommended_for_constitutional": ConsensusAlgorithm.CONSTITUTIONAL.value,
    }


def get_algorithm_description(algorithm: ConsensusAlgorithm) -> str:
    """Get description for consensus algorithm"""
    descriptions = {
        ConsensusAlgorithm.PBFT: "Practical Byzantine Fault Tolerance - handles malicious nodes",
        ConsensusAlgorithm.RAFT: "Raft consensus - simple majority with leader election",
        ConsensusAlgorithm.CONSTITUTIONAL: "Constitutional governance with enhanced validation",
        ConsensusAlgorithm.PROOF_OF_STAKE: "Proof of Stake - weighted by stake amount",
        ConsensusAlgorithm.DELEGATED_PROOF_OF_STAKE: "Delegated PoS - representatives vote",
        ConsensusAlgorithm.MULTI_AGENT_VOTING: "Multi-agent voting with reputation weighting",
        ConsensusAlgorithm.WEIGHTED_VOTING: "Weighted voting by stake and reputation",
        ConsensusAlgorithm.FEDERATED_CONSENSUS: "Federated Byzantine Agreement with quorum slices",
    }
    return descriptions.get(algorithm, "Unknown algorithm")


def get_algorithm_use_cases(algorithm: ConsensusAlgorithm) -> List[str]:
    """Get use cases for consensus algorithm"""
    use_cases = {
        ConsensusAlgorithm.PBFT: [
            "High-security environments",
            "Byzantine fault tolerance required",
            "Financial systems",
        ],
        ConsensusAlgorithm.RAFT: [
            "Simple distributed systems",
            "Configuration management",
            "Log replication",
        ],
        ConsensusAlgorithm.CONSTITUTIONAL: [
            "Governance decisions",
            "Constitutional compliance",
            "Multi-stakeholder voting",
        ],
        ConsensusAlgorithm.PROOF_OF_STAKE: [
            "Blockchain networks",
            "Token-based governance",
            "Economic incentives",
        ],
        ConsensusAlgorithm.DELEGATED_PROOF_OF_STAKE: [
            "Large-scale networks",
            "Representative democracy",
            "Scalable governance",
        ],
        ConsensusAlgorithm.MULTI_AGENT_VOTING: [
            "AI agent coordination",
            "Reputation-based decisions",
            "Multi-agent systems",
        ],
        ConsensusAlgorithm.WEIGHTED_VOTING: [
            "Stakeholder decisions",
            "Resource allocation",
            "Priority-based voting",
        ],
        ConsensusAlgorithm.FEDERATED_CONSENSUS: [
            "Federated networks",
            "Cross-organization decisions",
            "Trust-based consensus",
        ],
    }
    return use_cases.get(algorithm, [])


def get_algorithm_latency(algorithm: ConsensusAlgorithm) -> float:
    """Get theoretical latency for algorithm"""
    latencies = {
        ConsensusAlgorithm.PBFT: 150.0,  # Higher due to multiple rounds
        ConsensusAlgorithm.RAFT: 50.0,  # Simple majority
        ConsensusAlgorithm.CONSTITUTIONAL: 200.0,  # Enhanced validation
        ConsensusAlgorithm.PROOF_OF_STAKE: 100.0,
        ConsensusAlgorithm.DELEGATED_PROOF_OF_STAKE: 80.0,
        ConsensusAlgorithm.MULTI_AGENT_VOTING: 120.0,
        ConsensusAlgorithm.WEIGHTED_VOTING: 90.0,
        ConsensusAlgorithm.FEDERATED_CONSENSUS: 180.0,
    }
    return latencies.get(algorithm, 100.0)


def get_algorithm_scalability(algorithm: ConsensusAlgorithm) -> str:
    """Get scalability rating for algorithm"""
    scalability = {
        ConsensusAlgorithm.PBFT: "low",  # O(n²) messages
        ConsensusAlgorithm.RAFT: "medium",
        ConsensusAlgorithm.CONSTITUTIONAL: "medium",
        ConsensusAlgorithm.PROOF_OF_STAKE: "high",
        ConsensusAlgorithm.DELEGATED_PROOF_OF_STAKE: "very_high",
        ConsensusAlgorithm.MULTI_AGENT_VOTING: "medium",
        ConsensusAlgorithm.WEIGHTED_VOTING: "medium",
        ConsensusAlgorithm.FEDERATED_CONSENSUS: "high",
    }
    return scalability.get(algorithm, "medium")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8011))
    uvicorn.run(app, host="0.0.0.0", port=port)
