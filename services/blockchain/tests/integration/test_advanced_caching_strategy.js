const Redis = require('ioredis');

// Advanced Caching Strategy Test for ACGS-1 Governance Operations
class AdvancedCacheManager {
  constructor() {
    this.redis = new Redis({
      host: 'localhost',
      port: 6379,
      db: 0,
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3,
      lazyConnect: true,
    });

    // Cache statistics
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      invalidations: 0,
    };

    // Cache configurations for different data types
    this.cacheConfigs = {
      policy: {
        ttl: 300, // 5 minutes
        prefix: 'policy:',
        compression: true,
      },
      compliance: {
        ttl: 3600, // 1 hour
        prefix: 'compliance:',
        compression: false,
      },
      session: {
        ttl: 1800, // 30 minutes
        prefix: 'session:',
        compression: false,
      },
      governance: {
        ttl: 600, // 10 minutes
        prefix: 'governance:',
        compression: true,
      },
      constitutional: {
        ttl: 86400, // 24 hours
        prefix: 'constitutional:',
        compression: false,
      },
    };
  }

  async initialize() {
    try {
      await this.redis.connect();
      console.log('✅ Redis connection established');

      // Set constitutional hash for validation
      await this.redis.setex('config:constitutional_hash', 86400, 'cdd01ef066bc6cf2');

      return true;
    } catch (error) {
      console.error('❌ Redis connection failed:', error.message);
      return false;
    }
  }

  generateCacheKey(type, key) {
    const config = this.cacheConfigs[type];
    if (!config) {
      throw new Error(`Unknown cache type: ${type}`);
    }
    return `${config.prefix}${key}`;
  }

  async get(type, key) {
    const startTime = Date.now();
    const cacheKey = this.generateCacheKey(type, key);

    try {
      const value = await this.redis.get(cacheKey);
      const responseTime = Date.now() - startTime;

      if (value !== null) {
        this.stats.hits++;
        const parsed = JSON.parse(value);
        return {
          value: parsed,
          fromCache: true,
          responseTime,
          hit: true,
        };
      } else {
        this.stats.misses++;
        return {
          value: null,
          fromCache: false,
          responseTime,
          hit: false,
        };
      }
    } catch (error) {
      console.error(`Cache get error for ${cacheKey}:`, error.message);
      this.stats.misses++;
      return {
        value: null,
        fromCache: false,
        responseTime: Date.now() - startTime,
        hit: false,
        error: error.message,
      };
    }
  }

  async set(type, key, value) {
    const startTime = Date.now();
    const config = this.cacheConfigs[type];
    const cacheKey = this.generateCacheKey(type, key);

    try {
      const serialized = JSON.stringify(value);
      await this.redis.setex(cacheKey, config.ttl, serialized);

      this.stats.sets++;
      const responseTime = Date.now() - startTime;

      return {
        success: true,
        responseTime,
        ttl: config.ttl,
      };
    } catch (error) {
      console.error(`Cache set error for ${cacheKey}:`, error.message);
      return {
        success: false,
        responseTime: Date.now() - startTime,
        error: error.message,
      };
    }
  }

  async delete(type, key) {
    const cacheKey = this.generateCacheKey(type, key);

    try {
      const result = await this.redis.del(cacheKey);
      this.stats.deletes++;
      return result > 0;
    } catch (error) {
      console.error(`Cache delete error for ${cacheKey}:`, error.message);
      return false;
    }
  }

  async invalidatePattern(type, pattern) {
    const config = this.cacheConfigs[type];
    const searchPattern = `${config.prefix}${pattern}`;

    try {
      const keys = await this.redis.keys(searchPattern);
      if (keys.length > 0) {
        const result = await this.redis.del(...keys);
        this.stats.invalidations += result;
        return result;
      }
      return 0;
    } catch (error) {
      console.error(`Cache invalidation error for pattern ${searchPattern}:`, error.message);
      return 0;
    }
  }

  async batchGet(requests) {
    const pipeline = this.redis.pipeline();

    requests.forEach((req) => {
      const cacheKey = this.generateCacheKey(req.type, req.key);
      pipeline.get(cacheKey);
    });

    try {
      const results = await pipeline.exec();
      return results.map((result, index) => {
        const [error, value] = result;
        if (error) {
          this.stats.misses++;
          return { key: requests[index].key, value: null, hit: false, error: error.message };
        }

        if (value !== null) {
          this.stats.hits++;
          return { key: requests[index].key, value: JSON.parse(value), hit: true };
        } else {
          this.stats.misses++;
          return { key: requests[index].key, value: null, hit: false };
        }
      });
    } catch (error) {
      console.error('Batch get error:', error.message);
      return requests.map((req) => ({
        key: req.key,
        value: null,
        hit: false,
        error: error.message,
      }));
    }
  }

  async batchSet(requests) {
    const pipeline = this.redis.pipeline();

    requests.forEach((req) => {
      const config = this.cacheConfigs[req.type];
      const cacheKey = this.generateCacheKey(req.type, req.key);
      const serialized = JSON.stringify(req.value);
      pipeline.setex(cacheKey, config.ttl, serialized);
    });

    try {
      const results = await pipeline.exec();
      this.stats.sets += requests.length;
      return results.map((result, index) => {
        const [error] = result;
        return {
          key: requests[index].key,
          success: !error,
          error: error ? error.message : null,
        };
      });
    } catch (error) {
      console.error('Batch set error:', error.message);
      return requests.map((req) => ({ key: req.key, success: false, error: error.message }));
    }
  }

  getHitRate() {
    const total = this.stats.hits + this.stats.misses;
    return total > 0 ? (this.stats.hits / total) * 100 : 0;
  }

  getStats() {
    return {
      ...this.stats,
      hitRate: this.getHitRate(),
      totalOperations: this.stats.hits + this.stats.misses + this.stats.sets + this.stats.deletes,
    };
  }

  async getRedisInfo() {
    try {
      const info = await this.redis.info('memory');
      const stats = await this.redis.info('stats');

      // Parse Redis info
      const memoryInfo = this.parseRedisInfo(info);
      const statsInfo = this.parseRedisInfo(stats);

      return {
        memory: {
          used: memoryInfo.used_memory_human || '0B',
          peak: memoryInfo.used_memory_peak_human || '0B',
          rss: memoryInfo.used_memory_rss_human || '0B',
        },
        stats: {
          connections: statsInfo.total_connections_received || 0,
          commands: statsInfo.total_commands_processed || 0,
          keyspaceHits: statsInfo.keyspace_hits || 0,
          keyspaceMisses: statsInfo.keyspace_misses || 0,
          redisHitRate: this.calculateRedisHitRate(statsInfo),
        },
      };
    } catch (error) {
      console.error('Error getting Redis info:', error.message);
      return null;
    }
  }

  parseRedisInfo(infoString) {
    const info = {};
    infoString.split('\r\n').forEach((line) => {
      if (line && !line.startsWith('#')) {
        const [key, value] = line.split(':');
        if (key && value) {
          info[key] = isNaN(value) ? value : Number(value);
        }
      }
    });
    return info;
  }

  calculateRedisHitRate(stats) {
    const hits = stats.keyspace_hits || 0;
    const misses = stats.keyspace_misses || 0;
    const total = hits + misses;
    return total > 0 ? ((hits / total) * 100).toFixed(2) : '0.00';
  }

  async cleanup() {
    await this.redis.disconnect();
  }
}

