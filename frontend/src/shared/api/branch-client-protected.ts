import type { BranchProtectedProfile } from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

/**
 * Fetch for protected endpoint. Must be called with proper Authorization header.
 */
export async function fetchBranchProtected(
  clinicId: number,
  branchId: number,
  token?: string | null
): Promise<BranchProtectedProfile> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  } else {
    // Client-side fallback for API route proxy
    const stored = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (stored) {
      headers['Authorization'] = `Bearer ${stored}`
    }
  }

  const res = await fetch(
    `${BASE_URL}/api/v1/clinics/branches/${clinicId}/${branchId}`,
    { method: 'GET', headers, credentials: 'include' }
  )

  if (!res.ok) {
    const body = res.status === 204 ? '' : await res.text().catch(() => '')
    const err = new Error(
      `fetchBranchProtected failed: ${res.status} ${res.statusText}${body ? ` - ${body}` : ''}`
    ) as any
    err.status = res.status
    throw err
  }

  return res.json()
}
