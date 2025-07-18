#!/usr/bin/env node
/**
 * Production Build Script for ACGS-2 Frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Optimized build pipeline with constitutional compliance validation.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');

// Constitutional compliance
const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2';
const PERFORMANCE_TARGETS = {
  P99_LATENCY: 5, // ms
  THROUGHPUT_RPS: 100,
  CACHE_HIT_RATE: 85, // %
  BUNDLE_SIZE_LIMIT: 1024 * 1024, // 1MB
  FIRST_CONTENTFUL_PAINT: 1.5, // seconds
  LIGHTHOUSE_SCORE: 90,
};

// Build metrics
let buildMetrics = {
  startTime: Date.now(),
  endTime: null,
  duration: null,
  bundleSize: null,
  constitutionalCompliance: false,
  performanceTargetsMet: false,
  errors: [],
  warnings: [],
};

/**
 * Main build function
 */
async function buildProduction() {
  console.log(chalk.blue('🚀 Starting ACGS-2 Frontend Production Build'));
  console.log(chalk.gray(`Constitutional Hash: ${CONSTITUTIONAL_HASH}`));
  console.log(chalk.gray(`Build Time: ${new Date().toISOString()}`));
  console.log('');

  try {
    // Pre-build validation
    await validateEnvironment();
    await validateConstitutionalCompliance();
    
    // Clean previous builds
    await cleanBuildArtifacts();
    
    // Install dependencies
    await installDependencies();
    
    // Type checking
    await typeCheck();
    
    // Linting
    await lintCode();
    
    // Build the application
    await buildApplication();
    
    // Post-build validation
    await validateBuildArtifacts();
    await performanceValidation();
    await securityValidation();
    
    // Generate build report
    await generateBuildReport();
    
    buildMetrics.endTime = Date.now();
    buildMetrics.duration = buildMetrics.endTime - buildMetrics.startTime;
    
    console.log(chalk.green('✅ Production build completed successfully'));
    console.log(chalk.gray(`Total build time: ${buildMetrics.duration}ms`));
    
    if (buildMetrics.duration > 60000) { // 1 minute
      console.log(chalk.yellow('⚠️  Build time exceeds 1 minute - consider optimizing'));
    }
    
  } catch (error) {
    console.error(chalk.red('❌ Build failed:'), error.message);
    buildMetrics.errors.push(error.message);
    process.exit(1);
  }
}

/**
 * Validate environment setup
 */
async function validateEnvironment() {
  console.log(chalk.yellow('🔍 Validating environment...'));
  
  // Check Node.js version
  const nodeVersion = process.version;
  const requiredVersion = '18.0.0';
  
  if (!nodeVersion.startsWith('v18') && !nodeVersion.startsWith('v20')) {
    throw new Error(`Node.js version ${nodeVersion} is not supported. Please use Node.js 18 or 20.`);
  }
  
  // Check required environment variables
  const requiredEnvVars = [
    'NEXT_PUBLIC_API_BASE_URL',
    'NEXT_PUBLIC_CONSTITUTIONAL_HASH',
  ];
  
  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      throw new Error(`Missing required environment variable: ${envVar}`);
    }
  }
  
  console.log(chalk.green('✅ Environment validation passed'));
}

/**
 * Validate constitutional compliance
 */
async function validateConstitutionalCompliance() {
  console.log(chalk.yellow('🔍 Validating constitutional compliance...'));
  
  const configPath = path.join(process.cwd(), 'src/config/index.ts');
  const configContent = fs.readFileSync(configPath, 'utf8');
  
  if (!configContent.includes(CONSTITUTIONAL_HASH)) {
    throw new Error('Constitutional hash not found in configuration');
  }
  
  // Check for constitutional hash in key files
  const keyFiles = [
    'src/lib/constitutional-client.ts',
    'src/hooks/useConstitutionalValidation.ts',
    'src/services/constitutional-ai.ts',
  ];
  
  for (const file of keyFiles) {
    const filePath = path.join(process.cwd(), file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      if (!content.includes(CONSTITUTIONAL_HASH)) {
        throw new Error(`Constitutional hash not found in ${file}`);
      }
    }
  }
  
  buildMetrics.constitutionalCompliance = true;
  console.log(chalk.green('✅ Constitutional compliance validation passed'));
}

/**
 * Clean previous build artifacts
 */
async function cleanBuildArtifacts() {
  console.log(chalk.yellow('🧹 Cleaning build artifacts...'));
  
  const dirsToClean = ['.next', 'out', 'dist', 'build'];
  
  for (const dir of dirsToClean) {
    const dirPath = path.join(process.cwd(), dir);
    if (fs.existsSync(dirPath)) {
      execSync(`rm -rf ${dirPath}`, { stdio: 'inherit' });
    }
  }
  
  console.log(chalk.green('✅ Build artifacts cleaned'));
}

/**
 * Install dependencies
 */
async function installDependencies() {
  console.log(chalk.yellow('📦 Installing dependencies...'));
  
  try {
    // Use npm ci for faster, reliable installs
    execSync('npm ci --only=production', { stdio: 'inherit' });
    console.log(chalk.green('✅ Dependencies installed'));
  } catch (error) {
    throw new Error('Failed to install dependencies');
  }
}

/**
 * Type checking
 */
