/** Pagina de edicion de veterinario (FE-006) */

'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { VeterinarianForm } from '@/features/slice-006/components/veterinarian-form';
import { useVeterinarians } from '@/features/slice-006/hooks/use-veterinarians';
import { RequireAuth } from '@/shared/auth/RequireAuth';
import type { VeterinarianUpdateDTO } from '@/shared/api/slice-006';

interface PageProps {
  params: Promise<{ id: string }>;
}

function EditVeterinarianPageContent({ params }: PageProps) {
  const router = useRouter();
  const { id } = use(params);
  const { fetchOne, update, submitting, loading, error } = useVeterinarians();
  const [veterinarian, setVeterinarian] = useState<Awaited<ReturnType<typeof fetchOne>> | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchOne(parseInt(id, 10));
        setVeterinarian(data);
      } catch (err) {
        const apiErr = err as { status: number; detail: string };
        if (apiErr.status === 404) {
          router.push('/admin/veterinarians?error=veterinario_no_encontrado');
        } else {
          router.push('/admin/veterinarians?error=error_carga');
        }
      }
    };
    load();
  }, [id, fetchOne, router]);

  if (loading || !veterinarian) {
    return (
      <AdminLayout title="Editar veterinario">
        <div className="py-16 text-center" role="status">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-teal/30 border-t-teal" />
          <p className="mt-4 text-sm text-slate-500">Cargando veterinario...</p>
        </div>
      </AdminLayout>
    );
  }

  if (error?.status === 403) {
    return (
      <AdminLayout title="Editar veterinario">
        <section className="py-16" role="alert">
          <div className="mx-auto max-w-xl rounded-xl bg-red-50 p-8 text-center">
            <p className="text-lg font-semibold text-red-700">No tienes permiso para editar este veterinario.</p>
          </div>
        </section>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Editar veterinario">
      <VeterinarianForm
        initialData={veterinarian}
        onSubmit={(payload) => update(veterinarian.id, payload as VeterinarianUpdateDTO)}
        onCancel={() => router.push(`/admin/veterinarians/${veterinarian.id}`)}
        submitting={submitting}
      />
    </AdminLayout>
  );
}

export default function EditVeterinarianPage({ params }: PageProps) {
  return (
    <RequireAuth>
      <EditVeterinarianPageContent params={params} />
    </RequireAuth>
  );
}
