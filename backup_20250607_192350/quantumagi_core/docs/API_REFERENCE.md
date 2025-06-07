# 📡 Quantumagi API Reference

**Version:** 1.0.0  
**Last Updated:** June 7, 2025

---

## 🏛️ **Core Program API**

### **Program ID**
```
quantumagi_core: Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS
```

### **Instructions**

#### **initialize**
Initialize the constitutional governance system.

**Parameters:**
```rust
constitution_hash: [u8; 32]  // SHA-256 hash of constitution
```

**Accounts:**
```rust
constitution: Account<Constitution>  // PDA: ["constitution"]
authority: Signer                   // Constitution authority
system_program: Program<System>     // System program
```

**Example:**
```typescript
const tx = await program.methods
  .initialize(Buffer.from(constitutionHash))
  .accounts({
    constitution: constitutionPDA,
    authority: wallet.publicKey,
    systemProgram: SystemProgram.programId,
  })
  .rpc();
```

#### **propose_policy**
Create a new policy proposal.

**Parameters:**
```rust
policy_id: u64              // Unique policy identifier
rule: String                // Policy rule text (max 1000 chars)
category: PolicyCategory    // Policy category
priority: PolicyPriority    // Policy priority level
```

**Accounts:**
```rust
policy: Account<Policy>      // PDA: ["policy", policy_id]
authority: Signer           // Proposer
system_program: Program<System>
```

**Categories:**
```rust
enum PolicyCategory {
    PromptConstitution,  // PC-001 type rules
    Safety,              // Safety-critical policies
    Governance,          // DAO governance rules
    Financial,           // Treasury policies
}
```

**Priorities:**
```rust
enum PolicyPriority {
    Critical,    // Must be enforced immediately
    High,        // Important but not critical
    Medium,      // Standard priority
    Low,         // Advisory level
}
```

#### **vote_on_policy**
Cast a vote on a proposed policy.

**Parameters:**
```rust
vote: PolicyVote  // For or Against
```

**Accounts:**
```rust
policy: Account<Policy>           // Policy being voted on
voter_record: Account<VoterRecord> // PDA: ["vote", policy_id, voter]
voter: Signer                     // Voter
system_program: Program<System>
```

#### **enact_policy**
Activate a policy after successful voting.

**Accounts:**
```rust
policy: Account<Policy>           // Policy to enact
constitution: Account<Constitution> // Constitution reference
authority: Signer                 // Constitutional authority
```

#### **check_compliance**
Validate an action against active policies (PGC).

**Parameters:**
```rust
action_to_check: String      // Action description
action_context: ActionContext // Action context data
```

**Action Context:**
```rust
struct ActionContext {
    requires_governance: bool,    // Needs governance approval
    has_governance_approval: bool, // Has approval
    involves_funds: bool,         // Financial transaction
    amount: u64,                  // Transaction amount
    authorized_limit: u64,        // Authorized limit
    caller: Pubkey,              // Action initiator
}
```

**Returns:**
- Success: Action is compliant
- Error: `ComplianceFailed` with violation details

#### **update_constitution**
Update the constitutional hash (amendments).

**Parameters:**
```rust
new_hash: [u8; 32]  // New constitution hash
```

**Accounts:**
```rust
constitution: Account<Constitution> // Constitution to update
authority: Signer                  // Constitutional authority
```

#### **deactivate_policy**
Emergency deactivation of a policy.

**Accounts:**
```rust
policy: Account<Policy>           // Policy to deactivate
constitution: Account<Constitution> // Constitution reference
authority: Signer                 // Constitutional authority
```

---

## ⚖️ **Appeals Program API**

### **Program ID**
```
appeals: 78zPu8eaSztb8FSefhVaQkFZi9BhBmJQ4hrqUXyiJFvW
```

### **Instructions**

#### **submit_appeal**
Submit an appeal for a policy violation.

**Parameters:**
```rust
policy_id: u64              // Policy being appealed
violation_details: String   // Violation description (max 2000 chars)
evidence_hash: [u8; 32]    // Hash of supporting evidence
appeal_type: AppealType    // Type of appeal
```

**Appeal Types:**
```rust
enum AppealType {
    PolicyViolation,           // Appeal against violation ruling
    ProcessError,              // System/process error
    NewEvidence,               // New evidence available
    ConstitutionalChallenge,   // Challenge policy constitutionality
}
```

