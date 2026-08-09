'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/shared/ui/components/Button';
import { Input } from '@/shared/ui/components/Input';
import type { InternalUserDTO, InternalUserCreateDTO, InternalUserUpdateDTO, ApiError } from '@/shared/api/slice-006';

interface InternalUserFormProps {
  initialData?: InternalUserDTO;
  onSubmit: (payload: InternalUserCreateDTO | InternalUserUpdateDTO) => Promise<InternalUserDTO>;
  onCancel: () => void;
  submitting: boolean;
  onSuccess?: () => void;
}

const AVAILABLE_ROLES = ['admin', 'manager', 'receptionist', 'billing'];

export function InternalUserForm({ initialData, onSubmit, onCancel, submitting, onSuccess }: InternalUserFormProps) {
  const [userId, setUserId] = useState(String(initialData?.user_id ?? ''));
  const [nombre, setNombre] = useState(initialData?.nombre ?? '');
  const [rol, setRol] = useState(initialData?.rol ?? AVAILABLE_ROLES[0]);
  const [branchIds, setBranchIds] = useState(initialData?.branch_ids?.join(',') ?? '');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setUserId(String(initialData.user_id));
      setNombre(initialData.nombre);
      setRol(initialData.rol);
      setBranchIds(initialData.branch_ids.join(','));
    }
  }, [initialData]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!userId.trim()) newErrors.user_id = 'El user_id es obligatorio.';
    if (!nombre.trim()) newErrors.nombre = 'El nombre es obligatorio.';
    if (!rol) newErrors.rol = 'El rol es obligatorio.';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setApiError(null);

    const basePayload = {
      nombre: nombre.trim(),
      rol,
      branch_ids: branchIds.trim()
        ? branchIds.split(',').map((b) => parseInt(b.trim(), 10)).filter((n) => !isNaN(n))
        : undefined,
    };

    const payload: InternalUserCreateDTO | InternalUserUpdateDTO = initialData
      ? basePayload as InternalUserUpdateDTO
      : { ...basePayload, user_id: parseInt(userId.trim(), 10), clinic_id: 1 } as InternalUserCreateDTO;

    try {
      await onSubmit(payload);
      if (onSuccess) onSuccess();
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr.status === 422 && typeof apiErr.detail === 'object' && apiErr.detail !== null) {
        const detailErrors = apiErr.detail as Record<string, string>;
        setErrors(detailErrors);
      } else if (apiErr.status === 409) {
        setApiError('El user_id ya está asociado a un usuario interno.');
      } else {
        setApiError(apiErr.detail || 'Error al guardar el usuario interno.');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {apiError && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700" role="alert">{apiError}</div>
      )}

      {!initialData && (
        <Input
          label="user_id (referencia al usuario de autenticación)"
          type="number"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          error={errors.user_id}
          required
        />
      )}

      <Input
        label="Nombre"
        value={nombre}
        onChange={(e) => setNombre(e.target.value)}
        error={errors.nombre}
        required
      />

      <div className="w-full">
        <label htmlFor="rol" className="mb-1 block text-sm font-medium text-slate-700">
          Rol {rol && !errors.rol && <span className="text-teal">(actual: {rol})</span>}
        </label>
        <select
          id="rol"
          value={rol}
          onChange={(e) => setRol(e.target.value)}
          className={`w-full rounded-lg border px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-teal ${
            errors.rol ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
          }`}
        >
          <option value="">Seleccionar rol</option>
          {AVAILABLE_ROLES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        {errors.rol && (
          <p className="mt-1 text-xs text-red-600" role="alert">{errors.rol}</p>
        )}
      </div>

      <Input
        label="Sucursales (IDs separados por coma)"
        value={branchIds}
        onChange={(e) => setBranchIds(e.target.value)}
        placeholder="Ej: 1, 2, 3"
      />

      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>Cancelar</Button>
        <Button type="submit" variant="primary" disabled={submitting}>
          {submitting ? 'Guardando...' : initialData ? 'Guardar cambios' : 'Crear usuario interno'}
        </Button>
      </div>
    </form>
  );
}
