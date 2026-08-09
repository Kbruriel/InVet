/** Pagina de listado de servicios (FE-006) */

import { redirect } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { ServiceList } from '@/features/slice-006/components/service-list';

export default function ServicesPage() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) redirect('/login');

  return (
    <AdminLayout title="Servicios">
      <ServiceList />
    </AdminLayout>
  );
}
