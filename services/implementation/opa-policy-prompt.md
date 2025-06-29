# OPA Constitutional Policy Implementation Prompt

## Context

You are implementing comprehensive Rego policies for ACGS-1 Lite's constitutional governance. Currently, only a trivial health check policy exists. You need to encode all constitutional principles, safety rules, and governance constraints in Rego.

## Requirements

### Constitutional Principles to Encode

1. **Core Constitutional Principles**:

   ```rego
   package acgs.constitutional

   # Constitutional hash must be preserved
   constitutional_hash := "cdd01ef066bc6cf2"

   # Core principles
   principles := {
       "autonomy": "AI agents must respect user autonomy and choice",
       "beneficence": "AI actions must aim to benefit users and society",
       "non_maleficence": "AI must not cause harm",
       "transparency": "AI decision-making must be explainable",
       "fairness": "AI must not discriminate unfairly",
       "privacy": "User data must be protected",
       "accountability": "All actions must be traceable"
   }
   ```

2. **Action Authorization Rules**:

   ```rego
   # Main evaluation entry point
   evaluate = response {
       input.action
       input.context

       # Check all safety rules
       safety_check := check_safety(input.action, input.context)

       # Check constitutional compliance
       constitutional_check := check_constitutional_compliance(input.action)

       # Check resource limits
       resource_check := check_resource_limits(input.context)

       # Build response
       response := {
           "allow": safety_check.passed AND constitutional_check.passed AND resource_check.passed,
           "reasons": array.concat([
               safety_check.reasons,
               constitutional_check.reasons,
               resource_check.reasons
           ]),
           "constitutional_hash": constitutional_hash
       }
   }
   ```

3. **Safety Rules**:

   ```rego
   # Dangerous actions that are always denied
   dangerous_actions := {
       "system.execute_shell",
       "network.access_external",
       "file.write_system",
       "process.spawn_child",
       "memory.access_kernel"
   }

   check_safety(action, context) = result {
       # Check if action is dangerous
       action_safe := not action in dangerous_actions

       # Check if agent is trusted
       agent_trusted := context.agent.trust_level >= 0.8

       # Check sandboxing
       properly_sandboxed := context.environment.sandbox_enabled

       result := {
           "passed": action_safe AND properly_sandboxed,
           "reasons": array.concat(
               ["action_not_dangerous" | action_safe],
               ["sandbox_required" | not properly_sandboxed]
           )
       }
   }
   ```

4. **Resource Limit Rules**:

   ```rego
   # Resource limits per agent
   resource_limits := {
       "cpu_cores": 2,
       "memory_gb": 4,
       "disk_gb": 10,
       "network_bandwidth_mbps": 10,
       "max_execution_time_seconds": 300
   }

   check_resource_limits(context) = result {
       agent_resources := context.agent.requested_resources

       violations := [reason |
           some resource, limit in resource_limits
           agent_resources[resource] > limit
           reason := sprintf("Resource %s exceeds limit: requested %v, limit %v",
                           [resource, agent_resources[resource], limit])
       ]

       result := {
           "passed": count(violations) == 0,
           "reasons": violations
       }
   }
   ```

5. **Evolution Control Rules**:

   ```rego
   # Evolution approval rules
   evolution_allowed(request) = allow {
       # Check evolution type
       type_allowed := request.type in {"minor_update", "patch", "configuration"}

       # Check risk score
       low_risk := request.risk_score < 0.3

       # Check human approval for major changes
       has_approval := request.type == "major_update" -> request.human_approved

       # Check rollback capability
       can_rollback := request.rollback_plan != null

       allow := type_allowed AND low_risk AND has_approval AND can_rollback
   }
   ```

6. **Data Access Rules**:

   ```rego
   # Privacy-preserving data access
   data_access_allowed(request) = allow {
       # Check data classification
       data_public := request.data_classification == "public"

       # Check user consent for private data
       has_consent := request.data_classification == "private" ->
                     request.user_consent.granted

       # Check purpose limitation
       purpose_valid := request.purpose in request.user_consent.allowed_purposes

       # Check data minimization
       minimal_access := request.fields_requested <= request.fields_needed

       allow := data_public OR (has_consent AND purpose_valid AND minimal_access)
   }
   ```

### Policy Organization

1. **Directory Structure**:

   ```
   policies/
   ├── constitutional/
   │   ├── core_principles.rego
   │   ├── safety_rules.rego
   │   └── resource_limits.rego
   ├── evolution/
   │   ├── approval_rules.rego
   │   └── rollback_policies.rego
   ├── data/
   │   ├── privacy_rules.rego
   │   └── access_control.rego
   └── main.rego  # Entry point
   ```

2. **Policy Bundle Configuration**:

   ```yaml
   # .manifest
   roots: ["acgs"]

   # policies/main.rego
   package acgs.main

   import data.acgs.constitutional
   import data.acgs.evolution
   import data.acgs.data

   default allow = false

   allow {
       constitutional.evaluate.allow
   }
   ```

3. **Testing Framework**:

   ```rego
   # policies/constitutional/core_principles_test.rego
   package acgs.constitutional_test

   test_dangerous_action_denied {
       not evaluate with input as {
           "action": "system.execute_shell",
           "context": {"environment": {"sandbox_enabled": true}}
       }
   }

   test_safe_action_allowed {
       evaluate.allow with input as {
           "action": "data.read_public",
           "context": {
               "environment": {"sandbox_enabled": true},
               "agent": {"trust_level": 0.9}
           }
       }
   }
   ```

### Performance Optimization

1. **Policy Compilation**:

   ```bash
   # Build optimized bundle
   opa build -b policies/ -o bundle.tar.gz \
       --optimize 2 \
       --entrypoint acgs/main/allow
   ```

2. **Indexing Strategy**:

   ```rego
   # Use objects for O(1) lookups instead of arrays
   dangerous_actions_map[action] {
       action := dangerous_actions[_]
   }

   # Pre-compute common decisions
   cached_decisions[key] = decision {
       key := sprintf("%s-%s", [input.action, input.context.agent.id])
       decision := evaluate
   }
   ```

## Implementation Steps

1. **Create Base Policies**:

   - Implement core constitutional principles
   - Add safety and resource rules
   - Create data access policies

2. **Add Evolution Policies**:

   - Define approval thresholds
   - Implement risk assessment rules
   - Add rollback requirements

3. **Build Testing Suite**:

   - Unit tests for each rule
   - Integration tests for policy combinations
   - Performance benchmarks

4. **Deploy to OPA**:
   - Build optimized bundle
   - Load into OPA server
   - Configure policy updates

## Success Criteria

- [ ] All constitutional principles encoded
- [ ] 100% test coverage for safety rules
- [ ] <1ms policy evaluation time
- [ ] Zero false negatives for dangerous actions
- [ ] Policies pass security audit
