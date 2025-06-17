# Production Deployment Guide

## Deployment Architecture ✅

The governance dashboard is configured for production deployment with multiple provider options, optimized CI/CD pipelines, and comprehensive monitoring.

### Supported Deployment Providers
- **Vercel** (Recommended for Next.js applications)
- **Netlify** (Static site deployment)
- **AWS Amplify** (Full-stack deployment)
- **Docker** (Containerized deployment)

## Environment Configuration ✅

### Environment Variables
```bash
# .env.production
# Application Configuration
NODE_ENV=production
NEXT_PUBLIC_APP_VERSION=1.0.0

# API Endpoints
NEXT_PUBLIC_AC_API_URL=https://api.governance.example.com/ac/v1
NEXT_PUBLIC_GS_API_URL=https://api.governance.example.com/gs/v1
NEXT_PUBLIC_PGC_API_URL=https://api.governance.example.com/pgc/v1
NEXT_PUBLIC_INTEGRITY_API_URL=https://api.governance.example.com/integrity/v1

# Authentication
NEXT_PUBLIC_AUTH_URL=https://auth.governance.example.com
NEXTAUTH_SECRET=your-secure-secret-key
NEXTAUTH_URL=https://dashboard.governance.example.com

# Analytics and Monitoring
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Feature Flags
NEXT_PUBLIC_ENABLE_ALPHA_EVOLVE=true
NEXT_PUBLIC_ENABLE_CONSTITUTIONAL_COUNCIL=true
```

### Build Configuration
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    typedRoutes: true,
  },
  
  // Performance optimizations
  compress: true,
  poweredByHeader: false,
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;",
          },
        ],
      },
    ];
  },
  
  // Asset optimization
  images: {
    domains: ['images.pexels.com', 'via.placeholder.com'],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Bundle analysis
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: isServer ? '../analyze/server.html' : './analyze/client.html',
        })
      );
    }
    
    return config;
  },
};

module.exports = nextConfig;
```

## Vercel Deployment ✅

### Vercel Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  },
  "build": {
    "env": {
      "NEXT_TELEMETRY_DISABLED": "1"
    }
  }
}
```

### Deployment Script
```bash
#!/bin/bash
# deploy-vercel.sh

echo "🚀 Starting Vercel deployment..."

# Build and test
npm run build
npm run test:ci
npm run lint

# Deploy to Vercel
vercel --prod

echo "✅ Deployment completed successfully!"
```

## Docker Deployment ✅

### Multi-stage Dockerfile
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

### Docker Compose for Development
```yaml
# infrastructure/docker/docker-compose.yml
version: '3.8'

services:
  governance-dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/governance
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: governance
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - governance-dashboard

volumes:
  postgres_data:
```

## CI/CD Pipeline ✅

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run type check
        run: npm run type-check
      
      - name: Run linting
        run: npm run lint
      
      - name: Run unit tests
        run: npm run test:coverage
      
      - name: Run accessibility tests
        run: npm run test:a11y
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3

  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Build application
        run: npm run build
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload E2E test results
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/

  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Run Lighthouse CI
        run: npm run lhci:autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build-and-deploy:
    needs: [test, e2e-test, lighthouse, security-scan]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
        env:
          NODE_ENV: production
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-args: '--prod'
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
      
      - name: Post-deployment tests
        run: npm run test:production
        env:
          DEPLOYMENT_URL: ${{ steps.vercel.outputs.preview-url }}

  notify:
    needs: [build-and-deploy]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Release Automation
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Generate changelog
        id: changelog
        uses: requarks/changelog-action@v1
        with:
          token: ${{ github.token }}
          tag: ${{ github.ref_name }}
      
      - name: Create Release
        uses: ncipollo/release-action@v1
        with:
          allowUpdates: true
          draft: false
          makeLatest: true
          name: ${{ github.ref_name }}
          body: ${{ steps.changelog.outputs.changes }}
          token: ${{ github.token }}
      
      - name: Deploy to production
        run: npm run deploy:production
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

## Monitoring and Observability ✅

### Application Monitoring
```typescript
// lib/monitoring.ts
import * as Sentry from '@sentry/nextjs';

// Initialize Sentry
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
  debug: false,
});

// Performance monitoring
export const trackPerformance = (name: string, fn: () => void) => {
  const transaction = Sentry.startTransaction({ name });
  try {
    const result = fn();
    transaction.setStatus('ok');
    return result;
  } catch (error) {
    transaction.setStatus('internal_error');
    Sentry.captureException(error);
    throw error;
  } finally {
    transaction.finish();
  }
};

// Custom metrics
export const trackCustomMetric = (name: string, value: number, tags?: Record<string, string>) => {
  Sentry.setMeasurement(name, value, 'number');
  if (tags) {
    Sentry.setTags(tags);
  }
};

// Error tracking
export const trackError = (error: Error, context?: Record<string, any>) => {
  Sentry.withScope((scope) => {
    if (context) {
      scope.setContext('additional_info', context);
    }
    Sentry.captureException(error);
  });
};
```