#### **review_appeal**
Review an appeal (automated/AI review).

**Parameters:**
```rust
reviewer_decision: ReviewDecision // Review decision
review_evidence: String          // Review evidence (max 1000 chars)
confidence_score: u8             // Confidence (0-100)
```

**Review Decisions:**
```rust
enum ReviewDecision {
    Approve,    // Approve the appeal
    Reject,     // Reject the appeal
    Escalate,   // Escalate to human review
}
```

#### **escalate_to_human_committee**
Escalate appeal to human committee.

**Parameters:**
```rust
escalation_reason: String    // Reason for escalation (max 500 chars)
committee_type: CommitteeType // Committee type
```

**Committee Types:**
```rust
enum CommitteeType {
    Technical,      // Technical review
    Governance,     // Governance committee
    Ethics,         // Ethics review
    Constitutional, // Constitutional review
}
```

#### **resolve_with_ruling**
Final resolution of an appeal.

**Parameters:**
```rust
final_decision: FinalDecision    // Final decision
ruling_details: String           // Ruling explanation (max 2000 chars)
enforcement_action: EnforcementAction // Action to take
```

**Final Decisions:**
```rust
enum FinalDecision {
    Uphold,     // Uphold original decision
    Overturn,   // Overturn original decision
    Modify,     // Modify with conditions
}
```

**Enforcement Actions:**
```rust
enum EnforcementAction {
    None,                   // No action required
    PolicyUpdate,           // Update policy
    SystemAlert,            // Issue alert
    TemporaryExemption,     // Grant exemption
}
```

---

## 📝 **Logging Program API**

### **Program ID**
```
logging: 4rEgetuUsuf3PEDcPCpKH4ndjbfnCReRbmdiEKMkMUxo
```

### **Instructions**

#### **log_governance_event**
Log a governance-related event.

**Parameters:**
```rust
event_type: EventType       // Type of event
event_data: String          // Event data (JSON)
timestamp: i64              // Event timestamp
```

**Event Types:**
```rust
enum EventType {
    PolicyProposed,         // Policy proposal
    PolicyEnacted,          // Policy enactment
    ComplianceCheck,        // Compliance validation
    AppealSubmitted,        // Appeal submission
    AppealResolved,         // Appeal resolution
    ConstitutionUpdated,    // Constitution amendment
}
```

---

## 🐍 **Python Client API**

### **Installation**
```bash
pip install quantumagi-client
```

### **QuantumagiClient**

#### **Initialization**
```python
from quantumagi import QuantumagiClient

client = QuantumagiClient(
    cluster="devnet",  # "localnet", "devnet", "mainnet-beta"
    keypair_path="~/.config/solana/id.json",
    commitment="confirmed"
)
```

#### **Constitution Management**
```python
# Initialize constitution
result = await client.initialize_constitution(
    constitution_hash=hash_bytes,
    authority=authority_pubkey
)

# Update constitution
result = await client.update_constitution(
    new_hash=new_hash_bytes
)
```

#### **Policy Management**
```python
# Propose policy
policy = await client.propose_policy(
    policy_id=1,
    rule="DENY unauthorized_actions",
    category="Safety",
    priority="Critical"
)

# Vote on policy
vote_result = await client.vote_on_policy(
    policy_id=1,
    vote="For"  # "For" or "Against"
)

# Enact policy
enact_result = await client.enact_policy(policy_id=1)
```

#### **Compliance Checking**
```python
# Check compliance
compliance = await client.check_compliance(
    action="transfer_funds",
    context={
        "requires_governance": True,
        "has_governance_approval": True,
        "involves_funds": True,
        "amount": 1000,
        "authorized_limit": 5000,
        "caller": caller_pubkey
    }
)

print(f"Compliant: {compliance.is_compliant}")
print(f"Confidence: {compliance.confidence}%")
```

#### **Appeals Management**
```python
# Submit appeal
appeal = await client.submit_appeal(
    policy_id=1,
    violation_details="System error caused false positive",
    evidence_hash=evidence_hash,
    appeal_type="ProcessError"
)

# Review appeal
review = await client.review_appeal(
    appeal_id=appeal.id,
    decision="Escalate",
    evidence="Requires human review",
    confidence=75
)
```

---

## 🌐 **TypeScript SDK API**

