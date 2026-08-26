'use client';

/**
 * AppointmentDetail — Vista detallada de una cita con timeline de transiciones (FE-008).
 */

'use client';

import React, { useState, useEffect } from 'react';
import { getAppointment, transitionStatus } from '../api';
import type { Appointment, AppointmentStatus } from '../types';
import { StatusBadge } from './StatusBadge';
import { RatingForm } from '@/features/reviews/RatingForm';
import { LoadingSpinner } from '@/shared/ui/components/Loading';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';
import { getAccessToken } from '@/shared/auth/session';

interface AppointmentDetailProps {
  appointmentId: number;
  onBack?: () => void;
}

export function AppointmentDetail({ appointmentId, onBack }: AppointmentDetailProps) {
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confirmingStatus, setConfirmingStatus] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && getAccessToken() === null) {
      const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/login?returnUrl=${returnUrl}`;
      return;
    }
    let cancelled = false;

    async function fetchAppointment() {
      setLoading(true);
      setError(null);

      try {
        const data = await getAppointment(appointmentId);
        if (!cancelled) setAppointment(data);
      } catch (err: unknown) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Error al cargar la cita');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAppointment();
    return () => { cancelled = true; };
  }, [appointmentId]);

  const handleStatusTransition = async (newStatus: string) => {
    if (!window.confirm(`¿Confirmar cambio de estado a "${newStatus}"?`)) return;

    setConfirmingStatus(newStatus);
    try {
      await transitionStatus(appointmentId, { status: newStatus as AppointmentStatus });
      // Refetch to update the appointment
      const updated = await getAppointment(appointmentId);
      setAppointment(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al cambiar el estado');
    } finally {
      setConfirmingStatus(null);
    }
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Detalle de cita</h1>
          <p className="text-sm text-gray-500 mt-1">
            {appointment ? `ID: #${appointment.id}` : 'Cargando detalle de la cita'}
          </p>
        </div>
        {appointment ? <StatusBadge status={appointment.status} /> : null}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner />
        </div>
      )}

      {error && (
        <ErrorBanner
          message={error || 'No se encontró la cita'}
          onRetry={onBack}
          actionLabel="Volver"
        />
      )}

      {appointment && (
        <>
          {/* Info principal */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Información de la cita</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Fecha y hora</dt>
                <dd className="text-base text-gray-900">{formatDateTime(appointment.scheduled_start)}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Duración estimada</dt>
                <dd className="text-base text-gray-900">
                  {appointment.scheduled_end && appointment.scheduled_start
                    ? `${Math.round((new Date(appointment.scheduled_end).getTime() - new Date(appointment.scheduled_start).getTime()) / 60000)} min`
                    : 'No especificada'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Tipo de cita</dt>
                <dd className="text-base text-gray-900 capitalize">{appointment.appointment_type}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Mascota</dt>
                <dd className="text-base text-gray-900">{appointment.pet_id ? `#${appointment.pet_id}` : 'No asignada'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Propietario</dt>
                <dd className="text-base text-gray-900">{appointment.owner_id ? `#${appointment.owner_id}` : 'No asignado'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Veterinario</dt>
                <dd className="text-base text-gray-900">{appointment.veterinarian_id ? `#${appointment.veterinarian_id}` : 'No asignado'}</dd>
              </div>
            </dl>

            {appointment.reason && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <dt className="text-sm font-medium text-gray-500 mb-1">Motivo</dt>
                <dd className="text-base text-gray-900">{appointment.reason}</dd>
              </div>
            )}

            {appointment.notes && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <dt className="text-sm font-medium text-gray-500 mb-1">Notas</dt>
                <dd className="text-base text-gray-900 whitespace-pre-wrap">{appointment.notes}</dd>
              </div>
            )}
          </div>

          {/* Acciones según estado */}
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Acciones</h2>
            <div className="flex flex-wrap gap-3">
              {appointment.status === 'pending' && (
                <>
                  <button
                    onClick={() => handleStatusTransition('approved')}
                    disabled={confirmingStatus === 'approved'}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    Aprobar
                  </button>
                  <button
                    onClick={() => handleStatusTransition('cancelled')}
                    disabled={confirmingStatus === 'cancelled'}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </>
              )}
              {appointment.status === 'approved' && (
                <>
                  <button
                    onClick={() => handleStatusTransition('confirmed')}
                    disabled={confirmingStatus === 'confirmed'}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Confirmar
                  </button>
                  <button
                    onClick={() => handleStatusTransition('cancelled')}
                    disabled={confirmingStatus === 'cancelled'}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                </>
              )}
              {appointment.status === 'confirmed' && (
                <>
                  <button
                    onClick={() => handleStatusTransition('completed')}
                    disabled={confirmingStatus === 'completed'}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    Completar
                  </button>
                  <button
                    onClick={() => handleStatusTransition('no_show')}
                    disabled={confirmingStatus === 'no_show'}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
                  >
                    No se presentó
                  </button>
                  <button
                    onClick={() => handleStatusTransition('rescheduled')}
                    disabled={confirmingStatus === 'rescheduled'}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
                  >
                    Reprogramar
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Calificar cita */}
          {appointment.status === 'completed' && (
            <div className="mb-6">
              <RatingForm
                appointmentId={appointmentId}
                existingReview={null}
                onCreated={() => undefined}
              />
            </div>
          )}
        </>
      )}

      {/* Footer */}
      <button onClick={onBack} className="text-indigo-600 hover:text-indigo-800 font-medium">
        ← Volver a la agenda
      </button>
    </div>
  );
}
