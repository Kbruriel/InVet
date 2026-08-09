/** Pagina de listado de usuarios internos (FE-006) */

import { redirect } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { InternalUserList } from '@/features/slice-006/components/internal-user-list';

export default function InternalUsersPage() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) redirect('/login');

  return (
    <AdminLayout title="Usuarios internos">
      <InternalUserList />
    </AdminLayout>
  );
}
