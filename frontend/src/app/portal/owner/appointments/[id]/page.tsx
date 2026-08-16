'use client';

/**
 * Detalle de Cita — Página de detalle de una cita específica (FE-008).
 * RUTA: /portal/owner/appointments/[id]
 */

import { AppointmentDetail } from '@/features/appointments/components/AppointmentDetail';
import { notFound, redirect } from 'next/navigation';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function AppointmentDetailPage({ params }: PageProps) {
  const { id } = await params;
  const appointmentId = parseInt(id, 10);

  if (isNaN(appointmentId)) {
    notFound();
  }

  // Server-side rendering client component
  return <AppointmentDetail appointmentId={appointmentId} onBack={() => redirect('/portal/owner/appointments')} />;
}
