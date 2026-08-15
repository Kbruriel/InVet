/**
 * Listado de mascotas
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePets } from '../hooks/use-pets';
import { PetForm } from './pet-form';
import { Button, EmptyState, ErrorBanner, LoadingSpinner } from '@/shared/ui/components';

interface PetListProps {
  onPetAdded?: () => void;
  onPetDeleted?: () => void;
}

export function PetList({ onPetAdded, onPetDeleted }: PetListProps) {
  const { pets, loading, error, pagination, fetchPets, addPet, removePet } = usePets();
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPets();
  }, [fetchPets]);

  const handleAddPet = async (data: {
    nombre: string;
    especie: string;
    raza: string;
    edad: number;
    peso?: number;
    fecha_nacimiento?: string;
  }) => {
    setSubmitting(true);
    try {
      await addPet(data);
      setShowForm(false);
      onPetAdded?.();
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeletePet = async (petId: number) => {
    if (!confirm('¿Estás seguro de que deseas eliminar esta mascota?')) {
      return;
    }
    try {
      await removePet(petId);
      onPetDeleted?.();
    } catch {
      return;
    }
  };

  if (loading && pets.length === 0) {
    return <LoadingSpinner label="Cargando mascotas" />;
  }

  if (error && pets.length === 0) {
    return <ErrorBanner message={error} onRetry={() => fetchPets()} />;
  }

  if (pets.length === 0) {
    return (
      <EmptyState
        title="No tienes mascotas registradas"
        description="Comienza agregando tu primera mascota para consultar su historial y mantener sus datos al día."
        actionLabel="Agregar mascota"
        onAction={() => setShowForm(true)}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Mis mascotas ({pets.length})</h2>
          <p className="text-sm text-slate-500">Administra su información básica y consulta su historial.</p>
        </div>
        <Button
          type="button"
          onClick={() => setShowForm(true)}
        >
          Agregar mascota
        </Button>
      </div>

      {showForm && (
        <div>
          <PetForm onSubmit={handleAddPet} onCancel={() => setShowForm(false)} submitting={submitting} />
        </div>
      )}

      {error ? <ErrorBanner message={error} /> : null}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {pets.map((pet) => (
          <article key={pet.id} className="rounded-[28px] border border-sandy-300 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">{pet.nombre}</h3>
                <p className="text-sm capitalize text-slate-600">{pet.especie} · {pet.raza}</p>
                <p className="mt-2 text-sm text-slate-500">Edad: {pet.edad} años</p>
                {pet.peso ? <p className="text-sm text-slate-500">Peso: {pet.peso} kg</p> : null}
              </div>
              <button
                type="button"
                onClick={() => handleDeletePet(pet.id)}
                className="rounded-full p-2 text-red-600 transition-colors hover:bg-red-50 hover:text-red-800 focus:outline-none focus:ring-2 focus:ring-red-300"
                aria-label={`Eliminar ${pet.nombre}`}
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            <div className="mt-5 flex items-center justify-between gap-3 border-t border-sandy-200 pt-4">
              <span className="text-xs uppercase tracking-[0.2em] text-slate-400">Historial básico</span>
              <Link
                href={`/portal/owner/pets/${pet.id}`}
                className="text-sm font-semibold text-teal transition-colors hover:text-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
              >
                Ver detalle
              </Link>
            </div>
          </article>
        ))}
      </div>

      {pagination && pagination.pages > 1 && (
        <div className="flex justify-center gap-2">
          {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => fetchPets(page)}
              className={`px-3 py-1 rounded ${
                page === pagination.page
                  ? 'bg-teal text-white'
                  : 'bg-sandy-100 text-slate-700 hover:bg-sandy-200'
              }`}
            >
              {page}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
