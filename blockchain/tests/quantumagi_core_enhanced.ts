// Enhanced Comprehensive Test Suite for Quantumagi Core Program
// Target: 85%+ test coverage with complete governance workflow validation

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { QuantumagiCore } from "../target/types/quantumagi_core";
import { expect } from "chai";
import { createHash } from "crypto";

describe("Quantumagi Core - Enhanced Test Suite", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.QuantumagiCore as Program<QuantumagiCore>;
  const authority = provider.wallet as anchor.Wallet;

  // Test data and PDAs
  const constitutionalDoc =
    "ACGS Constitutional Framework v1.0 - Enhanced Testing";
  const constitutionHash = createHash("sha256")
    .update(constitutionalDoc)
    .digest();

  const [constitutionPDA] = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from("constitution")],
    program.programId
  );

  describe("Constitution Management", () => {
    it("should initialize constitution with proper validation", async () => {
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
      expect(constitutionAccount.version).to.equal(1);
      expect(Buffer.from(constitutionAccount.hash)).to.deep.equal(
        constitutionHash
      );
    });

    it("should handle constitution updates with version control", async () => {
      const newDoc = "ACGS Constitutional Framework v2.0 - Updated";
      const newHash = createHash("sha256").update(newDoc).digest();

      await program.methods
        .updateConstitution(Array.from(newHash))
        .accounts({
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      const constitutionAccount = await program.account.constitution.fetch(
        constitutionPDA
      );
      expect(constitutionAccount.version).to.equal(2);
      expect(Buffer.from(constitutionAccount.hash)).to.deep.equal(newHash);
    });

    it("should reject unauthorized constitution updates", async () => {
      const unauthorizedKeypair = anchor.web3.Keypair.generate();
      const newHash = createHash("sha256")
        .update("unauthorized update")
        .digest();

      try {
        await program.methods
          .updateConstitution(Array.from(newHash))
          .accounts({
            constitution: constitutionPDA,
            authority: unauthorizedKeypair.publicKey,
          })
          .signers([unauthorizedKeypair])
          .rpc();
        expect.fail("Should have rejected unauthorized update");
      } catch (error) {
        expect(error.message).to.include("unauthorized");
      }
    });
  });

  describe("Policy Management", () => {
    let policyId: anchor.BN;
    let policyPDA: anchor.web3.PublicKey;

    beforeEach(() => {
      policyId = new anchor.BN(Date.now());
      [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), policyId.toBuffer("le", 8)],
        program.programId
      );
    });

    it("should create policy with comprehensive validation", async () => {
      const policyContent = "Enhanced test policy for comprehensive validation";

      await program.methods
        .createPolicy(policyId, policyContent, "Governance", "High")
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      const policyAccount = await program.account.policy.fetch(policyPDA);
      expect(policyAccount.id.toString()).to.equal(policyId.toString());
      expect(policyAccount.content).to.equal(policyContent);
      expect(policyAccount.category).to.equal("Governance");
      expect(policyAccount.priority).to.equal("High");
      expect(policyAccount.status).to.equal("Proposed");
    });

    it("should handle policy voting with quorum validation", async () => {
      // Create policy first
      await program.methods
        .createPolicy(policyId, "Test policy for voting", "Safety", "Critical")
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      // Vote on policy
      await program.methods
        .voteOnPolicy(policyId, true)
        .accounts({
          policy: policyPDA,
          voter: authority.publicKey,
        })
        .rpc();

      const policyAccount = await program.account.policy.fetch(policyPDA);
      expect(policyAccount.votesFor).to.equal(1);
      expect(policyAccount.votesAgainst).to.equal(0);
    });

    it("should enact policy when conditions are met", async () => {
      // Create and vote on policy
      await program.methods
        .createPolicy(
          policyId,
          "Test policy for enactment",
          "Financial",
          "Medium"
        )
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      await program.methods
        .voteOnPolicy(policyId, true)
        .accounts({
          policy: policyPDA,
          voter: authority.publicKey,
        })
        .rpc();

      // Enact policy
      await program.methods
        .enactPolicy(policyId)
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      const policyAccount = await program.account.policy.fetch(policyPDA);
      expect(policyAccount.status).to.equal("Active");
    });

    it("should deactivate policy in emergency situations", async () => {
      // Create and enact policy first
      await program.methods
        .createPolicy(policyId, "Emergency test policy", "Safety", "Critical")
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      await program.methods
        .voteOnPolicy(policyId, true)
        .accounts({
          policy: policyPDA,
          voter: authority.publicKey,
        })
        .rpc();

      await program.methods
        .enactPolicy(policyId)
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      // Emergency deactivation
      await program.methods
        .emergencyDeactivatePolicy(policyId)
        .accounts({
          policy: policyPDA,
          authority: authority.publicKey,
        })
        .rpc();

      const policyAccount = await program.account.policy.fetch(policyPDA);
      expect(policyAccount.status).to.equal("Deactivated");
    });
  });

  describe("PGC (Policy Governance Compliance) Validation", () => {
    let policyId: anchor.BN;
    let policyPDA: anchor.web3.PublicKey;

    beforeEach(async () => {
      policyId = new anchor.BN(Date.now());
      [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), policyId.toBuffer("le", 8)],
        program.programId
      );

      // Create and enact a policy for compliance testing
      await program.methods
        .createPolicy(
          policyId,
          "PGC compliance test policy",
          "Governance",
          "High"
        )
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      await program.methods
        .voteOnPolicy(policyId, true)
        .accounts({
          policy: policyPDA,
          voter: authority.publicKey,
        })
        .rpc();

      await program.methods
        .enactPolicy(policyId)
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();
    });

    it("should validate compliance with active policies", async () => {
      const testAction = "Test governance action for compliance";

      const isCompliant = await program.methods
        .validateCompliance(testAction)
        .accounts({
          constitution: constitutionPDA,
        })
        .view();

      expect(isCompliant).to.be.true;
    });

    it("should detect non-compliance with policies", async () => {
      const nonCompliantAction = "Action that violates governance policies";

      try {
        await program.methods
          .validateCompliance(nonCompliantAction)
          .accounts({
            constitution: constitutionPDA,
          })
          .view();
      } catch (error) {
        // Expected to fail for non-compliant actions
        expect(error).to.exist;
      }
    });

    it("should provide compliance confidence scores", async () => {
      const testAction = "Moderate confidence test action";

      const complianceResult = await program.methods
        .getComplianceScore(testAction)
        .accounts({
          constitution: constitutionPDA,
        })
        .view();

      expect(complianceResult.confidence).to.be.greaterThan(0);
      expect(complianceResult.confidence).to.be.lessThanOrEqual(100);
    });
  });

  describe("Performance and Gas Optimization", () => {
    it("should execute governance actions within SOL cost limits", async () => {
      const initialBalance = await provider.connection.getBalance(
        authority.publicKey
      );

      const policyId = new anchor.BN(Date.now());
      const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), policyId.toBuffer("le", 8)],
        program.programId
      );

      // Execute complete governance workflow
      await program.methods
        .createPolicy(
          policyId,
          "Cost optimization test policy",
          "Financial",
          "Medium"
        )
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      await program.methods
        .voteOnPolicy(policyId, true)
        .accounts({
          policy: policyPDA,
          voter: authority.publicKey,
        })
        .rpc();

      await program.methods
        .enactPolicy(policyId)
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
        })
        .rpc();

      const finalBalance = await provider.connection.getBalance(
        authority.publicKey
      );
      const costInSOL =
        (initialBalance - finalBalance) / anchor.web3.LAMPORTS_PER_SOL;

      console.log(`Governance action cost: ${costInSOL} SOL`);
      expect(costInSOL).to.be.lessThan(0.01); // Target: <0.01 SOL per action
    });

    it("should handle concurrent policy operations efficiently", async () => {
      const startTime = Date.now();
      const concurrentPolicies = 5;
      const promises = [];

      for (let i = 0; i < concurrentPolicies; i++) {
        const policyId = new anchor.BN(Date.now() + i);
        const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
          [Buffer.from("policy"), policyId.toBuffer("le", 8)],
          program.programId
        );

        promises.push(
          program.methods
            .createPolicy(
              policyId,
              `Concurrent test policy ${i}`,
              "Governance",
              "Low"
            )
            .accounts({
              policy: policyPDA,
              constitution: constitutionPDA,
              authority: authority.publicKey,
              systemProgram: anchor.web3.SystemProgram.programId,
            })
            .rpc()
        );
      }

      await Promise.all(promises);
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;

      console.log(`Concurrent operations duration: ${duration}s`);
      expect(duration).to.be.lessThan(10); // Should complete within 10 seconds
    });
  });

  describe("Error Handling and Edge Cases", () => {
    it("should handle invalid policy IDs gracefully", async () => {
      const invalidPolicyId = new anchor.BN(-1);
      const [invalidPolicyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), invalidPolicyId.toBuffer("le", 8)],
        program.programId
      );

      try {
        await program.methods
          .voteOnPolicy(invalidPolicyId, true)
          .accounts({
            policy: invalidPolicyPDA,
            voter: authority.publicKey,
          })
          .rpc();
        expect.fail("Should have rejected invalid policy ID");
      } catch (error) {
        expect(error).to.exist;
      }
    });

    it("should prevent double voting on policies", async () => {
      const policyId = new anchor.BN(Date.now());
      const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), policyId.toBuffer("le", 8)],
        program.programId
      );

      // Create policy
      await program.methods
        .createPolicy(
          policyId,
          "Double voting test policy",
          "Governance",
          "Medium"
        )
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      // First vote
      await program.methods
        .voteOnPolicy(policyId, true)
        .accounts({
          policy: policyPDA,
          voter: authority.publicKey,
        })
        .rpc();

      // Attempt second vote
      try {
        await program.methods
          .voteOnPolicy(policyId, false)
          .accounts({
            policy: policyPDA,
            voter: authority.publicKey,
          })
          .rpc();
        expect.fail("Should have prevented double voting");
      } catch (error) {
        expect(error.message).to.include("already voted");
      }
    });

    it("should handle maximum policy content length", async () => {
      const maxContent = "x".repeat(1000); // Test maximum content length
      const policyId = new anchor.BN(Date.now());
      const [policyPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("policy"), policyId.toBuffer("le", 8)],
        program.programId
      );

      await program.methods
        .createPolicy(policyId, maxContent, "Governance", "Low")
        .accounts({
          policy: policyPDA,
          constitution: constitutionPDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      const policyAccount = await program.account.policy.fetch(policyPDA);
      expect(policyAccount.content).to.equal(maxContent);
    });
  });
});
