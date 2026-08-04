export interface BranchPublicProfile {
  id: number
  clinic_id: number
  name: string
  description?: string
  address: string
  city: string
  state: string
  country: string
  postal_code: string
  phone?: string
  email?: string
  is_active: boolean
  services: ServicePublic[]
  schedules: SchedulePublic[]
  rating_summary?: RatingSummaryPublic | null
  availability_summary?: AvailabilitySummaryPublic | null
}

export interface BranchProtectedProfile extends BranchPublicProfile {
  // Extended fields can go here when needed
}

export interface ServicePublic {
  id: number
  name: string
  description?: string
  is_active: boolean
}

export interface SchedulePublic {
  id: number
  day_of_week: number
  open_time: string
  close_time: string
  is_active: boolean
}

export interface RatingSummaryPublic {
  average_rating: number | null
  total_reviews: number
  review_distribution?: string | null
}

export interface AvailabilitySummaryPublic {
  is_available: boolean
  next_available_time?: string | null
  availability_type?: string | null
}
