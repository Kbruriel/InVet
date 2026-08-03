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