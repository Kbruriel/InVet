/** Pagina de creacion de veterinario (FE-006) */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { redirect } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { VeterinarianForm } from '@/features/slice-006/components/veterinarian-form';
import { useVeterinarians } from '@/features/slice-006/hooks/use-veterinarians';
import type { VeterinarianCreateDTO } from '@/shared/api/slice-006';

export default function CreateVeterinarianPage() {
  const router = useRouter();
  const { create, submitting } = useVeterinarians();
  const [success, setSuccess] = useState(false);

  if (typeof window !== 'undefined' && !localStorage.getItem('access_token')) {
    redirect('/login');
  }

  const handleSuccess = async () => {
    setSuccess(true);
    await new Promise((r) => setTimeout(r, 300));
    router.push('/admin/veterinarians');
  };

  return (
    <AdminLayout title="Crear veterinario">
      {success ? (
        <section className="rounded-xl bg-green-50 p-8 text-center" role="status">
          <p className="text-lg font-semibold text-green-700">Veterinario creado exitosamente.</p>
          <button
            type="button"
            onClick={() => router.push('/admin/veterinarians')}
            className="mt-4 inline-flex items-center justify-center rounded-full bg-teal px-6 py-2.5 text-sm font-semibold text-white hover:bg-teal-dark"
          >
            Ver listados
          </button>
        </section>
      ) : (
        <VeterinarianForm
          onSubmit={(p) => create(p as VeterinarianCreateDTO)}
          onCancel={() => router.push('/admin/veterinarians')}
          submitting={submitting}
          onSuccess={handleSuccess}
        />
      )}
    </AdminLayout>
  );
}
