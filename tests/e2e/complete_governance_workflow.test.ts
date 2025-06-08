
import { expect } from "chai";
import * as anchor from "@project-serum/anchor";
import { Program } from "@project-serum/anchor";

describe("E2E: complete_governance_workflow", () => {
  let program: Program;
  let provider: anchor.AnchorProvider;

  before(async () => {
    provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);
    program = anchor.workspace.QuantumagiCore;
  });

  it("should complete Constitution deployment → Policy creation → Voting → Enactment", async () => {
    // Test implementation for complete_governance_workflow
    const startTime = Date.now();

    try {
      // Execute test steps

      // Deploy constitution
      const constitution = anchor.web3.Keypair.generate();
      const constitutionHash = "e2e_test_constitution_hash";

      await program.methods
        .initialize(constitutionHash)
        .accounts({
          constitution: constitution.publicKey,
          authority: provider.wallet.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([constitution])
        .rpc();

      console.log("✅ Constitution deployed");


      // Propose policy
      const policy = anchor.web3.Keypair.generate();
      const policyContent = "E2E test policy content";

      await program.methods
        .proposePolicy(policyContent, "Safety")
        .accounts({
          policy: policy.publicKey,
          proposer: provider.wallet.publicKey,
          constitution: constitution.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([policy])
        .rpc();

      console.log("✅ Policy proposed");


      // Vote on policy
      await program.methods
        .voteOnPolicy(true)
        .accounts({
          policy: policy.publicKey,
          voter: provider.wallet.publicKey,
        })
        .rpc();

      console.log("✅ Vote cast");


      // Enact policy
      await program.methods
        .enactPolicy()
        .accounts({
          policy: policy.publicKey,
          authority: provider.wallet.publicKey,
        })
        .rpc();

      console.log("✅ Policy enacted");


      // Validate compliance
      const result = await program.methods
        .checkCompliance("test_action", "test_context")
        .accounts({
          policy: policy.publicKey,
          constitution: constitution.publicKey,
        })
        .view();

      expect(result.isCompliant).to.be.true;
      console.log("✅ Compliance validated");

      const endTime = Date.now();
      const duration = endTime - startTime;

      console.log(`E2E test completed in ${duration}ms`);
      expect(duration).to.be.lessThan(30000); // 30 second timeout

    } catch (error) {
      console.error(`E2E test failed: ${error.message}`);
      throw error;
    }
  });
});
