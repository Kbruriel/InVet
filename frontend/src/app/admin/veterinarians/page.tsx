/** Pagina de listado de veterinarios (FE-006) */

'use client';

import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { VeterinarianList } from '@/features/slice-006/components/veterinarian-list';
import { RequireAuth } from '@/shared/auth/RequireAuth';

function VeterinariansPageContent() {
  return (
    <AdminLayout title="Veterinarios">
      <VeterinarianList />
    </AdminLayout>
  );
}

export default function VeterinariansPage() {
  return (
    <RequireAuth>
      <VeterinariansPageContent />
    </RequireAuth>
  );
}
