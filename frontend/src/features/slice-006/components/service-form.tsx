'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/shared/ui/components/Button';
import { Input } from '@/shared/ui/components/Input';
import type { ServiceDTO, ServiceCreateDTO, ServiceUpdateDTO, ApiError } from '@/shared/api/slice-006';

interface ServiceFormProps {
  initialData?: ServiceDTO;
  onSubmit: (payload: ServiceCreateDTO | ServiceUpdateDTO) => Promise<ServiceDTO>;
  onCancel: () => void;
  submitting: boolean;
  onSuccess?: () => void;
}

export function ServiceForm({ initialData, onSubmit, onCancel, submitting, onSuccess }: ServiceFormProps) {
  const [name, setName] = useState(initialData?.name ?? '');
  const [description, setDescription] = useState(initialData?.description ?? '');
  const [price, setPrice] = useState(String(initialData?.price ?? ''));
  const [durationMinutes, setDurationMinutes] = useState(String(initialData?.duration_minutes ?? ''));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setDescription(initialData.description ?? '');
      setPrice(String(initialData.price));
      setDurationMinutes(String(initialData.duration_minutes));
    }
  }, [initialData]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!name.trim()) newErrors.name = 'El nombre es obligatorio.';
    const parsedPrice = parseFloat(price);
    if (isNaN(parsedPrice) || parsedPrice <= 0) newErrors.price = 'El precio debe ser un valor positivo.';
    const parsedDuration = parseInt(durationMinutes, 10);
    if (isNaN(parsedDuration) || parsedDuration <= 0) newErrors.duration_minutes = 'La duración debe ser positiva.';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setApiError(null);

    const basePayload = {
      name: name.trim(),
      description: description.trim() || undefined,
      price: parseFloat(price),
      duration_minutes: parseInt(durationMinutes, 10),
    };

    const payload: ServiceCreateDTO | ServiceUpdateDTO = initialData
      ? basePayload as ServiceUpdateDTO
      // MNR-006-001: clinic_id hardcoded to 1 — known limitation.
      // TODO: Replace with dynamic clinic context from auth session or route params.
      : { ...basePayload, clinic_id: 1 } as ServiceCreateDTO;

    try {
      await onSubmit(payload);
      if (onSuccess) onSuccess();
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr.status === 422 && typeof apiErr.detail === 'object' && apiErr.detail !== null) {
        const detailErrors = apiErr.detail as Record<string, string>;
        setErrors(detailErrors);
      } else if (apiErr.status === 409) {
        setApiError('Ya existe un servicio con este nombre en la clínica.');
      } else {
        setApiError(apiErr.detail || 'Error al guardar el servicio.');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {apiError && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">{apiError}</div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Input
          label="Nombre del servicio"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          required
          autoComplete="off"
        />
        <Input
          label="Precio"
          type="number"
          step="0.01"
          min="0.01"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          error={errors.price}
          required
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Input
          label="Duración (minutos)"
          type="number"
          min="1"
          value={durationMinutes}
          onChange={(e) => setDurationMinutes(e.target.value)}
          error={errors.duration_minutes}
          required
        />
        <div className="w-full">
          <label htmlFor="service-description" className="mb-1 block text-sm font-medium text-slate-700">
            Descripción
          </label>
          <textarea
            id="service-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full rounded-lg border border-sandy-300 bg-white px-4 py-3 text-sm transition-colors focus:border-teal focus:outline-none focus:ring-2 focus:ring-teal"
          />
        </div>
      </div>

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? 'Guardando...' : initialData ? 'Guardar cambios' : 'Crear servicio'}
        </Button>
      </div>
    </form>
  );
}
