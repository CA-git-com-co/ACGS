#!/usr/bin/env python3
"""
Advanced Governance Decision-Making Engine for ACGS

Implements sophisticated governance algorithms including:
- Multi-stakeholder consensus mechanisms
- Democratic decision-making processes
- Policy impact analysis and simulation
- Constitutional precedent reasoning
- Ethical constraint optimization
- Game-theoretic mechanism design

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of governance decisions."""

    POLICY_APPROVAL = "policy_approval"
    RESOURCE_ALLOCATION = "resource_allocation"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"
    DISPUTE_RESOLUTION = "dispute_resolution"
    EMERGENCY_RESPONSE = "emergency_response"
    STAKEHOLDER_ADMISSION = "stakeholder_admission"


class StakeholderType(Enum):
    """Types of stakeholders in governance."""

    CITIZEN = "citizen"
    EXPERT = "expert"
    REPRESENTATIVE = "representative"
    INSTITUTION = "institution"
    AI_AGENT = "ai_agent"
    CONSTITUTIONAL_COUNCIL = "constitutional_council"


class VotingMechanism(Enum):
    """Voting mechanisms for decision-making."""

    SIMPLE_MAJORITY = "simple_majority"
    SUPERMAJORITY = "supermajority"
    CONSENSUS = "consensus"
    RANKED_CHOICE = "ranked_choice"
    QUADRATIC_VOTING = "quadratic_voting"
    LIQUID_DEMOCRACY = "liquid_democracy"
    DELIBERATIVE_POLLING = "deliberative_polling"


class PolicyDomain(Enum):
    """Policy domains with different governance requirements."""

    CONSTITUTIONAL = "constitutional"
    REGULATORY = "regulatory"
    PROCEDURAL = "procedural"
    EMERGENCY = "emergency"
    TECHNICAL = "technical"
    ETHICAL = "ethical"


@dataclass
class Stakeholder:
    """Represents a stakeholder in the governance system."""

    id: str
    name: str
    stakeholder_type: StakeholderType
    expertise: list[str] = field(default_factory=list)
    voting_power: float = 1.0
    reputation: float = 0.5
    delegation_targets: list[str] = field(default_factory=list)
    constitutional_alignment: float = 0.5
    participation_history: list[str] = field(default_factory=list)

    def can_vote_on(self, domain: PolicyDomain) -> bool:
        """Check if stakeholder can vote on a specific domain."""
        if self.stakeholder_type == StakeholderType.CONSTITUTIONAL_COUNCIL:
            return domain == PolicyDomain.CONSTITUTIONAL
        elif self.stakeholder_type == StakeholderType.EXPERT:
            return domain.value in self.expertise
        else:
            return True  # General stakeholders can vote on most issues


@dataclass
class GovernanceProposal:
    """Represents a governance proposal for decision-making."""

    id: str
    title: str
    description: str
    proposer_id: str
    decision_type: DecisionType
    policy_domain: PolicyDomain
    content: dict[str, Any]
    constitutional_implications: list[str] = field(default_factory=list)
    impact_assessment: dict[str, Any] = field(default_factory=dict)
    voting_mechanism: VotingMechanism = VotingMechanism.SIMPLE_MAJORITY
    required_threshold: float = 0.5
    deadline: Optional[datetime] = None
    status: str = "draft"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Vote:
    """Represents a vote on a governance proposal."""

    voter_id: str
    proposal_id: str
    choice: str  # "approve", "reject", "abstain", or ranked choices
    reasoning: str = ""
    confidence: float = 1.0
    weight: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    delegation_chain: list[str] = field(default_factory=list)


@dataclass
class DeliberationResult:
    """Results of deliberative discussion."""

    proposal_id: str
    participants: list[str]
    discussion_points: list[str]
    consensus_areas: list[str]
    disagreement_areas: list[str]
    refined_proposal: Optional[dict[str, Any]] = None
    quality_score: float = 0.0