async function testAdvancedCachingStrategy() {
  console.log('🔍 Testing Advanced Caching Strategy');
  console.log('='.repeat(60));

  const cacheManager = new AdvancedCacheManager();

  // Initialize cache
  const initialized = await cacheManager.initialize();
  if (!initialized) {
    console.log('❌ Failed to initialize cache manager');
    return { success: false, error: 'Cache initialization failed' };
  }

  console.log('⚡ Testing Multi-Tier Caching Strategy...');

  // Test data for different cache types
  const testData = {
    policy: [
      {
        key: 'policy_001',
        value: {
          id: 'policy_001',
          title: 'Safety Policy',
          content: 'ENFORCE: All operations must pass safety validation',
        },
      },
      {
        key: 'policy_002',
        value: {
          id: 'policy_002',
          title: 'Approval Policy',
          content: 'REQUIRE: 60% approval threshold for governance decisions',
        },
      },
      {
        key: 'policy_003',
        value: {
          id: 'policy_003',
          title: 'Emergency Policy',
          content: 'ALLOW: Emergency actions with mandatory review',
        },
      },
    ],
    compliance: [
      {
        key: 'comp_001',
        value: {
          policyId: 'policy_001',
          score: 0.95,
          status: 'compliant',
          hash: 'cdd01ef066bc6cf2',
        },
      },
      {
        key: 'comp_002',
        value: {
          policyId: 'policy_002',
          score: 0.97,
          status: 'compliant',
          hash: 'cdd01ef066bc6cf2',
        },
      },
    ],
    session: [
      {
        key: 'session_001',
        value: {
          userId: 'user_001',
          permissions: ['read', 'write'],
          expires: Date.now() + 3600000,
        },
      },
      {
        key: 'session_002',
        value: { userId: 'user_002', permissions: ['read'], expires: Date.now() + 3600000 },
      },
    ],
    governance: [
      {
        key: 'gov_001',
        value: {
          actionType: 'policy_creation',
          status: 'pending',
          votes: { for: 75, against: 25 },
        },
      },
      {
        key: 'gov_002',
        value: {
          actionType: 'policy_approval',
          status: 'approved',
          votes: { for: 85, against: 15 },
        },
      },
    ],
    constitutional: [
      {
        key: 'const_hash',
        value: { hash: 'cdd01ef066bc6cf2', principles: 5, lastUpdated: Date.now() },
      },
    ],
  };

  // Test cache operations for each type
  console.log('\n📊 Testing Cache Operations by Type:');

  const performanceResults = {};

  for (const [type, items] of Object.entries(testData)) {
    console.log(`\n   ${type.toUpperCase()} Cache:`);

    const typeResults = {
      setTimes: [],
      getTimes: [],
      hitRate: 0,
    };

    // Test SET operations
    for (const item of items) {
      const setResult = await cacheManager.set(type, item.key, item.value);
      typeResults.setTimes.push(setResult.responseTime);
      console.log(
        `     SET ${item.key}: ${setResult.success ? '✅' : '❌'} (${setResult.responseTime}ms)`
      );
    }

    // Test GET operations (cache hits)
    for (const item of items) {
      const getResult = await cacheManager.get(type, item.key);
      typeResults.getTimes.push(getResult.responseTime);
      console.log(
        `     GET ${item.key}: ${getResult.hit ? '🔄 HIT' : '❌ MISS'} (${getResult.responseTime}ms)`
      );
    }

    // Test cache misses
    const missResult = await cacheManager.get(type, 'nonexistent_key');
    typeResults.getTimes.push(missResult.responseTime);
    console.log(
      `     GET nonexistent: ${missResult.hit ? '🔄 HIT' : '❌ MISS'} (${missResult.responseTime}ms)`
    );

    performanceResults[type] = typeResults;
  }

  // Test batch operations
  console.log('\n🔄 Testing Batch Operations:');

  const batchGetRequests = [
    { type: 'policy', key: 'policy_001' },
    { type: 'policy', key: 'policy_002' },
    { type: 'compliance', key: 'comp_001' },
    { type: 'governance', key: 'gov_001' },
  ];

  const batchStartTime = Date.now();
  const batchResults = await cacheManager.batchGet(batchGetRequests);
  const batchTime = Date.now() - batchStartTime;

  console.log(`   Batch GET (${batchGetRequests.length} items): ${batchTime}ms`);
  batchResults.forEach((result, index) => {
    console.log(`     ${batchGetRequests[index].key}: ${result.hit ? '🔄 HIT' : '❌ MISS'}`);
  });

  // Test cache invalidation
  console.log('\n🗑️ Testing Cache Invalidation:');

  const invalidationResults = {};
  for (const type of Object.keys(testData)) {
    const invalidated = await cacheManager.invalidatePattern(type, '*');
    invalidationResults[type] = invalidated;
    console.log(`   ${type.toUpperCase()}: ${invalidated} keys invalidated`);
  }

  // Performance analysis
  console.log('\n📈 Performance Analysis:');

  let totalSetTime = 0;
  let totalGetTime = 0;
  let totalOperations = 0;

  for (const [type, results] of Object.entries(performanceResults)) {
    const avgSetTime = results.setTimes.reduce((a, b) => a + b, 0) / results.setTimes.length;
    const avgGetTime = results.getTimes.reduce((a, b) => a + b, 0) / results.getTimes.length;

    totalSetTime += avgSetTime;
    totalGetTime += avgGetTime;
    totalOperations += results.setTimes.length + results.getTimes.length;

    console.log(`   ${type.toUpperCase()}:`);
    console.log(`     Average SET time: ${avgSetTime.toFixed(2)}ms`);
    console.log(`     Average GET time: ${avgGetTime.toFixed(2)}ms`);
  }

  const avgSetTime = totalSetTime / Object.keys(performanceResults).length;
  const avgGetTime = totalGetTime / Object.keys(performanceResults).length;

  // Cache statistics
  const cacheStats = cacheManager.getStats();
  const redisInfo = await cacheManager.getRedisInfo();

  console.log('\n📊 Cache Statistics:');
  console.log(`   Cache Hits: ${cacheStats.hits}`);
  console.log(`   Cache Misses: ${cacheStats.misses}`);
  console.log(`   Hit Rate: ${cacheStats.hitRate.toFixed(1)}%`);
  console.log(`   Total Operations: ${cacheStats.totalOperations}`);
  console.log(`   Sets: ${cacheStats.sets}`);
  console.log(`   Deletes: ${cacheStats.deletes}`);
  console.log(`   Invalidations: ${cacheStats.invalidations}`);

  if (redisInfo) {
    console.log('\n📊 Redis Server Statistics:');
    console.log(`   Memory Used: ${redisInfo.memory.used}`);
    console.log(`   Memory Peak: ${redisInfo.memory.peak}`);
    console.log(`   Total Commands: ${redisInfo.stats.commands}`);
    console.log(`   Redis Hit Rate: ${redisInfo.stats.redisHitRate}%`);
  }

  // Target validation
  const targetHitRate = 80.0;
  const targetResponseTime = 10.0; // ms

  const meetsHitRateTarget = cacheStats.hitRate >= targetHitRate;
  const meetsResponseTimeTarget = avgGetTime <= targetResponseTime;

  console.log('\n🎯 Target Validation:');
  console.log(`   Target Hit Rate: ≥${targetHitRate}%`);
  console.log(`   Achieved Hit Rate: ${cacheStats.hitRate.toFixed(1)}%`);
  console.log(`   Hit Rate Target: ${meetsHitRateTarget ? '✅ MET' : '❌ NOT MET'}`);
  console.log(`   Target Response Time: ≤${targetResponseTime}ms`);
  console.log(`   Achieved Response Time: ${avgGetTime.toFixed(2)}ms`);
  console.log(`   Response Time Target: ${meetsResponseTimeTarget ? '✅ MET' : '❌ NOT MET'}`);

  // Cleanup
  await cacheManager.cleanup();

  return {
    success: true,
    hitRate: cacheStats.hitRate,
    avgResponseTime: avgGetTime,
    meetsHitRateTarget,
    meetsResponseTimeTarget,
    totalOperations: cacheStats.totalOperations,
    redisInfo,
  };
}

async function main() {
  console.log('🚀 Starting Advanced Caching Strategy Test');
  console.log('='.repeat(70));

  const result = await testAdvancedCachingStrategy();

  if (result.success) {
    console.log('\n🎯 Advanced Caching Summary');
    console.log('='.repeat(50));
    console.log('📊 Hit Rate:', result.hitRate.toFixed(1) + '%');
    console.log('⚡ Average Response Time:', result.avgResponseTime.toFixed(2) + 'ms');
    console.log('🔄 Total Operations:', result.totalOperations);
    console.log('✅ Hit Rate Target:', result.meetsHitRateTarget ? 'MET' : 'NOT MET');
    console.log('✅ Response Time Target:', result.meetsResponseTimeTarget ? 'MET' : 'NOT MET');

    if (result.meetsHitRateTarget && result.meetsResponseTimeTarget) {
      console.log('\n🎉 Advanced caching strategy optimization successful!');
      process.exit(0);
    } else {
      console.log('\n⚠️ Caching optimization targets not fully met.');
      process.exit(1);
    }
  } else {
    console.log('\n❌ Advanced caching strategy test failed.');
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}
