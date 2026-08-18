/** Pagina de creacion de usuario interno (FE-006) */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { InternalUserForm } from '@/features/slice-006/components/internal-user-form';
import { useInternalUsers } from '@/features/slice-006/hooks/use-internal-users';
import { RequireAuth } from '@/shared/auth/RequireAuth';
import type { InternalUserCreateDTO } from '@/shared/api/slice-006';

function CreateInternalUserPageContent() {
  const router = useRouter();
  const { create, submitting } = useInternalUsers();
  const [success, setSuccess] = useState(false);

  const handleSuccess = async () => {
    setSuccess(true);
    await new Promise((r) => setTimeout(r, 300));
    router.push('/admin/internal-users');
  };

  return (
    <AdminLayout title="Crear usuario interno">
      {success ? (
        <section className="rounded-xl bg-green-50 p-8 text-center" role="status">
          <p className="text-lg font-semibold text-green-700">Usuario interno creado exitosamente.</p>
          <button
            type="button"
            onClick={() => router.push('/admin/internal-users')}
            className="mt-4 inline-flex items-center justify-center rounded-full bg-teal px-6 py-2.5 text-sm font-semibold text-white hover:bg-teal-dark"
          >
            Ver listados
          </button>
        </section>
      ) : (
        <InternalUserForm
          onSubmit={(p) => create(p as InternalUserCreateDTO)}
          onCancel={() => router.push('/admin/internal-users')}
          submitting={submitting}
          onSuccess={handleSuccess}
        />
      )}
    </AdminLayout>
  );
}

export default function CreateInternalUserPage() {
  return (
    <RequireAuth>
      <CreateInternalUserPageContent />
    </RequireAuth>
  );
}
