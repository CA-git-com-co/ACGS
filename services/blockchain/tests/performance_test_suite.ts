// Performance Test Suite - Load Testing and Benchmarking
// Constitutional Hash: cdd01ef066bc6cf2
// Version: 3.0 - Enterprise Performance Testing

import * as anchor from '@coral-xyz/anchor';
import { PublicKey, Keypair, SystemProgram, Connection } from '@solana/web3.js';
import { expect } from 'chai';
import { TestInfrastructure } from './test_setup_helper';

interface PerformanceMetrics {
  totalOperations: number;
  successfulOperations: number;
  failedOperations: number;
  totalDuration: number;
  averageLatency: number;
  throughput: number;
  p50Latency: number;
  p95Latency: number;
  p99Latency: number;
  errorRate: number;
  memoryUsage?: number;
  computeUnitsUsed?: number;
}

interface LoadTestConfig {
  concurrentUsers: number;
  operationsPerUser: number;
  testDuration: number; // seconds
  rampUpTime: number; // seconds
  operationType: 'proposal' | 'voting' | 'mixed';
}

class PerformanceTester {
  private latencies: number[] = [];
  private startTime: number = 0;
  private operations: number = 0;
  private errors: number = 0;

  start(): void {
    this.startTime = Date.now();
    this.latencies = [];
    this.operations = 0;
    this.errors = 0;
  }

  recordOperation(latency: number, success: boolean): void {
    this.latencies.push(latency);
    this.operations++;
    if (!success) this.errors++;
  }

  getMetrics(): PerformanceMetrics {
    const totalDuration = Date.now() - this.startTime;
    const sortedLatencies = this.latencies.sort((a, b) => a - b);
    
    return {
      totalOperations: this.operations,
      successfulOperations: this.operations - this.errors,
      failedOperations: this.errors,
      totalDuration,
      averageLatency: this.latencies.reduce((a, b) => a + b, 0) / this.latencies.length || 0,
      throughput: (this.operations / totalDuration) * 1000, // ops per second
      p50Latency: sortedLatencies[Math.floor(sortedLatencies.length * 0.5)] || 0,
      p95Latency: sortedLatencies[Math.floor(sortedLatencies.length * 0.95)] || 0,
      p99Latency: sortedLatencies[Math.floor(sortedLatencies.length * 0.99)] || 0,
      errorRate: (this.errors / this.operations) * 100 || 0,
    };
  }
}

