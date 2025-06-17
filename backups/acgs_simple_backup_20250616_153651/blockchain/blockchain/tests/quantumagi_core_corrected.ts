// Corrected Test Suite for Quantumagi Core Program
// Demonstrates proper method signatures and account structures

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { QuantumagiCore } from "../target/types/quantumagi_core";
import { expect } from "chai";

describe("Quantumagi Core - Corrected Test Suite", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.QuantumagiCore as Program<QuantumagiCore>;
  const authority = provider.wallet as anchor.Wallet;

  // Correct PDAs - Use simple governance seed to avoid max length error
  const [governancePDA] = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from("governance"), Buffer.from("quantuma")],
    program.programId
  );

  describe("✅ Governance Initialization", () => {
    it("should initialize governance with constitutional principles", async () => {
      const principles = [
        "PC-001: No unauthorized state mutations",
        "GV-001: Democratic governance required",
        "FN-001: Treasury protection mandatory"
      ];

      // ✅ CORRECT: Use initializeGovernance method
      await program.methods
        .initializeGovernance(authority.publicKey, principles)
        .accounts({
          governance: governancePDA,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      // ✅ CORRECT: Fetch governanceState account
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      
      expect(governanceAccount.authority.toString()).to.equal(authority.publicKey.toString());
      expect(governanceAccount.principles.length).to.equal(principles.length);
      expect(governanceAccount.totalPolicies).to.equal(0);
      expect(governanceAccount.activeProposals).to.equal(0);
      
      console.log("✅ Governance initialized successfully");
    });
  });

  describe("✅ Policy Proposal Management", () => {
    let policyId: anchor.BN;
    let proposalPDA: anchor.web3.PublicKey;

    beforeEach(() => {
      policyId = new anchor.BN(Date.now());
      // ✅ CORRECT: Use "proposal" seed
      [proposalPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("proposal"), policyId.toBuffer("le", 8)],
        program.programId
      );
    });

    it("should create policy proposal", async () => {
      const title = "Test Governance Policy";
      const description = "A test policy for governance validation";
      const policyText = "ENFORCE: All governance actions require proper authorization";

      // ✅ CORRECT: Use createPolicyProposal method
      await program.methods
        .createPolicyProposal(policyId, title, description, policyText)
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      // ✅ CORRECT: Fetch policyProposal account
      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);
      
      expect(proposalAccount.policyId.toString()).to.equal(policyId.toString());
      expect(proposalAccount.title).to.equal(title);
      expect(proposalAccount.policyText).to.equal(policyText);
      expect(proposalAccount.status).to.deep.equal({ active: {} });
      
      console.log("✅ Policy proposal created successfully");
    });

    it("should vote on proposal", async () => {
      // Create proposal first
      await program.methods
        .createPolicyProposal(
          policyId,
          "Voting Test Policy",
          "Policy for testing voting mechanism",
          "ENFORCE: Voting validation requirements"
        )
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          proposer: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      // ✅ CORRECT: Use "vote_record" seed
      const [voteRecordPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [
          Buffer.from("vote_record"),
          policyId.toBuffer("le", 8),
          authority.publicKey.toBuffer(),
        ],
        program.programId
      );

      // ✅ CORRECT: Use voteOnProposal method with proper parameters
      await program.methods
        .voteOnProposal(policyId, true, new anchor.BN(1)) // policyId, vote, votingPower
        .accounts({
          proposal: proposalPDA,
          voteRecord: voteRecordPDA,
          voter: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      // ✅ CORRECT: Fetch voteRecord account
      const voteRecordAccount = await program.account.voteRecord.fetch(voteRecordPDA);
      
      expect(voteRecordAccount.vote).to.equal(true);
      expect(voteRecordAccount.votingPower.toNumber()).to.equal(1);
      expect(voteRecordAccount.voter.toString()).to.equal(authority.publicKey.toString());
      
      console.log("✅ Vote cast successfully");
    });

    it("should finalize proposal", async () => {
      // ✅ CORRECT: Use finalizeProposal method
      await program.methods
        .finalizeProposal(policyId)
        .accounts({
          proposal: proposalPDA,
          governance: governancePDA,
          finalizer: authority.publicKey,
        })
        .rpc();

      const proposalAccount = await program.account.policyProposal.fetch(proposalPDA);
      expect(proposalAccount.status).to.deep.equal({ approved: {} });
      
      console.log("✅ Proposal finalized successfully");
    });
  });

  describe("✅ Emergency Actions", () => {
    it("should execute emergency action", async () => {
      // ✅ CORRECT: Use emergencyAction method
      await program.methods
        .emergencyAction(
          { systemMaintenance: {} }, // EmergencyActionType
          null // No specific policy target
        )
        .accounts({
          governance: governancePDA,
          authority: authority.publicKey,
        })
        .rpc();

      console.log("✅ Emergency action executed successfully");
    });
  });

  describe("✅ System Validation", () => {
    it("should validate governance state", async () => {
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      
      expect(governanceAccount.authority.toString()).to.equal(authority.publicKey.toString());
      expect(governanceAccount.principles.length).to.be.greaterThan(0);
      expect(governanceAccount.totalPolicies).to.be.greaterThan(0);
      
      console.log("✅ Governance state validation successful");
      console.log(`   Authority: ${governanceAccount.authority.toString().substring(0, 8)}...`);
      console.log(`   Principles: ${governanceAccount.principles.length}`);
      console.log(`   Total Policies: ${governanceAccount.totalPolicies}`);
    });
  });
});
