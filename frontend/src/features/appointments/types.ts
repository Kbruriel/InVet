/**
 * Tipos TypeScript para el módulo de citas (FE-008).
 * Contratos basados en BE-008-plan.md endpoints documentation.
 */

export type AppointmentStatus = 
  | 'pending'
  | 'approved'
  | 'confirmed'
  | 'completed'
  | 'no_show'
  | 'cancelled'
  | 'rescheduled';

export type AppointmentType =
  | 'consultation'
  | 'vaccination'
  | 'surgery'
  | 'follow_up'
  | 'emergency'
  | 'other';

export interface Appointment {
  id: number;
  owner_id: number;
  pet_id: number | null;
  veterinarian_id: number | null;
  clinic_id: number;
  branch_id: number | null;
  scheduled_start: string;
  scheduled_end: string;
  status: AppointmentStatus;
  appointment_type: AppointmentType;
  reason: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppointmentCreate {
  owner_id: number;
  pet_id?: number;
  veterinarian_id?: number | null;
  scheduled_start: string;
  scheduled_end: string;
  reason?: string;
  appointment_type?: AppointmentType;
}

export interface StatusTransition {
  status: AppointmentStatus;
}

export interface AppointmentListResponse {
  items: Appointment[];
  meta: {
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface AvailabilitySlot {
  start: string;
  end: string;
  available: boolean;
  veterinarian_id?: number | null;
}

export interface AvailabilityResponse {
  slots: AvailabilitySlot[];
  date: string;
  clinic_id: number;
  branch_id?: number | null;
}

export interface AppointmentFormData {
  pet_id: number;
  veterinarian_id?: number | null;
  appointment_type: AppointmentType;
  scheduled_start: string;
  scheduled_end: string;
  reason?: string;
}

export type ActionMenuAction = 
  | 'approve'
  | 'confirm'
  | 'complete'
  | 'cancel'
  | 'no_show'
  | 'reschedule';
