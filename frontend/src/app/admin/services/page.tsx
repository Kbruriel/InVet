/** Pagina de listado de servicios (FE-006) */

'use client';

import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { ServiceList } from '@/features/slice-006/components/service-list';
import { RequireAuth } from '@/shared/auth/RequireAuth';

function ServicesPageContent() {
  return (
    <AdminLayout title="Servicios">
      <ServiceList />
    </AdminLayout>
  );
}

export default function ServicesPage() {
  return (
    <RequireAuth>
      <ServicesPageContent />
    </RequireAuth>
  );
}
