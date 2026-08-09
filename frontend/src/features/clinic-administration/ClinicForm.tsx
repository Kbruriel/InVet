'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/shared/ui/components/Button';
import { Input } from '@/shared/ui/components/Input';
import type { ClinicRead, ClinicCreatePayload, ClinicUpdatePayload } from '@/shared/api/clinic-admin-client';

interface ClinicFormProps {
  initialData?: ClinicRead;
  onSubmit: (payload: ClinicCreatePayload | ClinicUpdatePayload) => Promise<void>;
  onCancel: () => void;
  submitting: boolean;
}

export function ClinicForm({ initialData, onSubmit, onCancel, submitting }: ClinicFormProps) {
  const [name, setName] = useState(initialData?.name ?? '');
  const [description, setDescription] = useState(initialData?.description ?? '');
  const [address, setAddress] = useState(initialData?.address ?? '');
  const [city, setCity] = useState(initialData?.city ?? '');
  const [state, setState] = useState(initialData?.state ?? '');
  const [country, setCountry] = useState(initialData?.country ?? 'Mexico');
  const [postalCode, setPostalCode] = useState(initialData?.postal_code ?? '');
  const [phone, setPhone] = useState(initialData?.phone ?? '');
  const [email, setEmail] = useState(initialData?.email ?? '');
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setDescription(initialData.description ?? '');
      setAddress(initialData.address);
      setCity(initialData.city);
      setState(initialData.state);
      setCountry(initialData.country);
      setPostalCode(initialData.postal_code);
      setPhone(initialData.phone ?? '');
      setEmail(initialData.email ?? '');
    }
  }, [initialData]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) newErrors.name = 'El nombre es obligatorio.';
    if (!address.trim()) newErrors.address = 'La direccion es obligatoria.';
    if (!city.trim()) newErrors.city = 'La ciudad es obligatoria.';
    if (!state.trim()) newErrors.state = 'El estado es obligatorio.';
    if (!country.trim()) newErrors.country = 'El pais es obligatorio.';
    if (!postalCode.trim()) newErrors.postal_code = 'El codigo postal es obligatorio.';
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Email invalido.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = {
      name: name.trim(),
      description: description.trim() || undefined,
      address: address.trim(),
      city: city.trim(),
      state: state.trim(),
      country: country.trim(),
      postal_code: postalCode.trim(),
      phone: phone.trim() || undefined,
      email: email.trim() || undefined,
    };

    if (initialData) {
      await onSubmit(payload as ClinicUpdatePayload);
    } else {
      await onSubmit(payload as ClinicCreatePayload);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
      noValidate
    >
      <h2 className="text-lg font-semibold text-[#0a2540] mb-4">
        {initialData ? 'Editar Clinica' : 'Nueva Clinica'}
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Nombre */}
        <Input
          label="Nombre *"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          required
          placeholder="Nombre de la clinica"
        />

        {/* Email */}
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
          placeholder="contacto@clinica.com"
        />

        {/* Direccion */}
        <div className="sm:col-span-2">
          <Input
            label="Direccion *"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            error={errors.address}
            required
            placeholder="Calle y numero"
          />
        </div>

        {/* Ciudad */}
        <Input
          label="Ciudad *"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          error={errors.city}
          required
          placeholder="Ciudad"
        />

        {/* Estado */}
        <Input
          label="Estado *"
          value={state}
          onChange={(e) => setState(e.target.value)}
          error={errors.state}
          required
          placeholder="Estado/Provincia"
        />

        {/* Pais */}
        <Input
          label="Pais *"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          error={errors.country}
          required
          placeholder="Pais"
        />

        {/* Codigo Postal */}
        <Input
          label="Codigo Postal *"
          value={postalCode}
          onChange={(e) => setPostalCode(e.target.value)}
          error={errors.postal_code}
          required
          placeholder="12345"
        />

        {/* Telefono */}
        <Input
          label="Telefono"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="555-1234"
        />
      </div>

      {/* Descripcion */}
      <div className="mt-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Descripcion
        </label>
        <textarea
          id="description"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-[#006065] focus:ring-1 focus:ring-[#006065] bg-white"
          placeholder="Descripcion opcional de la clinica..."
        />
      </div>

      {/* Acciones */}
      <div className="flex justify-end gap-3 mt-6">
        <Button variant="secondary" type="button" onClick={onCancel} disabled={submitting}>
          Cancelar
        </Button>
        <Button variant="primary" type="submit" disabled={submitting}>
          {submitting ? 'Guardando...' : initialData ? 'Guardar Cambios' : 'Crear Clinica'}
        </Button>
      </div>
    </form>
  );
}
