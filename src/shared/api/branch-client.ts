import { BranchPublicProfile } from './types';

export class BranchClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to /api/v1 for development
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
  }

  /**
   * Fetch branch public profile by branch ID
   */
  async getBranchPublicProfile(branchId: string): Promise<BranchPublicProfile> {
    const response = await fetch(`${this.baseUrl}/clinics/branches/${branchId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// Export a singleton instance
export const branchClient = new BranchClient();