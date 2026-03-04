/** @type {import('next').NextConfig} */
const nextConfig = {
  // API calls go directly from browser to http://localhost:8000 via NEXT_PUBLIC_API_URL.
  // No rewrite proxy needed — it had a ~60s socket timeout that killed long AI requests.
};

module.exports = nextConfig;
