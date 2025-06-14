
import { expect } from "chai";
import * as anchor from "@project-serum/anchor";
import { Program } from "@project-serum/anchor";

describe("E2E: appeals_workflow", () => {
  let appealsProgram: Program;
  let loggingProgram: Program;
  let provider: anchor.AnchorProvider;

  before(async () => {
    provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);
    appealsProgram = anchor.workspace.Appeals as Program;
    loggingProgram = anchor.workspace.Logging as Program;
  });

  it("should complete Policy violation → Appeal submission → Resolution", async () => {
    // Test implementation for appeals_workflow
    const startTime = Date.now();

    try {
      // Execute test steps
      // Step 1: Trigger violation via logging program
      const violationTimestamp = Date.now();
      const [securityLogPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [
          Buffer.from("security_log"),
          Buffer.from(violationTimestamp.toString().slice(-8)),
        ],
        loggingProgram.programId
      );

      const alertType = { policyViolation: {} };
      const severity = { medium: {} };
      const description = "Policy violation detected";
      const affectedPolicyId = new anchor.BN(1234);

      await loggingProgram.methods
        .logSecurityAlert(alertType, severity, description, affectedPolicyId)
        .accounts({
          securityLog: securityLogPDA,
          reporter: provider.wallet.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      const securityLogAccount = await loggingProgram.account.securityLog.fetch(
        securityLogPDA
      );
      expect(securityLogAccount.alertType).to.deep.equal(alertType);

      // Step 2: Submit appeal
      const [appealPDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [
          Buffer.from("appeal"),
          affectedPolicyId.toBuffer("le", 8),
          provider.wallet.publicKey.toBuffer(),
        ],
        appealsProgram.programId
      );

      const violationDetails = "Automated test violation appeal";
      const evidenceHash = Array.from(Buffer.alloc(32, 5));
      const appealType = { policyViolation: {} };

      await appealsProgram.methods
        .submitAppeal(affectedPolicyId, violationDetails, evidenceHash, appealType)
        .accounts({
          appeal: appealPDA,
          appellant: provider.wallet.publicKey,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .rpc();

      let appealAccount = await appealsProgram.account.appeal.fetch(appealPDA);
      expect(appealAccount.status).to.deep.equal({ submitted: {} });

      // Step 3: Review appeal with low confidence to trigger human review
      const reviewDecision = { approve: {} };
      const reviewEvidence = "Initial automated review";
      const confidenceScore = 80; // below high confidence threshold

      await appealsProgram.methods
        .reviewAppeal(reviewDecision, reviewEvidence, confidenceScore)
        .accounts({
          appeal: appealPDA,
          reviewer: provider.wallet.publicKey,
        })
        .rpc();

      appealAccount = await appealsProgram.account.appeal.fetch(appealPDA);
      expect(appealAccount.status).to.deep.equal({ pendingHumanReview: {} });

      // Step 4: Resolve appeal with final ruling
      const finalDecision = { overturn: {} };
      const rulingDetails = "Human review overturned decision";
      const enforcementAction = { none: {} };

      await appealsProgram.methods
        .resolveWithRuling(finalDecision, rulingDetails, enforcementAction)
        .accounts({
          appeal: appealPDA,
          resolver: provider.wallet.publicKey,
        })
        .rpc();

      appealAccount = await appealsProgram.account.appeal.fetch(appealPDA);
      expect(appealAccount.status).to.deep.equal({ approved: {} });

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
