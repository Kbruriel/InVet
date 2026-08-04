import type { BranchPublicProfile, BranchProtectedProfile } from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

export async function fetchBranchPublic(branchId: number): Promise<BranchPublicProfile> {
  const res = await fetch(`${BASE_URL}/api/v1/clinics/branches/${branchId}`)
  if (!res.ok) {
    throw new Error(`fetchBranchPublic failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}
