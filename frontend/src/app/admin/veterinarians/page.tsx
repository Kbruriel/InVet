/** Pagina de listado de veterinarios (FE-006) */

import { redirect } from 'next/navigation';
import { AdminLayout } from '@/features/slice-006/components/admin-layout';
import { VeterinarianList } from '@/features/slice-006/components/veterinarian-list';

export default function VeterinariansPage() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) redirect('/login');

  return (
    <AdminLayout title="Veterinarios">
      <VeterinarianList />
    </AdminLayout>
  );
}
