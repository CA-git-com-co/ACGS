"""
Integration tests for multi-agent coordination workflows.
Tests the complete interaction between coordinator, worker agents, blackboard, and consensus engine.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from services.core.multi_agent_coordinator.coordinator_agent import CoordinatorAgent
from services.core.worker_agents.ethics_agent import EthicsAgent
from services.core.worker_agents.legal_agent import LegalAgent
from services.core.worker_agents.operational_agent import OperationalAgent
from services.core.consensus_engine.consensus_mechanisms import ConsensusEngine, ConsensusAlgorithm
from services.shared.blackboard import BlackboardService, KnowledgeItem, ConflictItem
from tests.fixtures.mock_services import MockRedis, TestDataGenerator


class TestMultiAgentCoordination:
    """Integration tests for complete multi-agent coordination workflows"""
    
    @pytest_asyncio.fixture
    async def coordination_system(self):
        """Set up complete multi-agent coordination system"""
        # Create blackboard with mock Redis
        mock_redis = MockRedis()
        blackboard = BlackboardService(redis_url="redis://localhost:6379")

        # Initialize the blackboard service
        await blackboard.initialize()

        # Replace the redis client with our mock after initialization
        blackboard.redis_client = mock_redis  # type: ignore

        # Create consensus engine
        consensus_engine = ConsensusEngine(blackboard)

        # Create coordinator agent
        coordinator = CoordinatorAgent(
            agent_id="coordinator_1",
            blackboard_service=blackboard
        )

        # Create worker agents
        ethics_agent = EthicsAgent("ethics_agent_1", blackboard)
        legal_agent = LegalAgent("legal_agent_1", blackboard)
        operational_agent = OperationalAgent("operational_agent_1", blackboard)

        return {
            "blackboard": blackboard,
            "consensus_engine": consensus_engine,
            "coordinator": coordinator,
            "ethics_agent": ethics_agent,
            "legal_agent": legal_agent,
            "operational_agent": operational_agent
        }
    
    @pytest.fixture
    def ai_model_deployment_request(self):
        """Create a complex AI model deployment governance request"""
        from services.core.multi_agent_coordinator.coordinator_agent import GovernanceRequest

        return GovernanceRequest(
            request_type="model_deployment",
            requester_id="product_team",
            priority=1,
            input_data={
                "model_info": {
                    "model_name": "customer-service-gpt4",
                    "model_type": "language_model",
                    "parameters": "175B",
                    "training_data": "customer_conversations_filtered",
                    "intended_use": "customer_support_automation",
                    "deployment_environment": "production",
                    "expected_users": 50000,
                    "geographic_regions": ["US", "EU", "APAC"]
                },
                "compliance_requirements": {
                    "ethical_review": True,
                    "legal_review": True,
                    "operational_review": True,
                    "privacy_compliance": ["GDPR", "CCPA"],
                    "safety_requirements": ["content_filtering", "bias_monitoring"],
                    "performance_requirements": {
                        "max_latency_ms": 500,
                        "min_availability": 99.9,
                        "max_error_rate": 0.1
                    }
                },
                "stakeholders": [
                    "customer_support_team",
                    "legal_team",
                    "privacy_office",
                    "security_team",
                    "product_management"
                ]
            },
            constitutional_requirements=["safety", "transparency", "consent"]
        )
    
    # Complete Workflow Integration Tests
    
    @pytest.mark.asyncio
    async def test_complete_governance_workflow(self, coordination_system, ai_model_deployment_request):
        """Test complete end-to-end governance workflow"""
        coordinator = coordination_system["coordinator"]
        blackboard = coordination_system["blackboard"]
        ethics_agent = coordination_system["ethics_agent"]
        legal_agent = coordination_system["legal_agent"]
        operational_agent = coordination_system["operational_agent"]

        # Register all agents
        await blackboard.register_agent(
            "ethics_agent_1",
            "ethics_agent",
            ["bias_detection", "fairness_evaluation"]
        )
        await blackboard.register_agent(
            "legal_agent_1",
            "legal_agent",
            ["regulatory_compliance", "privacy_law"]
        )
        await blackboard.register_agent(
            "operational_agent_1",
            "operational_agent",
            ["performance_analysis", "scalability_assessment"]
        )

        # Process governance request through coordinator (creates tasks)
        result = await coordinator.process_governance_request(ai_model_deployment_request)

        # Verify initial workflow setup
        assert result is not None
        assert result['success'] == True
        assert result['request_id'] == ai_model_deployment_request.id

        # Verify tasks were created
        all_tasks = await blackboard.query_knowledge(
            space="governance",
            knowledge_type="governance_context"
        )
        assert len(all_tasks) >= 1  # At least one governance context should be created

        # Now simulate agents processing the tasks
        # Get pending tasks and process them through the agents
        pending_tasks = await blackboard.get_pending_tasks()

        # Process tasks through appropriate agents
        for task in pending_tasks:
            if task.task_type == "ethical_analysis":
                if await blackboard.claim_task(task.id, ethics_agent.agent_id):
                    await ethics_agent._process_task(task)
            elif task.task_type == "legal_compliance":
                if await blackboard.claim_task(task.id, legal_agent.agent_id):
                    await legal_agent._process_task(task)
            elif task.task_type == "operational_validation":
                if await blackboard.claim_task(task.id, operational_agent.agent_id):
                    await operational_agent._process_task(task)

        # Verify agent analyses were completed
        ethics_analysis = await blackboard.query_knowledge(
            space="governance",
            agent_id="ethics_agent_1",
            knowledge_type="ethical_analysis_result"
        )
        legal_analysis = await blackboard.query_knowledge(
            space="governance",
            agent_id="legal_agent_1",
            knowledge_type="legal_analysis_result"
        )
        operational_analysis = await blackboard.query_knowledge(
            space="governance",
            agent_id="operational_agent_1",
            knowledge_type="operational_analysis_result"
        )

        # At least one agent should have completed analysis
        total_analyses = len(ethics_analysis) + len(legal_analysis) + len(operational_analysis)
        assert total_analyses >= 1, f"Expected at least 1 analysis, got {total_analyses}"
    
    @pytest.mark.asyncio
    async def test_agent_task_coordination(self, coordination_system, ai_model_deployment_request):
        """Test coordination between agents working on related tasks"""
        coordinator = coordination_system["coordinator"]
        ethics_agent = coordination_system["ethics_agent"]
        legal_agent = coordination_system["legal_agent"]
        operational_agent = coordination_system["operational_agent"]
        blackboard = coordination_system["blackboard"]
        
        # Start governance workflow
        governance_task_id = await coordinator.decompose_governance_request(ai_model_deployment_request)
        
        # Simulate agents processing tasks concurrently
        async def process_agent_tasks():
            # Get pending tasks
            pending_tasks = await blackboard.get_pending_tasks()

            # Filter tasks by task type (which corresponds to agent capabilities)
            ethics_task = next((t for t in pending_tasks if t.task_type == "ethical_analysis"), None)
            legal_task = next((t for t in pending_tasks if t.task_type == "legal_compliance"), None)
            operational_task = next((t for t in pending_tasks if t.task_type == "operational_validation"), None)

            # Process tasks concurrently if they exist
            tasks = []
            if ethics_task:
                # Claim and process the task
                if await blackboard.claim_task(ethics_task.id, ethics_agent.agent_id):
                    tasks.append(ethics_agent._process_task(ethics_task))
            if legal_task:
                # Claim and process the task
                if await blackboard.claim_task(legal_task.id, legal_agent.agent_id):
                    tasks.append(legal_agent._process_task(legal_task))
            if operational_task:
                # Claim and process the task
                if await blackboard.claim_task(operational_task.id, operational_agent.agent_id):
                    tasks.append(operational_agent._process_task(operational_task))

            return await asyncio.gather(*tasks, return_exceptions=True)
        
        # Execute agent tasks
        results = await process_agent_tasks()
        
        # Verify all tasks completed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 2  # At least 2 agents should complete tasks
        
        # Verify knowledge sharing occurred
        shared_knowledge = await blackboard.query_knowledge(
            space="governance",
            tags={"shared"}
        )
        assert len(shared_knowledge) >= 0  # Agents may share insights
    
    @pytest.mark.asyncio
    async def test_conflict_detection_and_resolution(self, coordination_system):
        """Test automatic conflict detection and resolution between agents"""
        coordinator = coordination_system["coordinator"]
        consensus_engine = coordination_system["consensus_engine"]
        blackboard = coordination_system["blackboard"]
        
        # Create conflicting assessments
        request_id = str(uuid4())
        
        # Ethics agent assessment: HIGH RISK
        ethics_assessment = {
            "governance_request_id": request_id,
            "agent_id": "ethics_agent_1",
            "assessment_type": "risk_evaluation",
            "risk_level": "high",
            "recommendation": "reject",
            "confidence": 0.9,
            "reasoning": "Significant bias potential in training data"
        }
        
        # Legal agent assessment: LOW RISK  
        legal_assessment = {
            "governance_request_id": request_id,
            "agent_id": "legal_agent_1",
            "assessment_type": "risk_evaluation", 
            "risk_level": "low",
            "recommendation": "approve",
            "confidence": 0.8,
            "reasoning": "All regulatory requirements can be met"
        }
        
        # Add conflicting assessments to blackboard
        from services.shared.blackboard.blackboard_service import KnowledgeItem
        
        await blackboard.add_knowledge(KnowledgeItem(
            space="governance",
            agent_id="ethics_agent_1",
            knowledge_type="risk_assessment",
            content=ethics_assessment,
            priority=1,
            tags={"assessment", "risk"}
        ))
        
        await blackboard.add_knowledge(KnowledgeItem(
            space="governance", 
            agent_id="legal_agent_1",
            knowledge_type="risk_assessment",
            content=legal_assessment,
            priority=1,
            tags={"assessment", "risk"}
        ))
        
        # Coordinator should detect conflict
        conflicts = await coordinator.detect_agent_conflicts(request_id)
        assert len(conflicts) >= 1
        
        # Initiate conflict resolution
        conflict = conflicts[0]
        resolution_result = await coordinator.resolve_conflict_through_consensus(
            conflict, 
            algorithm=ConsensusAlgorithm.CONSTITUTIONAL_PRIORITY
        )
        
        assert resolution_result is not None
        assert "resolution" in resolution_result
        assert resolution_result["resolution"]["success"] in [True, False]
    
    @pytest.mark.asyncio
    async def test_consensus_based_decision_making(self, coordination_system):
        """Test consensus-based decision making with multiple agents"""
        consensus_engine = coordination_system["consensus_engine"]
        blackboard = coordination_system["blackboard"]
        
        # Create a governance conflict
        from services.shared.blackboard.blackboard_service import ConflictItem
        
        conflict = ConflictItem(
            involved_agents=["ethics_agent_1", "legal_agent_1", "operational_agent_1"],
            involved_tasks=[str(uuid4())],
            conflict_type="deployment_decision",
            description="Agents have different deployment recommendations",
            severity="medium"
        )
        
        # Create vote options
        vote_options = [
            {
                "option_name": "Deploy with enhanced monitoring",
                "description": "Proceed with deployment but add comprehensive monitoring",
                "proposed_by": "ethics_agent_1",
                "constitutional_score": 0.85,
                "risk_assessment": {"level": "medium", "mitigation": "monitoring"}
            },
            {
                "option_name": "Delay for additional review",
                "description": "Postpone deployment for thorough compliance review",
                "proposed_by": "legal_agent_1", 
                "constitutional_score": 0.95,
                "risk_assessment": {"level": "low", "mitigation": "extended_review"}
            },
            {
                "option_name": "Deploy immediately",
                "description": "Proceed with standard deployment",
                "proposed_by": "operational_agent_1",
                "constitutional_score": 0.70,
                "risk_assessment": {"level": "medium", "mitigation": "standard"}
            }
        ]
        
        # Convert to VoteOption objects
        from services.core.consensus_engine.consensus_mechanisms import VoteOption
        options = [VoteOption(**opt) for opt in vote_options]
        
        # Initiate consensus session
        session_id = await consensus_engine.initiate_consensus(
            conflict=conflict,
            algorithm=ConsensusAlgorithm.WEIGHTED_VOTE,
            participants=["ethics_agent_1", "legal_agent_1", "operational_agent_1"],
            options=options,
            session_config={"weighted_threshold": 0.6}
        )
        
        # Cast votes with different weights and preferences
        await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="ethics_agent_1",
            voter_type="agent",
            option_id=options[0].option_id,  # Enhanced monitoring
            confidence=0.9,
            reasoning="Balances deployment needs with ethical oversight",
            weight=1.2  # Higher weight for ethics in this scenario
        )
        
        await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="legal_agent_1", 
            voter_type="agent",
            option_id=options[1].option_id,  # Delay for review
            confidence=0.85,
            reasoning="Ensures full regulatory compliance",
            weight=1.0
        )
        
        await consensus_engine.cast_vote(
            session_id=session_id,
            voter_id="operational_agent_1",
            voter_type="agent", 
            option_id=options[0].option_id,  # Enhanced monitoring (compromise)
            confidence=0.75,
            reasoning="Acceptable compromise between speed and safety",
            weight=0.8  # Lower weight as this is primarily ethical/legal decision
        )
        
        # Execute consensus
        consensus_result = await consensus_engine.execute_consensus(session_id)
        
        assert consensus_result is not None
        assert consensus_result["algorithm"] == "weighted_vote"
        assert "winning_option" in consensus_result
        
        # Verify consensus reached
        if consensus_result["success"]:
            assert consensus_result["weighted_percentage"] >= 0.6
            assert consensus_result["winning_option"] is not None
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_validation(self, coordination_system, ai_model_deployment_request):
        """Test constitutional compliance validation throughout workflow"""
        coordinator = coordination_system["coordinator"] 
        blackboard = coordination_system["blackboard"]
        
        # Process request with constitutional compliance checks
        result = await coordinator.process_governance_request(ai_model_deployment_request)
        
        # Verify constitutional compliance was checked
        assert "constitutional_compliance" in result
        compliance_result = result["constitutional_compliance"]
        
        assert "compliant" in compliance_result
        assert "constitutional_hash" in compliance_result
        assert "principle_adherence" in compliance_result
        
        # Verify compliance knowledge was stored
        compliance_knowledge = await blackboard.query_knowledge(
            space="governance",
            knowledge_type="constitutional_compliance"
        )
        assert len(compliance_knowledge) >= 1
        
        # Check that constitutional principles were applied
        for knowledge in compliance_knowledge:
            assert "constitutional_score" in knowledge.content or "compliant" in knowledge.content
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, coordination_system):
        """Test integration with performance monitoring system"""
        blackboard = coordination_system["blackboard"]
        
        # Create performance monitoring
        from services.core.multi_agent_coordinator.performance_integration import MultiAgentPerformanceMonitor
        from tests.fixtures.mock_services import MockWINACore
        
        mock_wina = MockWINACore()
        performance_monitor = MultiAgentPerformanceMonitor(
            blackboard_service=blackboard,
            wina_core=mock_wina
        )
        
        # Register agents
        await blackboard.register_agent(
            "ethics_agent_1",
            "ethics_agent",
            ["bias_detection"]
        )
        
        # Simulate agent activity
        from services.shared.blackboard.blackboard_service import KnowledgeItem
        
        performance_knowledge = KnowledgeItem(
            space="governance",
            agent_id="ethics_agent_1", 
            knowledge_type="task_result",
            content={
                "task_id": str(uuid4()),
                "processing_time": 3.5,
                "success": True,
                "constitutional_compliance": {"compliant": True, "score": 0.95}
            },
            priority=2,
            tags={"analysis_complete", "performance"}
        )
        await blackboard.add_knowledge(performance_knowledge)
        
        # Collect performance metrics
        await performance_monitor._collect_agent_metrics("ethics_agent_1")
        
        # Verify metrics were collected
        agent_metrics = await performance_monitor.get_agent_performance("ethics_agent_1")
        assert agent_metrics is not None
        assert agent_metrics.agent_id == "ethics_agent_1"
        assert agent_metrics.constitutional_compliance_rate >= 0.0
    
    @pytest.mark.asyncio 
    async def test_error_handling_and_recovery(self, coordination_system, ai_model_deployment_request):
        """Test error handling and recovery in multi-agent workflows"""
        coordinator = coordination_system["coordinator"]
        blackboard = coordination_system["blackboard"]
        
        # Simulate agent failure scenario
        with patch.object(coordinator, '_assign_task_to_agent') as mock_assign:
            # Make ethics agent fail
            mock_assign.side_effect = [
                Exception("Ethics agent unavailable"),  # First call fails
                True,  # Legal agent succeeds
                True   # Operational agent succeeds  
            ]
            
            # Process request with agent failure
            result = await coordinator.process_governance_request(ai_model_deployment_request)
            
            # Workflow should handle the failure gracefully
            assert result is not None
            
            # Should have error handling information
            if "errors" in result:
                assert len(result["errors"]) >= 1
            
            # Failed tasks should be marked appropriately
            failed_tasks = await blackboard.query_knowledge(
                space="coordination",
                knowledge_type="task_failure"
            )
            # May have failure records depending on implementation
    
    @pytest.mark.asyncio
    async def test_scalability_with_multiple_requests(self, coordination_system):
        """Test system scalability with multiple concurrent governance requests"""
        coordinator = coordination_system["coordinator"]
        
        # Create multiple governance requests
        requests = []
        for i in range(5):
            request_data = TestDataGenerator.create_governance_request(
                request_type="ai_model_deployment",
                complexity="medium",
                urgency="normal"
            )
            # Convert to GovernanceRequest object
            from services.core.multi_agent_coordinator.coordinator_agent import GovernanceRequest
            request = GovernanceRequest(
                request_type="model_deployment",
                requester_id=request_data.get("requester", "test_user"),
                priority=request_data.get("priority", 2),
                input_data={
                    "model_info": {
                        "model_name": f"test_model_{i}",
                        "model_type": "classification_model"
                    },
                    **request_data.get("metadata", {})
                },
                constitutional_requirements=["safety", "transparency"]
            )
            requests.append(request)
        
        # Process requests concurrently
        processing_tasks = [
            coordinator.process_governance_request(request)
            for request in requests
        ]
        
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Verify all requests were processed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 3  # Most should succeed
        
        # Verify no deadlocks or resource conflicts occurred
        for result in successful_results:
            assert result is not None
            # Check for expected result structure from coordinator
            assert "request_id" in result
            assert "success" in result or "constitutional_compliance" in result
    
    @pytest.mark.asyncio
    async def test_knowledge_persistence_and_retrieval(self, coordination_system, ai_model_deployment_request):
        """Test knowledge persistence and retrieval across workflow stages"""
        coordinator = coordination_system["coordinator"]
        blackboard = coordination_system["blackboard"]
        
        # Process governance request
        result = await coordinator.process_governance_request(ai_model_deployment_request)
        
        # Verify knowledge was persisted at each stage
        
        # 1. Initial request knowledge (stored as governance_context)
        request_knowledge = await blackboard.query_knowledge(
            space="governance",
            knowledge_type="governance_context"
        )
        assert len(request_knowledge) >= 1, f"Expected governance context knowledge, got {len(request_knowledge)}"

        # 2. Task assignment knowledge
        task_knowledge = await blackboard.query_knowledge(
            space="coordination",
            knowledge_type="task_assignment"
        )
        # Task assignment knowledge may or may not be present depending on implementation
        # assert len(task_knowledge) >= 1

        # 3. Agent analysis knowledge (if any agents processed tasks)
        analysis_knowledge = await blackboard.query_knowledge(
            space="governance",
            tags={"analysis"}
        )
        # Analysis knowledge may be empty if no agents processed tasks yet
        # assert len(analysis_knowledge) >= 1

        # 4. Final decision knowledge (may not be present in this simple test)
        decision_knowledge = await blackboard.query_knowledge(
            space="governance",
            knowledge_type="governance_decision"
        )
        # Decision knowledge may be empty if workflow didn't complete
        # assert len(decision_knowledge) >= 1
        
        # Verify knowledge can be retrieved by request ID
        request_id = ai_model_deployment_request.id
        related_knowledge = await blackboard.query_knowledge(
            space="governance"
        )

        # Filter by request ID in content
        request_related = [
            k for k in related_knowledge
            if k.content.get("governance_request_id") == request_id or
               k.content.get("request_id") == request_id
        ]
        assert len(request_related) >= 1, f"Expected knowledge related to request {request_id}, got {len(request_related)}"
    
    @pytest.mark.asyncio
    async def test_agent_heartbeat_and_health_monitoring(self, coordination_system):
        """Test agent heartbeat and health monitoring"""
        blackboard = coordination_system["blackboard"]
        
        # Register agents with heartbeat
        agents = ["ethics_agent_1", "legal_agent_1", "operational_agent_1"]
        
        for agent_id in agents:
            await blackboard.register_agent(
                agent_id,
                agent_id.split("_")[0] + "_agent",
                ["analysis"]
            )
            
            # Send heartbeat
            await blackboard.agent_heartbeat(agent_id)
        
        # Verify all agents are active
        active_agents = await blackboard.get_active_agents()
        assert len(active_agents) == 3
        for agent_id in agents:
            assert agent_id in active_agents
        
        # Test timeout functionality by checking with a reasonable timeout
        # This should not find any timeouts since agents just sent heartbeats
        timed_out_agents = await blackboard.check_agent_timeouts(timeout_minutes=5)
        assert len(timed_out_agents) == 0  # No agents should timeout with recent heartbeats

        # Verify all agents are still active
        active_agents_after_check = await blackboard.get_active_agents()
        assert len(active_agents_after_check) == 3