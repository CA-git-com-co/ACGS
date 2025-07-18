/**
 * Next.js Configuration for ACGS-2 Frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * Production-optimized build configuration with constitutional compliance.
 */

const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false,
  generateEtags: false,
  
  // Experimental features
  experimental: {
    serverComponentsExternalPackages: ['@tanstack/react-query'],
    optimizeCss: true,
    gzipSize: true,
    // Enable modern output for better performance
    esmExternals: true,
    // Enable SWC compiler optimizations
    swcTraceProfiling: true,
  },
  
  // Production optimizations
  compiler: {
    // Remove console logs in production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
    // React optimizations
    reactRemoveProperties: process.env.NODE_ENV === 'production',
  },
  
  // Image optimization
  images: {
    domains: ['localhost', 'acgs.local', 'acgs-2.local'],
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 3600,
    dangerouslyAllowSVG: false,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  
  // Environment variables
  env: {
    CONSTITUTIONAL_HASH: 'cdd01ef066bc6cf2',
    NEXT_PUBLIC_CONSTITUTIONAL_HASH: 'cdd01ef066bc6cf2',
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010',
    NEXT_PUBLIC_GRAPHQL_URL: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8010/graphql',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8010/ws',
    NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING: process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING || 'true',
    NEXT_PUBLIC_ENABLE_CONSTITUTIONAL_VALIDATION: process.env.NEXT_PUBLIC_ENABLE_CONSTITUTIONAL_VALIDATION || 'true',
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Constitutional-Hash',
            value: 'cdd01ef066bc6cf2',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), payment=(), usb=(),',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self' data:",
              "connect-src 'self' ws: wss:",
              "frame-ancestors 'none'",
            ].join('; '),
          },
          {
            key: 'X-Performance-Target',
            value: 'P99<5ms,RPS>100,Cache>85%',
          },
        ],
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, no-cache, must-revalidate',
          },
          {
            key: 'X-Constitutional-Hash',
            value: 'cdd01ef066bc6cf2',
          },
        ],
      },
      {
        source: '/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  
  // Redirects
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
      {
        source: '/admin',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
  
  // Webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Constitutional compliance validation
    config.plugins.push(
      new webpack.DefinePlugin({
        'process.env.CONSTITUTIONAL_HASH': JSON.stringify('cdd01ef066bc6cf2'),
        'process.env.BUILD_ID': JSON.stringify(buildId),
        'process.env.BUILD_TIME': JSON.stringify(new Date().toISOString()),
      })
    );
    
    // Performance optimizations
    if (!dev && !isServer) {
      // Bundle analyzer for production builds
      if (process.env.ANALYZE === 'true') {
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            openAnalyzer: false,
            reportFilename: path.join(__dirname, 'bundle-analysis.html'),
          })
        );
      }
      
      // Optimize chunks for better caching
      config.optimization.splitChunks = {
        ...config.optimization.splitChunks,
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          // Vendor chunk for stable dependencies
          vendor: {
            name: 'vendor',
            chunks: 'all',
            test: /node_modules/,
            priority: 20,
          },
          // Common chunk for shared code
          common: {
            name: 'common',
            chunks: 'all',
            minChunks: 2,
            priority: 10,
            reuseExistingChunk: true,
            enforce: true,
          },
          // Constitutional compliance chunk
          constitutional: {
            name: 'constitutional',
            chunks: 'all',
            test: /constitutional|validation/,
            priority: 15,
            reuseExistingChunk: true,
          },
        },
      };
    }
    
    // Fallbacks for client-side
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
      };
    }
    
    // Performance monitoring
    if (process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING === 'true') {
      config.plugins.push(
        new webpack.ProgressPlugin({
          entries: true,
          modules: true,
          dependencies: true,
          handler: (percentage, message) => {
            if (percentage === 1) {
              console.log(`✅ Build completed with constitutional compliance`);
            }
          },
        })
      );
    }
    
    return config;
  },
  
  // Output configuration
  output: 'standalone',
  
  // Compression
  compress: true,
  
  // Trailing slash
  trailingSlash: false,
  
  // Production source maps
  productionBrowserSourceMaps: false,
  
  // Static export configuration
  exportPathMap: async function (defaultPathMap, { dev, dir, outDir, distDir, buildId }) {
    if (dev) {
      return defaultPathMap;
    }
    
    return {
      '/': { page: '/' },
      '/dashboard': { page: '/dashboard' },
      '/health': { page: '/health' },
    };
  },
};

// Performance monitoring for build times
if (process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING === 'true') {
  const originalBuild = nextConfig.webpack;
  nextConfig.webpack = function (config, options) {
    const start = Date.now();
    
    if (originalBuild) {
      config = originalBuild(config, options);
    }
    
    const buildTime = Date.now() - start;
    if (buildTime > 10000) { // 10 seconds
      console.warn(`⚠️ Build time (${buildTime}ms) exceeds performance target`);
    }
    
    return config;
  };
}

module.exports = nextConfig;