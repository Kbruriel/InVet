// Proxy the shared API on same-origin so browser fetches stay same-origin and
// avoid CORS; the FE reads `access_token` from localStorage on :3000 and sends
// it in the Authorization header on every request (client.ts `buildHeaders`).
// In production there is a reverse proxy that does this the same way.
// Inside docker compose the backend is reachable via the service alias
// (`BACKEND_INTERNAL_URL`, set by docker-compose.yml); standalone dev falls
// back to localhost:8000.
const BACKEND_API_BASE =
  process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000';

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_API_BASE}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
