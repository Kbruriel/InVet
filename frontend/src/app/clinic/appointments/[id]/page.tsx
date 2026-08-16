'use client';

/**
 * Detalle de Cita (Clinica) — Página de detalle desde perspectiva clinica (FE-008).
 * RUTA: /clinic/appointments/[id]
 */

import { AppointmentDetail } from '@/features/appointments/components/AppointmentDetail';
import { notFound, redirect } from 'next/navigation';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function ClinicAppointmentDetailPage({ params }: PageProps) {
  const { id } = await params;
  const appointmentId = parseInt(id, 10);

  if (isNaN(appointmentId)) {
    notFound();
  }

  return <AppointmentDetail appointmentId={appointmentId} onBack={() => redirect('/clinic/appointments')} />;
}
