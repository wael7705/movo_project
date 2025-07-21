import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      '*.css': {
        loaders: ['@tailwindcss/postcss'],
        as: '*.css',
      },
    },
  },
};

export default nextConfig;
