import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // Add rewrites to proxy API requests to the FastAPI backend
    async rewrites() {
      const apiUrl = process.env.API_URL || 'http://localhost:8000';
      return [
        {
          source: '/api/:path*',
          destination: `${apiUrl}/api/:path*`, // Proxy to Backend
        },
      ];
    },
  };

export default nextConfig;