### **Installation**
```bash
npm install @quantumagi/sdk
```

### **QuantumagiSDK**

#### **Initialization**
```typescript
import { QuantumagiSDK } from '@quantumagi/sdk';
import { Connection, Keypair } from '@solana/web3.js';

const connection = new Connection('https://api.devnet.solana.com');
const wallet = Keypair.fromSecretKey(secretKey);

const sdk = new QuantumagiSDK({
  connection,
  wallet,
  programIds: {
    core: 'Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS',
    appeals: '78zPu8eaSztb8FSefhVaQkFZi9BhBmJQ4hrqUXyiJFvW',
    logging: '4rEgetuUsuf3PEDcPCpKH4ndjbfnCReRbmdiEKMkMUxo'
  }
});
```

#### **Event Monitoring**
```typescript
// Listen for policy proposals
sdk.onPolicyProposed((event) => {
  console.log('New policy proposed:', {
    id: event.policyId,
    rule: event.rule,
    category: event.category,
    proposer: event.proposer
  });
});

// Listen for compliance checks
sdk.onComplianceCheck((event) => {
  console.log('Compliance check:', {
    action: event.action,
    result: event.isCompliant,
    confidence: event.confidence
  });
});

// Listen for appeals
sdk.onAppealSubmitted((event) => {
  console.log('Appeal submitted:', {
    id: event.appealId,
    policyId: event.policyId,
    type: event.appealType,
    appellant: event.appellant
  });
});
```

#### **Real-time Updates**
```typescript
// Subscribe to real-time updates
const subscription = sdk.subscribe({
  policies: true,
  appeals: true,
  compliance: true
});

// Unsubscribe
subscription.unsubscribe();
```

---

## 🔧 **Governance Synthesis Engine API**

### **GovernanceSynthesis**

```python
from quantumagi.gs_engine import GovernanceSynthesis

gs_engine = GovernanceSynthesis(
    acgs_endpoint="https://api.acgs.example.com",
    models=["gpt-4", "claude-3", "llama-2", "palm-2", "gemini"],
    consensus_threshold=0.85
)

# Synthesize policy from principle
policy = gs_engine.synthesize_policy(
    principle="Ensure system resilience under adversarial conditions",
    context={
        "current_policies": existing_policies,
        "system_state": current_state,
        "threat_level": "medium"
    }
)

print(f"Synthesized rule: {policy.rule}")
print(f"Confidence: {policy.confidence}")
print(f"Validation scores: {policy.validation_scores}")
```

---

## 📊 **Error Codes**

### **Core Program Errors**
```rust
#[error_code]
pub enum QuantumagiError {
    #[msg("You are not authorized to perform this action.")]
    Unauthorized = 6000,
    
    #[msg("The proposed action violates an active policy.")]
    ComplianceFailed = 6001,
    
    #[msg("The policy being checked is not currently active.")]
    PolicyNotActive = 6002,
    
    #[msg("The constitution is not currently active.")]
    ConstitutionInactive = 6003,
    
    #[msg("The policy is already active and cannot be voted on.")]
    PolicyAlreadyActive = 6004,
    
    #[msg("You have already voted on this policy.")]
    AlreadyVoted = 6005,
    
    #[msg("The rule text is too long.")]
    RuleTooLong = 6006,
}
```

### **Appeals Program Errors**
```rust
#[error_code]
pub enum AppealsError {
    #[msg("Violation details are too long.")]
    ViolationDetailsTooLong = 7000,
    
    #[msg("Review evidence is too long.")]
    ReviewEvidenceTooLong = 7001,
    
    #[msg("Invalid confidence score. Must be 0-100.")]
    InvalidConfidenceScore = 7002,
    
    #[msg("Appeal is not in the correct status for this operation.")]
    InvalidAppealStatus = 7003,
    
    #[msg("Review deadline has expired.")]
    ReviewDeadlineExpired = 7004,
    
    #[msg("Appeal cannot be escalated in its current status.")]
    CannotEscalate = 7005,
    
    #[msg("Maximum number of escalations reached.")]
    MaxEscalationsReached = 7006,
    
    #[msg("Appeal cannot be resolved in its current status.")]
    CannotResolve = 7007,
}
```

---

**📡 Complete API reference for Quantumagi constitutional governance framework**

*For more examples and tutorials, visit [docs.quantumagi.org](https://docs.quantumagi.org)*
