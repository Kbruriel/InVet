'use client';

/**
 * Agenda Clinica — Página de agenda para personal clinico (FE-008).
 * RUTA: /clinic/appointments
 */

import { ClinicAgenda } from '@/features/appointments/components/ClinicAgenda';

export default function ClinicAppointmentsPage() {
  // TODO: Replace with actual clinic/veterinarian ID from auth context/session
  const clinicId = 1;
  const veterinarianId = 1;

  return (
    <div className="min-h-screen bg-gray-50">
      <ClinicAgenda
        clinicId={clinicId}
        veterinarianId={veterinarianId}
        onAppointmentClick={(id) => {
          window.location.href = `/clinic/appointments/${id}`;
        }}
        onStatusChange={(aptId, newStatus) => {
          console.log(`Cita ${aptId} cambio a estado: ${newStatus}`);
        }}
      />
    </div>
  );
}
