/** Pagina de listado de usuarios internos (FE-006) */

'use client';

import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { InternalUserList } from '@/features/slice-006/components/internal-user-list';
import { RequireAuth } from '@/shared/auth/RequireAuth';

function InternalUsersPageContent() {
  return (
    <AdminLayout title="Usuarios internos">
      <InternalUserList />
    </AdminLayout>
  );
}

export default function InternalUsersPage() {
  return (
    <RequireAuth>
      <InternalUsersPageContent />
    </RequireAuth>
  );
}