### Health Check Endpoint
```typescript
// pages/api/health.ts
import { NextApiRequest, NextApiResponse } from 'next';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  checks: {
    database: boolean;
    redis: boolean;
    external_apis: boolean;
  };
  uptime: number;
  memory: {
    used: number;
    free: number;
    total: number;
  };
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthStatus>
) {
  try {
    const startTime = process.hrtime.bigint();
    
    // Check database connectivity
    const dbCheck = await checkDatabase();
    
    // Check external API connectivity
    const apiCheck = await checkExternalAPIs();
    
    const endTime = process.hrtime.bigint();
    const responseTime = Number(endTime - startTime) / 1000000; // Convert to milliseconds
    
    const memoryUsage = process.memoryUsage();
    
    const health: HealthStatus = {
      status: dbCheck && apiCheck ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
      checks: {
        database: dbCheck,
        redis: true, // Add Redis check if using Redis
        external_apis: apiCheck,
      },
      uptime: process.uptime(),
      memory: {
        used: memoryUsage.heapUsed,
        free: memoryUsage.heapTotal - memoryUsage.heapUsed,
        total: memoryUsage.heapTotal,
      },
    };

    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.status(health.status === 'healthy' ? 200 : 503).json(health);
  } catch (error) {
    console.error('Health check failed:', error);
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
      checks: {
        database: false,
        redis: false,
        external_apis: false,
      },
      uptime: process.uptime(),
      memory: {
        used: 0,
        free: 0,
        total: 0,
      },
    });
  }
}

async function checkDatabase(): Promise<boolean> {
  try {
    // Add database connectivity check
    return true;
  } catch {
    return false;
  }
}

async function checkExternalAPIs(): Promise<boolean> {
  try {
    // Check critical external APIs
    const checks = await Promise.allSettled([
      fetch(`${process.env.NEXT_PUBLIC_AC_API_URL}/health`),
      fetch(`${process.env.NEXT_PUBLIC_GS_API_URL}/health`),
    ]);
    
    return checks.every(check => check.status === 'fulfilled');
  } catch {
    return false;
  }
}
```

### Performance Monitoring
```typescript
// lib/analytics.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export function reportWebVitals() {
  getCLS((metric) => {
    sendToAnalytics('CLS', metric.value, metric.rating);
  });

  getFID((metric) => {
    sendToAnalytics('FID', metric.value, metric.rating);
  });

  getFCP((metric) => {
    sendToAnalytics('FCP', metric.value, metric.rating);
  });

  getLCP((metric) => {
    sendToAnalytics('LCP', metric.value, metric.rating);
  });

  getTTFB((metric) => {
    sendToAnalytics('TTFB', metric.value, metric.rating);
  });
}

function sendToAnalytics(name: string, value: number, rating: string) {
  // Send to your analytics provider
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', name, {
      custom_parameter_1: value,
      custom_parameter_2: rating,
    });
  }
  
  // Also send to custom monitoring
  fetch('/api/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metric: name, value, rating }),
  }).catch(console.error);
}
```

## Security Configuration ✅

### Content Security Policy
```typescript
// lib/csp.ts
export const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  img-src 'self' data: https: blob:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.governance.example.com https://vitals.vercel-insights.com;
  frame-src 'none';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
`;
```

### Security Headers
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { ContentSecurityPolicy } from './lib/csp';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Security headers
  response.headers.set('X-DNS-Prefetch-Control', 'on');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'origin-when-cross-origin');
  response.headers.set('Content-Security-Policy', ContentSecurityPolicy);

  return response;
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## Performance Optimization ✅

### Bundle Analysis
```bash
# Analyze bundle size
npm run build
ANALYZE=true npm run build

# Performance budget check
npm run lighthouse:budget
```

### Caching Strategy
```typescript
// next.config.js cache headers
const nextConfig = {
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/image',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

## Backup and Recovery ✅

### Database Backup Strategy
```bash
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="governance_db_backup_$DATE.sql"

# Create backup
pg_dump $DATABASE_URL > /backups/$BACKUP_FILE

# Upload to S3
aws s3 cp /backups/$BACKUP_FILE s3://governance-backups/database/

# Cleanup old backups (keep last 30 days)
find /backups -name "governance_db_backup_*.sql" -mtime +30 -delete

echo "Database backup completed: $BACKUP_FILE"
```

### Disaster Recovery Plan
1. **Database Recovery**: Restore from latest automated backup
2. **Application Recovery**: Redeploy from last known good commit
3. **CDN Purge**: Clear CDN cache if needed
4. **DNS Failover**: Switch to backup infrastructure
5. **Monitoring**: Verify all systems are operational

This deployment guide ensures a robust, secure, and scalable production environment for the governance dashboard with comprehensive monitoring, automated deployments, and disaster recovery capabilities.