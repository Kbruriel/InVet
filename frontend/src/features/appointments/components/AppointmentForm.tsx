'use client';

/**
 * AppointmentForm — Formulario de solicitud de nueva cita desde perfil propietario (FE-008).
 */

'use client';

import React, { useState } from 'react';
import { createAppointment } from '../api';
import type { AppointmentType } from '../types';
import { Button } from '@/shared/ui/components/Button';
import { Input } from '@/shared/ui/components/Input';
import { LoadingSpinner } from '@/shared/ui/components/Loading';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';

interface Pet {
  id: number;
  name: string;
  species: string;
}

interface AppointmentFormProps {
  ownerId: number;
  pets: Pet[];
  onSuccess: (appointmentId: number) => void;
  onError: (message: string) => void;
}

const APPOINTMENT_TYPES: { value: AppointmentType; label: string }[] = [
  { value: 'consultation', label: 'Consulta general' },
  { value: 'vaccination', label: 'Vacunación' },
  { value: 'surgery', label: 'Cirugía' },
  { value: 'follow_up', label: 'Control' },
  { value: 'emergency', label: 'Emergencia' },
  { value: 'other', label: 'Otro' },
];

export function AppointmentForm({ ownerId, pets, onSuccess, onError }: AppointmentFormProps) {
  const [formData, setFormData] = useState({
    pet_id: '' as string | number,
    veterinarian_id: '' as string | number | null,
    appointment_type: 'consultation' as AppointmentType,
    scheduled_start: '',
    scheduled_end: '',
    reason: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field: string, value: string | number | null) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.pet_id || formData.pet_id === '') {
      newErrors.pet_id = 'Selecciona una mascota';
    }

    if (!formData.scheduled_start) {
      newErrors.scheduled_start = 'Fecha y hora de inicio requerida';
    } else if (new Date(formData.scheduled_start) <= new Date()) {
      newErrors.scheduled_start = 'La fecha debe estar en el futuro';
    }

    if (!formData.scheduled_end) {
      newErrors.scheduled_end = 'Fecha y hora de fin requerida';
    } else if (formData.scheduled_start && formData.scheduled_end) {
      const diffMs = new Date(formData.scheduled_end).getTime() - new Date(formData.scheduled_start).getTime();
      if (diffMs < 15 * 60 * 1000 || diffMs > 120 * 60 * 1000) {
        newErrors.scheduled_end = 'La duración debe ser entre 15 y 120 minutos';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setSubmitting(true);
    setLoading(true);

    try {
      const data = await createAppointment({
        owner_id: ownerId,
        pet_id: formData.pet_id ? Number(formData.pet_id) : null,
        veterinarian_id: formData.veterinarian_id ? Number(formData.veterinarian_id) : null,
        appointment_type: formData.appointment_type,
        scheduled_start: formData.scheduled_start,
        scheduled_end: formData.scheduled_end,
        reason: formData.reason || undefined,
      });

      onSuccess(data.id);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al crear la cita';
      onError(message);
    } finally {
      setSubmitting(false);
      setLoading(false);
    }
  };

  if (loading && pets.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (pets.length === 0 && !loading) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <ErrorBanner title="Sin mascotas registradas" message="Primero debes registrar una mascota en tu perfil para poder solicitar una cita.">
          <a href="/portal/owner/pets/new" className="text-indigo-600 hover:text-indigo-800 font-medium">
            Registrar mascota
          </a>
        </ErrorBanner>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Solicitar nueva cita</h1>

      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        {/* Mascota */}
        <div>
          <label htmlFor="pet_id" className="block text-sm font-medium text-gray-700 mb-1">
            Mascota *
          </label>
          <select
            id="pet_id"
            value={formData.pet_id}
            onChange={(e) => handleChange('pet_id', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg ${errors.pet_id ? 'border-red-500' : 'border-gray-300'} focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`}
            disabled={submitting}
            aria-invalid={!!errors.pet_id}
            aria-describedby={errors.pet_id ? 'pet_id-error' : undefined}
          >
            <option value="">Selecciona una mascota</option>
            {pets.map((pet) => (
              <option key={pet.id} value={pet.id}>
                {pet.name} ({pet.species})
              </option>
            ))}
          </select>
          {errors.pet_id && (
            <p id="pet_id-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.pet_id}
            </p>
          )}
        </div>

        {/* Tipo de cita */}
        <div>
          <label htmlFor="appointment_type" className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de cita *
          </label>
          <select
            id="appointment_type"
            value={formData.appointment_type}
            onChange={(e) => handleChange('appointment_type', e.target.value as AppointmentType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            disabled={submitting}
          >
            {APPOINTMENT_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Veterinario */}
        <div>
          <label htmlFor="veterinarian_id" className="block text-sm font-medium text-gray-700 mb-1">
            Veterinario (opcional)
          </label>
          <Input
            id="veterinarian_id"
            type="number"
            placeholder="ID del veterinario"
            value={formData.veterinarian_id || ''}
            onChange={(value) => handleChange('veterinarian_id', value || null)}
            disabled={submitting}
          />
        </div>

        {/* Fecha y hora */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="scheduled_start" className="block text-sm font-medium text-gray-700 mb-1">
              Fecha y hora de inicio *
            </label>
            <Input
              id="scheduled_start"
              type="datetime-local"
              value={formData.scheduled_start}
              onChange={(value) => handleChange('scheduled_start', value)}
              disabled={submitting}
              min={new Date().toISOString().slice(0, 16)}
              aria-invalid={!!errors.scheduled_start}
            />
            {errors.scheduled_start && (
              <p className="mt-1 text-sm text-red-600" role="alert">{errors.scheduled_start}</p>
            )}
          </div>
          <div>
            <label htmlFor="scheduled_end" className="block text-sm font-medium text-gray-700 mb-1">
              Fecha y hora de fin *
            </label>
            <Input
              id="scheduled_end"
              type="datetime-local"
              value={formData.scheduled_end}
              onChange={(value) => handleChange('scheduled_end', value)}
              disabled={submitting}
              min={new Date().toISOString().slice(0, 16)}
              aria-invalid={!!errors.scheduled_end}
            />
            {errors.scheduled_end && (
              <p className="mt-1 text-sm text-red-600" role="alert">{errors.scheduled_end}</p>
            )}
          </div>
        </div>

        {/* Motivo */}
        <div>
          <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-1">
            Motivo (opcional, máximo 500 caracteres)
          </label>
          <textarea
            id="reason"
            rows={3}
            maxLength={500}
            value={formData.reason}
            onChange={(e) => handleChange('reason', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
            placeholder="Describe brevemente el motivo de la cita..."
            disabled={submitting}
          />
        </div>

        {/* Boton */}
        <Button
          type="submit"
          variant="primary"
          isLoading={submitting}
          isDisabled={submitting}
          className="w-full"
        >
          {submitting ? 'Enviando...' : 'Solicitar cita'}
        </Button>
      </form>
    </div>
  );
}
