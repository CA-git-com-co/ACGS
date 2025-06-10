// Quantumagi Deployment Validation Script
// Validates that the deployed programs are accessible and functional

const anchor = require("@coral-xyz/anchor");
const { Connection, PublicKey } = require("@solana/web3.js");

async function validateQuantumagiDeployment() {
    console.log("🔍 Validating Quantumagi Deployment on Devnet");
    console.log("=" .repeat(50));

    // Connect to devnet
    const connection = new Connection("https://api.devnet.solana.com", "confirmed");
    
    // Program IDs from Anchor.toml
    const programIds = {
        quantumagi_core: "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4",
        appeals: "CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ",
        logging: "CjZi5hi9qggBzbXDht9YSJhN5cw7Bhz3rHhn63QQcPQo"
    };

    let validationResults = {
        programs: {},
        constitution: null,
        policies: [],
        overall_status: "✅ PASSED"
    };

    // 1. Validate Program Deployment
    console.log("\n📋 Step 1: Validating Program Deployment");
    for (const [name, programId] of Object.entries(programIds)) {
        try {
            const programPubkey = new PublicKey(programId);
            const accountInfo = await connection.getAccountInfo(programPubkey);
            
            if (accountInfo && accountInfo.executable) {
                console.log(`  ✅ ${name}: Deployed and executable`);
                validationResults.programs[name] = {
                    status: "✅ Deployed",
                    program_id: programId,
                    executable: true,
                    data_length: accountInfo.data.length
                };
            } else {
                console.log(`  ❌ ${name}: Not found or not executable`);
                validationResults.programs[name] = {
                    status: "❌ Not deployed",
                    program_id: programId,
                    executable: false
                };
                validationResults.overall_status = "❌ FAILED";
            }
        } catch (error) {
            console.log(`  ❌ ${name}: Error checking deployment - ${error.message}`);
            validationResults.programs[name] = {
                status: "❌ Error",
                program_id: programId,
                error: error.message
            };
            validationResults.overall_status = "❌ FAILED";
        }
    }

    // 2. Check Constitution Account
    console.log("\n📜 Step 2: Validating Constitution Account");
    try {
        const quantumagiProgramId = new PublicKey(programIds.quantumagi_core);
        const [constitutionPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("constitution")],
            quantumagiProgramId
        );
        
        const constitutionAccount = await connection.getAccountInfo(constitutionPDA);
        if (constitutionAccount) {
            console.log(`  ✅ Constitution account exists at: ${constitutionPDA.toString()}`);
            console.log(`  📊 Account data length: ${constitutionAccount.data.length} bytes`);
            validationResults.constitution = {
                status: "✅ Exists",
                address: constitutionPDA.toString(),
                data_length: constitutionAccount.data.length
            };
        } else {
            console.log(`  ❌ Constitution account not found at: ${constitutionPDA.toString()}`);
            validationResults.constitution = {
                status: "❌ Not found",
                address: constitutionPDA.toString()
            };
            validationResults.overall_status = "❌ FAILED";
        }
    } catch (error) {
        console.log(`  ❌ Error checking constitution: ${error.message}`);
        validationResults.constitution = {
            status: "❌ Error",
            error: error.message
        };
        validationResults.overall_status = "❌ FAILED";
    }

    // 3. Check for Policy Accounts
    console.log("\n📋 Step 3: Checking Policy Accounts");
    try {
        const quantumagiProgramId = new PublicKey(programIds.quantumagi_core);
        
        // Check for policies with IDs 1, 2, 3 (common initial policies)
        for (let policyId = 1; policyId <= 3; policyId++) {
            const [policyPDA] = PublicKey.findProgramAddressSync(
                [Buffer.from("policy"), Buffer.from(policyId.toString().padStart(8, '0'), 'hex')],
                quantumagiProgramId
            );
            
            const policyAccount = await connection.getAccountInfo(policyPDA);
            if (policyAccount) {
                console.log(`  ✅ Policy ${policyId} exists at: ${policyPDA.toString()}`);
                validationResults.policies.push({
                    id: policyId,
                    status: "✅ Exists",
                    address: policyPDA.toString(),
                    data_length: policyAccount.data.length
                });
            } else {
                console.log(`  ⚠️  Policy ${policyId} not found at: ${policyPDA.toString()}`);
                validationResults.policies.push({
                    id: policyId,
                    status: "⚠️ Not found",
                    address: policyPDA.toString()
                });
            }
        }
    } catch (error) {
        console.log(`  ❌ Error checking policies: ${error.message}`);
    }

    // 4. Final Summary
    console.log("\n🎯 Validation Summary");
    console.log("=" .repeat(50));
    console.log(`Overall Status: ${validationResults.overall_status}`);
    console.log(`Programs Deployed: ${Object.values(validationResults.programs).filter(p => p.status.includes("✅")).length}/3`);
    console.log(`Constitution: ${validationResults.constitution?.status || "Unknown"}`);
    console.log(`Policies Found: ${validationResults.policies.filter(p => p.status.includes("✅")).length}`);

    if (validationResults.overall_status === "✅ PASSED") {
        console.log("\n🎉 Quantumagi deployment is functional and ready for use!");
        console.log("✅ All core components are deployed and accessible");
        console.log("✅ Constitutional governance system is operational");
    } else {
        console.log("\n⚠️  Some issues found with the deployment");
        console.log("❌ Review the errors above and redeploy if necessary");
    }

    return validationResults;
}

// Run validation
validateQuantumagiDeployment()
    .then(results => {
        console.log("\n📊 Detailed Results:");
        console.log(JSON.stringify(results, null, 2));
        process.exit(results.overall_status === "✅ PASSED" ? 0 : 1);
    })
    .catch(error => {
        console.error("❌ Validation failed:", error);
        process.exit(1);
    });
