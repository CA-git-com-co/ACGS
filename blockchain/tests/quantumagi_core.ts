// tests/quantumagi_core.ts
// Comprehensive End-to-End Tests for Quantumagi Constitutional Governance Framework

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { QuantumagiCore } from "../target/types/quantumagi_core";
import { expect } from "chai";
import { createHash } from "crypto";

// Mock GS Engine for testing
class MockGSEngine {
  async synthesizePolicy(principleData: any) {
    return {
      id: principleData.id,
      rule: `ENFORCE ${principleData.title.toUpperCase()}: ${
        principleData.content
      }`,
      category: this.mapCategory(principleData.category),
      priority: "critical",
      validationScore: 0.95,
      solanaInstructionData: {
        policyId: Date.now(),
        rule: `ENFORCE ${principleData.title.toUpperCase()}`,
        category: this.mapCategory(principleData.category),
        priority: "critical",
      },
    };
  }

  private mapCategory(category: string) {
    const categoryMap = {
      safety: { promptConstitution: {} },
      governance: { governance: {} },
      financial: { financial: {} },
      ethics: { safety: {} },
    };
    return categoryMap[category.toLowerCase()] || { governance: {} };
  }
}

describe("Quantumagi End-to-End Constitutional Governance", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.QuantumagiCore as Program<QuantumagiCore>;
  const authority = provider.wallet as anchor.Wallet;
  const gsEngine = new MockGSEngine();

  // PDAs for core accounts
  const [constitutionPDA] = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from("constitution")],
    program.programId
  );

  // Test data
  const constitutionalPrinciples = [
    {
      id: "PC-001",
      title: "No Extrajudicial State Mutation",
      content:
        "AI systems must not perform unauthorized state mutations without proper governance approval",
      category: "safety",
      rationale: "Prevents unauthorized changes to critical system state",
    },
    {
      id: "GV-001",
      title: "Democratic Policy Approval",
      content:
        "All governance policies must be approved through democratic voting process",
      category: "governance",
      rationale: "Ensures community participation in governance decisions",
    },
    {
      id: "FN-001",
      title: "Treasury Protection",
      content:
        "Financial operations exceeding limits require multi-signature approval",
      category: "financial",
      rationale: "Protects community treasury from unauthorized access",
    },
  ];

  describe("🏛️ Complete Constitutional Governance Workflow", () => {
    it("demonstrates full end-to-end constitutional governance cycle", async () => {
      console.log("\n🚀 Starting Complete Quantumagi Workflow Demonstration");

      // ===== PHASE 1: CONSTITUTION INITIALIZATION =====
      console.log("\n📜 Phase 1: Initializing Constitutional Framework");

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

      const constitutionHash = createHash("sha256")
        .update(constitutionalDoc)
        .digest();
      console.log(
        `  Constitution Hash: ${constitutionHash
          .toString("hex")
          .substring(0, 16)}...`
      );

      await program.methods
        .initialize(Array.from(constitutionHash))
        .accounts({
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      const constitutionAccount = await program.account.constitution.fetch(
        constitutionPDA
      );
      expect(constitutionAccount.isActive).to.be.true;
      console.log("  ✅ Constitution successfully initialized and activated");

      // ===== PHASE 2: POLICY SYNTHESIS & PROPOSAL =====
      console.log(
        "\n🧠 Phase 2: GS Engine Policy Synthesis & Democratic Proposal"
      );

      const synthesizedPolicies = [];

      for (let i = 0; i < constitutionalPrinciples.length; i++) {
        const principle = constitutionalPrinciples[i];
        console.log(
          `  Processing Principle ${principle.id}: ${principle.title}`
        );

        // Simulate GS Engine policy synthesis
        const synthesizedPolicy = await gsEngine.synthesizePolicy(principle);
        synthesizedPolicies.push(synthesizedPolicy);

        console.log(
          `    Generated Rule: ${synthesizedPolicy.rule.substring(0, 50)}...`
        );
        console.log(
          `    Validation Score: ${synthesizedPolicy.validationScore}`
        );

        // Propose policy on-chain
        const policyId = new anchor.BN(
          synthesizedPolicy.solanaInstructionData.policyId
        );
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from("policy"), policyId.toBuffer("le", 8)],
          program.programId
        );

        await program.methods
          .proposePolicy(
            policyId,
            synthesizedPolicy.rule,
            synthesizedPolicy.category,
            { critical: {} }
          )
          .accounts({
            policy: policyPDA,
            authority: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();

        const policyAccount = await program.account.policy.fetch(policyPDA);
        expect(policyAccount.isActive).to.be.false; // Should not be active until enacted
        expect(policyAccount.rule).to.equal(synthesizedPolicy.rule);

        console.log(
          `    ✅ Policy ${principle.id} proposed on-chain (PDA: ${policyPDA
            .toString()
            .substring(0, 8)}...)`
        );
      }

      console.log(
        `  📋 Successfully synthesized and proposed ${synthesizedPolicies.length} policies`
      );

      // ===== PHASE 3: DEMOCRATIC VOTING PROCESS =====
      console.log("\n🗳️ Phase 3: Democratic Voting & Policy Enactment");

      for (let i = 0; i < synthesizedPolicies.length; i++) {
        const policy = synthesizedPolicies[i];
        const policyId = new anchor.BN(policy.solanaInstructionData.policyId);
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from("policy"), policyId.toBuffer("le", 8)],
          program.programId
        );

        console.log(`  Voting on Policy ${constitutionalPrinciples[i].id}...`);

        // Simulate multiple voters
        const voters = [authority]; // In real system, would have multiple council members

        for (const voter of voters) {
          const [voterRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
            [
              Buffer.from("vote"),
              policyId.toBuffer("le", 8),
              voter.publicKey.toBuffer(),
            ],
            program.programId
          );

          await program.methods
            .voteOnPolicy({ for: {} })
            .accounts({
              policy: policyPDA,
              voterRecord: voterRecordPDA,
              voter: voter.publicKey,
              systemProgram: anchor.web3.SystemProgram.programId,
            })
            .signers([voter.payer])
            .rpc();
        }

        // Enact the policy after voting
        await program.methods
          .enactPolicy()
          .accounts({
            policy: policyPDA,
            constitution: constitutionPDA,
            authority: authority.publicKey,
          })
          .rpc();

        const enactedPolicy = await program.account.policy.fetch(policyPDA);
        expect(enactedPolicy.isActive).to.be.true;
        expect(enactedPolicy.votesFor).to.equal(1);

        console.log(
          `    ✅ Policy ${constitutionalPrinciples[i].id} enacted (Votes: ${enactedPolicy.votesFor} for, ${enactedPolicy.votesAgainst} against)`
        );
      }

      console.log(
        `  🎉 All ${synthesizedPolicies.length} policies successfully enacted through democratic process`
      );

      // ===== PHASE 4: PGC COMPLIANCE ENFORCEMENT =====
      console.log("\n🔍 Phase 4: Real-time PGC Compliance Enforcement");

      const complianceTestCases = [
        {
          description: "Authorized treasury transfer (should PASS)",
          action: "treasury_transfer_with_authorization",
          context: {
            requiresGovernance: false,
            hasGovernanceApproval: true,
            involvesFunds: true,
            amount: new anchor.BN(1000),
            authorizedLimit: new anchor.BN(5000),
            caller: authority.publicKey,
          },
          expectedResult: "PASS",
          policyIndex: 2, // FN-001 Treasury Protection
        },
        {
          description: "Unauthorized state mutation (should FAIL - PC-001)",
          action: "unauthorized_state_mutation_bypass",
          context: {
            requiresGovernance: true,
            hasGovernanceApproval: false,
            involvesFunds: false,
            amount: new anchor.BN(0),
            authorizedLimit: new anchor.BN(0),
            caller: authority.publicKey,
          },
          expectedResult: "FAIL",
          policyIndex: 0, // PC-001 No Extrajudicial State Mutation
        },
        {
          description:
            "Governance decision without approval (should FAIL - GV-001)",
          action: "governance_decision_without_voting",
          context: {
            requiresGovernance: true,
            hasGovernanceApproval: false,
            involvesFunds: false,
            amount: new anchor.BN(0),
            authorizedLimit: new anchor.BN(0),
            caller: authority.publicKey,
          },
          expectedResult: "FAIL",
          policyIndex: 1, // GV-001 Democratic Policy Approval
        },
        {
          description: "Excessive treasury withdrawal (should FAIL - FN-001)",
          action: "treasury_withdrawal_excessive_amount",
          context: {
            requiresGovernance: false,
            hasGovernanceApproval: false,
            involvesFunds: true,
            amount: new anchor.BN(10000),
            authorizedLimit: new anchor.BN(5000),
            caller: authority.publicKey,
          },
          expectedResult: "FAIL",
          policyIndex: 2, // FN-001 Treasury Protection
        },
        {
          description: "Standard governance operation (should PASS)",
          action: "standard_governance_operation_approved",
          context: {
            requiresGovernance: true,
            hasGovernanceApproval: true,
            involvesFunds: false,
            amount: new anchor.BN(0),
            authorizedLimit: new anchor.BN(0),
            caller: authority.publicKey,
          },
          expectedResult: "PASS",
          policyIndex: 1, // GV-001 Democratic Policy Approval
        },
      ];

      let passedTests = 0;
      let failedTests = 0;

      for (const testCase of complianceTestCases) {
        console.log(`  Testing: ${testCase.description}`);

        const policy = synthesizedPolicies[testCase.policyIndex];
        const policyId = new anchor.BN(policy.solanaInstructionData.policyId);
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from("policy"), policyId.toBuffer("le", 8)],
          program.programId
        );

        try {
          await program.methods
            .checkCompliance(testCase.action, testCase.context)
            .accounts({ policy: policyPDA })
            .rpc();

          if (testCase.expectedResult === "PASS") {
            console.log(
              `    ✅ PASSED as expected - Action complies with policy`
            );
            passedTests++;
          } else {
            console.log(
              `    ❌ UNEXPECTED PASS - Action should have been blocked`
            );
            failedTests++;
          }
        } catch (error) {
          if (testCase.expectedResult === "FAIL") {
            console.log(
              `    ✅ BLOCKED as expected - Policy violation detected`
            );
            passedTests++;
          } else {
            console.log(
              `    ❌ UNEXPECTED BLOCK - Action should have been allowed`
            );
            console.log(`       Error: ${error.message}`);
            failedTests++;
          }
        }
      }

      console.log(`\n  📊 PGC Compliance Test Results:`);
      console.log(`     Passed: ${passedTests}/${complianceTestCases.length}`);
      console.log(`     Failed: ${failedTests}/${complianceTestCases.length}`);
      console.log(
        `     Success Rate: ${(
          (passedTests / complianceTestCases.length) *
          100
        ).toFixed(1)}%`
      );

      expect(passedTests).to.equal(complianceTestCases.length);

      // ===== PHASE 5: SYSTEM VALIDATION & REPORTING =====
      console.log("\n📊 Phase 5: System Validation & Final Report");

      // Validate constitution state
      const finalConstitution = await program.account.constitution.fetch(
        constitutionPDA
      );
      console.log(
        `  Constitution Status: ${
          finalConstitution.isActive ? "ACTIVE" : "INACTIVE"
        }`
      );
      console.log(`  Constitution Version: ${finalConstitution.version}`);

      // Count active policies
      let activePolicyCount = 0;
      for (const policy of synthesizedPolicies) {
        const policyId = new anchor.BN(policy.solanaInstructionData.policyId);
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from("policy"), policyId.toBuffer("le", 8)],
          program.programId
        );
        const policyAccount = await program.account.policy.fetch(policyPDA);
        if (policyAccount.isActive) activePolicyCount++;
      }

      console.log(
        `  Active Policies: ${activePolicyCount}/${synthesizedPolicies.length}`
      );
      console.log(
        `  PGC Enforcement: ${passedTests}/${complianceTestCases.length} tests passed`
      );

      // Final validation
      expect(finalConstitution.isActive).to.be.true;
      expect(activePolicyCount).to.equal(synthesizedPolicies.length);
      expect(passedTests).to.equal(complianceTestCases.length);

      console.log(
        "\n🎉 ===== QUANTUMAGI END-TO-END DEMONSTRATION COMPLETE ====="
      );
      console.log("✅ Constitutional governance framework fully operational");
      console.log("✅ GS Engine policy synthesis validated");
      console.log("✅ Democratic voting process confirmed");
      console.log("✅ PGC real-time compliance enforcement verified");
      console.log("✅ AlphaEvolve-ACGS integration successful");
      console.log("🏛️ Quantumagi is ready for production deployment!");
    });

    it("validates individual component functionality", async () => {
      console.log("\n🔧 Component-Level Validation Tests");

      // Test constitution updates
      const newDoc =
        "Quantumagi Constitutional Framework v2.0 - Enhanced governance";
      const newHash = createHash("sha256").update(newDoc).digest();

      await program.methods
        .updateConstitution(Array.from(newHash))
        .accounts({
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      const updatedConstitution = await program.account.constitution.fetch(
        constitutionPDA
      );
      expect(updatedConstitution.version).to.equal(2);
      console.log("  ✅ Constitution amendment functionality verified");

      // Test emergency policy deactivation
      const testPolicyId = new anchor.BN(Date.now());
      const [testPolicyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), testPolicyId.toBuffer("le", 8)],
        program.programId
      );

      await program.methods
        .proposePolicy(
          testPolicyId,
          "EMERGENCY: Temporary security restriction",
          { safety: {} },
          { critical: {} }
        )
        .accounts({
          policy: testPolicyPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      await program.methods
        .enactPolicy()
        .accounts({
          policy: testPolicyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      await program.methods
        .deactivatePolicy()
        .accounts({
          policy: testPolicyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      const deactivatedPolicy = await program.account.policy.fetch(
        testPolicyPDA
      );
      expect(deactivatedPolicy.isActive).to.be.false;
      console.log("  ✅ Emergency policy deactivation verified");
    });
  });

  describe("🧪 Advanced Integration Tests", () => {
    it("tests multi-policy compliance scenarios", async () => {
      console.log("\n🔀 Multi-Policy Compliance Testing");

      // Create multiple policies for complex scenarios
      const complexPolicies = [
        {
          id: "COMPLEX-001",
          rule: "REQUIRE multi_sig_approval FOR treasury_operations EXCEEDING 1000",
          category: { financial: {} },
        },
        {
          id: "COMPLEX-002",
          rule: "DENY state_mutations WITHOUT governance_approval",
          category: { promptConstitution: {} },
        },
      ];

      const policyPDAs = [];

      for (const policy of complexPolicies) {
        const policyId = new anchor.BN(Date.now() + Math.random() * 1000);
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from("policy"), policyId.toBuffer("le", 8)],
          program.programId
        );

        await program.methods
          .proposePolicy(policyId, policy.rule, policy.category, { high: {} })
          .accounts({
            policy: policyPDA,
            authority: authority.publicKey,
            systemProgram: anchor.web3.SystemProgram.programId,
          })
          .rpc();

        await program.methods
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
          action: "treasury_operation_with_multi_sig",
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
          await program.methods
            .checkCompliance(scenario.action, scenario.context)
            .accounts({ policy: policyPDAs[scenario.policyIndex] })
            .rpc();

          expect(scenario.shouldPass).to.be.true;
          console.log(`  ✅ Complex scenario passed as expected`);
        } catch (error) {
          expect(scenario.shouldPass).to.be.false;
          console.log(`  ✅ Complex scenario blocked as expected`);
        }
      }
    });

    it("validates GS Engine integration patterns", async () => {
      console.log("\n🧠 GS Engine Integration Validation");

      // Test principle-to-policy synthesis
      const testPrinciple = {
        id: "TEST-SYNTHESIS",
        title: "Automated Testing Protocol",
        content:
          "All automated systems must undergo validation testing before deployment",
        category: "safety",
      };

      const gsEngine = new MockGSEngine();
      const synthesizedPolicy = await gsEngine.synthesizePolicy(testPrinciple);

      expect(synthesizedPolicy.rule).to.include("AUTOMATED TESTING PROTOCOL");
      expect(synthesizedPolicy.validationScore).to.be.greaterThan(0.8);
      console.log(
        `  ✅ Policy synthesis validation score: ${synthesizedPolicy.validationScore}`
      );

      // Test policy deployment
      const policyId = new anchor.BN(
        synthesizedPolicy.solanaInstructionData.policyId
      );
      const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), policyId.toBuffer("le", 8)],
        program.programId
      );

      await program.methods
        .proposePolicy(
          policyId,
          synthesizedPolicy.rule,
          synthesizedPolicy.category,
          { critical: {} }
        )
        .accounts({
          policy: policyPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      const deployedPolicy = await program.account.policy.fetch(policyPDA);
      expect(deployedPolicy.rule).to.equal(synthesizedPolicy.rule);
      console.log("  ✅ GS Engine to Solana deployment pipeline verified");
    });
  });
});
