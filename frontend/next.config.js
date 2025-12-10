/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // For production deployment: export as static site
  output: process.env.NODE_ENV === 'production' ? 'export' : undefined,
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
