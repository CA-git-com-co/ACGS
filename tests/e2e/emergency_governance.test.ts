
import { expect } from "chai";
import * as anchor from "@project-serum/anchor";
import { Program } from "@project-serum/anchor";

describe("E2E: emergency_governance", () => {
  let program: Program;
  let provider: anchor.AnchorProvider;

  before(async () => {
    provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);
    program = anchor.workspace.QuantumagiCore;
  });

  it("should complete Emergency policy deactivation workflow", async () => {
    // Test implementation for emergency_governance
    const startTime = Date.now();

    try {
      // Execute test steps
      // Step 1: Detect potential emergency via policy enforcement workflow
      const enforcementResponse = await fetch(
        "http://localhost:8005/api/v1/workflows/policy-enforcement",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            policy_id: "POL-E2E",
            context: {
              user_id: "e2e_tester",
              action: "delete",
              resource: "critical_system_file",
            },
            auto_remediation: true,
          }),
        }
      );

      expect(enforcementResponse.status).to.equal(200);
      const enforcementData = await enforcementResponse.json();
      expect(
        enforcementData.enforcement_result.enforcement_action.action_taken
      ).to.equal("emergency_lockdown");
      console.log("✅ Emergency detected via enforcement workflow");

      // Step 2: Deactivate policy using on-chain emergency action
      const [governancePDA] = anchor.web3.PublicKey.findProgramAddressSync(
        [Buffer.from("governance_emergency")],
        program.programId
      );

      await program.methods
        .emergencyAction({ systemMaintenance: {} }, null)
        .accounts({
          governance: governancePDA,
          authority: provider.wallet.publicKey,
        })
        .rpc();

      console.log("✅ Policy deactivated via emergency action");

      // Step 3: Notify stakeholders through governance workflow endpoint
      const notifyResponse = await fetch(
        "http://localhost:8005/api/v1/governance/workflows",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            workflow_type: "policy_enforcement",
            policy_id: "POL-E2E",
            stakeholders: ["security_team", "executive_team"],
          }),
        }
      );

      expect(notifyResponse.status).to.equal(200);
      const notifyData = await notifyResponse.json();
      expect(notifyData.workflow_id).to.be.a("string");
      console.log("✅ Stakeholders notified");

      // Step 4: Validate policy deactivation status
      const statusResponse = await fetch(
        `http://localhost:8005/api/v1/workflows/status/${enforcementData.workflow_id}`
      );

      expect(statusResponse.status).to.equal(200);
      const statusData = await statusResponse.json();
      expect(statusData.status).to.not.equal("not_found");
      console.log("✅ Deactivation validated via workflow status");

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
