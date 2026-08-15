'use client';

import { useEffect, useState } from 'react';
import { Button, EmptyState, ErrorBanner, LoadingSpinner } from '@/shared/ui/components';
import { usePets } from '../hooks/use-pets';
import { PetForm } from './pet-form';
import type { PetHistoryEntry, PetResponse } from '../api/owners-api';

interface PetDetailProps {
  petId: number;
  onBack: () => void;
}

function formatHistoryDate(value?: string | null): string {
  if (!value) {
    return 'Sin fecha registrada';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('es-DO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

export function PetDetail({ petId, onBack }: PetDetailProps) {
  const { editPet, fetchPetById, fetchPetHistory } = usePets();
  const [pet, setPet] = useState<PetResponse | null>(null);
  const [history, setHistory] = useState<PetHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadPetDetail() {
      setLoading(true);
      setError(null);

      try {
        const [petData, historyData] = await Promise.all([
          fetchPetById(petId),
          fetchPetHistory(petId),
        ]);

        if (!active) {
          return;
        }

        setPet(petData);
        setHistory(historyData.items);
      } catch (err) {
        if (!active) {
          return;
        }

        if (typeof err === 'object' && err && 'detail' in err && typeof err.detail === 'string') {
          setError(err.detail);
        } else {
          setError('No fue posible cargar el detalle de la mascota.');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadPetDetail();

    return () => {
      active = false;
    };
  }, [fetchPetById, fetchPetHistory, petId]);

  const handleEdit = async (data: {
    nombre: string;
    especie: string;
    raza: string;
    edad: number;
    peso?: number;
    fecha_nacimiento?: string;
  }) => {
    setSubmitting(true);
    try {
      const updated = await editPet(petId, data);
      setPet(updated);
      setEditing(false);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Cargando detalle de la mascota" />;
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={onBack} actionLabel="Volver al portal" />;
  }

  if (!pet) {
    return (
      <EmptyState
        title="Mascota no encontrada"
        description="La mascota que intentas consultar ya no está disponible o no pertenece a tu cuenta."
        actionLabel="Volver al portal"
        onAction={onBack}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-[32px] bg-sandy-100 p-6 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-teal">Ficha del paciente</p>
          <h2 className="mt-2 text-3xl font-semibold text-slate-900">{pet.nombre}</h2>
          <p className="mt-2 text-sm capitalize text-slate-600">{pet.especie} · {pet.raza}</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Button type="button" variant="outline" onClick={onBack}>
            Volver al portal
          </Button>
          <Button type="button" onClick={() => setEditing(current => !current)}>
            {editing ? 'Cancelar edición' : 'Editar mascota'}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-[28px] border border-sandy-300 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Edad</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{pet.edad} años</p>
        </div>
        <div className="rounded-[28px] border border-sandy-300 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Peso</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{pet.peso ? `${pet.peso} kg` : 'Sin registro'}</p>
        </div>
        <div className="rounded-[28px] border border-sandy-300 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Fecha de nacimiento</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{pet.fecha_nacimiento || 'Sin registro'}</p>
        </div>
        <div className="rounded-[28px] border border-sandy-300 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Identificador</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{pet.id}</p>
        </div>
      </div>

      {editing ? (
        <PetForm
          onSubmit={handleEdit}
          onCancel={() => setEditing(false)}
          submitting={submitting}
          initialData={{
            nombre: pet.nombre,
            especie: pet.especie,
            raza: pet.raza,
            edad: pet.edad,
            peso: pet.peso || undefined,
            fecha_nacimiento: pet.fecha_nacimiento || undefined,
          }}
        />
      ) : null}

      <section className="rounded-[32px] border border-sandy-300 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Historial básico</p>
            <h3 className="text-xl font-semibold text-slate-900">Consultas previas</h3>
          </div>
          <p className="text-sm text-slate-500">Se muestran referencias del slice 009 cuando existen.</p>
        </div>

        {history.length === 0 ? (
          <EmptyState
            title="Aún no hay consultas registradas"
            description="Cuando esta mascota tenga consultas médicas previas, aparecerán aquí de forma cronológica."
          />
        ) : (
          <div className="mt-6 space-y-4">
            {history.map((entry) => (
              <article key={entry.id} className="rounded-[24px] border border-sandy-200 bg-sandy-50 p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{entry.motivo || 'Consulta médica'}</p>
                    <p className="mt-1 text-sm text-slate-600">{entry.diagnostico || 'Sin diagnóstico registrado'}</p>
                  </div>
                  <div className="text-sm text-slate-500">
                    <p>{formatHistoryDate(entry.fecha)}</p>
                    <p>{entry.veterinario || 'Veterinario por confirmar'}</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}