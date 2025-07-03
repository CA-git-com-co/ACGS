"""
Consensus Mechanisms for Multi-Agent Conflict Resolution
Implements various consensus algorithms for resolving conflicts between agents.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from ...shared.blackboard import BlackboardService, ConflictItem


class ConsensusAlgorithm(str, Enum):
    """Available consensus algorithms"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    RANKED_CHOICE = "ranked_choice"
    CONSENSUS_THRESHOLD = "consensus_threshold"
    HIERARCHICAL_OVERRIDE = "hierarchical_override"
    CONSTITUTIONAL_PRIORITY = "constitutional_priority"
    EXPERT_MEDIATION = "expert_mediation"


class VoteOption(BaseModel):
    """Represents a voting option"""
    option_id: str = Field(default_factory=lambda: str(uuid4()))
    option_name: str
    description: str
    proposed_by: str
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    constitutional_score: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)


class Vote(BaseModel):
    """Represents a single vote"""
    voter_id: str
    voter_type: str  # 'agent', 'human', 'coordinator'
    option_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""
    cast_at: datetime = Field(default_factory=datetime.utcnow)
    weight: float = Field(default=1.0, ge=0.0)


class ConsensusSession(BaseModel):
    """Represents a consensus-building session"""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    conflict_id: str
    algorithm: ConsensusAlgorithm
    participants: List[str] = Field(default_factory=list)
    options: List[VoteOption] = Field(default_factory=list)
    votes: List[Vote] = Field(default_factory=list)
    status: str = Field(default="active")  # 'active', 'completed', 'failed', 'escalated'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    session_config: Dict[str, Any] = Field(default_factory=dict)


class MajorityVoteConsensus:
    """Simple majority voting consensus mechanism"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute majority vote consensus"""
        
        if not session.votes:
            return {
                'success': False,
                'reason': 'No votes cast',
                'result': None
            }
        
        # Count votes for each option
        vote_counts = {}
        for vote in session.votes:
            if vote.option_id not in vote_counts:
                vote_counts[vote.option_id] = 0
            vote_counts[vote.option_id] += 1
        
        # Find option with most votes
        winning_option_id = max(vote_counts, key=vote_counts.get)
        winning_votes = vote_counts[winning_option_id]
        total_votes = len(session.votes)
        
        # Check if majority achieved
        majority_threshold = total_votes / 2
        has_majority = winning_votes > majority_threshold
        
        winning_option = next((opt for opt in session.options if opt.option_id == winning_option_id), None)
        
        result = {
            'success': has_majority,
            'algorithm': 'majority_vote',
            'winning_option': winning_option.model_dump() if winning_option else None,
            'vote_distribution': vote_counts,
            'winning_votes': winning_votes,
            'total_votes': total_votes,
            'majority_achieved': has_majority,
            'confidence_score': winning_votes / total_votes if total_votes > 0 else 0.0
        }
        
        if not has_majority:
            result['reason'] = 'No majority achieved'
            result['next_steps'] = ['escalate', 'add_participants', 'extend_deadline']
        
        return result


class WeightedVoteConsensus:
    """Weighted voting consensus mechanism"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute weighted vote consensus"""
        
        if not session.votes:
            return {
                'success': False,
                'reason': 'No votes cast',
                'result': None
            }
        
        # Calculate weighted votes for each option
        weighted_counts = {}
        total_weight = 0
        
        for vote in session.votes:
            if vote.option_id not in weighted_counts:
                weighted_counts[vote.option_id] = 0
            
            # Weight based on voter confidence and assigned weight
            vote_weight = vote.weight * vote.confidence
            weighted_counts[vote.option_id] += vote_weight
            total_weight += vote_weight
        
        # Find option with highest weighted score
        winning_option_id = max(weighted_counts, key=weighted_counts.get)
        winning_weight = weighted_counts[winning_option_id]
        
        # Check if weighted majority achieved
        weighted_threshold = session.session_config.get('weighted_threshold', 0.5)
        weighted_percentage = winning_weight / total_weight if total_weight > 0 else 0.0
        has_weighted_majority = weighted_percentage >= weighted_threshold
        
        winning_option = next((opt for opt in session.options if opt.option_id == winning_option_id), None)
        
        result = {
            'success': has_weighted_majority,
            'algorithm': 'weighted_vote',
            'winning_option': winning_option.model_dump() if winning_option else None,
            'weighted_distribution': weighted_counts,
            'winning_weight': winning_weight,
            'total_weight': total_weight,
            'weighted_percentage': weighted_percentage,
            'threshold': weighted_threshold,
            'confidence_score': weighted_percentage
        }
        
        if not has_weighted_majority:
            result['reason'] = f'Weighted threshold not met: {weighted_percentage:.2f} < {weighted_threshold}'
            result['next_steps'] = ['escalate', 'adjust_weights', 'extend_deadline']
        
        return result


