'use client';

/**
 * Nueva Cita — Página para solicitar nueva cita (FE-008).
 * RUTA: /portal/owner/appointments/new
 */

import { AppointmentForm } from '@/features/appointments/components/AppointmentForm';

export default function NewAppointmentPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4">
        <AppointmentForm onSuccess={() => { window.location.href = '/portal/owner/appointments'; }} />
      </div>
    </div>
  );
}
