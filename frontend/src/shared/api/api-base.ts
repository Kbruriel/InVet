const DEFAULT_SERVER_API_BASE = 'http://localhost:8000/api/v1';
// Same-origin base so the browser stays on the FE origin; Next.js `rewrites`
// in `next.config.js` forwards `/api/v1/*` to the backend. Domain service
// callers (`public.ts`, `owner-portal.ts`, `auth.ts`, consultation, etc.)
// append just `/resource` (see their unit tests expecting `${base}/resource`).
const SAME_ORIGIN_API_BASE = '/api/v1';

export function resolveApiBase(): string {
  if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'test') {
    return SAME_ORIGIN_API_BASE;
  }

  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!configured) {
    return DEFAULT_SERVER_API_BASE;
  }

  return configured.replace(/\/$/, '');
}
