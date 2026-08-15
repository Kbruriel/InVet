/**
 * Formulario de perfil del propietario
 */

'use client';

import { useState, useEffect } from 'react';
import { useOwnerProfile } from '../hooks/use-owner-profile';
import { Button, ErrorBanner, Input, LoadingSpinner } from '@/shared/ui/components';

interface OwnerProfileFormProps {
  onSuccess?: () => void;
}

export function OwnerProfileForm({ onSuccess }: OwnerProfileFormProps) {
  const { owner, loading, error, fetchOwner, updateProfile } = useOwnerProfile();
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
  });

  useEffect(() => {
    fetchOwner();
  }, [fetchOwner]);

  useEffect(() => {
    if (owner) {
      setFormData({
        nombre: owner.nombre || '',
        email: owner.email || '',
        telefono: owner.telefono || '',
        direccion: owner.direccion || '',
      });
    }
  }, [owner]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setValidationError(null);
  };

  const validate = (): boolean => {
    if (!formData.nombre.trim()) {
      setValidationError('El nombre completo es obligatorio.');
      return false;
    }

    if (!formData.email.trim()) {
      setValidationError('El correo electrónico es obligatorio.');
      return false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(formData.email)) {
      setValidationError('Ingresa un correo electrónico válido.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      return;
    }

    setSubmitting(true);
    try {
      await updateProfile({
        nombre: formData.nombre.trim(),
        email: formData.email.trim(),
        telefono: formData.telefono.trim(),
        direccion: formData.direccion.trim(),
      });
      onSuccess?.();
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !owner) {
    return <LoadingSpinner label="Cargando perfil del propietario" />;
  }

  if (error && !owner) {
    return <ErrorBanner message={error} onRetry={fetchOwner} />;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <Input
          id="nombre"
          name="nombre"
          label="Nombre completo *"
          value={formData.nombre}
          onChange={handleChange}
          placeholder="Juan Pérez"
          required
        />
        <Input
          id="email"
          name="email"
          type="email"
          label="Correo electrónico *"
          value={formData.email}
          onChange={handleChange}
          placeholder="juan@ejemplo.com"
          required
        />
        <Input
          id="telefono"
          name="telefono"
          type="tel"
          label="Teléfono"
          value={formData.telefono}
          onChange={handleChange}
          placeholder="809-555-0100"
        />
        <Input
          id="direccion"
          name="direccion"
          label="Dirección"
          value={formData.direccion}
          onChange={handleChange}
          placeholder="Calle 123, Ciudad"
        />
      </div>

      {validationError ? <ErrorBanner message={validationError} /> : null}
      {error ? <ErrorBanner message={error} /> : null}

      <div className="flex justify-end">
        <Button type="submit" disabled={submitting || !owner} className="min-w-44">
          {submitting ? 'Guardando...' : 'Guardar perfil'}
        </Button>
      </div>
    </form>
  );
}
