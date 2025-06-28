/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Enable ESLint during builds
    ignoreDuringBuilds: false,
    // Include accessibility linting
    dirs: ['pages', 'components', 'lib', 'src'],
  },
  // Enable accessibility features
  experimental: {
    optimizeCss: true,
  },
  // Add security headers for accessibility
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
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
        ],
      },
    ];
  },
};

module.exports = nextConfig;
