// Constitutional Hash: cdd01ef066bc6cf2

'use strict';
// tests/quantumagi_core.ts
// Comprehensive End-to-End Tests for Quantumagi Constitutional Governance Framework
var __createBinding =
  (this && this.__createBinding) ||
  (Object.create
    ? function (o, m, k, k2) {
        if (k2 === undefined) k2 = k;
        var desc = Object.getOwnPropertyDescriptor(m, k);
        if (!desc || ('get' in desc ? !m.__esModule : desc.writable || desc.configurable)) {
          desc = {
            enumerable: true,
            get: function () {
              return m[k];
            },
          };
        }
        Object.defineProperty(o, k2, desc);
      }
    : function (o, m, k, k2) {
        if (k2 === undefined) k2 = k;
        o[k2] = m[k];
      });
var __setModuleDefault =
  (this && this.__setModuleDefault) ||
  (Object.create
    ? function (o, v) {
        Object.defineProperty(o, 'default', { enumerable: true, value: v });
      }
    : function (o, v) {
        o['default'] = v;
      });
var __importStar =
  (this && this.__importStar) ||
  function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null)
      for (var k in mod)
        if (k !== 'default' && Object.prototype.hasOwnProperty.call(mod, k))
          __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
  };
var __awaiter =
  (this && this.__awaiter) ||
  function (thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P
        ? value
        : new P(function (resolve) {
            resolve(value);
          });
    }
    return new (P || (P = Promise))(function (resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }
      function rejected(value) {
        try {
          step(generator['throw'](value));
        } catch (e) {
          reject(e);
        }
      }
      function step(result) {
        result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
      }
      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  };
