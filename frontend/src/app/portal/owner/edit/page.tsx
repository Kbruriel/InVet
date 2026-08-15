/**
 * Página de edición de perfil
 * Ruta: /portal/owner/edit
 */

'use client';

import { OwnerPortalLayout } from '@/features/owners/layout/owner-portal-layout';
import { OwnerProfileForm } from '@/features/owners/components/owner-profile-form';
import { useState } from 'react';

export default function EditOwnerProfilePage() {
  const [successMessage, setSuccessMessage] = useState('');

  const handleSuccess = () => {
    setSuccessMessage('Perfil actualizado exitosamente');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  return (
    <OwnerPortalLayout>
      {successMessage && (
        <div className="mb-6 rounded-[24px] border border-mint bg-mint/40 px-5 py-4 text-sm font-medium text-teal-dark">
          {successMessage}
        </div>
      )}

      <div className="max-w-3xl rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">Perfil</p>
        <h2 className="mb-6 mt-2 text-2xl font-semibold text-slate-900">Editar perfil</h2>
        <OwnerProfileForm onSuccess={handleSuccess} />
      </div>
    </OwnerPortalLayout>
  );
}
