/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverComponentsExternalPackages: ['@tanstack/react-query'],
  },
  images: {
    domains: ['localhost', 'acgs.local'],
    formats: ['image/avif', 'image/webp'],
  },
  env: {
    CONSTITUTIONAL_HASH: 'cdd01ef066bc6cf2',
    NEXT_PUBLIC_CONSTITUTIONAL_HASH: 'cdd01ef066bc6cf2',
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010',
    NEXT_PUBLIC_GRAPHQL_URL: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8010/graphql',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8010/ws',
  },
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
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        fs: false,
        path: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;