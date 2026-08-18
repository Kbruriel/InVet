'use client';

/**
 * AppointmentAgenda — Agenda del propietario con tabs por estado (FE-008).
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { listMyAppointments } from '../api';
import type { Appointment } from '../types';
import { StatusBadge } from './StatusBadge';
import { LoadingSpinner } from '@/shared/ui/components/Loading';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';
import { EmptyState } from '@/shared/ui/components/EmptyState';

interface OwnerAgendaProps {
  ownerId: number;
  onAppointmentClick?: (id: number) => void;
}

const STATUS_TABS: { value: string | 'all'; label: string }[] = [
  { value: 'all', label: 'Todas' },
  { value: 'pending', label: 'Pendientes' },
  { value: 'approved', label: 'Aprobadas' },
  { value: 'confirmed', label: 'Activas' },
  { value: 'completed', label: 'Completadas' },
  { value: 'cancelled', label: 'Canceladas' },
];

export function OwnerAgenda({ ownerId, onAppointmentClick }: OwnerAgendaProps) {
  const router = useRouter();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('all');

  useEffect(() => {
    let cancelled = false;

    async function fetchAppointments() {
      setLoading(true);
      setError(null);

      try {
        const data = await listMyAppointments({ page: 1, page_size: 50 });
        if (!cancelled) {
          setAppointments(data.items || []);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Error al cargar citas');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAppointments();
    return () => { cancelled = true; };
  }, [ownerId]);

  const filteredAppointments = activeTab === 'all'
    ? appointments
    : appointments.filter((apt) => apt.status === activeTab);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mi agenda de citas</h1>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-200 overflow-x-auto" role="tablist">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            role="tab"
            aria-selected={activeTab === tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`px-4 py-2 text-sm font-medium whitespace-nowrap ${
              activeTab === tab.value
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {error && (
        <ErrorBanner
          message={error}
          onRetry={() => window.location.reload()}
          actionLabel="Reintentar"
        />
      )}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner />
        </div>
      )}

      {/* Empty state */}
      {!loading && filteredAppointments.length === 0 ? (
        <EmptyState
          title={activeTab === 'all' ? 'No tienes citas registradas' : `No hay citas ${STATUS_TABS.find((t) => t.value === activeTab)?.label.toLowerCase()}`}
          description="Puedes solicitar una nueva cita desde tu perfil."
          actionLabel="Solicitar primera cita"
          onAction={() => router.push('/portal/owner/appointments/new')}
        />
      ) : (
        /* Lista de citas */
        <div className="space-y-4">
          {filteredAppointments.map((apt) => (
            <div
              key={apt.id}
              onClick={() => onAppointmentClick?.(apt.id)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              role="button"
              tabIndex={0}
              aria-label={`Cita ${formatDate(apt.scheduled_start)}`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatDate(apt.scheduled_start)}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Tipo: {apt.appointment_type}
                  </p>
                  {apt.reason && (
                    <p className="text-sm text-gray-500 mt-1 italic">{apt.reason}</p>
                  )}
                </div>
                <StatusBadge status={apt.status} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
