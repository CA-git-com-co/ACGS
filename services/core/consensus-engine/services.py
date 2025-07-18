"""
Consensus Engine Services
Constitutional Hash: cdd01ef066bc6cf2

Core business logic for distributed consensus including PBFT, Raft,
constitutional governance, and multi-agent decision making.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict
import random
import logging
import json
import hashlib
import time
from asyncio import Queue, Lock

from .models import (
    ConsensusAlgorithm,
    NodeIdentity,
    NodeRole,
    Proposal,
    ProposalType,
    Vote,
    VoteType,
    ConsensusRound,
    ConsensusResult,
    ConsensusStatus,
    ConstitutionalRule,
    ConsensusMetrics,
    ReputationScore,
    EmergencyProtocol,
    ConsensusAuditTrail,
    VotingPool,
    CONSTITUTIONAL_HASH,
)

logger = logging.getLogger(__name__)


class ConstitutionalValidator:
    """Validate proposals against constitutional rules"""

    def __init__(self):
        self.rules: Dict[str, ConstitutionalRule] = {}
        self.load_default_rules()

    def load_default_rules(self):
        """Load default constitutional rules"""
        default_rules = [
            ConstitutionalRule(
                name="Constitutional Hash Requirement",
                description="All proposals must maintain constitutional hash compliance",
                category="fundamental",
                rule_text=f"All proposals must reference constitutional hash {CONSTITUTIONAL_HASH}",
                priority=10,
                applicable_proposal_types=list(ProposalType),
                violation_consequences=["immediate_rejection"],
            ),
            ConstitutionalRule(
                name="Performance Requirements",
                description="Proposals must not violate performance targets",
                category="performance",
                rule_text="P99 latency must remain <5ms, throughput >100 RPS",
                priority=9,
                applicable_proposal_types=[
                    ProposalType.SYSTEM_UPGRADE,
                    ProposalType.PARAMETER_ADJUSTMENT,
                ],
                violation_consequences=["performance_review_required"],
            ),
            ConstitutionalRule(
                name="Supermajority for Constitutional Changes",
                description="Constitutional amendments require 80% consensus",
                category="governance",
                rule_text="Constitutional amendments require 80% approval",
                priority=10,
                applicable_proposal_types=[ProposalType.CONSTITUTIONAL_AMENDMENT],
                violation_consequences=["automatic_rejection"],
            ),
            ConstitutionalRule(
                name="Emergency Action Limits",
                description="Emergency actions have time and scope limits",
                category="emergency",
                rule_text="Emergency actions limited to 1 hour and specific scope",
                priority=8,
                applicable_proposal_types=[ProposalType.EMERGENCY_ACTION],
                violation_consequences=["audit_required", "time_limit_enforcement"],
            ),
            ConstitutionalRule(
                name="Transparency Requirement",
                description="All proposals must include full disclosure",
                category="transparency",
                rule_text="Proposals must include complete implementation details",
                priority=7,
                applicable_proposal_types=list(ProposalType),
                violation_consequences=["clarification_required"],
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

    async def validate_proposal(
        self, proposal: Proposal
    ) -> Tuple[bool, List[str], List[ConstitutionalRule]]:
        """Validate proposal against constitutional rules"""

        is_valid = True
        violations = []
        applicable_rules = []

        for rule in self.rules.values():
            if not rule.enforced:
                continue

            # Check if rule applies to this proposal type
            if (
                rule.applicable_proposal_types
                and proposal.proposal_type not in rule.applicable_proposal_types
            ):
                continue

            applicable_rules.append(rule)

            # Apply specific rule validations
            rule_valid = await self._validate_specific_rule(proposal, rule)

            if not rule_valid:
                is_valid = False
                violations.append(f"Violation of rule: {rule.name}")
                logger.warning(
                    f"Proposal {proposal.proposal_id} violates rule {rule.name}"
                )

        return is_valid, violations, applicable_rules

    async def _validate_specific_rule(
        self, proposal: Proposal, rule: ConstitutionalRule
    ) -> bool:
        """Validate proposal against specific rule"""

        if rule.name == "Constitutional Hash Requirement":
            # Check if proposal content references constitutional hash
            content_str = json.dumps(proposal.content)
            if CONSTITUTIONAL_HASH not in content_str:
                return False

        elif rule.name == "Performance Requirements":
            # Check if proposal might violate performance requirements
            if "performance_impact" in proposal.content:
                impact = proposal.content["performance_impact"]
                if impact.get("latency_increase_ms", 0) > 1:
                    return False
                if impact.get("throughput_decrease_rps", 0) > 10:
                    return False

        elif rule.name == "Supermajority for Constitutional Changes":
            if proposal.proposal_type == ProposalType.CONSTITUTIONAL_AMENDMENT:
                if proposal.required_threshold < 0.8:
                    return False

        elif rule.name == "Emergency Action Limits":
            if proposal.proposal_type == ProposalType.EMERGENCY_ACTION:
                if proposal.timeout_seconds > 3600:  # 1 hour limit
                    return False

        elif rule.name == "Transparency Requirement":
            required_fields = [
                "implementation_plan",
                "risk_assessment",
                "rollback_plan",
            ]
            for field in required_fields:
                if field not in proposal.content:
                    return False

        return True


class ReputationSystem:
    """Manage reputation scores for consensus participants"""

    def __init__(self):
        self.scores: Dict[str, ReputationScore] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    async def get_reputation(self, participant_id: str) -> ReputationScore:
        """Get reputation score for participant"""
        if participant_id not in self.scores:
            self.scores[participant_id] = ReputationScore(participant_id=participant_id)
        return self.scores[participant_id]

    async def update_reputation(
        self,
        participant_id: str,
        action: str,
        outcome: str,
        context: Dict[str, Any] = None,
    ):
        """Update reputation based on action and outcome"""

        reputation = await self.get_reputation(participant_id)

        # Record performance event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "outcome": outcome,
            "context": context or {},
        }
        self.performance_history[participant_id].append(event)

        # Update specific metrics based on action
        if action == "vote":
            if outcome == "aligned_with_consensus":
                reputation.voting_accuracy = min(1.0, reputation.voting_accuracy + 0.01)
            else:
                reputation.voting_accuracy = max(
                    0.0, reputation.voting_accuracy - 0.005
                )

        elif action == "propose":
            if outcome == "accepted":
                reputation.leadership_effectiveness = min(
                    1.0, reputation.leadership_effectiveness + 0.02
                )
            elif outcome == "rejected":
                reputation.leadership_effectiveness = max(
                    0.0, reputation.leadership_effectiveness - 0.01
                )

        elif action == "participate":
            reputation.participation_rate = min(
                1.0, reputation.participation_rate + 0.005
            )

        elif action == "constitutional_compliance":
            if outcome == "compliant":
                reputation.constitutional_alignment = min(
                    1.0, reputation.constitutional_alignment + 0.001
                )
            else:
                reputation.constitutional_alignment = max(
                    0.0, reputation.constitutional_alignment - 0.05
                )

        # Recalculate overall score
        reputation.current_score = (
            reputation.voting_accuracy * 0.3
            + reputation.participation_rate * 0.2
            + reputation.constitutional_alignment * 0.3
            + reputation.leadership_effectiveness * 0.2
        )

        reputation.last_updated = datetime.utcnow()


class ConsensusAlgorithmEngine:
    """Engine for different consensus algorithms"""

    def __init__(
        self, validator: ConstitutionalValidator, reputation: ReputationSystem
    ):
        self.validator = validator
        self.reputation = reputation
        self.active_rounds: Dict[str, ConsensusRound] = {}
        self.consensus_history: List[ConsensusResult] = []

    async def run_consensus(
        self,
        proposal: Proposal,
        participants: List[NodeIdentity],
        algorithm: ConsensusAlgorithm = None,
    ) -> ConsensusResult:
        """Run consensus for a proposal"""

        algorithm = algorithm or proposal.algorithm

        # Validate proposal constitutionally
        is_valid, violations, _ = await self.validator.validate_proposal(proposal)

        if not is_valid:
            return ConsensusResult(
                proposal_id=proposal.proposal_id,
                status=ConsensusStatus.CONSTITUTIONAL_VIOLATION,
                final_decision=False,
                vote_summary={"violations": violations},
                winning_votes=0,
                total_votes=0,
                participation_rate=0.0,
                constitutional_compliance=False,
            )

        # Route to appropriate algorithm
        if algorithm == ConsensusAlgorithm.PBFT:
            return await self._run_pbft_consensus(proposal, participants)
        elif algorithm == ConsensusAlgorithm.RAFT:
            return await self._run_raft_consensus(proposal, participants)
        elif algorithm == ConsensusAlgorithm.CONSTITUTIONAL:
            return await self._run_constitutional_consensus(proposal, participants)
        elif algorithm == ConsensusAlgorithm.MULTI_AGENT_VOTING:
            return await self._run_multi_agent_voting(proposal, participants)
        elif algorithm == ConsensusAlgorithm.WEIGHTED_VOTING:
            return await self._run_weighted_voting(proposal, participants)
        else:
            # Default to simple majority voting
            return await self._run_simple_majority(proposal, participants)

    async def _run_pbft_consensus(
        self, proposal: Proposal, participants: List[NodeIdentity]
    ) -> ConsensusResult:
        """Run PBFT (Practical Byzantine Fault Tolerance) consensus"""

        # PBFT requires 3f+1 nodes to tolerate f Byzantine faults
        min_nodes = len(participants)
        max_byzantine = (min_nodes - 1) // 3

        if len(participants) < 4:
            return ConsensusResult(
                proposal_id=proposal.proposal_id,
                status=ConsensusStatus.FAILED,
                final_decision=False,
                vote_summary={"error": "Insufficient nodes for PBFT (minimum 4)"},
                winning_votes=0,
                total_votes=len(participants),
                participation_rate=1.0,
                constitutional_compliance=True,
            )

        # Three phases: pre-prepare, prepare, commit
        phases_completed = 0

        # Phase 1: Pre-prepare (leader broadcasts proposal)
        leader = self._select_leader(participants, ConsensusAlgorithm.PBFT)
        pre_prepare_votes = await self._collect_votes(
            proposal, participants, "pre_prepare", timeout_seconds=30
        )

        if len(pre_prepare_votes) >= (2 * max_byzantine + 1):
            phases_completed += 1

        # Phase 2: Prepare (nodes confirm they received pre-prepare)
        if phases_completed >= 1:
            prepare_votes = await self._collect_votes(
                proposal, participants, "prepare", timeout_seconds=30
            )

            if len(prepare_votes) >= (2 * max_byzantine + 1):
                phases_completed += 1

        # Phase 3: Commit (nodes commit to the proposal)
        commit_votes = {}
        if phases_completed >= 2:
            commit_votes = await self._collect_votes(
                proposal, participants, "commit", timeout_seconds=30
            )

        # Determine result
        success = phases_completed >= 2 and len(commit_votes) >= (2 * max_byzantine + 1)

        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            status=ConsensusStatus.ACHIEVED if success else ConsensusStatus.FAILED,
            final_decision=success,
            vote_summary={
                "phases_completed": phases_completed,
                "pre_prepare_votes": len(pre_prepare_votes),
                "prepare_votes": len(prepare_votes) if phases_completed >= 1 else 0,
                "commit_votes": len(commit_votes),
                "required_votes": 2 * max_byzantine + 1,
                "max_byzantine_faults": max_byzantine,
            },
            winning_votes=len(commit_votes) if success else 0,
            total_votes=len(participants),
            participation_rate=len(commit_votes) / len(participants),
            consensus_achieved_at=datetime.utcnow() if success else None,
            constitutional_compliance=True,
        )

    async def _run_raft_consensus(
        self, proposal: Proposal, participants: List[NodeIdentity]
    ) -> ConsensusResult:
        """Run Raft consensus algorithm"""

        # Select leader (highest reputation or random if tied)
        leader = self._select_leader(participants, ConsensusAlgorithm.RAFT)

        # Leader proposes to followers
        votes = await self._collect_votes(
            proposal, participants, "raft_vote", timeout_seconds=60
        )

        # Raft requires majority
        required_votes = (len(participants) // 2) + 1
        yes_votes = sum(1 for vote in votes.values() if vote.vote_type == VoteType.YES)

        success = yes_votes >= required_votes

        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            status=ConsensusStatus.ACHIEVED if success else ConsensusStatus.FAILED,
            final_decision=success,
            vote_summary={
                "leader_id": leader.node_id,
                "yes_votes": yes_votes,
                "total_votes": len(votes),
                "required_votes": required_votes,
            },
            winning_votes=yes_votes,
            total_votes=len(participants),
            participation_rate=len(votes) / len(participants),
            consensus_achieved_at=datetime.utcnow() if success else None,
            constitutional_compliance=True,
        )

    async def _run_constitutional_consensus(
        self, proposal: Proposal, participants: List[NodeIdentity]
    ) -> ConsensusResult:
        """Run constitutional consensus with enhanced validation"""

        # Enhanced constitutional validation
        is_valid, violations, applicable_rules = await self.validator.validate_proposal(
            proposal
        )

        if not is_valid:
            return ConsensusResult(
                proposal_id=proposal.proposal_id,
                status=ConsensusStatus.CONSTITUTIONAL_VIOLATION,
                final_decision=False,
                vote_summary={"constitutional_violations": violations},
                winning_votes=0,
                total_votes=0,
                participation_rate=0.0,
                constitutional_compliance=False,
            )

        # Constitutional guardians get enhanced voting power
        enhanced_participants = []
        for participant in participants:
            if participant.role == NodeRole.CONSTITUTIONAL_GUARDIAN:
                participant.voting_power = min(2.0, participant.voting_power * 1.5)
            enhanced_participants.append(participant)

        # Collect weighted votes
        votes = await self._collect_weighted_votes(
            proposal, enhanced_participants, timeout_seconds=300  # 5 minutes
        )

        # Calculate weighted threshold
        total_weight = sum(
            p.voting_power * p.constitutional_compliance for p in enhanced_participants
        )
        threshold_weight = total_weight * proposal.required_threshold

        # Tally weighted votes
        yes_weight = sum(
            vote.weight * participants_dict[vote.voter_id].voting_power
            for vote in votes.values()
            if vote.vote_type == VoteType.YES
        )

        participants_dict = {p.node_id: p for p in enhanced_participants}

        success = yes_weight >= threshold_weight

        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            status=ConsensusStatus.ACHIEVED if success else ConsensusStatus.FAILED,
            final_decision=success,
            vote_summary={
                "weighted_yes_votes": yes_weight,
                "total_weight": total_weight,
                "threshold_weight": threshold_weight,
                "constitutional_rules_applied": len(applicable_rules),
            },
            winning_votes=int(yes_weight),
            total_votes=len(participants),
            participation_rate=len(votes) / len(participants),
            consensus_achieved_at=datetime.utcnow() if success else None,
            constitutional_compliance=True,
        )

    async def _run_multi_agent_voting(
        self, proposal: Proposal, participants: List[NodeIdentity]
    ) -> ConsensusResult:
        """Run multi-agent voting with reputation weighting"""

        # Get reputation scores for all participants
        reputation_weights = {}
        for participant in participants:
            reputation = await self.reputation.get_reputation(participant.node_id)
            reputation_weights[participant.node_id] = reputation.current_score

        # Collect votes
        votes = await self._collect_votes(
            proposal, participants, "multi_agent_vote", timeout_seconds=180
        )

        # Calculate reputation-weighted results
        total_weight = sum(reputation_weights.values())
        threshold_weight = total_weight * proposal.required_threshold

        yes_weight = sum(
            reputation_weights.get(vote.voter_id, 0.5)
            for vote in votes.values()
            if vote.vote_type == VoteType.YES
        )

        success = yes_weight >= threshold_weight

        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            status=ConsensusStatus.ACHIEVED if success else ConsensusStatus.FAILED,
            final_decision=success,
            vote_summary={
                "reputation_weighted_yes": yes_weight,
                "total_reputation_weight": total_weight,
                "threshold_weight": threshold_weight,
                "average_reputation": (
                    total_weight / len(participants) if participants else 0
                ),
            },
            winning_votes=int(yes_weight * 100),  # Scale for display
            total_votes=len(participants),
            participation_rate=len(votes) / len(participants),
            consensus_achieved_at=datetime.utcnow() if success else None,
            constitutional_compliance=True,
        )

    async def _run_weighted_voting(
        self, proposal: Proposal, participants: List[NodeIdentity]
    ) -> ConsensusResult:
        """Run weighted voting based on stake and reputation"""

        # Collect weighted votes
        votes = await self._collect_weighted_votes(proposal, participants)

        # Calculate total weights
        total_weight = sum(p.stake_amount * p.reputation_score for p in participants)
        threshold_weight = total_weight * proposal.required_threshold

        # Tally weighted votes
        participants_dict = {p.node_id: p for p in participants}
        yes_weight = 0

        for vote in votes.values():
            if vote.vote_type == VoteType.YES:
                participant = participants_dict.get(vote.voter_id)
                if participant:
                    yes_weight += (
                        participant.stake_amount * participant.reputation_score
                    )

        success = yes_weight >= threshold_weight

        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            status=ConsensusStatus.ACHIEVED if success else ConsensusStatus.FAILED,
            final_decision=success,
            vote_summary={
                "stake_weighted_yes": yes_weight,
                "total_stake_weight": total_weight,
                "threshold_weight": threshold_weight,
            },
            winning_votes=int(yes_weight),
            total_votes=len(participants),
            participation_rate=len(votes) / len(participants),
            consensus_achieved_at=datetime.utcnow() if success else None,
            constitutional_compliance=True,
        )

    async def _run_simple_majority(
        self, proposal: Proposal, participants: List[NodeIdentity]
    ) -> ConsensusResult:
        """Run simple majority voting"""

        votes = await self._collect_votes(proposal, participants, "simple_vote")

        yes_votes = sum(1 for vote in votes.values() if vote.vote_type == VoteType.YES)
        required_votes = int(len(participants) * proposal.required_threshold)

        success = yes_votes >= required_votes

        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            status=ConsensusStatus.ACHIEVED if success else ConsensusStatus.FAILED,
            final_decision=success,
            vote_summary={
                "yes_votes": yes_votes,
                "total_votes": len(votes),
                "required_votes": required_votes,
            },
            winning_votes=yes_votes,
            total_votes=len(participants),
            participation_rate=len(votes) / len(participants),
            consensus_achieved_at=datetime.utcnow() if success else None,
            constitutional_compliance=True,
        )

    def _select_leader(
        self, participants: List[NodeIdentity], algorithm: ConsensusAlgorithm
    ) -> NodeIdentity:
        """Select leader for consensus round"""

        # Filter eligible leaders
        eligible = [p for p in participants if p.is_active]

        if algorithm == ConsensusAlgorithm.RAFT:
            # Raft: highest reputation or random
            eligible.sort(key=lambda p: p.reputation_score, reverse=True)
        elif algorithm == ConsensusAlgorithm.CONSTITUTIONAL:
            # Constitutional: prefer guardians
            guardians = [
                p for p in eligible if p.role == NodeRole.CONSTITUTIONAL_GUARDIAN
            ]
            if guardians:
                eligible = guardians

        return eligible[0] if eligible else participants[0]

    async def _collect_votes(
        self,
        proposal: Proposal,
        participants: List[NodeIdentity],
        vote_type: str = "standard",
        timeout_seconds: int = 120,
    ) -> Dict[str, Vote]:
        """Simulate vote collection from participants"""

        votes = {}

        # Simulate voting process
        for participant in participants:
            if not participant.is_active:
                continue

            # Simulate vote decision based on reputation and constitutional compliance
            vote_probability = (
                participant.reputation_score * participant.constitutional_compliance
            )

            # Higher probability of voting yes for constitutional guardians
            if participant.role == NodeRole.CONSTITUTIONAL_GUARDIAN:
                vote_probability *= 1.2

            # Simulate voting delay
            await asyncio.sleep(random.uniform(0.1, 0.5))

            # Determine vote
            if random.random() < 0.9:  # 90% participation rate
                if random.random() < vote_probability:
                    vote_decision = VoteType.YES
                else:
                    vote_decision = (
                        VoteType.NO if random.random() < 0.8 else VoteType.ABSTAIN
                    )

                vote = Vote(
                    proposal_id=proposal.proposal_id,
                    voter_id=participant.node_id,
                    vote_type=vote_decision,
                    weight=participant.voting_power,
                    reasoning=f"Automated vote based on {vote_type}",
                )

                votes[participant.node_id] = vote

                # Update reputation for participation
                await self.reputation.update_reputation(
                    participant.node_id, "participate", "voted"
                )

        return votes

    async def _collect_weighted_votes(
        self,
        proposal: Proposal,
        participants: List[NodeIdentity],
        timeout_seconds: int = 120,
    ) -> Dict[str, Vote]:
        """Collect votes with weight consideration"""

        return await self._collect_votes(
            proposal, participants, "weighted", timeout_seconds
        )


class ConsensusEngine:
    """Main consensus engine orchestrator"""

    def __init__(self):
        self.validator = ConstitutionalValidator()
        self.reputation = ReputationSystem()
        self.algorithm_engine = ConsensusAlgorithmEngine(
            self.validator, self.reputation
        )
        self.metrics = ConsensusMetrics()
        self.active_proposals: Dict[str, Proposal] = {}
        self.nodes: Dict[str, NodeIdentity] = {}
        self.audit_trail: List[ConsensusAuditTrail] = []

    async def register_node(self, node: NodeIdentity) -> bool:
        """Register a consensus node"""

        # Validate constitutional compliance
        if node.constitutional_hash != CONSTITUTIONAL_HASH:
            logger.error(f"Node {node.node_id} failed constitutional validation")
            return False

        self.nodes[node.node_id] = node

        # Initialize reputation
        await self.reputation.get_reputation(node.node_id)

        logger.info(f"Registered consensus node: {node.node_id} ({node.role})")
        return True

    async def submit_proposal(self, proposal: Proposal) -> str:
        """Submit proposal for consensus"""

        # Validate proposal
        is_valid, violations, _ = await self.validator.validate_proposal(proposal)

        if not is_valid:
            logger.error(f"Proposal {proposal.proposal_id} rejected: {violations}")
            raise ValueError(f"Constitutional violations: {violations}")

        # Store proposal
        self.active_proposals[proposal.proposal_id] = proposal

        # Create audit trail entry
        audit_entry = ConsensusAuditTrail(
            proposal_id=proposal.proposal_id,
            action_type="proposal_submitted",
            actor_id=proposal.proposer_id,
            action_details={
                "proposal_type": proposal.proposal_type.value,
                "title": proposal.title,
                "algorithm": proposal.algorithm.value,
            },
            constitutional_impact=proposal.constitutional_impact,
        )
        self.audit_trail.append(audit_entry)

        logger.info(f"Submitted proposal: {proposal.proposal_id}")
        return proposal.proposal_id

    async def run_consensus(
        self, proposal_id: str, algorithm: ConsensusAlgorithm = None
    ) -> ConsensusResult:
        """Run consensus for proposal"""

        if proposal_id not in self.active_proposals:
            raise ValueError(f"Proposal {proposal_id} not found")

        proposal = self.active_proposals[proposal_id]

        # Get active nodes
        active_nodes = [node for node in self.nodes.values() if node.is_active]

        if not active_nodes:
            raise ValueError("No active nodes available for consensus")

        # Run consensus
        start_time = datetime.utcnow()

        try:
            result = await self.algorithm_engine.run_consensus(
                proposal, active_nodes, algorithm
            )

            # Update metrics
            await self._update_metrics(result, start_time)

            # Update reputation scores
            await self._update_participant_reputations(result)

            # Create audit trail entry
            audit_entry = ConsensusAuditTrail(
                proposal_id=proposal.proposal_id,
                action_type="consensus_completed",
                actor_id="system",
                action_details={
                    "status": result.status.value,
                    "final_decision": result.final_decision,
                    "participation_rate": result.participation_rate,
                    "algorithm_used": (algorithm or proposal.algorithm).value,
                },
                constitutional_impact=proposal.constitutional_impact,
            )
            self.audit_trail.append(audit_entry)

            # Remove from active proposals
            if proposal_id in self.active_proposals:
                del self.active_proposals[proposal_id]

            logger.info(f"Consensus completed for {proposal_id}: {result.status.value}")

            return result

        except Exception as e:
            logger.error(f"Consensus failed for {proposal_id}: {e}")

            # Create failure audit entry
            audit_entry = ConsensusAuditTrail(
                proposal_id=proposal.proposal_id,
                action_type="consensus_failed",
                actor_id="system",
                action_details={
                    "error": str(e),
                    "algorithm": (algorithm or proposal.algorithm).value,
                },
            )
            self.audit_trail.append(audit_entry)

            raise

    async def _update_metrics(self, result: ConsensusResult, start_time: datetime):
        """Update consensus metrics"""

        self.metrics.total_proposals += 1

        duration = (datetime.utcnow() - start_time).total_seconds()

        if result.status == ConsensusStatus.ACHIEVED:
            self.metrics.successful_consensus += 1
        elif result.status == ConsensusStatus.FAILED:
            self.metrics.failed_consensus += 1
        elif result.status == ConsensusStatus.TIMEOUT:
            self.metrics.timeout_consensus += 1
        elif result.status == ConsensusStatus.VETOED:
            self.metrics.vetoed_proposals += 1
        elif result.status == ConsensusStatus.CONSTITUTIONAL_VIOLATION:
            self.metrics.constitutional_violations += 1

        # Update average consensus time
        if self.metrics.average_consensus_time_seconds == 0:
            self.metrics.average_consensus_time_seconds = duration
        else:
            self.metrics.average_consensus_time_seconds = (
                self.metrics.average_consensus_time_seconds * 0.9 + duration * 0.1
            )

        # Update P95 consensus time (simplified)
        if duration > self.metrics.p95_consensus_time_seconds:
            self.metrics.p95_consensus_time_seconds = (
                self.metrics.p95_consensus_time_seconds * 0.95 + duration * 0.05
            )

        # Update success rate
        if self.metrics.total_proposals > 0:
            self.metrics.success_rate = (
                self.metrics.successful_consensus / self.metrics.total_proposals
            )

        # Update participation rate
        if self.metrics.average_participation_rate == 0:
            self.metrics.average_participation_rate = result.participation_rate
        else:
            self.metrics.average_participation_rate = (
                self.metrics.average_participation_rate * 0.9
                + result.participation_rate * 0.1
            )

    async def _update_participant_reputations(self, result: ConsensusResult):
        """Update reputation scores based on consensus result"""

        # This would analyze voting patterns and update reputations
        # For now, just update participation
        for participant_id in self.nodes:
            await self.reputation.update_reputation(
                participant_id,
                "consensus_participation",
                (
                    "participated"
                    if result.participation_rate > 0.5
                    else "low_participation"
                ),
            )

    async def get_metrics(self) -> ConsensusMetrics:
        """Get current consensus metrics"""

        # Calculate throughput
        if self.metrics.average_consensus_time_seconds > 0:
            self.metrics.throughput_proposals_per_hour = (
                3600 / self.metrics.average_consensus_time_seconds
            )

        return self.metrics

    async def get_node_reputation(self, node_id: str) -> Optional[ReputationScore]:
        """Get reputation score for node"""
        if node_id in self.nodes:
            return await self.reputation.get_reputation(node_id)
        return None

    async def get_audit_trail(
        self, proposal_id: Optional[str] = None, limit: int = 100
    ) -> List[ConsensusAuditTrail]:
        """Get audit trail entries"""

        entries = self.audit_trail

        if proposal_id:
            entries = [e for e in entries if e.proposal_id == proposal_id]

        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)

        return entries[:limit]
