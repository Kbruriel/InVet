/**
 * Página de registro de nueva mascota
 * Ruta: /portal/owner/pets/new
 */

'use client';

import { OwnerPortalLayout } from '@/features/owners/layout/owner-portal-layout';
import { PetForm } from '@/features/owners/components/pet-form';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { usePets } from '@/features/owners/hooks/use-pets';

export default function NewPetPage() {
  const router = useRouter();
  const { addPet, error } = usePets();
  const [successMessage, setSuccessMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSuccess = async (data: {
    nombre: string;
    especie: string;
    raza: string;
    edad: number;
    peso?: number;
    fecha_nacimiento?: string;
  }): Promise<void> => {
    setSubmitting(true);
    try {
      await addPet(data);
      setSuccessMessage('Mascota registrada exitosamente');
      setTimeout(() => {
        router.push('/portal/owner');
      }, 1500);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <OwnerPortalLayout>
      {successMessage && (
        <div className="mb-6 rounded-[24px] border border-mint bg-mint/40 px-5 py-4 text-sm font-medium text-teal-dark">
          {successMessage}
        </div>
      )}

      <div className="max-w-3xl rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">Mascotas</p>
        <h2 className="mb-3 mt-2 text-2xl font-semibold text-slate-900">Registrar nueva mascota</h2>
        <p className="mb-6 text-sm text-slate-600">Completa la ficha básica para asociarla a tu perfil de propietario.</p>
        {error ? <p className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}
        <PetForm onSubmit={handleSuccess} onCancel={() => router.push('/portal/owner')} submitting={submitting} />
      </div>
    </OwnerPortalLayout>
  );
}
