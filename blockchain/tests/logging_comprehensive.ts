
import * as anchor from "@project-serum/anchor";
import { Program } from "@project-serum/anchor";
import { expect } from "chai";

describe("logging", () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = anchor.workspace.logging_CAMEL as Program<logging_CAMEL>;

  // Test accounts
  let authority: anchor.web3.Keypair;
  let constitution: anchor.web3.Keypair;
  let policy: anchor.web3.Keypair;

  before(async () => {
    authority = anchor.web3.Keypair.generate();
    constitution = anchor.web3.Keypair.generate();
    policy = anchor.web3.Keypair.generate();

    // Airdrop SOL for testing
    await program.provider.connection.confirmTransaction(
      await program.provider.connection.requestAirdrop(
        authority.publicKey,
        2 * anchor.web3.LAMPORTS_PER_SOL
      )
    );
  });

  describe("Constitution Management", () => {
    it("Should initialize constitution successfully", async () => {
      // Test constitution initialization
      const constitutionHash = "test_hash_12345";

      await program.methods
        .initialize(constitutionHash)
        .accounts({
          constitution: constitution.publicKey,
          authority: authority.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([constitution, authority])
        .rpc();

      const constitutionAccount = await program.account.constitution.fetch(
        constitution.publicKey
      );

      expect(constitutionAccount.hash).to.equal(constitutionHash);
      expect(constitutionAccount.authority.toString()).to.equal(
        authority.publicKey.toString()
      );
    });

    it("Should update constitution with proper authority", async () => {
      // Test constitution updates
      const newHash = "updated_hash_67890";

      await program.methods
        .updateConstitution(newHash)
        .accounts({
          constitution: constitution.publicKey,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const constitutionAccount = await program.account.constitution.fetch(
        constitution.publicKey
      );

      expect(constitutionAccount.hash).to.equal(newHash);
    });

    it("Should reject unauthorized constitution updates", async () => {
      const unauthorizedUser = anchor.web3.Keypair.generate();

      try {
        await program.methods
          .updateConstitution("unauthorized_hash")
          .accounts({
            constitution: constitution.publicKey,
            authority: unauthorizedUser.publicKey,
          })
          .signers([unauthorizedUser])
          .rpc();

        expect.fail("Should have thrown an error");
      } catch (error) {
        expect(error.message).to.include("unauthorized");
      }
    });
  });

  describe("Policy Management", () => {
    it("Should propose policy successfully", async () => {
      const policyContent = "Test policy content";
      const category = "Safety";

      await program.methods
        .proposePolicy(policyContent, category)
        .accounts({
          policy: policy.publicKey,
          proposer: authority.publicKey,
          constitution: constitution.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([policy, authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);

      expect(policyAccount.content).to.equal(policyContent);
      expect(policyAccount.category).to.equal(category);
      expect(policyAccount.status).to.equal("Proposed");
    });

    it("Should vote on policy", async () => {
      const vote = true; // Support

      await program.methods
        .voteOnPolicy(vote)
        .accounts({
          policy: policy.publicKey,
          voter: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);
      expect(policyAccount.supportVotes).to.equal(1);
    });

    it("Should enact policy after sufficient votes", async () => {
      await program.methods
        .enactPolicy()
        .accounts({
          policy: policy.publicKey,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);
      expect(policyAccount.status).to.equal("Active");
    });
  });

  describe("PGC Compliance Checking", () => {
    it("Should validate compliant actions", async () => {
      const action = "compliant_action";
      const context = "test_context";

      const result = await program.methods
        .checkCompliance(action, context)
        .accounts({
          policy: policy.publicKey,
          constitution: constitution.publicKey,
        })
        .view();

      expect(result.isCompliant).to.be.true;
      expect(result.confidence).to.be.greaterThan(0.9);
    });

    it("Should reject non-compliant actions", async () => {
      const action = "extrajudicial_state_mutation";
      const context = "unauthorized_context";

      const result = await program.methods
        .checkCompliance(action, context)
        .accounts({
          policy: policy.publicKey,
          constitution: constitution.publicKey,
        })
        .view();

      expect(result.isCompliant).to.be.false;
      expect(result.violatedPolicies).to.have.length.greaterThan(0);
    });
  });

  describe("Emergency Governance", () => {
    it("Should deactivate policy in emergency", async () => {
      await program.methods
        .deactivatePolicy("Emergency deactivation")
        .accounts({
          policy: policy.publicKey,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const policyAccount = await program.account.policy.fetch(policy.publicKey);
      expect(policyAccount.status).to.equal("Deactivated");
    });
  });
});
