import { BranchProtectedProfile } from './types';

export class BranchProtectedClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to /api/v1 for development
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
  }

  /**
   * Fetch branch protected profile by clinic ID and branch ID
   */
  async getBranchProtectedProfile(clinicId: string, branchId: string): Promise<BranchProtectedProfile> {
    const response = await fetch(`${this.baseUrl}/clinics/${clinicId}/${branchId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // In real implementation, this would include authentication token
        // 'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// Export a singleton instance
export const branchProtectedClient = new BranchProtectedClient();