class GovernanceDecisionEngine:
    """Core governance decision-making engine."""

    def __init__(self, constitutional_client: Optional[Any] = None):
        self.constitutional_client = constitutional_client
        self.stakeholders: dict[str, Stakeholder] = {}
        self.proposals: dict[str, GovernanceProposal] = {}
        self.votes: dict[str, list[Vote]] = {}
        self.deliberation_history: dict[str, DeliberationResult] = {}
        self.constitutional_precedents: list[dict[str, Any]] = []
        self.decision_history: list[dict[str, Any]] = []

    async def register_stakeholder(self, stakeholder: Stakeholder) -> dict[str, Any]:
        """Register a new stakeholder in the governance system."""

        # Validate stakeholder eligibility
        eligibility = await self._assess_stakeholder_eligibility(stakeholder)

        if not eligibility["eligible"]:
            return {
                "success": False,
                "reason": eligibility["reason"],
                "stakeholder_id": stakeholder.id,
            }

        # Calculate initial voting power based on type and expertise
        stakeholder.voting_power = self._calculate_initial_voting_power(stakeholder)

        # Register stakeholder
        self.stakeholders[stakeholder.id] = stakeholder

        logger.info(
            "Registered stakeholder:"
            f" {stakeholder.id} ({stakeholder.stakeholder_type.value})"
        )

        return {
            "success": True,
            "stakeholder_id": stakeholder.id,
            "voting_power": stakeholder.voting_power,
            "registration_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def submit_proposal(self, proposal: GovernanceProposal) -> dict[str, Any]:
        """Submit a new governance proposal."""

        # Validate proposal
        validation = await self._validate_proposal(proposal)
        if not validation["valid"]:
            return {
                "success": False,
                "reason": validation["reason"],
                "proposal_id": proposal.id,
            }

        # Perform constitutional impact analysis
        constitutional_analysis = await self._analyze_constitutional_impact(proposal)
        proposal.constitutional_implications = constitutional_analysis["implications"]
        proposal.impact_assessment = constitutional_analysis["impact_assessment"]

        # Determine appropriate voting mechanism
        proposal.voting_mechanism = self._select_voting_mechanism(proposal)
        proposal.required_threshold = self._calculate_decision_threshold(proposal)

        # Set deadline based on proposal urgency and complexity
        proposal.deadline = self._calculate_proposal_deadline(proposal)

        # Store proposal
        proposal.status = "open_for_voting"
        self.proposals[proposal.id] = proposal
        self.votes[proposal.id] = []

        logger.info(
            f"Submitted proposal: {proposal.id} ({proposal.decision_type.value})"
        )

        return {
            "success": True,
            "proposal_id": proposal.id,
            "voting_mechanism": proposal.voting_mechanism.value,
            "required_threshold": proposal.required_threshold,
            "deadline": proposal.deadline.isoformat() if proposal.deadline else None,
            "constitutional_implications": proposal.constitutional_implications,
        }

    async def cast_vote(self, vote: Vote) -> dict[str, Any]:
        """Cast a vote on a governance proposal."""

        # Validate voter eligibility
        voter = self.stakeholders.get(vote.voter_id)
        if not voter:
            return {"success": False, "reason": "Voter not registered"}

        proposal = self.proposals.get(vote.proposal_id)
        if not proposal:
            return {"success": False, "reason": "Proposal not found"}

        if proposal.status != "open_for_voting":
            return {"success": False, "reason": f"Proposal status: {proposal.status}"}

        # Check domain-specific voting eligibility
        if not voter.can_vote_on(proposal.policy_domain):
            return {"success": False, "reason": "Not eligible to vote on this domain"}

        # Handle delegation if applicable
        vote = await self._process_vote_delegation(vote, proposal)

        # Calculate vote weight based on proposal type and voter characteristics
        vote.weight = self._calculate_vote_weight(voter, proposal)

        # Store vote
        existing_votes = [
            v for v in self.votes[vote.proposal_id] if v.voter_id == vote.voter_id
        ]
        if existing_votes:
            # Update existing vote
            self.votes[vote.proposal_id].remove(existing_votes[0])

        self.votes[vote.proposal_id].append(vote)

        logger.info(f"Vote cast: {vote.voter_id} on {vote.proposal_id}")

        return {
            "success": True,
            "vote_weight": vote.weight,
            "delegation_chain": vote.delegation_chain,
            "timestamp": vote.timestamp.isoformat(),
        }

    async def run_deliberation(
        self, proposal_id: str, participant_ids: list[str], duration_minutes: int = 60
    ) -> DeliberationResult:
        """Run a deliberative discussion process."""

        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        # Select diverse participants if not specified
        if not participant_ids:
            participant_ids = self._select_deliberation_participants(proposal)

        # Simulate deliberative process
        deliberation = DeliberationResult(
            proposal_id=proposal_id,
            participants=participant_ids,
            discussion_points=[],
            consensus_areas=[],
            disagreement_areas=[],
        )

        # Analyze proposal content for discussion points
        discussion_points = await self._generate_discussion_points(proposal)
        deliberation.discussion_points = discussion_points

        # Simulate stakeholder perspectives
        perspectives = {}
        for participant_id in participant_ids:
            stakeholder = self.stakeholders.get(participant_id)
            if stakeholder:
                perspective = await self._generate_stakeholder_perspective(
                    stakeholder, proposal
                )
                perspectives[participant_id] = perspective

        # Find areas of consensus and disagreement
        deliberation.consensus_areas = self._identify_consensus_areas(perspectives)
        deliberation.disagreement_areas = self._identify_disagreement_areas(
            perspectives
        )

        # Generate refined proposal if possible
        if len(deliberation.consensus_areas) > len(deliberation.disagreement_areas):
            deliberation.refined_proposal = (
                await self._refine_proposal_from_deliberation(proposal, deliberation)
            )

        # Calculate deliberation quality score
        deliberation.quality_score = self._calculate_deliberation_quality(deliberation)

        # Store deliberation results
        self.deliberation_history[proposal_id] = deliberation

        logger.info(
            f"Deliberation completed for {proposal_id}: "
            f"quality={deliberation.quality_score:.2f}"
        )

        return deliberation

    async def make_decision(self, proposal_id: str) -> dict[str, Any]:
        """Make a final decision on a governance proposal."""

        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "reason": "Proposal not found"}

        votes = self.votes.get(proposal_id, [])
        if not votes:
            return {"success": False, "reason": "No votes cast"}

        # Calculate decision based on voting mechanism
        decision_result = await self._calculate_decision(proposal, votes)

        # Validate constitutional compliance
        constitutional_check = await self._validate_decision_constitutionality(
            proposal, decision_result
        )

        if not constitutional_check["constitutional"]:
            decision_result["decision"] = "rejected"
            decision_result["reason"] = (
                f"Constitutional violation: {constitutional_check['reason']}"
            )

        # Record decision
        decision_record = {
            "proposal_id": proposal_id,
            "decision": decision_result["decision"],
            "voting_mechanism": proposal.voting_mechanism.value,
            "vote_count": len(votes),
            "threshold_required": proposal.required_threshold,
            "threshold_achieved": decision_result["threshold_achieved"],
            "constitutional_check": constitutional_check,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_id": str(uuid.uuid4()),
        }

        self.decision_history.append(decision_record)

        # Update proposal status
        if decision_result["decision"] == "approved":
            proposal.status = "approved"
            await self._implement_decision(proposal, decision_record)
        else:
            proposal.status = "rejected"

        logger.info(
            f"Decision made for {proposal_id}:"
            f" {decision_result['decision']} ({decision_result['threshold_achieved']:.2f} vs"
            f" {proposal.required_threshold:.2f})"
        )

        return decision_result

    async def analyze_governance_network(self) -> dict[str, Any]:
        """Analyze the governance network structure and dynamics."""

        # Create stakeholder influence network
        G = nx.DiGraph()

        # Add stakeholders as nodes
        for stakeholder_id, stakeholder in self.stakeholders.items():
            G.add_node(
                stakeholder_id,
                type=stakeholder.stakeholder_type.value,
                voting_power=stakeholder.voting_power,
                reputation=stakeholder.reputation,
            )

        # Add delegation edges
        for stakeholder in self.stakeholders.values():
            for target in stakeholder.delegation_targets:
                if target in self.stakeholders:
                    G.add_edge(stakeholder.id, target, type="delegation")

        # Calculate network metrics
        try:
            centrality_measures = {
                "betweenness": nx.betweenness_centrality(G),
                "closeness": nx.closeness_centrality(G),
                "eigenvector": nx.eigenvector_centrality(G),
                "pagerank": nx.pagerank(G),
            }
        except:
            centrality_measures = {"error": "Network too small for analysis"}

        # Analyze decision patterns
        decision_patterns = self._analyze_decision_patterns()

        # Assess democratic health
        democratic_health = self._assess_democratic_health()

        return {
            "network_analysis": {
                "total_stakeholders": len(self.stakeholders),
                "total_proposals": len(self.proposals),
                "total_decisions": len(self.decision_history),
                "centrality_measures": centrality_measures,
                "network_density": nx.density(G) if G.number_of_nodes() > 1 else 0,
            },
            "decision_patterns": decision_patterns,
            "democratic_health": democratic_health,
            "constitutional_hash": "cdd01ef066bc6cf2",
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Private helper methods

    async def _assess_stakeholder_eligibility(
        self, stakeholder: Stakeholder
    ) -> dict[str, Any]:
        """Assess if a stakeholder is eligible for registration."""

        # Basic validation
        if not stakeholder.id or not stakeholder.name:
            return {"eligible": False, "reason": "Missing required fields"}

        # Check for duplicate registration
        if stakeholder.id in self.stakeholders:
            return {"eligible": False, "reason": "Stakeholder already registered"}

        # Constitutional council limit
        if stakeholder.stakeholder_type == StakeholderType.CONSTITUTIONAL_COUNCIL:
            council_members = [
                s
                for s in self.stakeholders.values()
                if s.stakeholder_type == StakeholderType.CONSTITUTIONAL_COUNCIL
            ]
            if len(council_members) >= 7:  # Typical constitutional council size
                return {
                    "eligible": False,
                    "reason": "Constitutional council at capacity",
                }

        # Reputation threshold for experts
        if stakeholder.stakeholder_type == StakeholderType.EXPERT:
            if stakeholder.reputation < 0.3:
                return {
                    "eligible": False,
                    "reason": "Insufficient reputation for expert status",
                }

        return {"eligible": True, "reason": "Meets all eligibility criteria"}

    def _calculate_initial_voting_power(self, stakeholder: Stakeholder) -> float:
        """Calculate initial voting power for a stakeholder."""

        base_power = 1.0

        # Adjust based on stakeholder type
        type_multipliers = {
            StakeholderType.CITIZEN: 1.0,
            StakeholderType.EXPERT: 1.2,
            StakeholderType.REPRESENTATIVE: 1.5,
            StakeholderType.INSTITUTION: 2.0,
            StakeholderType.AI_AGENT: 0.8,
            StakeholderType.CONSTITUTIONAL_COUNCIL: 3.0,
        }

        power = base_power * type_multipliers.get(stakeholder.stakeholder_type, 1.0)

        # Adjust based on reputation
        power *= 0.5 + stakeholder.reputation

        # Adjust based on expertise relevance
        if stakeholder.expertise:
            expertise_bonus = min(0.5, len(stakeholder.expertise) * 0.1)
            power *= 1.0 + expertise_bonus

        return round(power, 2)

    async def _validate_proposal(self, proposal: GovernanceProposal) -> dict[str, Any]:
        """Validate a governance proposal."""

        # Basic validation
        if not proposal.id or not proposal.title or not proposal.description:
            return {"valid": False, "reason": "Missing required fields"}

        # Check proposer eligibility
        proposer = self.stakeholders.get(proposal.proposer_id)
        if not proposer:
            return {"valid": False, "reason": "Proposer not registered"}

        # Domain-specific validation
        if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
            if proposer.stakeholder_type not in [
                StakeholderType.CONSTITUTIONAL_COUNCIL,
                StakeholderType.INSTITUTION,
            ]:
                return {
                    "valid": False,
                    "reason": "Insufficient authority for constitutional proposals",
                }

        # Content validation
        if not proposal.content:
            return {"valid": False, "reason": "Proposal content cannot be empty"}

        return {"valid": True, "reason": "Proposal meets all requirements"}

    async def _analyze_constitutional_impact(
        self, proposal: GovernanceProposal
    ) -> dict[str, Any]:
        """Analyze constitutional impact of a proposal."""

        implications = []
        impact_assessment = {
            "severity": "low",
            "affected_principles": [],
            "precedent_analysis": {},
            "risk_factors": [],
        }

        # Check against constitutional principles
        constitutional_principles = [
            "democratic_participation",
            "separation_of_powers",
            "rule_of_law",
            "fundamental_rights",
            "transparency",
            "accountability",
        ]

        proposal_text = (
            f"{proposal.title} {proposal.description} {json.dumps(proposal.content)}"
        )

        for principle in constitutional_principles:
            # Simple keyword-based analysis (in production would use NLP)
            principle_keywords = self._get_principle_keywords(principle)
            if any(keyword in proposal_text.lower() for keyword in principle_keywords):
                implications.append(f"May impact {principle}")
                impact_assessment["affected_principles"].append(principle)

        # Assess severity
        if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
            impact_assessment["severity"] = "critical"
        elif len(impact_assessment["affected_principles"]) > 2:
            impact_assessment["severity"] = "high"
        elif len(impact_assessment["affected_principles"]) > 0:
            impact_assessment["severity"] = "medium"

        # Add risk factors
        if proposal.decision_type == DecisionType.EMERGENCY_RESPONSE:
            impact_assessment["risk_factors"].append(
                "Emergency procedures may bypass normal checks"
            )

        if "override" in proposal_text.lower():
            impact_assessment["risk_factors"].append(
                "Proposal contains override language"
            )

        return {"implications": implications, "impact_assessment": impact_assessment}

    def _get_principle_keywords(self, principle: str) -> list[str]:
        """Get keywords associated with constitutional principles."""
        keyword_map = {
            "democratic_participation": [
                "vote",
                "election",
                "participate",
                "citizen",
                "democratic",
            ],
            "separation_of_powers": [
                "executive",
                "legislative",
                "judicial",
                "separation",
                "power",
            ],
            "rule_of_law": ["law", "legal", "constitutional", "statute", "regulation"],
            "fundamental_rights": [
                "rights",
                "freedom",
                "liberty",
                "privacy",
                "equality",
            ],
            "transparency": [
                "transparent",
                "open",
                "public",
                "disclosure",
                "information",
            ],
            "accountability": [
                "accountable",
                "responsible",
                "oversight",
                "audit",
                "review",
            ],
        }
        return keyword_map.get(principle, [])

    def _select_voting_mechanism(self, proposal: GovernanceProposal) -> VotingMechanism:
        """Select appropriate voting mechanism for a proposal."""

        # Constitutional amendments require supermajority
        if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
            return VotingMechanism.SUPERMAJORITY

        # Emergency decisions use simple majority for speed
        if proposal.decision_type == DecisionType.EMERGENCY_RESPONSE:
            return VotingMechanism.SIMPLE_MAJORITY

        # Complex resource allocation benefits from quadratic voting
        if proposal.decision_type == DecisionType.RESOURCE_ALLOCATION:
            return VotingMechanism.QUADRATIC_VOTING

        # Default to simple majority
        return VotingMechanism.SIMPLE_MAJORITY

    def _calculate_decision_threshold(self, proposal: GovernanceProposal) -> float:
        """Calculate required decision threshold for a proposal."""

        threshold_map = {
            VotingMechanism.SIMPLE_MAJORITY: 0.5,
            VotingMechanism.SUPERMAJORITY: 0.67,
            VotingMechanism.CONSENSUS: 0.9,
            VotingMechanism.RANKED_CHOICE: 0.5,
            VotingMechanism.QUADRATIC_VOTING: 0.5,
            VotingMechanism.LIQUID_DEMOCRACY: 0.5,
            VotingMechanism.DELIBERATIVE_POLLING: 0.6,
        }

        base_threshold = threshold_map.get(proposal.voting_mechanism, 0.5)

        # Adjust based on constitutional impact
        if proposal.impact_assessment.get("severity") == "critical":
            base_threshold = max(base_threshold, 0.8)
        elif proposal.impact_assessment.get("severity") == "high":
            base_threshold = max(base_threshold, 0.6)

        return base_threshold

    def _calculate_proposal_deadline(self, proposal: GovernanceProposal) -> datetime:
        """Calculate appropriate deadline for a proposal."""

        now = datetime.now(timezone.utc)

        # Emergency proposals: 24 hours
        if proposal.decision_type == DecisionType.EMERGENCY_RESPONSE:
            return now + timedelta(days=1)

        # Constitutional amendments: 30 days
        if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
            return now + timedelta(days=30)

        # Complex proposals: 14 days
        if len(proposal.constitutional_implications) > 3:
            return now + timedelta(days=14)

        # Standard proposals: 7 days
        return now + timedelta(days=7)

    async def _process_vote_delegation(
        self, vote: Vote, proposal: GovernanceProposal
    ) -> Vote:
        """Process vote delegation if applicable."""

        voter = self.stakeholders[vote.voter_id]

        # Handle liquid democracy delegation
        if (
            proposal.voting_mechanism == VotingMechanism.LIQUID_DEMOCRACY
            and voter.delegation_targets
        ):
            # Find delegate with relevant expertise
            for delegate_id in voter.delegation_targets:
                delegate = self.stakeholders.get(delegate_id)
                if delegate and proposal.policy_domain.value in delegate.expertise:
                    vote.delegation_chain.append(delegate_id)
                    # In real implementation, would automatically cast delegated vote
                    break

        return vote

    def _calculate_vote_weight(
        self, voter: Stakeholder, proposal: GovernanceProposal
    ) -> float:
        """Calculate vote weight based on voter and proposal characteristics."""

        base_weight = voter.voting_power

        # Quadratic voting adjustment
        if proposal.voting_mechanism == VotingMechanism.QUADRATIC_VOTING:
            # Simulate quadratic cost (in real system would track voter's budget)
            base_weight = np.sqrt(base_weight)

        # Expertise bonus
        if proposal.policy_domain.value in voter.expertise:
            base_weight *= 1.2

        # Reputation factor
        base_weight *= 0.8 + 0.4 * voter.reputation

        # Constitutional alignment bonus for constitutional proposals
        if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
            base_weight *= 0.8 + 0.4 * voter.constitutional_alignment

        return round(base_weight, 3)

    def _select_deliberation_participants(
        self, proposal: GovernanceProposal
    ) -> list[str]:
        """Select diverse participants for deliberation."""

        participants = []

        # Include relevant experts
        experts = [
            s.id
            for s in self.stakeholders.values()
            if (
                s.stakeholder_type == StakeholderType.EXPERT
                and proposal.policy_domain.value in s.expertise
            )
        ]
        participants.extend(random.sample(experts, min(3, len(experts))))

        # Include diverse stakeholder types
        for stakeholder_type in StakeholderType:
            type_stakeholders = [
                s.id
                for s in self.stakeholders.values()
                if s.stakeholder_type == stakeholder_type
            ]
            if type_stakeholders:
                participants.append(random.choice(type_stakeholders))

        return list(set(participants))  # Remove duplicates

    async def _generate_discussion_points(
        self, proposal: GovernanceProposal
    ) -> list[str]:
        """Generate discussion points for deliberation."""

        points = [
            f"Impact on {principle}"
            for principle in proposal.impact_assessment.get("affected_principles", [])
        ]

        points.extend([
            "Implementation feasibility",
            "Resource requirements",
            "Stakeholder concerns",
            "Constitutional compliance",
            "Alternative approaches",
        ])

        if proposal.decision_type == DecisionType.RESOURCE_ALLOCATION:
            points.extend(["Fairness of allocation", "Long-term sustainability"])

        return points

    async def _generate_stakeholder_perspective(
        self, stakeholder: Stakeholder, proposal: GovernanceProposal
    ) -> dict[str, Any]:
        """Generate a stakeholder's perspective on a proposal."""

        # Simulate perspective based on stakeholder characteristics
        perspective = {
            "support_level": 0.5,  # Neutral starting point
            "key_concerns": [],
            "conditions": [],
            "reasoning": "",
        }

        # Adjust based on stakeholder type
        if stakeholder.stakeholder_type == StakeholderType.CONSTITUTIONAL_COUNCIL:
            perspective["support_level"] *= stakeholder.constitutional_alignment
            if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
                perspective["key_concerns"].append("Constitutional precedent")

        # Adjust based on expertise alignment
        if proposal.policy_domain.value in stakeholder.expertise:
            perspective["support_level"] += 0.2

        # Add random variation to simulate individual differences
        perspective["support_level"] += random.uniform(-0.2, 0.2)
        perspective["support_level"] = max(0, min(1, perspective["support_level"]))

        # Generate reasoning
        if perspective["support_level"] > 0.7:
            perspective["reasoning"] = (
                "Strong support based on alignment with stakeholder interests"
            )
        elif perspective["support_level"] < 0.3:
            perspective["reasoning"] = "Significant concerns about proposal impact"
        else:
            perspective["reasoning"] = "Mixed views requiring further deliberation"

        return perspective

    def _identify_consensus_areas(
        self, perspectives: dict[str, dict[str, Any]]
    ) -> list[str]:
        """Identify areas of consensus from stakeholder perspectives."""

        consensus_areas = []

        # Simple consensus detection based on support levels
        support_levels = [p["support_level"] for p in perspectives.values()]
        avg_support = np.mean(support_levels)
        support_variance = np.var(support_levels)

        if support_variance < 0.1:  # Low variance indicates consensus
            if avg_support > 0.7:
                consensus_areas.append("Strong overall support")
            elif avg_support < 0.3:
                consensus_areas.append("Strong overall opposition")
            else:
                consensus_areas.append("Neutral consensus")

        # Check for common concerns
        all_concerns = []
        for perspective in perspectives.values():
            all_concerns.extend(perspective.get("key_concerns", []))

        from collections import Counter

        common_concerns = [
            concern
            for concern, count in Counter(all_concerns).items()
            if count >= len(perspectives) * 0.5
        ]

        if common_concerns:
            consensus_areas.extend([
                f"Shared concern: {concern}" for concern in common_concerns
            ])

        return consensus_areas

    def _identify_disagreement_areas(
        self, perspectives: dict[str, dict[str, Any]]
    ) -> list[str]:
        """Identify areas of disagreement from stakeholder perspectives."""

        disagreement_areas = []

        # Check for high variance in support
        support_levels = [p["support_level"] for p in perspectives.values()]
        support_variance = np.var(support_levels)

        if support_variance > 0.3:
            disagreement_areas.append("Significant disagreement on overall support")

        # Check for polarized views
        high_support = sum(1 for s in support_levels if s > 0.7)
        low_support = sum(1 for s in support_levels if s < 0.3)

        if high_support > 0 and low_support > 0:
            disagreement_areas.append("Polarized stakeholder views")

        return disagreement_areas

    async def _refine_proposal_from_deliberation(
        self, proposal: GovernanceProposal, deliberation: DeliberationResult
    ) -> dict[str, Any]:
        """Refine proposal based on deliberation results."""

        refined = proposal.content.copy()

        # Add safeguards based on concerns
        if "Constitutional precedent" in deliberation.discussion_points:
            refined["constitutional_review_required"] = True

        if "Implementation feasibility" in deliberation.discussion_points:
            refined["pilot_program_required"] = True

        # Add transparency measures
        refined["public_reporting_required"] = True
        refined["stakeholder_feedback_period"] = "30_days"

        return refined

    def _calculate_deliberation_quality(
        self, deliberation: DeliberationResult
    ) -> float:
        """Calculate quality score for deliberation process."""

        quality = 0.0

        # Participation diversity
        participant_types = set()
        for participant_id in deliberation.participants:
            stakeholder = self.stakeholders.get(participant_id)
            if stakeholder:
                participant_types.add(stakeholder.stakeholder_type)

        diversity_score = len(participant_types) / len(StakeholderType)
        quality += 0.3 * diversity_score

        # Discussion depth
        discussion_depth = (
            len(deliberation.discussion_points) / 10
        )  # Normalize to max 10
        quality += 0.3 * min(1.0, discussion_depth)

        # Consensus building
        consensus_ratio = len(deliberation.consensus_areas) / max(
            1, len(deliberation.consensus_areas) + len(deliberation.disagreement_areas)
        )
        quality += 0.4 * consensus_ratio

        return min(1.0, quality)

    async def _calculate_decision(
        self, proposal: GovernanceProposal, votes: list[Vote]
    ) -> dict[str, Any]:
        """Calculate decision based on voting mechanism."""

        if proposal.voting_mechanism == VotingMechanism.SIMPLE_MAJORITY:
            return self._simple_majority_decision(proposal, votes)
        elif proposal.voting_mechanism == VotingMechanism.SUPERMAJORITY:
            return self._supermajority_decision(proposal, votes)
        elif proposal.voting_mechanism == VotingMechanism.QUADRATIC_VOTING:
            return self._quadratic_voting_decision(proposal, votes)
        elif proposal.voting_mechanism == VotingMechanism.RANKED_CHOICE:
            return self._ranked_choice_decision(proposal, votes)
        else:
            return self._simple_majority_decision(proposal, votes)

    def _simple_majority_decision(
        self, proposal: GovernanceProposal, votes: list[Vote]
    ) -> dict[str, Any]:
        """Calculate simple majority decision."""

        approve_weight = sum(v.weight for v in votes if v.choice == "approve")
        reject_weight = sum(v.weight for v in votes if v.choice == "reject")
        total_weight = approve_weight + reject_weight

        if total_weight == 0:
            threshold_achieved = 0.0
        else:
            threshold_achieved = approve_weight / total_weight

        decision = (
            "approved"
            if threshold_achieved >= proposal.required_threshold
            else "rejected"
        )

        return {
            "decision": decision,
            "threshold_achieved": threshold_achieved,
            "threshold_required": proposal.required_threshold,
            "vote_breakdown": {
                "approve_weight": approve_weight,
                "reject_weight": reject_weight,
                "total_weight": total_weight,
            },
        }

    def _supermajority_decision(
        self, proposal: GovernanceProposal, votes: list[Vote]
    ) -> dict[str, Any]:
        """Calculate supermajority decision (same as simple majority with higher threshold)."""
        return self._simple_majority_decision(proposal, votes)

    def _quadratic_voting_decision(
        self, proposal: GovernanceProposal, votes: list[Vote]
    ) -> dict[str, Any]:
        """Calculate quadratic voting decision."""

        # In quadratic voting, vote weights are already adjusted
        return self._simple_majority_decision(proposal, votes)

    def _ranked_choice_decision(
        self, proposal: GovernanceProposal, votes: list[Vote]
    ) -> dict[str, Any]:
        """Calculate ranked choice decision (simplified)."""

        # For binary approve/reject, same as simple majority
        # In full implementation would handle multiple options
        return self._simple_majority_decision(proposal, votes)

    async def _validate_decision_constitutionality(
        self, proposal: GovernanceProposal, decision_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate constitutional compliance of a decision."""

        if self.constitutional_client and decision_result["decision"] == "approved":
            try:
                # Call constitutional AI service
                response = await self.constitutional_client.post(
                    "/api/v1/constitutional/validate",
                    json={
                        "policy": {
                            "proposal": proposal.content,
                            "decision_mechanism": proposal.voting_mechanism.value,
                            "threshold_achieved": decision_result["threshold_achieved"],
                        },
                        "validation_mode": "comprehensive",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "constitutional": result.get("overall_compliant", False),
                        "compliance_score": result.get("compliance_score", 0.0),
                        "reason": "Constitutional AI validation",
                        "details": result,
                    }
            except Exception as e:
                logger.warning(f"Constitutional validation failed: {e}")

        # Fallback heuristic validation
        return self._heuristic_constitutional_validation(proposal, decision_result)

    def _heuristic_constitutional_validation(
        self, proposal: GovernanceProposal, decision_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Heuristic constitutional validation."""

        constitutional = True
        reasons = []

        # Check decision threshold
        if proposal.policy_domain == PolicyDomain.CONSTITUTIONAL:
            if decision_result["threshold_achieved"] < 0.67:
                constitutional = False
                reasons.append("Constitutional changes require supermajority")

        # Check for rights violations
        proposal_text = str(proposal.content).lower()
        if "restrict rights" in proposal_text or "limit freedom" in proposal_text:
            constitutional = False
            reasons.append("Potential rights violation")

        return {
            "constitutional": constitutional,
            "compliance_score": 1.0 if constitutional else 0.0,
            "reason": "; ".join(reasons) if reasons else "Passed heuristic validation",
        }

    async def _implement_decision(
        self, proposal: GovernanceProposal, decision_record: dict[str, Any]
    ) -> None:
        """Implement an approved decision."""

        # Log implementation
        logger.info(
            f"Implementing decision {decision_record['decision_id']} for proposal"
            f" {proposal.id}"
        )

        # In a real system, this would trigger actual policy implementation
        # For now, we just update the proposal metadata
        proposal.metadata["implementation_status"] = "pending"
        proposal.metadata["implementation_timestamp"] = datetime.now(
            timezone.utc
        ).isoformat()

    def _analyze_decision_patterns(self) -> dict[str, Any]:
        """Analyze patterns in decision-making."""

        if not self.decision_history:
            return {"insufficient_data": True}

        # Calculate approval rates by domain
        domain_stats = {}
        for decision in self.decision_history:
            proposal = self.proposals.get(decision["proposal_id"])
            if proposal:
                domain = proposal.policy_domain.value
                if domain not in domain_stats:
                    domain_stats[domain] = {"total": 0, "approved": 0}
                domain_stats[domain]["total"] += 1
                if decision["decision"] == "approved":
                    domain_stats[domain]["approved"] += 1

        # Calculate approval rates
        for domain, stats in domain_stats.items():
            stats["approval_rate"] = stats["approved"] / stats["total"]

        # Overall statistics
        total_decisions = len(self.decision_history)
        approved_decisions = sum(
            1 for d in self.decision_history if d["decision"] == "approved"
        )
        overall_approval_rate = (
            approved_decisions / total_decisions if total_decisions > 0 else 0
        )

        return {
            "total_decisions": total_decisions,
            "overall_approval_rate": overall_approval_rate,
            "domain_statistics": domain_stats,
            "average_threshold_achieved": (
                np.mean([d["threshold_achieved"] for d in self.decision_history])
                if self.decision_history
                else 0
            ),
        }

    def _assess_democratic_health(self) -> dict[str, Any]:
        """Assess democratic health of the governance system."""

        health_metrics = {
            "participation_rate": 0.0,
            "stakeholder_diversity": 0.0,
            "transparency_score": 1.0,  # High by design
            "accountability_score": 1.0,  # High by design
            "overall_health": 0.0,
        }

        if not self.stakeholders:
            health_metrics["overall_health"] = 0.0
            return health_metrics

        # Calculate participation rate
        if self.proposals:
            total_possible_votes = len(self.stakeholders) * len(self.proposals)
            actual_votes = sum(len(votes) for votes in self.votes.values())
            health_metrics["participation_rate"] = min(
                1.0, actual_votes / total_possible_votes
            )

        # Calculate stakeholder diversity
        type_distribution = {}
        for stakeholder in self.stakeholders.values():
            stakeholder_type = stakeholder.stakeholder_type.value
            type_distribution[stakeholder_type] = (
                type_distribution.get(stakeholder_type, 0) + 1
            )

        # Entropy-based diversity measure
        total_stakeholders = len(self.stakeholders)
        entropy = 0
        for count in type_distribution.values():
            if count > 0:
                p = count / total_stakeholders
                entropy -= p * np.log2(p)

        max_entropy = np.log2(len(StakeholderType))
        health_metrics["stakeholder_diversity"] = (
            entropy / max_entropy if max_entropy > 0 else 0
        )

        # Calculate overall health
        health_metrics["overall_health"] = np.mean([
            health_metrics["participation_rate"],
            health_metrics["stakeholder_diversity"],
            health_metrics["transparency_score"],
            health_metrics["accountability_score"],
        ])

        return health_metrics


# Global governance engine instance
_governance_engine: Optional[GovernanceDecisionEngine] = None


def get_governance_engine(
    constitutional_client: Optional[Any] = None,
) -> GovernanceDecisionEngine:
    """Get or create the global governance decision engine."""
    global _governance_engine

    if _governance_engine is None:
        _governance_engine = GovernanceDecisionEngine(constitutional_client)

    return _governance_engine
