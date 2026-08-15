/**
 * Página principal del portal de propietario
 * Ruta: /portal/owner
 */

'use client';

import { OwnerPortalLayout } from '@/features/owners/layout/owner-portal-layout';
import { OwnerProfileForm } from '@/features/owners/components/owner-profile-form';
import { PetList } from '@/features/owners/components/pet-list';
import { useState } from 'react';

export default function OwnerPortalPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'pets'>('profile');
  const [successMessage, setSuccessMessage] = useState('');

  const handleProfileSuccess = () => {
    setSuccessMessage('Perfil guardado exitosamente');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handlePetAdded = () => {
    setSuccessMessage('Mascota registrada exitosamente');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  return (
    <OwnerPortalLayout>
      {successMessage && (
        <div className="mb-6 rounded-[24px] border border-mint bg-mint/40 px-5 py-4 text-sm font-medium text-teal-dark">
          {successMessage}
        </div>
      )}

      <section className="mb-6 rounded-[32px] bg-white p-6 shadow-sm ring-1 ring-sandy-200">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">Resumen</p>
        <h2 className="mt-2 text-3xl font-semibold text-slate-900">Administra tu perfil y tus mascotas</h2>
        <p className="mt-3 max-w-2xl text-sm text-slate-600">
          Mantén tus datos de contacto actualizados, registra nuevas mascotas y consulta su historial básico desde un solo lugar.
        </p>
      </section>

      <div className="mb-6 rounded-[32px] border border-sandy-200 bg-white p-3 shadow-sm">
        <nav className="flex flex-wrap gap-2" aria-label="Secciones del portal propietario">
          <button
            type="button"
            onClick={() => setActiveTab('profile')}
            className={`rounded-full px-5 py-3 text-sm font-semibold transition-colors ${
              activeTab === 'profile'
                ? 'bg-teal text-white'
                : 'text-slate-500 hover:bg-sandy-100 hover:text-slate-800'
            }`}
          >
            Mi Perfil
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('pets')}
            className={`rounded-full px-5 py-3 text-sm font-semibold transition-colors ${
              activeTab === 'pets'
                ? 'bg-teal text-white'
                : 'text-slate-500 hover:bg-sandy-100 hover:text-slate-800'
            }`}
          >
            Mis Mascotas
          </button>
        </nav>
      </div>

      {activeTab === 'profile' && (
        <div className="rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Perfil</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">Información personal</h2>
          </div>
          <OwnerProfileForm onSuccess={handleProfileSuccess} />
        </div>
      )}

      {activeTab === 'pets' && (
        <div className="rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
          <PetList onPetAdded={handlePetAdded} />
        </div>
      )}
    </OwnerPortalLayout>
  );
}
