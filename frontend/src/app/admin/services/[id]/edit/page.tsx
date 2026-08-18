/** Pagina de edicion de servicio (FE-006) */

'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { ServiceForm } from '@/features/slice-006/components/service-form';
import { useServices } from '@/features/slice-006/hooks/use-services';
import { RequireAuth } from '@/shared/auth/RequireAuth';
import type { ServiceUpdateDTO } from '@/shared/api/slice-006';

interface PageProps {
  params: Promise<{ id: string }>;
}

function EditServicePageContent({ params }: PageProps) {
  const router = useRouter();
  const { id } = use(params);
  const { fetchOne, update, submitting, loading, error } = useServices();
  const [service, setService] = useState<Awaited<ReturnType<typeof fetchOne>> | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchOne(parseInt(id, 10));
        setService(data);
      } catch (err) {
        const apiErr = err as { status: number; detail: string };
        if (apiErr.status === 404) {
          router.push('/admin/services?error=servicio_no_encontrado');
        } else {
          router.push('/admin/services?error=error_carga');
        }
      }
    };
    load();
  }, [id, fetchOne, router]);

  if (loading || !service) {
    return (
      <AdminLayout title="Editar servicio">
        <div className="py-16 text-center" role="status">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-teal/30 border-t-teal" />
          <p className="mt-4 text-sm text-slate-500">Cargando servicio...</p>
        </div>
      </AdminLayout>
    );
  }

  if (error?.status === 403) {
    return (
      <AdminLayout title="Editar servicio">
        <section className="py-16" role="alert">
          <div className="mx-auto max-w-xl rounded-xl bg-red-50 p-8 text-center">
            <p className="text-lg font-semibold text-red-700">No tienes permiso para editar este servicio.</p>
          </div>
        </section>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Editar servicio">
      <ServiceForm
        initialData={service}
        onSubmit={(payload) => update(service.id, payload as ServiceUpdateDTO)}
        onCancel={() => router.push(`/admin/services/${service.id}`)}
        submitting={submitting}
      />
    </AdminLayout>
  );
}

export default function EditServicePage({ params }: PageProps) {
  return (
    <RequireAuth>
      <EditServicePageContent params={params} />
    </RequireAuth>
  );
}
