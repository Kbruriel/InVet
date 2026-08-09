'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/shared/ui/components/Button';
import { Input } from '@/shared/ui/components/Input';
import type { VeterinarianDTO, VeterinarianCreateDTO, VeterinarianUpdateDTO, ApiError } from '@/shared/api/slice-006';

interface VeterinarianFormProps {
  initialData?: VeterinarianDTO;
  onSubmit: (payload: VeterinarianCreateDTO | VeterinarianUpdateDTO) => Promise<VeterinarianDTO>;
  onCancel: () => void;
  submitting: boolean;
  onSuccess?: () => void;
}

export function VeterinarianForm({ initialData, onSubmit, onCancel, submitting, onSuccess }: VeterinarianFormProps) {
  const [nombreCompleto, setNombreCompleto] = useState(initialData?.nombre_completo ?? '');
  const [licenciaProfesional, setLicenciaProfesional] = useState(initialData?.licencia_profesional ?? '');
  const [especialidad, setEspecialidad] = useState(initialData?.especialidad ?? '');
  const [telefono, setTelefono] = useState(initialData?.telefono ?? '');
  const [email, setEmail] = useState(initialData?.email ?? '');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setNombreCompleto(initialData.nombre_completo);
      setLicenciaProfesional(initialData.licencia_profesional);
      setEspecialidad(initialData.especialidad);
      setTelefono(initialData.telefono ?? '');
      setEmail(initialData.email ?? '');
    }
  }, [initialData]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!nombreCompleto.trim()) newErrors.nombre_completo = 'El nombre completo es obligatorio.';
    if (!licenciaProfesional.trim()) newErrors.licencia_profesional = 'La licencia profesional es obligatoria.';
    if (!especialidad.trim()) newErrors.especialidad = 'La especialidad es obligatoria.';
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Email inválido.';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setApiError(null);

    const basePayload = {
      nombre_completo: nombreCompleto.trim(),
      licencia_profesional: licenciaProfesional.trim(),
      especialidad: especialidad.trim(),
      telefono: telefono.trim() || undefined,
      email: email.trim() || undefined,
    };

    const payload: VeterinarianCreateDTO | VeterinarianUpdateDTO = initialData
      ? basePayload as VeterinarianUpdateDTO
      : { ...basePayload, clinic_id: 1 } as VeterinarianCreateDTO;

    try {
      await onSubmit(payload);
      if (onSuccess) onSuccess();
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr.status === 422 && typeof apiErr.detail === 'object' && apiErr.detail !== null) {
        const detailErrors = apiErr.detail as Record<string, string>;
        setErrors(detailErrors);
      } else if (apiErr.status === 409) {
        setApiError('Ya existe un veterinario con esta licencia en la clínica.');
      } else {
        setApiError(apiErr.detail || 'Error al guardar el veterinario.');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {apiError && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">{apiError}</div>
      )}

      <Input
        label="Nombre completo"
        value={nombreCompleto}
        onChange={(e) => setNombreCompleto(e.target.value)}
        error={errors.nombre_completo}
        required
        autoComplete="name"
      />

      <Input
        label="Licencia profesional"
        value={licenciaProfesional}
        onChange={(e) => setLicenciaProfesional(e.target.value)}
        error={errors.licencia_profesional}
        required
        autoComplete="off"
      />

      <Input
        label="Especialidad"
        value={especialidad}
        onChange={(e) => setEspecialidad(e.target.value)}
        error={errors.especialidad}
        required
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Input
          label="Teléfono"
          type="tel"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
        />
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />
      </div>

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>Cancelar</Button>
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? 'Guardando...' : initialData ? 'Guardar cambios' : 'Crear veterinario'}
        </Button>
      </div>
    </form>
  );
}
