/**
 * Página de detalle de mascota con historial básico
 * Ruta: /portal/owner/pets/[petId]
 */

'use client';

import { OwnerPortalLayout } from '@/features/owners/layout/owner-portal-layout';
import { PetDetail } from '@/features/owners/components/pet-detail';
import { useRouter, useParams } from 'next/navigation';

export default function PetDetailPage() {
  const router = useRouter();
  const params = useParams();
  const petId = params.petId as string;

  return (
    <OwnerPortalLayout>
      <PetDetail petId={Number(petId)} onBack={() => router.push('/portal/owner')} />
    </OwnerPortalLayout>
  );
}
