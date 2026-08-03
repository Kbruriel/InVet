import { Clinic, ClinicSearchResponse } from './types';

export class ApiClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to /api/v1 for development
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
  }

  /**
   * Fetch clinics with pagination and filters
   */
  async getClinics({
    page = 1,
    size = 10,
    search,
    city
  }: {
    page?: number;
    size?: number;
    search?: string;
    city?: string;
  }): Promise<ClinicSearchResponse> {
    const params = new URLSearchParams();
    
    if (page) params.append('page', page.toString());
    if (size) params.append('size', size.toString());
    if (search) params.append('search', search);
    if (city) params.append('city', city);

    const url = `${this.baseUrl}/clinics?${params.toString()}`;
    
    const response = await fetch(url, {
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

  /**
   * Fetch clinic by ID
   */
  async getClinicById(id: string): Promise<Clinic> {
    const response = await fetch(`${this.baseUrl}/clinics/${id}`, {
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
export const apiClient = new ApiClient();