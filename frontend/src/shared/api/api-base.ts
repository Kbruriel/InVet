const DEFAULT_SERVER_API_BASE = 'http://localhost:8000/api/v1';
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
