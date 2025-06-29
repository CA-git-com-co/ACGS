# Evolution Oversight Service Completion Prompt

## Context

You are completing the Evolution Oversight Service for ACGS-1 Lite. The service structure exists with basic endpoints, but needs full implementation of evaluation logic, approval workflows, and integration with other services. The service must ensure 100% human oversight for critical changes while automating routine approvals.

## Requirements

### Core Functionality

1. **Evaluation Criteria Pipeline**:

   ```python
   class EvaluationCriteria:
       def __init__(self):
           self.criteria = {
               "constitutional_compliance": {
                   "weight": 0.4,
                   "threshold": 0.99,
                   "source": "policy_engine"
               },
               "performance_regression": {
                   "weight": 0.3,
                   "threshold": 0.05,  # Max 5% regression
                   "source": "metrics"
               },
               "anomaly_score": {
                   "weight": 0.2,
                   "threshold": 0.1,
                   "source": "anomaly_detector"
               },
               "risk_assessment": {
                   "weight": 0.1,
                   "threshold": 0.2,
                   "source": "risk_analyzer"
               }
           }

       async def evaluate_agent(self, agent_id: str, new_version: dict) -> EvaluationResult:
           scores = {}

           # Get constitutional compliance from Policy Engine
           compliance = await self.check_constitutional_compliance(new_version)
           scores["constitutional_compliance"] = compliance.score

           # Check performance metrics
           perf_delta = await self.analyze_performance_delta(agent_id, new_version)
           scores["performance_regression"] = 1.0 - abs(perf_delta)

           # Get anomaly score
           anomaly = await self.detect_anomalies(new_version)
           scores["anomaly_score"] = 1.0 - anomaly.score

           # Risk assessment
           risk = await self.assess_risk(new_version)
           scores["risk_assessment"] = 1.0 - risk.score

           # Calculate weighted score
           total_score = sum(
               scores[criterion] * config["weight"]
               for criterion, config in self.criteria.items()
           )

           return EvaluationResult(
               agent_id=agent_id,
               scores=scores,
               total_score=total_score,
               requires_human_review=total_score < 0.9
           )
   ```

2. **Approval Workflow Engine**:

   ```python
   class ApprovalWorkflow:
       async def process_evolution(self, evolution_request: EvolutionRequest):
           # Step 1: Evaluate the agent
           evaluation = await self.criteria.evaluate_agent(
               evolution_request.agent_id,
               evolution_request.new_version
           )

           # Step 2: Determine approval path
           if evaluation.total_score >= 0.95:
               # Auto-approve low-risk changes
               return await self.auto_approve(evolution_request, evaluation)

           elif evaluation.total_score >= 0.90:
               # Fast-track review for medium risk
               return await self.fast_track_review(evolution_request, evaluation)

           else:
               # Full human review for high risk
               return await self.human_review_required(evolution_request, evaluation)

       async def auto_approve(self, request, evaluation):
           # Additional safety check
           safety_check = await self.final_safety_validation(request)
           if not safety_check.passed:
               return await self.escalate_to_human(request, safety_check.reason)

           # Log decision
           await self.audit_decision(
               request.evolution_id,
               decision="AUTO_APPROVED",
               evaluation=evaluation,
               reviewer="SYSTEM"
           )

           # Deploy agent
           return await self.deploy_agent(request)
   ```

3. **Human Review Integration**:

   ```python
   class HumanReviewInterface:
       async def create_review_task(self, evolution_request, evaluation):
           task = ReviewTask(
               id=str(uuid.uuid4()),
               evolution_id=evolution_request.evolution_id,
               agent_id=evolution_request.agent_id,
               priority=self.calculate_priority(evaluation),
               created_at=datetime.utcnow(),
               evaluation_summary=evaluation.to_summary(),
               diff_view=await self.generate_diff_view(evolution_request),
               risk_factors=evaluation.get_risk_factors(),
               recommended_action=self.get_recommendation(evaluation)
           )

           # Store in database
           await self.db.review_tasks.insert(task)

           # Notify reviewers
           await self.notify_reviewers(task)

           return task
   ```

4. **Rollback Mechanism**:

   ```python
   class RollbackManager:
       async def rollback_agent(self, agent_id: str, reason: str):
           # Get current and previous versions
           current = await self.get_current_version(agent_id)
           previous = await self.get_previous_version(agent_id)

           if not previous:
               raise ValueError("No previous version available for rollback")

           # Validate previous version is safe
           validation = await self.validate_version(previous)
           if not validation.safe:
               raise ValueError("Previous version failed safety validation")

           # Execute rollback
           rollback_id = str(uuid.uuid4())
           await self.deploy_version(agent_id, previous, rollback_id)

           # Log rollback
           await self.audit_rollback(
               agent_id=agent_id,
               from_version=current.version,
               to_version=previous.version,
               reason=reason,
               rollback_id=rollback_id
           )
   ```

### Integration Requirements

1. **Policy Engine Integration**:

   - Call `/v1/evaluate` for constitutional compliance
   - Cache policy decisions for 5 minutes
   - Handle Policy Engine downtime gracefully

2. **Audit Engine Integration**:

   - Log all evolution decisions
   - Include full evaluation scores
   - Track human reviewer actions

3. **Database Schema**:

   ```sql
   CREATE TABLE agent_evolutions (
     evolution_id UUID PRIMARY KEY,
     agent_id VARCHAR(255) NOT NULL,
     version VARCHAR(50) NOT NULL,
     status VARCHAR(50) NOT NULL,
     evaluation_scores JSONB,
     total_score FLOAT,
     decision VARCHAR(50),
     reviewer_id VARCHAR(255),
     decision_timestamp TIMESTAMPTZ,
     justification TEXT,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );

   CREATE TABLE review_tasks (
     task_id UUID PRIMARY KEY,
     evolution_id UUID REFERENCES agent_evolutions(evolution_id),
     priority INTEGER,
     status VARCHAR(50),
     assigned_to VARCHAR(255),
     created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

### Performance Requirements

- Evaluation completion <5 seconds
- Auto-approval decision <500ms
- Support 100 concurrent evaluations
- Review task creation <1 second

## Implementation Steps

1. **Complete Evaluation Logic**:

   - Implement all evaluation criteria functions
   - Add metric collection from Prometheus
   - Create anomaly detection integration

2. **Build Approval Workflow**:

   - Implement state machine for approval flow
   - Add timeout handling for human reviews
   - Create escalation paths

3. **Dashboard Integration**:

   - Expose WebSocket for real-time updates
   - Create REST API for review actions
   - Add bulk approval capabilities

4. **Testing**:
   - Unit tests for each evaluation criterion
   - Integration tests with mock services
   - End-to-end workflow testing

## Success Criteria

- [ ] 90%+ auto-approval rate for low-risk changes
- [ ] <5 minute average human review time
- [ ] Zero unauthorized deployments
- [ ] 100% audit trail coverage
- [ ] Successful rollback in <30 seconds