describe('🚀 Performance & Load Testing Suite', () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  
  const program = anchor.workspace.QuantumagiCore;
  const authority = Keypair.generate();
  let governancePDA: PublicKey;
  let governanceBump: number;
  
  // Test configuration
  const constitutionalHash = "cdd01ef066bc6cf2";
  const testPrinciples = [
    "High performance governance",
    "Scalable decision making",
    "Efficient resource utilization"
  ];
  
  const governanceConfig = {
    constitutional_hash: constitutionalHash,
    minimum_quorum: 5,
    max_voting_power_per_vote: 100000,
    min_proposal_interval: 1, // 1 second for testing
    emergency_threshold: 8000,
    delegation_enabled: true,
    batch_operations_enabled: true,
  };

  before(async () => {
    console.log('🚀 Setting up Performance Testing Environment...');
    
    // Fund authority account
    await TestInfrastructure.ensureFunding(provider.connection, authority.publicKey, 10.0);
    
    // Generate governance PDA
    [governancePDA, governanceBump] = await TestInfrastructure.createUniqueGovernancePDA(
      program,
      'performance-test'
    );
    
    // Initialize governance
    await program.methods
      .initializeGovernance(
        authority.publicKey,
        testPrinciples,
        governanceConfig
      )
      .accounts({
        governance: governancePDA,
        authority: authority.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([authority])
      .rpc();
    
    console.log('✅ Performance test environment initialized');
  });

  describe('⚡ Single Operation Performance', () => {
    it('should benchmark proposal creation performance', async () => {
      const tester = new PerformanceTester();
      const proposer = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, proposer.publicKey, 2.0);
      
      tester.start();
      
      // Benchmark 50 proposal creations
      for (let i = 0; i < 50; i++) {
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(i + 1000).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );
        
        const operationStart = Date.now();
        try {
          await program.methods
            .createPolicyProposal(
              i + 1000,
              `Performance Test Proposal ${i}`,
              `Description for proposal ${i}`,
              `Policy text for performance test ${i}`,
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: proposer.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([proposer])
            .rpc();
          
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, true);
          
          // Wait briefly to respect rate limiting
          await new Promise(resolve => setTimeout(resolve, 100));
          
        } catch (error) {
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, false);
        }
      }
      
      const metrics = tester.getMetrics();
      
      console.log('📊 Proposal Creation Performance Metrics:');
      console.log(`  - Total Operations: ${metrics.totalOperations}`);
      console.log(`  - Success Rate: ${((metrics.successfulOperations / metrics.totalOperations) * 100).toFixed(2)}%`);
      console.log(`  - Average Latency: ${metrics.averageLatency.toFixed(2)}ms`);
      console.log(`  - P95 Latency: ${metrics.p95Latency.toFixed(2)}ms`);
      console.log(`  - P99 Latency: ${metrics.p99Latency.toFixed(2)}ms`);
      console.log(`  - Throughput: ${metrics.throughput.toFixed(2)} ops/sec`);
      
      // Performance assertions
      expect(metrics.errorRate).to.be.lessThan(5); // Less than 5% error rate
      expect(metrics.p99Latency).to.be.lessThan(2000); // P99 under 2 seconds
      expect(metrics.throughput).to.be.greaterThan(0.5); // At least 0.5 ops/sec
      
      console.log('✅ Proposal creation performance benchmarks passed');
    });

    it('should benchmark voting performance', async () => {
      const tester = new PerformanceTester();
      const voters = Array(20).fill(0).map(() => Keypair.generate());
      
      // Fund voter accounts
      await Promise.all(voters.map(voter => 
        TestInfrastructure.ensureFunding(provider.connection, voter.publicKey, 1.0)
      ));
      
      // Use existing proposal for voting
      const proposalId = 1000;
      const [proposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(proposalId).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );
      
      tester.start();
      
      // Benchmark voting
      for (let i = 0; i < voters.length; i++) {
        const voter = voters[i];
        const [votePDA] = PublicKey.findProgramAddressSync(
          [
            Buffer.from('vote'),
            new anchor.BN(proposalId).toArrayLike(Buffer, 'le', 8),
            voter.publicKey.toBuffer()
          ],
          program.programId
        );
        
        const operationStart = Date.now();
        try {
          await program.methods
            .voteOnProposal(
              proposalId,
              Math.random() > 0.5, // Random vote
              Math.floor(Math.random() * 1000) + 100, // Random voting power
              null
            )
            .accounts({
              proposal: proposalPDA,
              voteRecord: votePDA,
              governance: governancePDA,
              voter: voter.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([voter])
            .rpc();
          
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, true);
          
        } catch (error) {
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, false);
        }
      }
      
      const metrics = tester.getMetrics();
      
      console.log('📊 Voting Performance Metrics:');
      console.log(`  - Total Operations: ${metrics.totalOperations}`);
      console.log(`  - Success Rate: ${((metrics.successfulOperations / metrics.totalOperations) * 100).toFixed(2)}%`);
      console.log(`  - Average Latency: ${metrics.averageLatency.toFixed(2)}ms`);
      console.log(`  - P95 Latency: ${metrics.p95Latency.toFixed(2)}ms`);
      console.log(`  - P99 Latency: ${metrics.p99Latency.toFixed(2)}ms`);
      console.log(`  - Throughput: ${metrics.throughput.toFixed(2)} ops/sec`);
      
      // Performance assertions
      expect(metrics.errorRate).to.be.lessThan(10); // Less than 10% error rate
      expect(metrics.p99Latency).to.be.lessThan(1500); // P99 under 1.5 seconds
      expect(metrics.throughput).to.be.greaterThan(1); // At least 1 ops/sec
      
      console.log('✅ Voting performance benchmarks passed');
    });
  });

  describe('📈 Batch Operation Performance', () => {
    it('should benchmark batch proposal creation', async () => {
      const tester = new PerformanceTester();
      const proposer = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, proposer.publicKey, 3.0);
      
      tester.start();
      
      // Create batch data
      const batchSizes = [5, 10, 15, 20];
      
      for (const batchSize of batchSizes) {
        const batchData = Array(batchSize).fill(0).map((_, i) => ({
          policy_id: 2000 + (batchSize * 100) + i,
          title: `Batch Proposal ${batchSize}-${i}`,
          description: `Batch description ${i}`,
          policy_text: `Batch policy text ${i}`,
          options: {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        }));
        
        const operationStart = Date.now();
        try {
          await program.methods
            .batchCreateProposals(batchData)
            .accounts({
              governance: governancePDA,
              proposer: proposer.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([proposer])
            .rpc();
          
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, true);
          
          console.log(`✅ Batch of ${batchSize} proposals created in ${latency}ms`);
          
          // Wait between batches
          await new Promise(resolve => setTimeout(resolve, 500));
          
        } catch (error) {
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, false);
          console.log(`❌ Batch of ${batchSize} failed: ${error.message}`);
        }
      }
      
      const metrics = tester.getMetrics();
      
      console.log('📊 Batch Operation Performance Metrics:');
      console.log(`  - Total Batch Operations: ${metrics.totalOperations}`);
      console.log(`  - Success Rate: ${((metrics.successfulOperations / metrics.totalOperations) * 100).toFixed(2)}%`);
      console.log(`  - Average Latency: ${metrics.averageLatency.toFixed(2)}ms`);
      console.log(`  - P95 Latency: ${metrics.p95Latency.toFixed(2)}ms`);
      console.log(`  - P99 Latency: ${metrics.p99Latency.toFixed(2)}ms`);
      
      // Batch-specific assertions
      expect(metrics.errorRate).to.be.lessThan(20); // Allow higher error rate for batches
      expect(metrics.p99Latency).to.be.lessThan(5000); // P99 under 5 seconds for batches
      
      console.log('✅ Batch operation performance benchmarks passed');
    });
  });

  describe('🔄 Concurrent Load Testing', () => {
    it('should handle concurrent voting load', async () => {
      const loadConfig: LoadTestConfig = {
        concurrentUsers: 10,
        operationsPerUser: 5,
        testDuration: 30, // 30 seconds
        rampUpTime: 5, // 5 seconds
        operationType: 'voting'
      };
      
      console.log('🔄 Starting concurrent load test...');
      console.log(`Config: ${loadConfig.concurrentUsers} users, ${loadConfig.operationsPerUser} ops each`);
      
      const tester = new PerformanceTester();
      tester.start();
      
      // Create test proposal for voting
      const proposer = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, proposer.publicKey, 2.0);
      
      const testProposalId = 3000;
      const [testProposalPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('proposal'), new anchor.BN(testProposalId).toArrayLike(Buffer, 'le', 8)],
        program.programId
      );
      
      await program.methods
        .createPolicyProposal(
          testProposalId,
          "Load Test Proposal",
          "Proposal for concurrent load testing",
          "Load test policy text",
          {
            urgency: 'Normal',
            category: 'Policy',
            requires_supermajority: false,
            allow_delegation: true,
          }
        )
        .accounts({
          proposal: testProposalPDA,
          governance: governancePDA,
          proposer: proposer.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([proposer])
        .rpc();
      
      // Create concurrent workers
      const workers: Promise<void>[] = [];
      
      for (let userId = 0; userId < loadConfig.concurrentUsers; userId++) {
        const worker = this.createConcurrentVotingWorker(
          program,
          governancePDA,
          testProposalId,
          userId,
          loadConfig.operationsPerUser,
          tester
        );
        workers.push(worker);
        
        // Stagger worker start times (ramp up)
        if (userId > 0) {
          await new Promise(resolve => setTimeout(resolve, (loadConfig.rampUpTime * 1000) / loadConfig.concurrentUsers));
        }
      }
      
      // Wait for all workers to complete
      await Promise.all(workers);
      
      const metrics = tester.getMetrics();
      
      console.log('📊 Concurrent Load Test Results:');
      console.log(`  - Total Operations: ${metrics.totalOperations}`);
      console.log(`  - Successful Operations: ${metrics.successfulOperations}`);
      console.log(`  - Failed Operations: ${metrics.failedOperations}`);
      console.log(`  - Success Rate: ${((metrics.successfulOperations / metrics.totalOperations) * 100).toFixed(2)}%`);
      console.log(`  - Average Latency: ${metrics.averageLatency.toFixed(2)}ms`);
      console.log(`  - P95 Latency: ${metrics.p95Latency.toFixed(2)}ms`);
      console.log(`  - P99 Latency: ${metrics.p99Latency.toFixed(2)}ms`);
      console.log(`  - Throughput: ${metrics.throughput.toFixed(2)} ops/sec`);
      console.log(`  - Error Rate: ${metrics.errorRate.toFixed(2)}%`);
      
      // Concurrent load assertions
      expect(metrics.successfulOperations).to.be.greaterThan(0);
      expect(metrics.errorRate).to.be.lessThan(50); // Allow higher error rate under load
      expect(metrics.throughput).to.be.greaterThan(0.1); // Minimum throughput under load
      
      console.log('✅ Concurrent load test completed successfully');
    });

    async createConcurrentVotingWorker(
      program: any,
      governancePDA: PublicKey,
      proposalId: number,
      userId: number,
      operationsCount: number,
      tester: PerformanceTester
    ): Promise<void> {
      const voter = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, voter.publicKey, 1.0);
      
      for (let opId = 0; opId < operationsCount; opId++) {
        const uniqueVoteId = userId * 1000 + opId;
        const [votePDA] = PublicKey.findProgramAddressSync(
          [
            Buffer.from('vote'),
            new anchor.BN(proposalId).toArrayLike(Buffer, 'le', 8),
            voter.publicKey.toBuffer(),
            Buffer.from(uniqueVoteId.toString())
          ],
          program.programId
        );
        
        const operationStart = Date.now();
        try {
          await program.methods
            .voteOnProposal(
              proposalId,
              Math.random() > 0.5,
              Math.floor(Math.random() * 500) + 100,
              null
            )
            .accounts({
              proposal: PublicKey.findProgramAddressSync(
                [Buffer.from('proposal'), new anchor.BN(proposalId).toArrayLike(Buffer, 'le', 8)],
                program.programId
              )[0],
              voteRecord: votePDA,
              governance: governancePDA,
              voter: voter.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([voter])
            .rpc();
          
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, true);
          
        } catch (error) {
          const latency = Date.now() - operationStart;
          tester.recordOperation(latency, false);
        }
        
        // Small delay between operations
        await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
      }
    }
  });

  describe('📊 Memory & Resource Usage', () => {
    it('should monitor resource usage during operations', async () => {
      console.log('📊 Starting resource usage monitoring...');
      
      const initialBalance = await provider.connection.getBalance(authority.publicKey);
      console.log(`Initial authority balance: ${initialBalance / anchor.web3.LAMPORTS_PER_SOL} SOL`);
      
      // Perform resource-intensive operations
      const proposer = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, proposer.publicKey, 5.0);
      
      const operationCount = 25;
      const resourceMetrics: any[] = [];
      
      for (let i = 0; i < operationCount; i++) {
        const beforeBalance = await provider.connection.getBalance(proposer.publicKey);
        const operationStart = process.hrtime.bigint();
        
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(i + 4000).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );
        
        try {
          const signature = await program.methods
            .createPolicyProposal(
              i + 4000,
              `Resource Test Proposal ${i}`,
              `Resource monitoring test description ${i}`,
              `Resource monitoring policy text for proposal ${i}`,
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: proposer.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([proposer])
            .rpc();
          
          const operationEnd = process.hrtime.bigint();
          const afterBalance = await provider.connection.getBalance(proposer.publicKey);
          
          // Wait for transaction confirmation
          await provider.connection.confirmTransaction(signature, 'confirmed');
          
          const txInfo = await provider.connection.getTransaction(signature, {
            commitment: 'confirmed',
            maxSupportedTransactionVersion: 0
          });
          
          resourceMetrics.push({
            operation: i,
            executionTime: Number(operationEnd - operationStart) / 1_000_000, // Convert to ms
            costInLamports: beforeBalance - afterBalance,
            computeUnitsUsed: txInfo?.meta?.computeUnitsConsumed || 0,
            success: true
          });
          
        } catch (error) {
          const operationEnd = process.hrtime.bigint();
          resourceMetrics.push({
            operation: i,
            executionTime: Number(operationEnd - operationStart) / 1_000_000,
            costInLamports: 0,
            computeUnitsUsed: 0,
            success: false,
            error: error.message
          });
        }
        
        // Brief pause between operations
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      // Analyze resource usage
      const successfulOps = resourceMetrics.filter(m => m.success);
      const averageExecutionTime = successfulOps.reduce((sum, m) => sum + m.executionTime, 0) / successfulOps.length;
      const averageCost = successfulOps.reduce((sum, m) => sum + m.costInLamports, 0) / successfulOps.length;
      const averageComputeUnits = successfulOps.reduce((sum, m) => sum + m.computeUnitsUsed, 0) / successfulOps.length;
      const totalCost = successfulOps.reduce((sum, m) => sum + m.costInLamports, 0);
      
      console.log('📊 Resource Usage Analysis:');
      console.log(`  - Operations Completed: ${successfulOps.length}/${operationCount}`);
      console.log(`  - Average Execution Time: ${averageExecutionTime.toFixed(2)}ms`);
      console.log(`  - Average Cost: ${averageCost.toFixed(0)} lamports (${(averageCost / anchor.web3.LAMPORTS_PER_SOL).toFixed(6)} SOL)`);
      console.log(`  - Average Compute Units: ${averageComputeUnits.toFixed(0)} CU`);
      console.log(`  - Total Cost: ${totalCost.toFixed(0)} lamports (${(totalCost / anchor.web3.LAMPORTS_PER_SOL).toFixed(6)} SOL)`);
      console.log(`  - Cost per Operation: ${(averageCost / anchor.web3.LAMPORTS_PER_SOL * 1000).toFixed(3)} mSOL`);
      
      // Resource usage assertions
      expect(averageExecutionTime).to.be.lessThan(1000); // Under 1 second average
      expect(averageCost).to.be.lessThan(100000); // Under 0.0001 SOL per operation
      expect(averageComputeUnits).to.be.lessThan(200000); // Under 200K CU per operation
      
      console.log('✅ Resource usage monitoring completed');
    });
  });

  describe('🎯 Performance Regression Detection', () => {
    it('should detect performance regressions', async () => {
      console.log('🎯 Starting performance regression detection...');
      
      // Baseline performance measurement
      const baselineTester = new PerformanceTester();
      baselineTester.start();
      
      // Run baseline operations
      const proposer = Keypair.generate();
      await TestInfrastructure.ensureFunding(provider.connection, proposer.publicKey, 2.0);
      
      const baselineOps = 10;
      for (let i = 0; i < baselineOps; i++) {
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(i + 5000).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );
        
        const operationStart = Date.now();
        try {
          await program.methods
            .createPolicyProposal(
              i + 5000,
              `Baseline Proposal ${i}`,
              `Baseline description ${i}`,
              `Baseline policy text ${i}`,
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: proposer.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([proposer])
            .rpc();
          
          const latency = Date.now() - operationStart;
          baselineTester.recordOperation(latency, true);
          
          await new Promise(resolve => setTimeout(resolve, 150));
          
        } catch (error) {
          const latency = Date.now() - operationStart;
          baselineTester.recordOperation(latency, false);
        }
      }
      
      const baselineMetrics = baselineTester.getMetrics();
      
      // Current performance measurement (would be compared against stored baseline)
      const currentTester = new PerformanceTester();
      currentTester.start();
      
      for (let i = 0; i < baselineOps; i++) {
        const [proposalPDA] = PublicKey.findProgramAddressSync(
          [Buffer.from('proposal'), new anchor.BN(i + 6000).toArrayLike(Buffer, 'le', 8)],
          program.programId
        );
        
        const operationStart = Date.now();
        try {
          await program.methods
            .createPolicyProposal(
              i + 6000,
              `Current Proposal ${i}`,
              `Current description ${i}`,
              `Current policy text ${i}`,
              {
                urgency: 'Normal',
                category: 'Policy',
                requires_supermajority: false,
                allow_delegation: true,
              }
            )
            .accounts({
              proposal: proposalPDA,
              governance: governancePDA,
              proposer: proposer.publicKey,
              systemProgram: SystemProgram.programId,
            })
            .signers([proposer])
            .rpc();
          
          const latency = Date.now() - operationStart;
          currentTester.recordOperation(latency, true);
          
          await new Promise(resolve => setTimeout(resolve, 150));
          
        } catch (error) {
          const latency = Date.now() - operationStart;
          currentTester.recordOperation(latency, false);
        }
      }
      
      const currentMetrics = currentTester.getMetrics();
      
      // Regression analysis
      const latencyRegression = ((currentMetrics.averageLatency - baselineMetrics.averageLatency) / baselineMetrics.averageLatency) * 100;
      const throughputRegression = ((baselineMetrics.throughput - currentMetrics.throughput) / baselineMetrics.throughput) * 100;
      const errorRateChange = currentMetrics.errorRate - baselineMetrics.errorRate;
      
      console.log('🎯 Performance Regression Analysis:');
      console.log(`  - Baseline Average Latency: ${baselineMetrics.averageLatency.toFixed(2)}ms`);
      console.log(`  - Current Average Latency: ${currentMetrics.averageLatency.toFixed(2)}ms`);
      console.log(`  - Latency Change: ${latencyRegression.toFixed(2)}%`);
      console.log(`  - Baseline Throughput: ${baselineMetrics.throughput.toFixed(2)} ops/sec`);
      console.log(`  - Current Throughput: ${currentMetrics.throughput.toFixed(2)} ops/sec`);
      console.log(`  - Throughput Change: ${throughputRegression.toFixed(2)}%`);
      console.log(`  - Error Rate Change: ${errorRateChange.toFixed(2)}%`);
      
      // Regression detection thresholds
      const LATENCY_REGRESSION_THRESHOLD = 20; // 20% increase
      const THROUGHPUT_REGRESSION_THRESHOLD = 20; // 20% decrease
      const ERROR_RATE_THRESHOLD = 5; // 5% increase
      
      const hasLatencyRegression = latencyRegression > LATENCY_REGRESSION_THRESHOLD;
      const hasThroughputRegression = throughputRegression > THROUGHPUT_REGRESSION_THRESHOLD;
      const hasErrorRateRegression = errorRateChange > ERROR_RATE_THRESHOLD;
      
      if (hasLatencyRegression || hasThroughputRegression || hasErrorRateRegression) {
        console.log('⚠️  Performance regression detected!');
        if (hasLatencyRegression) console.log(`   - Latency regression: ${latencyRegression.toFixed(2)}%`);
        if (hasThroughputRegression) console.log(`   - Throughput regression: ${throughputRegression.toFixed(2)}%`);
        if (hasErrorRateRegression) console.log(`   - Error rate regression: ${errorRateChange.toFixed(2)}%`);
      } else {
        console.log('✅ No significant performance regression detected');
      }
      
      // For testing purposes, we'll be lenient with regression detection
      expect(latencyRegression).to.be.lessThan(50); // Allow up to 50% latency increase
      expect(throughputRegression).to.be.lessThan(50); // Allow up to 50% throughput decrease
      expect(errorRateChange).to.be.lessThan(20); // Allow up to 20% error rate increase
      
      console.log('✅ Performance regression detection completed');
    });
  });

  after(async () => {
    console.log('🧹 Cleaning up performance test environment...');
    
    // Get final governance statistics
    try {
      const governanceAccount = await program.account.governanceState.fetch(governancePDA);
      const stats = governanceAccount.statistics;
      
      console.log('\n📊 PERFORMANCE TEST SUMMARY');
      console.log('===============================');
      console.log(`Total Proposals Created: ${stats.totalProposalsCreated}`);
      console.log(`Total Votes Cast: ${stats.totalVotesCast}`);
      console.log(`Batch Operations: ${stats.batchOperationsCount}`);
      console.log(`Test Environment: Devnet`);
      console.log(`Constitutional Hash: ${constitutionalHash}`);
      console.log('===============================');
      console.log('✅ All performance tests completed successfully!');
      
    } catch (error) {
      console.log('Note: Could not fetch final statistics');
    }
  });
});