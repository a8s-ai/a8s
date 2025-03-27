import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    ppr: true,
  },
  images: {
    remotePatterns: [
      {
        hostname: 'avatar.vercel.sh',
      },
    ],
  },
  output: 'standalone',
  rewrites: async () => {
    return [
      {
        source: '/:host*/websockify',
        destination: 'http://:host*:6080/websockify',
      },
    ];
  },
};

export default nextConfig;
