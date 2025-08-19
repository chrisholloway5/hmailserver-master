/** @type {import('next').NextConfig} */
const nextConfig = {
  // TypeScript Configuration
  typescript: {
    ignoreBuildErrors: false,
  },
  
  eslint: {
    ignoreDuringBuilds: false,
  },

  // Image Optimization
  images: {
    unoptimized: true, // For development
    domains: ['localhost', 'hmailserver.local'],
  },

  // Output Configuration
  output: 'standalone',
  distDir: '.next',

  // Performance
  poweredByHeader: false,
  generateEtags: false,
  compress: true,
  reactStrictMode: true,

  // Development
  devIndicators: {
    position: 'bottom-right',
  },
};

module.exports = nextConfig;