class RankedChoiceConsensus:
    """Ranked choice voting consensus mechanism"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute ranked choice consensus"""
        
        if not session.votes:
            return {
                'success': False,
                'reason': 'No votes cast',
                'result': None
            }
        
        # For ranked choice, we need ranking information in votes
        # For simplicity, we'll use confidence scores as proxy for ranking
        
        # Calculate score for each option based on confidence-weighted votes
        option_scores = {}
        for option in session.options:
            option_scores[option.option_id] = 0
        
        for vote in session.votes:
            # Higher confidence means higher preference
            option_scores[vote.option_id] += vote.confidence * vote.weight
        
        # Sort options by score
        sorted_options = sorted(option_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Check if top option has sufficient support
        if not sorted_options:
            return {
                'success': False,
                'reason': 'No valid options to rank',
                'result': None
            }
        
        winning_option_id = sorted_options[0][0]
        winning_score = sorted_options[0][1]
        
        # Calculate confidence based on score gap
        if len(sorted_options) > 1:
            second_score = sorted_options[1][1]
            score_gap = winning_score - second_score
            confidence = min(1.0, score_gap / winning_score) if winning_score > 0 else 0.0
        else:
            confidence = 1.0
        
        # Require minimum confidence for success
        min_confidence = session.session_config.get('min_confidence', 0.6)
        success = confidence >= min_confidence
        
        winning_option = next((opt for opt in session.options if opt.option_id == winning_option_id), None)
        
        result = {
            'success': success,
            'algorithm': 'ranked_choice',
            'winning_option': winning_option.model_dump() if winning_option else None,
            'option_rankings': [(opt_id, score) for opt_id, score in sorted_options],
            'confidence_score': confidence,
            'min_confidence_threshold': min_confidence,
            'score_gap': score_gap if len(sorted_options) > 1 else winning_score
        }
        
        if not success:
            result['reason'] = f'Insufficient confidence: {confidence:.2f} < {min_confidence}'
            result['next_steps'] = ['gather_more_input', 'expert_review', 'escalate']
        
        return result


class ConsensusThresholdConsensus:
    """Consensus threshold mechanism - requires minimum agreement level"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute consensus threshold mechanism"""
        
        if not session.votes:
            return {
                'success': False,
                'reason': 'No votes cast',
                'result': None
            }
        
        consensus_threshold = session.session_config.get('consensus_threshold', 0.8)  # 80% agreement
        
        # Calculate support level for each option
        option_support = {}
        total_participants = len(session.participants)
        
        for option in session.options:
            supporting_votes = [v for v in session.votes if v.option_id == option.option_id]
            support_level = len(supporting_votes) / total_participants if total_participants > 0 else 0.0
            
            # Weight by confidence
            weighted_support = sum(v.confidence for v in supporting_votes) / total_participants if total_participants > 0 else 0.0
            
            option_support[option.option_id] = {
                'vote_count': len(supporting_votes),
                'support_percentage': support_level,
                'weighted_support': weighted_support,
                'meets_threshold': weighted_support >= consensus_threshold
            }
        
        # Find options that meet consensus threshold
        consensus_options = [
            (opt_id, support) for opt_id, support in option_support.items() 
            if support['meets_threshold']
        ]
        
        if consensus_options:
            # Choose option with highest weighted support
            winning_option_id = max(consensus_options, key=lambda x: x[1]['weighted_support'])[0]
            winning_support = option_support[winning_option_id]
            success = True
        else:
            # No consensus achieved
            winning_option_id = max(option_support, key=lambda x: option_support[x]['weighted_support'])
            winning_support = option_support[winning_option_id]
            success = False
        
        winning_option = next((opt for opt in session.options if opt.option_id == winning_option_id), None)
        
        result = {
            'success': success,
            'algorithm': 'consensus_threshold',
            'winning_option': winning_option.model_dump() if winning_option else None,
            'option_support': option_support,
            'consensus_threshold': consensus_threshold,
            'achieved_consensus': success,
            'confidence_score': winning_support['weighted_support']
        }
        
        if not success:
            result['reason'] = f'Consensus threshold not met: {winning_support["weighted_support"]:.2f} < {consensus_threshold}'
            result['next_steps'] = ['facilitate_discussion', 'modify_options', 'lower_threshold']
        
        return result


class HierarchicalOverrideConsensus:
    """Hierarchical override mechanism - higher authority can override"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute hierarchical override consensus"""
        
        # Define hierarchy levels
        hierarchy_levels = {
            'coordinator': 100,
            'human_expert': 80,
            'senior_agent': 60,
            'agent': 40,
            'automated_system': 20
        }
        
        # Find highest authority vote
        highest_authority_vote = None
        highest_level = 0
        
        for vote in session.votes:
            voter_level = hierarchy_levels.get(vote.voter_type, 0)
            if voter_level > highest_level:
                highest_level = voter_level
                highest_authority_vote = vote
        
        if not highest_authority_vote:
            return {
                'success': False,
                'reason': 'No valid authority votes found',
                'result': None
            }
        
        # Check if override threshold is met
        override_threshold = session.session_config.get('override_threshold', 60)  # Minimum authority level
        can_override = highest_level >= override_threshold
        
        winning_option = next(
            (opt for opt in session.options if opt.option_id == highest_authority_vote.option_id), 
            None
        )
        
        # Also consider regular consensus if no override
        regular_consensus = None
        if not can_override and len(session.votes) > 1:
            # Fall back to majority vote
            majority_result = await MajorityVoteConsensus.execute_consensus(session, blackboard)
            regular_consensus = majority_result
        
        result = {
            'success': can_override or (regular_consensus and regular_consensus.get('success', False)),
            'algorithm': 'hierarchical_override',
            'override_applied': can_override,
            'highest_authority_level': highest_level,
            'override_threshold': override_threshold,
            'authority_vote': highest_authority_vote.model_dump() if highest_authority_vote else None,
            'winning_option': winning_option.model_dump() if winning_option else None,
            'fallback_consensus': regular_consensus,
            'confidence_score': highest_authority_vote.confidence if highest_authority_vote else 0.0
        }
        
        if not result['success']:
            result['reason'] = 'Insufficient authority level and no regular consensus'
            result['next_steps'] = ['escalate_to_higher_authority', 'seek_expert_input']
        
        return result


class ConstitutionalPriorityConsensus:
    """Constitutional priority mechanism - options ranked by constitutional compliance"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute constitutional priority consensus"""
        
        if not session.options:
            return {
                'success': False,
                'reason': 'No options available',
                'result': None
            }
        
        # Rank options by constitutional score
        constitutional_ranking = sorted(
            session.options, 
            key=lambda opt: opt.constitutional_score, 
            reverse=True
        )
        
        # Get highest constitutional score option
        top_constitutional_option = constitutional_ranking[0]
        
        # Check if it meets minimum constitutional threshold
        min_constitutional_score = session.session_config.get('min_constitutional_score', 0.7)
        meets_constitutional_threshold = top_constitutional_option.constitutional_score >= min_constitutional_score
        
        # Consider votes as well - weighted by constitutional compliance
        if session.votes:
            option_scores = {}
            for option in session.options:
                # Base score from constitutional compliance
                base_score = option.constitutional_score
                
                # Add voting support weighted by constitutional score
                supporting_votes = [v for v in session.votes if v.option_id == option.option_id]
                vote_support = sum(v.confidence * v.weight for v in supporting_votes)
                
                # Combined score: constitutional compliance + voting support
                combined_score = (base_score * 0.7) + (vote_support * 0.3)
                option_scores[option.option_id] = combined_score
            
            # Find highest combined score
            winning_option_id = max(option_scores, key=option_scores.get)
            winning_option = next(
                (opt for opt in session.options if opt.option_id == winning_option_id), 
                None
            )
            final_score = option_scores[winning_option_id]
        else:
            # No votes, use pure constitutional ranking
            winning_option = top_constitutional_option
            final_score = winning_option.constitutional_score
        
        # Success if constitutional threshold is met
        success = winning_option.constitutional_score >= min_constitutional_score
        
        result = {
            'success': success,
            'algorithm': 'constitutional_priority',
            'winning_option': winning_option.model_dump() if winning_option else None,
            'constitutional_ranking': [
                {
                    'option_id': opt.option_id,
                    'option_name': opt.option_name,
                    'constitutional_score': opt.constitutional_score
                } for opt in constitutional_ranking
            ],
            'min_constitutional_threshold': min_constitutional_score,
            'winning_constitutional_score': winning_option.constitutional_score if winning_option else 0.0,
            'confidence_score': final_score
        }
        
        if not success:
            result['reason'] = f'Constitutional threshold not met: {winning_option.constitutional_score:.2f} < {min_constitutional_score}'
            result['next_steps'] = ['improve_constitutional_compliance', 'seek_expert_review', 'escalate']
        
        return result


class ExpertMediationConsensus:
    """Expert mediation mechanism - human experts facilitate consensus"""
    
    @staticmethod
    async def execute_consensus(
        session: ConsensusSession,
        blackboard: BlackboardService
    ) -> Dict[str, Any]:
        """Execute expert mediation consensus"""
        
        # Check if human experts are involved
        expert_votes = [v for v in session.votes if v.voter_type in ['human_expert', 'human']]
        
        if not expert_votes:
            return {
                'success': False,
                'reason': 'No expert input available for mediation',
                'result': None,
                'next_steps': ['request_expert_input', 'escalate_for_human_review']
            }
        
        # Expert consensus requires agreement between experts
        expert_options = {}
        for vote in expert_votes:
            if vote.option_id not in expert_options:
                expert_options[vote.option_id] = []
            expert_options[vote.option_id].append(vote)
        
        # Check for expert consensus
        expert_threshold = session.session_config.get('expert_consensus_threshold', 0.7)
        total_experts = len(expert_votes)
        
        consensus_achieved = False
        winning_option_id = None
        expert_agreement_level = 0.0
        
        for option_id, votes in expert_options.items():
            agreement_level = len(votes) / total_experts
            if agreement_level >= expert_threshold:
                consensus_achieved = True
                winning_option_id = option_id
                expert_agreement_level = agreement_level
                break
        
        # If no expert consensus, use highest expert support
        if not consensus_achieved and expert_options:
            winning_option_id = max(expert_options, key=lambda x: len(expert_options[x]))
            expert_agreement_level = len(expert_options[winning_option_id]) / total_experts
        
        winning_option = next(
            (opt for opt in session.options if opt.option_id == winning_option_id), 
            None
        ) if winning_option_id else None
        
        # Consider agent input as supporting evidence
        agent_votes = [v for v in session.votes if v.voter_type not in ['human_expert', 'human']]
        agent_support = {}
        if agent_votes:
            for vote in agent_votes:
                if vote.option_id not in agent_support:
                    agent_support[vote.option_id] = 0
                agent_support[vote.option_id] += vote.confidence * vote.weight
        
        result = {
            'success': consensus_achieved,
            'algorithm': 'expert_mediation',
            'winning_option': winning_option.model_dump() if winning_option else None,
            'expert_consensus_achieved': consensus_achieved,
            'expert_agreement_level': expert_agreement_level,
            'expert_threshold': expert_threshold,
            'total_experts': total_experts,
            'expert_vote_distribution': {opt_id: len(votes) for opt_id, votes in expert_options.items()},
            'agent_support': agent_support,
            'confidence_score': expert_agreement_level
        }
        
        if not consensus_achieved:
            result['reason'] = f'Expert consensus not achieved: {expert_agreement_level:.2f} < {expert_threshold}'
            result['next_steps'] = ['facilitate_expert_discussion', 'seek_additional_experts', 'escalate']
        
        return result


class ConsensusEngine:
    """Main consensus engine that coordinates different consensus mechanisms"""
    
    def __init__(self, blackboard_service: BlackboardService):
        self.blackboard = blackboard_service
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, ConsensusSession] = {}
        
        # Algorithm implementations
        self.algorithms = {
            ConsensusAlgorithm.MAJORITY_VOTE: MajorityVoteConsensus,
            ConsensusAlgorithm.WEIGHTED_VOTE: WeightedVoteConsensus,
            ConsensusAlgorithm.RANKED_CHOICE: RankedChoiceConsensus,
            ConsensusAlgorithm.CONSENSUS_THRESHOLD: ConsensusThresholdConsensus,
            ConsensusAlgorithm.HIERARCHICAL_OVERRIDE: HierarchicalOverrideConsensus,
            ConsensusAlgorithm.CONSTITUTIONAL_PRIORITY: ConstitutionalPriorityConsensus,
            ConsensusAlgorithm.EXPERT_MEDIATION: ExpertMediationConsensus
        }

    async def initiate_consensus(
        self,
        conflict: ConflictItem,
        algorithm: ConsensusAlgorithm,
        participants: List[str],
        options: List[VoteOption],
        deadline_hours: int = 24,
        session_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Initiate a consensus session for conflict resolution"""
        
        session = ConsensusSession(
            conflict_id=conflict.id,
            algorithm=algorithm,
            participants=participants,
            options=options,
            deadline=datetime.utcnow() + timedelta(hours=deadline_hours),
            session_config=session_config or {}
        )
        
        self.active_sessions[session.session_id] = session
        
        # Add session knowledge to blackboard
        await self._add_session_knowledge(session, 'initiated')
        
        self.logger.info(f"Initiated consensus session {session.session_id} for conflict {conflict.id}")
        return session.session_id

    async def cast_vote(
        self,
        session_id: str,
        voter_id: str,
        voter_type: str,
        option_id: str,
        confidence: float,
        reasoning: str = "",
        weight: float = 1.0
    ) -> bool:
        """Cast a vote in a consensus session"""
        
        if session_id not in self.active_sessions:
            self.logger.error(f"Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        
        if session.status != 'active':
            self.logger.error(f"Session {session_id} is not active (status: {session.status})")
            return False
        
        # Check if voter is authorized
        if voter_id not in session.participants:
            self.logger.error(f"Voter {voter_id} not authorized for session {session_id}")
            return False
        
        # Check if option exists
        if not any(opt.option_id == option_id for opt in session.options):
            self.logger.error(f"Option {option_id} not found in session {session_id}")
            return False
        
        # Remove any existing vote from this voter (allow vote changes)
        session.votes = [v for v in session.votes if v.voter_id != voter_id]
        
        # Add new vote
        vote = Vote(
            voter_id=voter_id,
            voter_type=voter_type,
            option_id=option_id,
            confidence=confidence,
            reasoning=reasoning,
            weight=weight
        )
        
        session.votes.append(vote)
        
        # Update session knowledge
        await self._add_session_knowledge(session, 'vote_cast', {'voter_id': voter_id, 'option_id': option_id})
        
        self.logger.info(f"Vote cast by {voter_id} in session {session_id}")
        return True

    async def execute_consensus(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Execute consensus algorithm for a session"""
        
        if session_id not in self.active_sessions:
            self.logger.error(f"Session {session_id} not found")
            return None
        
        session = self.active_sessions[session_id]
        
        if session.status != 'active':
            self.logger.error(f"Session {session_id} is not active")
            return None
        
        # Get algorithm implementation
        algorithm_class = self.algorithms.get(session.algorithm)
        if not algorithm_class:
            self.logger.error(f"Algorithm {session.algorithm} not implemented")
            return None
        
        try:
            # Execute consensus algorithm
            result = await algorithm_class.execute_consensus(session, self.blackboard)
            
            # Update session with result
            session.result = result
            session.status = 'completed' if result.get('success', False) else 'failed'
            
            # Add result knowledge to blackboard
            await self._add_session_knowledge(session, 'completed', {'result': result})
            
            # If consensus failed, check for escalation
            if not result.get('success', False):
                await self._handle_failed_consensus(session)
            
            self.logger.info(f"Consensus executed for session {session_id}, success: {result.get('success', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing consensus for session {session_id}: {str(e)}")
            session.status = 'failed'
            session.result = {'success': False, 'error': str(e)}
            return session.result

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a consensus session"""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            'session_id': session.session_id,
            'conflict_id': session.conflict_id,
            'algorithm': session.algorithm,
            'status': session.status,
            'participants': session.participants,
            'options_count': len(session.options),
            'votes_count': len(session.votes),
            'deadline': session.deadline.isoformat() if session.deadline else None,
            'result': session.result,
            'created_at': session.created_at.isoformat()
        }

    async def check_session_deadlines(self) -> List[str]:
        """Check for sessions that have passed their deadlines"""
        
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if (session.status == 'active' and 
                session.deadline and 
                current_time > session.deadline):
                
                # Mark session as expired
                session.status = 'failed'
                session.result = {
                    'success': False,
                    'reason': 'Deadline expired',
                    'deadline': session.deadline.isoformat()
                }
                
                expired_sessions.append(session_id)
                await self._add_session_knowledge(session, 'expired')
                
                # Attempt escalation
                await self._handle_failed_consensus(session)
        
        return expired_sessions

    async def escalate_session(
        self,
        session_id: str,
        escalation_type: str = 'human_review',
        escalation_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Escalate a consensus session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.status = 'escalated'
        
        escalation_info = {
            'escalation_type': escalation_type,
            'escalation_data': escalation_data or {},
            'escalated_at': datetime.utcnow().isoformat()
        }
        
        if session.result:
            session.result['escalation'] = escalation_info
        else:
            session.result = {'escalation': escalation_info}
        
        await self._add_session_knowledge(session, 'escalated', escalation_info)
        
        self.logger.info(f"Session {session_id} escalated with type: {escalation_type}")
        return True

    async def _add_session_knowledge(
        self,
        session: ConsensusSession,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add session event knowledge to blackboard"""

        from ...shared.blackboard import KnowledgeItem
        import json

        # Serialize event_data to handle datetime objects
        serialized_event_data = {}
        if event_data:
            try:
                # Convert to JSON and back to handle datetime serialization
                serialized_event_data = json.loads(json.dumps(event_data, default=str))
            except (TypeError, ValueError):
                # If serialization fails, convert all values to strings
                serialized_event_data = {k: str(v) for k, v in event_data.items()}

        knowledge = KnowledgeItem(
            space='coordination',
            agent_id='consensus_engine',
            knowledge_type='consensus_session_event',
            content={
                'session_id': session.session_id,
                'conflict_id': session.conflict_id,
                'event_type': event_type,
                'event_data': serialized_event_data,
                'session_status': session.status,
                'algorithm': session.algorithm,
                'participants_count': len(session.participants),
                'votes_count': len(session.votes),
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=2,
            tags={'consensus', 'coordination', event_type}
        )

        await self.blackboard.add_knowledge(knowledge)

    async def _handle_failed_consensus(self, session: ConsensusSession) -> None:
        """Handle failed consensus session"""
        
        # Determine escalation strategy based on failure reason
        if session.result and 'next_steps' in session.result:
            next_steps = session.result['next_steps']
            
            if 'escalate' in next_steps or 'expert_review' in next_steps:
                await self.escalate_session(session.session_id, 'human_review')
            elif 'add_participants' in next_steps:
                await self.escalate_session(session.session_id, 'expand_participants')
            elif 'extend_deadline' in next_steps:
                # Extend deadline by 24 hours
                if session.deadline:
                    session.deadline = session.deadline + timedelta(hours=24)
                    session.status = 'active'  # Reactivate session
        else:
            # Default escalation
            await self.escalate_session(session.session_id, 'human_review')

    async def get_consensus_metrics(self) -> Dict[str, Any]:
        """Get metrics about consensus sessions"""
        
        total_sessions = len(self.active_sessions)
        if total_sessions == 0:
            return {
                'total_sessions': 0,
                'success_rate': 0.0,
                'algorithm_distribution': {},
                'average_resolution_time': 0.0
            }
        
        completed_sessions = [s for s in self.active_sessions.values() if s.status == 'completed']
        successful_sessions = [s for s in completed_sessions if s.result and s.result.get('success', False)]
        
        success_rate = len(successful_sessions) / len(completed_sessions) if completed_sessions else 0.0
        
        # Algorithm distribution
        algorithm_distribution = {}
        for session in self.active_sessions.values():
            algo = session.algorithm
            if algo not in algorithm_distribution:
                algorithm_distribution[algo] = 0
            algorithm_distribution[algo] += 1
        
        # Average resolution time for completed sessions
        resolution_times = []
        for session in completed_sessions:
            if session.result:
                duration = (datetime.utcnow() - session.created_at).total_seconds() / 3600  # hours
                resolution_times.append(duration)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0.0
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': len([s for s in self.active_sessions.values() if s.status == 'active']),
            'completed_sessions': len(completed_sessions),
            'successful_sessions': len(successful_sessions),
            'success_rate': success_rate,
            'escalated_sessions': len([s for s in self.active_sessions.values() if s.status == 'escalated']),
            'algorithm_distribution': algorithm_distribution,
            'average_resolution_time_hours': avg_resolution_time
        }

    def cleanup_old_sessions(self, max_age_days: int = 7) -> int:
        """Clean up old sessions"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
        cleaned_count = 0
        
        sessions_to_remove = []
        for session_id, session in self.active_sessions.items():
            if session.created_at < cutoff_time and session.status in ['completed', 'failed', 'escalated']:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
            cleaned_count += 1
        
        return cleaned_count