/**
 * Formulario de registro/edición de mascota
 */

'use client';

import { useState, useEffect } from 'react';
import { Button, Input } from '@/shared/ui/components';

interface PetFormProps {
  onSubmit: (data: PetFormData) => Promise<void>;
  onCancel: () => void;
  submitting?: boolean;
  initialData?: {
    nombre?: string;
    especie?: string;
    raza?: string;
    edad?: number;
    peso?: number;
    fecha_nacimiento?: string;
  };
}

interface PetFormData {
  nombre: string;
  especie: string;
  raza: string;
  edad: number;
  peso?: number;
  fecha_nacimiento?: string;
}

const ESPECIES = [
  { value: 'perro', label: 'Perro' },
  { value: 'gato', label: 'Gato' },
  { value: 'otro', label: 'Otro' },
];

export function PetForm({ onSubmit, onCancel, submitting = false, initialData }: PetFormProps) {
  const [formData, setFormData] = useState({
    nombre: initialData?.nombre || '',
    especie: initialData?.especie || 'perro',
    raza: initialData?.raza || '',
    edad: initialData?.edad?.toString() || '',
    peso: initialData?.peso?.toString() || '',
    fecha_nacimiento: initialData?.fecha_nacimiento || '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (initialData) {
      setFormData({
        nombre: initialData.nombre || '',
        especie: initialData.especie || 'perro',
        raza: initialData.raza || '',
        edad: initialData.edad?.toString() || '',
        peso: initialData.peso?.toString() || '',
        fecha_nacimiento: initialData.fecha_nacimiento || '',
      });
    }
  }, [initialData]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    if (!formData.especie) {
      newErrors.especie = 'La especie es requerida';
    }

    if (!formData.raza.trim()) {
      newErrors.raza = 'La raza es requerida';
    }

    if (!formData.edad || parseInt(formData.edad) < 0 || parseInt(formData.edad) > 50) {
      newErrors.edad = 'La edad debe estar entre 0 y 50 años';
    }

    if (formData.peso && (parseFloat(formData.peso) <= 0 || parseFloat(formData.peso) > 500)) {
      newErrors.peso = 'El peso debe estar entre 0 y 500 kg';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    await onSubmit({
      nombre: formData.nombre.trim(),
      especie: formData.especie,
      raza: formData.raza.trim(),
      edad: parseInt(formData.edad),
      peso: formData.peso ? parseFloat(formData.peso) : undefined,
      fecha_nacimiento: formData.fecha_nacimiento || undefined,
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-[28px] border border-sandy-300 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">
        {initialData ? 'Editar Mascota' : 'Registrar Nueva Mascota'}
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          type="text"
          id="nombre"
          name="nombre"
          label="Nombre *"
          value={formData.nombre}
          onChange={handleChange}
          required
          error={errors.nombre}
          placeholder="Firulais"
        />

        <div>
          <label htmlFor="especie" className="mb-1 block text-sm font-medium text-slate-700">
            Especie *
          </label>
          <select
            id="especie"
            name="especie"
            value={formData.especie}
            onChange={handleChange}
            required
            className={`w-full rounded-lg border px-4 py-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-teal ${
              errors.especie
                ? 'border-red-400 bg-red-50 focus:border-red-500'
                : 'border-sandy-300 bg-white focus:border-teal'
            }`}
          >
            {ESPECIES.map(esp => (
              <option key={esp.value} value={esp.value}>{esp.label}</option>
            ))}
          </select>
          {errors.especie && <p className="mt-1 text-xs text-red-600">{errors.especie}</p>}
        </div>

        <Input
          type="text"
          id="raza"
          name="raza"
          label="Raza *"
          value={formData.raza}
          onChange={handleChange}
          required
          error={errors.raza}
          placeholder="Labrador"
        />

        <Input
          type="number"
          id="edad"
          name="edad"
          label="Edad (años) *"
          value={formData.edad}
          onChange={handleChange}
          required
          min="0"
          max="50"
          error={errors.edad}
          placeholder="5"
        />

        <Input
          type="number"
          id="peso"
          name="peso"
          label="Peso (kg)"
          value={formData.peso}
          onChange={handleChange}
          min="0"
          max="500"
          step="0.1"
          error={errors.peso}
          placeholder="25.5"
        />

        <Input
          type="date"
          id="fecha_nacimiento"
          name="fecha_nacimiento"
          label="Fecha de nacimiento"
          value={formData.fecha_nacimiento}
          onChange={handleChange}
        />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          variant="outline"
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          disabled={submitting}
          className="min-w-40"
        >
          {submitting ? 'Guardando...' : (initialData ? 'Guardar Cambios' : 'Registrar')}
        </Button>
      </div>
    </form>
  );
}