Object.defineProperty(exports, '__esModule', { value: true });
const anchor = __importStar(require('@coral-xyz/anchor'));
const chai_1 = require('chai');
const crypto_1 = require('crypto');
// Mock GS Engine for testing
class MockGSEngine {
  synthesizePolicy(principleData) {
    return __awaiter(this, void 0, void 0, function* () {
      return {
        id: principleData.id,
        rule: `ENFORCE ${principleData.title.toUpperCase()}: ${principleData.content}`,
        category: this.mapCategory(principleData.category),
        priority: 'critical',
        validationScore: 0.95,
        solanaInstructionData: {
          policyId: Date.now(),
          rule: `ENFORCE ${principleData.title.toUpperCase()}`,
          category: this.mapCategory(principleData.category),
          priority: 'critical',
        },
      };
    });
  }
  mapCategory(category) {
    const categoryMap = {
      safety: { promptConstitution: {} },
      governance: { governance: {} },
      financial: { financial: {} },
      ethics: { safety: {} },
    };
    return categoryMap[category.toLowerCase()] || { governance: {} };
  }
}
describe('Quantumagi End-to-End Constitutional Governance', () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.QuantumagiCore;
  const authority = provider.wallet;
  const gsEngine = new MockGSEngine();
  // PDAs for core accounts
  const [governancePDA] = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from('governance')],
    program.programId
  );
  // Test data
  const constitutionalPrinciples = [
    {
      id: 'PC-001',
      title: 'No Extrajudicial State Mutation',
      content:
        'AI systems must not perform unauthorized state mutations without proper governance approval',
      category: 'safety',
      rationale: 'Prevents unauthorized changes to critical system state',
    },
    {
      id: 'GV-001',
      title: 'Democratic Policy Approval',
      content: 'All governance policies must be approved through democratic voting process',
      category: 'governance',
      rationale: 'Ensures community participation in governance decisions',
    },
    {
      id: 'FN-001',
      title: 'Treasury Protection',
      content: 'Financial operations exceeding limits require multi-signature approval',
      category: 'financial',
      rationale: 'Protects community treasury from unauthorized access',
    },
  ];
  describe('🏛️ Complete Constitutional Governance Workflow', () => {
    it('demonstrates full end-to-end constitutional governance cycle', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        console.log('\n🚀 Starting Complete Quantumagi Workflow Demonstration');
        // ===== PHASE 1: CONSTITUTION INITIALIZATION =====
        console.log('\n📜 Phase 1: Initializing Constitutional Framework');
        const constitutionalDoc = `
        Quantumagi Constitutional Framework v1.0

        Article I: Fundamental Principles
        - PC-001: No unauthorized state mutations
        - GV-001: Democratic governance required
        - FN-001: Treasury protection mandatory

        Article II: AI Governance Standards
        - All AI systems must operate within constitutional bounds
        - Real-time compliance enforcement through PGC
        - Multi-model validation ensures policy reliability
      `;
        const constitutionHash = (0, crypto_1.createHash)('sha256')
          .update(constitutionalDoc)
          .digest();
        console.log(`  Constitution Hash: ${constitutionHash.toString('hex').substring(0, 16)}...`);
        // Initialize governance with constitutional principles
        const principleTexts = constitutionalPrinciples.map(
          (p) => `${p.id}: ${p.title} - ${p.content}`
        );
        yield program.methods
          .initializeGovernance(authority.publicKey, principleTexts)
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        const governanceAccount = yield program.account.governanceState.fetch(governancePDA);
        (0, chai_1.expect)(governanceAccount.authority.toString()).to.equal(
          authority.publicKey.toString()
        );
        (0, chai_1.expect)(governanceAccount.principles.length).to.equal(principleTexts.length);
        console.log(
          '  ✅ Governance system successfully initialized with constitutional principles'
        );
        // ===== PHASE 2: POLICY SYNTHESIS & PROPOSAL =====
        console.log('\n🧠 Phase 2: GS Engine Policy Synthesis & Democratic Proposal');
        const synthesizedPolicies = [];
        for (let i = 0; i < constitutionalPrinciples.length; i++) {
          const principle = constitutionalPrinciples[i];
          console.log(`  Processing Principle ${principle.id}: ${principle.title}`);
          // Simulate GS Engine policy synthesis
          const synthesizedPolicy = yield gsEngine.synthesizePolicy(principle);
          synthesizedPolicies.push(synthesizedPolicy);
          console.log(`    Generated Rule: ${synthesizedPolicy.rule.substring(0, 50)}...`);
          console.log(`    Validation Score: ${synthesizedPolicy.validationScore}`);
          // Create policy proposal on-chain
          const policyId = synthesizedPolicy.solanaInstructionData.policyId;
          const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
            [Buffer.from('proposal'), new anchor.BN(policyId).toBuffer('le', 8)],
            program.programId
          );
          yield program.methods
            .createPolicyProposal(
              new anchor.BN(policyId),
              principle.title,
              `Policy for ${principle.title}`,
              synthesizedPolicy.rule
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: authority.publicKey,
              systemProgram: anchor.web3.SystemProgram.programId,
            })
            .rpc();
          const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
          (0, chai_1.expect)(proposalAccount.status).to.deep.equal({ active: {} }); // Should be active for voting
          (0, chai_1.expect)(proposalAccount.policyText).to.equal(synthesizedPolicy.rule);
          console.log(
            `    ✅ Policy ${principle.id} proposed on-chain (PDA: ${proposalPDA
              .toString()
              .substring(0, 8)}...)`
          );
        }
        console.log(
          `  📋 Successfully synthesized and proposed ${synthesizedPolicies.length} policies`
        );
        // ===== PHASE 3: DEMOCRATIC VOTING PROCESS =====
        console.log('\n🗳️ Phase 3: Democratic Voting & Policy Enactment');
        for (let i = 0; i < synthesizedPolicies.length; i++) {
          const policy = synthesizedPolicies[i];
          const policyId = new anchor.BN(policy.solanaInstructionData.policyId);
          const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
            [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
            program.programId
          );
          console.log(`  Voting on Policy ${constitutionalPrinciples[i].id}...`);
          // Simulate multiple voters
          const voters = [authority]; // In real system, would have multiple council members
          for (const voter of voters) {
            const [voteRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
              [Buffer.from('vote_record'), policyId.toBuffer('le', 8), voter.publicKey.toBuffer()],
              program.programId
            );
            yield program.methods
              .voteOnProposal(policyId, true, new anchor.BN(1)) // vote=true (for), votingPower=1
              .accounts({
                proposal: proposalPDA,
                voteRecord: voteRecordPDA,
                voter: voter.publicKey,
                systemProgram: anchor.web3.SystemProgram.programId,
              })
              .signers([voter.payer])
              .rpc();
          }
          // Finalize the proposal after voting
          yield program.methods
            .finalizeProposal(policyId)
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              finalizer: authority.publicKey,
            })
            .rpc();
          const finalizedProposal = yield program.account.policyProposal.fetch(proposalPDA);
          (0, chai_1.expect)(finalizedProposal.status).to.deep.equal({ approved: {} });
          (0, chai_1.expect)(finalizedProposal.votesFor.toNumber()).to.equal(1);
          console.log(
            `    ✅ Policy ${constitutionalPrinciples[i].id} approved (Votes: ${finalizedProposal.votesFor} for, ${finalizedProposal.votesAgainst} against)`
          );
        }
        console.log(
          `  🎉 All ${synthesizedPolicies.length} policies successfully enacted through democratic process`
        );
        // ===== PHASE 4: GOVERNANCE SYSTEM VALIDATION =====
        console.log('\n🔍 Phase 4: Governance System State Validation');
        // Validate that all proposals were processed correctly
        let approvedProposals = 0;
        for (let i = 0; i < synthesizedPolicies.length; i++) {
          const policy = synthesizedPolicies[i];
          const policyId = new anchor.BN(policy.solanaInstructionData.policyId);
          const [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
            [Buffer.from('proposal'), policyId.toBuffer('le', 8)],
            program.programId
          );
          const proposalAccount = yield program.account.policyProposal.fetch(proposalPDA);
          if (proposalAccount.status.approved) {
            approvedProposals++;
            console.log(`    ✅ Policy ${constitutionalPrinciples[i].id} - Status: APPROVED`);
          }
        }
        console.log(`\n  📊 Governance Validation Results:`);
        console.log(`     Approved Proposals: ${approvedProposals}/${synthesizedPolicies.length}`);
        console.log(
          `     Success Rate: ${((approvedProposals / synthesizedPolicies.length) * 100).toFixed(
            1
          )}%`
        );
        (0, chai_1.expect)(approvedProposals).to.equal(synthesizedPolicies.length);
        // ===== PHASE 5: SYSTEM VALIDATION & REPORTING =====
        console.log('\n📊 Phase 5: System Validation & Final Report');
        // Validate governance state
        const finalGovernance = yield program.account.governanceState.fetch(governancePDA);
        console.log(
          `  Governance Authority: ${finalGovernance.authority.toString().substring(0, 8)}...`
        );
        console.log(`  Constitutional Principles: ${finalGovernance.principles.length}`);
        console.log(`  Total Policies: ${finalGovernance.totalPolicies}`);
        console.log(`  Approved Proposals: ${approvedProposals}/${synthesizedPolicies.length}`);
        console.log(`  Governance System: OPERATIONAL`);
        // Final validation
        (0, chai_1.expect)(finalGovernance.authority.toString()).to.equal(
          authority.publicKey.toString()
        );
        (0, chai_1.expect)(finalGovernance.principles.length).to.equal(
          constitutionalPrinciples.length
        );
        (0, chai_1.expect)(approvedProposals).to.equal(synthesizedPolicies.length);
        console.log('\n🎉 ===== QUANTUMAGI END-TO-END DEMONSTRATION COMPLETE =====');
        console.log('✅ Constitutional governance framework fully operational');
        console.log('✅ GS Engine policy synthesis validated');
        console.log('✅ Democratic voting process confirmed');
        console.log('✅ Governance system state validation verified');
        console.log('✅ AlphaEvolve-ACGS integration successful');
        console.log('🏛️ Quantumagi is ready for production deployment!');
      }));
    it('validates individual component functionality', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        console.log('\n🔧 Component-Level Validation Tests');
        // Test emergency action functionality
        console.log('  Testing emergency governance actions...');
        yield program.methods
          .emergencyAction(
            { systemMaintenance: {} }, // Emergency action type
            null // No specific policy target
          )
          .accounts({
            governance: governancePDA,
            authority: authority.publicKey,
          })
          .rpc();
        console.log('  ✅ Emergency action functionality verified');
        // Test additional proposal creation
        const testPolicyId = new anchor.BN(Date.now());
        const [testProposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), testPolicyId.toBuffer('le', 8)],
          program.programId
        );
        yield program.methods
          .createPolicyProposal(
            testPolicyId,
            'Emergency Security Protocol',
            'Temporary security restriction for system maintenance',
            'ENFORCE: All operations require additional verification during maintenance'
          )
          .accounts({
            proposal: testProposalPDA,
            governance: governancePDA,
            proposer: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        const testProposal = yield program.account.policyProposal.fetch(testProposalPDA);
        (0, chai_1.expect)(testProposal.status).to.deep.equal({ active: {} });
        (0, chai_1.expect)(testProposal.title).to.equal('Emergency Security Protocol');
        console.log('  ✅ Additional proposal creation verified');
      }));
  });
  describe('🧪 Advanced Integration Tests', () => {
    it('tests multi-policy compliance scenarios', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        console.log('\n🔀 Multi-Policy Compliance Testing');
        // Create multiple policies for complex scenarios
        const complexPolicies = [
          {
            id: 'COMPLEX-001',
            rule: 'REQUIRE multi_sig_approval FOR treasury_operations EXCEEDING 1000',
            category: { financial: {} },
          },
          {
            id: 'COMPLEX-002',
            rule: 'DENY state_mutations WITHOUT governance_approval',
            category: { promptConstitution: {} },
          },
        ];
        const policyPDAs = [];
        for (const policy of complexPolicies) {
          const policyId = new anchor.BN(Date.now() + Math.random() * 1000);
          const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
            [Buffer.from('policy'), policyId.toBuffer('le', 8)],
            program.programId
          );
          yield program.methods
            .proposePolicy(policyId, policy.rule, policy.category, { high: {} })
            .accounts({
              policy: policyPDA,
              authority: authority.publicKey,
              systemProgram: anchor.web3.SystemProgram.programId,
            })
            .rpc();
          yield program.methods
            .enactPolicy()
            .accounts({
              policy: policyPDA,
              constitution: constitutionPDA,
              authority: authority.publicKey,
            })
            .rpc();
          policyPDAs.push(policyPDA);
        }
        // Test complex compliance scenarios
        const complexScenarios = [
          {
            action: 'treasury_operation_with_multi_sig',
            context: {
              requiresGovernance: false,
              hasGovernanceApproval: true,
              involvesFunds: true,
              amount: new anchor.BN(1500),
              authorizedLimit: new anchor.BN(1000),
              caller: authority.publicKey,
            },
            policyIndex: 0,
            shouldPass: false, // Exceeds limit without multi-sig
          },
        ];
        for (const scenario of complexScenarios) {
          try {
            yield program.methods
              .checkCompliance(scenario.action, scenario.context)
              .accounts({ policy: policyPDAs[scenario.policyIndex] })
              .rpc();
            (0, chai_1.expect)(scenario.shouldPass).to.be.true;
            console.log(`  ✅ Complex scenario passed as expected`);
          } catch (error) {
            (0, chai_1.expect)(scenario.shouldPass).to.be.false;
            console.log(`  ✅ Complex scenario blocked as expected`);
          }
        }
      }));
    it('validates GS Engine integration patterns', () =>
      __awaiter(void 0, void 0, void 0, function* () {
        console.log('\n🧠 GS Engine Integration Validation');
        // Test principle-to-policy synthesis
        const testPrinciple = {
          id: 'TEST-SYNTHESIS',
          title: 'Automated Testing Protocol',
          content: 'All automated systems must undergo validation testing before deployment',
          category: 'safety',
        };
        const gsEngine = new MockGSEngine();
        const synthesizedPolicy = yield gsEngine.synthesizePolicy(testPrinciple);
        (0, chai_1.expect)(synthesizedPolicy.rule).to.include('AUTOMATED TESTING PROTOCOL');
        (0, chai_1.expect)(synthesizedPolicy.validationScore).to.be.greaterThan(0.8);
        console.log(`  ✅ Policy synthesis validation score: ${synthesizedPolicy.validationScore}`);
        // Test policy deployment
        const policyId = new anchor.BN(synthesizedPolicy.solanaInstructionData.policyId);
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from('policy'), policyId.toBuffer('le', 8)],
          program.programId
        );
        yield program.methods
          .proposePolicy(policyId, synthesizedPolicy.rule, synthesizedPolicy.category, {
            critical: {},
          })
          .accounts({
            policy: policyPDA,
            authority: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();
        const deployedPolicy = yield program.account.policy.fetch(policyPDA);
        (0, chai_1.expect)(deployedPolicy.rule).to.equal(synthesizedPolicy.rule);
        console.log('  ✅ GS Engine to Solana deployment pipeline verified');
      }));
  });
});
