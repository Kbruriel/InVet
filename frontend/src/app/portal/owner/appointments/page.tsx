'use client';

/**
 * Mi Agenda — Página de agenda del propietario (FE-008).
 * RUTA: /portal/owner/appointments
 */

import { OwnerAgenda } from '@/features/appointments/components/OwnerAgenda';

export default function OwnerAppointmentsPage() {
  // TODO: Replace with actual owner ID from auth context/session
  const ownerId = 1;

  return (
    <div className="min-h-screen bg-gray-50">
      <OwnerAgenda
        ownerId={ownerId}
        onAppointmentClick={(id) => {
          window.location.href = `/portal/owner/appointments/${id}`;
        }}
      />
    </div>
  );
}
