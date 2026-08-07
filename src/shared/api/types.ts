export interface Clinic {
  id: string;
  name: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  opening_hours: string;
  latitude: number;
  longitude: number;
  branches?: Branch[];
}

export interface Branch {
  id: string;
  name: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  opening_hours: string;
  latitude: number;
  longitude: number;
  clinic_id: string;
}

export interface ClinicSearchResponse {
  data: Clinic[];
  pagination: {
    page: number;
    size: number;
    total: number;
    total_pages: number;
  };
}

// Branch Profile Types

export interface BranchPublicProfile {
  id: string;
  clinic_id: string;
  name: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  latitude: number;
  longitude: number;
  opening_hours: string;
  services: {
    id: string;
    name: string;
    description: string;
    is_active: boolean;
  }[];
  schedule: {
    day_of_week: number; // Monday=0, Sunday=6
    open_time: string;  // HH:MM format
    close_time: string; // HH:MM format
    is_closed: boolean;
  }[];
  rating_summary: {
    average_rating: number;
    total_reviews: number;
    rating_distribution: {
      [rating: number]: number;
    };
  };
  availability_summary: {
    is_available: boolean;
    next_available_time?: string;
    notes?: string;
  };
}

export interface BranchProtectedProfile {
  id: string;
  clinic_id: string;
  name: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  latitude: number;
  longitude: number;
  opening_hours: string;
  services: {
    id: string;
    name: string;
    description: string;
    is_active: boolean;
  }[];
  schedule: {
    day_of_week: number; // Monday=0, Sunday=6
    open_time: string;  // HH:MM format
    close_time: string; // HH:MM format
    is_closed: boolean;
  }[];
  rating_summary: {
    average_rating: number;
    total_reviews: number;
    rating_distribution: {
      [rating: number]: number;
    };
  };
  availability_summary: {
    is_available: boolean;
    next_available_time?: string;
    notes?: string;
  };
  // Protected fields (not in public profile)
  owner_id?: string;
  created_at?: string;
  updated_at?: string;
}