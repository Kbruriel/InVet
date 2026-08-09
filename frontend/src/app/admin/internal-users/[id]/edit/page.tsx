/** Pagina de edicion de usuario interno (FE-006) */

'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { redirect } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { InternalUserForm } from '@/features/slice-006/components/internal-user-form';
import { useInternalUsers } from '@/features/slice-006/hooks/use-internal-users';
import type { InternalUserUpdateDTO } from '@/shared/api/slice-006';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function EditInternalUserPage({ params }: PageProps) {
  const router = useRouter();
  const { id } = use(params);
  const { fetchOne, update, submitting, loading, error } = useInternalUsers();
  const [user, setUser] = useState<Awaited<ReturnType<typeof fetchOne>> | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && !localStorage.getItem('access_token')) {
      redirect('/login');
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchOne(parseInt(id, 10));
        setUser(data);
      } catch (err) {
        const apiErr = err as { status: number; detail: string };
        if (apiErr.status === 404) {
          router.push('/admin/internal-users?error=usuario_no_encontrado');
        } else {
          router.push('/admin/internal-users?error=error_carga');
        }
      }
    };
    load();
  }, [id, fetchOne, router]);

  if (loading || !user) {
    return (
      <AdminLayout title="Editar usuario interno">
        <div className="py-16 text-center" role="status">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-teal/30 border-t-teal" />
          <p className="mt-4 text-sm text-slate-500">Cargando usuario...</p>
        </div>
      </AdminLayout>
    );
  }

  if (error?.status === 403) {
    return (
      <AdminLayout title="Editar usuario interno">
        <section className="py-16" role="alert">
          <div className="mx-auto max-w-xl rounded-xl bg-red-50 p-8 text-center">
            <p className="text-lg font-semibold text-red-700">No tienes permiso para editar este usuario.</p>
          </div>
        </section>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Editar usuario interno">
      <InternalUserForm
        initialData={user}
        onSubmit={(payload) => update(user.id, payload as InternalUserUpdateDTO)}
        onCancel={() => router.push(`/admin/internal-users/${user.id}`)}
        submitting={submitting}
      />
    </AdminLayout>
  );
}