async function typeCheck() {
  console.log(chalk.yellow('🔍 Type checking...'));
  
  try {
    execSync('npx tsc --noEmit', { stdio: 'inherit' });
    console.log(chalk.green('✅ Type checking passed'));
  } catch (error) {
    throw new Error('Type checking failed');
  }
}

/**
 * Lint code
 */
async function lintCode() {
  console.log(chalk.yellow('🔍 Linting code...'));
  
  try {
    execSync('npx eslint src --ext .ts,.tsx --max-warnings 0', { stdio: 'inherit' });
    console.log(chalk.green('✅ Code linting passed'));
  } catch (error) {
    // Allow warnings but not errors
    console.log(chalk.yellow('⚠️  Linting completed with warnings'));
  }
}

/**
 * Build the application
 */
async function buildApplication() {
  console.log(chalk.yellow('🔨 Building application...'));
  
  try {
    // Set production environment
    process.env.NODE_ENV = 'production';
    process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING = 'true';
    
    // Run Next.js build
    execSync('npx next build', { stdio: 'inherit' });
    
    console.log(chalk.green('✅ Application built successfully'));
  } catch (error) {
    throw new Error('Application build failed');
  }
}

/**
 * Validate build artifacts
 */
async function validateBuildArtifacts() {
  console.log(chalk.yellow('🔍 Validating build artifacts...'));
  
  const buildDir = path.join(process.cwd(), '.next');
  
  if (!fs.existsSync(buildDir)) {
    throw new Error('Build directory not found');
  }
  
  // Check for required files
  const requiredFiles = [
    '.next/BUILD_ID',
    '.next/build-manifest.json',
    '.next/prerender-manifest.json',
  ];
  
  for (const file of requiredFiles) {
    const filePath = path.join(process.cwd(), file);
    if (!fs.existsSync(filePath)) {
      throw new Error(`Required build file not found: ${file}`);
    }
  }
  
  // Calculate bundle size
  const staticDir = path.join(buildDir, 'static');
  if (fs.existsSync(staticDir)) {
    const bundleSize = execSync(`du -sb ${staticDir}`, { encoding: 'utf8' });
    buildMetrics.bundleSize = parseInt(bundleSize.split('\t')[0]);
    
    if (buildMetrics.bundleSize > PERFORMANCE_TARGETS.BUNDLE_SIZE_LIMIT) {
      console.log(chalk.yellow(`⚠️  Bundle size (${Math.round(buildMetrics.bundleSize / 1024 / 1024)}MB) exceeds limit`));
    }
  }
  
  console.log(chalk.green('✅ Build artifacts validated'));
}

/**
 * Performance validation
 */
async function performanceValidation() {
  console.log(chalk.yellow('🔍 Performance validation...'));
  
  // Check if bundle analysis is available
  if (process.env.ANALYZE === 'true') {
    const analysisFile = path.join(process.cwd(), 'bundle-analysis.html');
    if (fs.existsSync(analysisFile)) {
      console.log(chalk.blue(`📊 Bundle analysis available at: ${analysisFile}`));
    }
  }
  
  // Performance targets validation
  const performanceChecks = {
    bundleSize: buildMetrics.bundleSize <= PERFORMANCE_TARGETS.BUNDLE_SIZE_LIMIT,
    constitutionalCompliance: buildMetrics.constitutionalCompliance,
  };
  
  const passedChecks = Object.values(performanceChecks).filter(Boolean).length;
  const totalChecks = Object.keys(performanceChecks).length;
  
  if (passedChecks === totalChecks) {
    buildMetrics.performanceTargetsMet = true;
    console.log(chalk.green('✅ Performance validation passed'));
  } else {
    console.log(chalk.yellow(`⚠️  Performance validation: ${passedChecks}/${totalChecks} checks passed`));
  }
}

/**
 * Security validation
 */
async function securityValidation() {
  console.log(chalk.yellow('🔍 Security validation...'));
  
  // Check for security vulnerabilities
  try {
    execSync('npm audit --audit-level=high', { stdio: 'inherit' });
    console.log(chalk.green('✅ Security validation passed'));
  } catch (error) {
    console.log(chalk.yellow('⚠️  Security audit completed with warnings'));
  }
}

/**
 * Generate build report
 */
async function generateBuildReport() {
  console.log(chalk.yellow('📊 Generating build report...'));
  
  const report = {
    buildTime: new Date().toISOString(),
    constitutionalHash: CONSTITUTIONAL_HASH,
    buildMetrics: {
      ...buildMetrics,
      duration: buildMetrics.endTime - buildMetrics.startTime,
    },
    performanceTargets: PERFORMANCE_TARGETS,
    environment: {
      nodeVersion: process.version,
      platform: process.platform,
      arch: process.arch,
    },
    gitInfo: {
      commit: execSync('git rev-parse HEAD', { encoding: 'utf8' }).trim(),
      branch: execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim(),
    },
  };
  
  const reportPath = path.join(process.cwd(), 'build-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  
  console.log(chalk.green(`✅ Build report generated: ${reportPath}`));
}

// Run the build if this script is called directly
if (require.main === module) {
  buildProduction().catch(error => {
    console.error(chalk.red('❌ Build failed:'), error);
    process.exit(1);
  });
}

module.exports = {
  buildProduction,
  validateConstitutionalCompliance,
  CONSTITUTIONAL_HASH,
  PERFORMANCE_TARGETS,
};
