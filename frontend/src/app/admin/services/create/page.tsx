/** Pagina de creacion de servicio (FE-006) */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { ServiceForm } from '@/features/slice-006/components/service-form';
import { useServices } from '@/features/slice-006/hooks/use-services';
import { RequireAuth } from '@/shared/auth/RequireAuth';
import type { ServiceCreateDTO } from '@/shared/api/slice-006';

function CreateServicePageContent() {
  const router = useRouter();
  const { create, submitting } = useServices();
  const [success, setSuccess] = useState(false);

  const handleSuccess = async () => {
    setSuccess(true);
    await new Promise((r) => setTimeout(r, 300));
    router.push('/admin/services');
  };

  return (
    <AdminLayout title="Crear servicio">
      {success ? (
        <section className="rounded-xl bg-green-50 p-8 text-center" role="status">
          <p className="text-lg font-semibold text-green-700">Servicio creado exitosamente.</p>
          <button
            type="button"
            onClick={() => router.push('/admin/services')}
            className="mt-4 inline-flex items-center justify-center rounded-full bg-teal px-6 py-2.5 text-sm font-semibold text-white hover:bg-teal-dark"
          >
            Ver listados
          </button>
        </section>
      ) : (
        <ServiceForm
          onSubmit={(p) => create(p as ServiceCreateDTO)}
          onCancel={() => router.push('/admin/services')}
          submitting={submitting}
          onSuccess={handleSuccess}
        />
      )}
    </AdminLayout>
  );
}

export default function CreateServicePage() {
  return (
    <RequireAuth>
      <CreateServicePageContent />
    </RequireAuth>
  );
}
