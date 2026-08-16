'use client';

/**
 * ClinicAgenda — Vista de agenda para clinica con filtros y acciones (FE-008).
 */

'use client';

import React, { useState, useEffect } from 'react';
import { listClinicAppointments, transitionStatus } from '../api';
import type { Appointment } from '../types';
import { StatusBadge } from './StatusBadge';
import { LoadingSpinner } from '@/shared/ui/components/Loading';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';

interface ClinicAgendaProps {
  clinicId: number;
  veterinarianId?: number;
  onAppointmentClick?: (id: number) => void;
  onStatusChange: (appointmentId: number, newStatus: string) => void;
}

const STATUS_FILTERS = [
  { value: 'all', label: 'Todas' },
  { value: 'pending', label: 'Pendientes' },
  { value: 'approved', label: 'Aprobadas' },
  { value: 'confirmed', label: 'Activas' },
];

const ACTIONS_PER_STATUS: Record<string, { action: string; label: string }[]> = {
  pending: [
    { action: 'approved', label: 'Aprobar' },
    { action: 'cancelled', label: 'Cancelar' },
  ],
  approved: [
    { action: 'confirmed', label: 'Confirmar' },
    { action: 'cancelled', label: 'Cancelar' },
  ],
  confirmed: [
    { action: 'completed', label: 'Completar' },
    { action: 'no_show', label: 'No se presentó' },
    { action: 'rescheduled', label: 'Reprogramar' },
  ],
};

export function ClinicAgenda({ clinicId, veterinarianId, onAppointmentClick, onStatusChange }: ClinicAgendaProps) {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  useEffect(() => {
    let cancelled = false;

    async function fetchAppointments() {
      setLoading(true);
      setError(null);

      try {
        const params: Record<string, string | number> = { page: 1, page_size: 100 };
        if (veterinarianId) params.veterinarian_id = veterinarianId;
        if (dateRange.start) params.date_from = dateRange.start;
        if (dateRange.end) params.date_to = dateRange.end;

        const data = await listClinicAppointments(clinicId, params);
        if (!cancelled) setAppointments(data.items || []);
      } catch (err: unknown) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Error al cargar citas de clinica');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAppointments();
    return () => { cancelled = true; };
  }, [clinicId, veterinarianId, dateRange]);

  const filteredAppointments = activeFilter === 'all'
    ? appointments
    : appointments.filter((apt) => apt.status === activeFilter);

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

  const handleStatusAction = async (appointmentId: number, action: string) => {
    if (!window.confirm(`¿Estás seguro de realizar esta acción?`)) return;

    try {
      await transitionStatus(appointmentId, { new_status: action as any });
      onStatusChange(appointmentId, action);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al cambiar el estado');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Agenda de la clínica</h1>

      {/* Filtros */}
      <div className="flex flex-wrap gap-4 mb-6">
        {/* Status tabs */}
        <div className="flex flex-wrap gap-2" role="tablist">
          {STATUS_FILTERS.map((filter) => (
            <button
              key={filter.value}
              role="tab"
              aria-selected={activeFilter === filter.value}
              onClick={() => setActiveFilter(filter.value)}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap ${
                activeFilter === filter.value
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Date range */}
        <div className="flex gap-2 ml-auto">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange((prev) => ({ ...prev, start: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            placeholder="Desde"
          />
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange((prev) => ({ ...prev, end: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            placeholder="Hasta"
          />
        </div>
      </div>

      {error && (
        <ErrorBanner title="Error" message={error}>
          <button onClick={() => window.location.reload()} className="text-indigo-600 hover:text-indigo-800 font-medium">
            Reintentar
          </button>
        </ErrorBanner>
      )}

      {/* Lista de citas */}
      {filteredAppointments.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-500">No hay citas para los filtros seleccionados.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredAppointments.map((apt) => (
            <div
              key={apt.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 cursor-pointer" onClick={() => onAppointmentClick?.(apt.id)}>
                  <div className="flex items-center gap-3 mb-2">
                    <p className="text-lg font-semibold text-gray-900">{formatDate(apt.scheduled_start)}</p>
                    <StatusBadge status={apt.status} />
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
                    {apt.pet_id && <p className="text-gray-600"><span className="font-medium">Mascota:</span> #{apt.pet_id}</p>}
                    {apt.owner_id && <p className="text-gray-600"><span className="font-medium">Propietario:</span> #{apt.owner_id}</p>}
                    {apt.veterinarian_id && <p className="text-gray-600"><span className="font-medium">Veterinario:</span> #{apt.veterinarian_id}</p>}
                    <p className="text-gray-600"><span className="font-medium">Tipo:</span> {apt.appointment_type}</p>
                  </div>
                  {apt.reason && (
                    <p className="text-sm text-gray-500 mt-2 italic">{apt.reason}</p>
                  )}
                </div>

                {/* Acciones */}
                <div className="flex gap-2 ml-4">
                  {(ACTIONS_PER_STATUS[apt.status] || []).map((action) => (
                    <button
                      key={action.action}
                      onClick={() => handleStatusAction(apt.id, action.action)}
                      className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                        action.action === 'cancelled' || action.action === 'no_show'
                          ? 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100'
                          : 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100'
                      }`}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
