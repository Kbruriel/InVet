'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Card, Button, ErrorBanner, EmptyState, LoadingSpinner } from '@/shared/ui/components';
import { fetchBranchPublic, BranchProfilePublic, AvailabilitySummary } from '@/shared/api/branch-client';
import { ReviewPublicList } from '@/features/reviews/ReviewPublicList';

type UiState = 'loading' | 'success' | 'error' | 'empty';

interface BranchProfileProps {
  branchId: number;
}

function formatDay(day: string): string {
  const days: Record<string, string> = {
    monday: 'Lunes',
    tuesday: 'Martes',
    wednesday: 'Miércoles',
    thursday: 'Jueves',
    friday: 'Viernes',
    saturday: 'Sábado',
    sunday: 'Domingo',
  };
  return days[day.toLowerCase()] || day;
}

function formatTime(time: string): string {
  if (!time) return '--:--';
  const [hours, minutes] = time.split(':');
  return `${hours}:${minutes}`;
}

function renderStars(rating: number | null): string {
  if (rating == null) return '';
  const full = Math.round(rating);
  return '★'.repeat(full) + '☆'.repeat(5 - full);
}

function AvailabilityBadge({ availability }: { availability: AvailabilitySummary }) {
  const labels: Record<string, { text: string; color: string }> = {
    available: { text: 'Disponible', color: 'bg-green-100 text-green-800' },
    unavailable: { text: 'No disponible', color: 'bg-red-100 text-red-800' },
    full: { text: 'Sin cupos', color: 'bg-yellow-100 text-yellow-800' },
  };
  const config = labels[availability.status] || labels.unavailable;
  return (
    <span
      role="status"
      aria-label={config.text}
      className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${config.color}`}
    >
      {config.text}
    </span>
  );
}

function ServicesSection({ services }: { services: BranchProfilePublic['services'] }) {
  if (services.length === 0) return null;

  return (
    <div className="border-t border-sandy-300 pt-6">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Servicios</h2>
      <ul className="space-y-3">
        {services.map((service) => (
          <li key={service.id} className="flex items-start justify-between rounded-lg bg-slate-50 p-4">
            <div className="flex-1">
              <p className="font-medium text-slate-900">{service.name}</p>
              {service.description && (
                <p className="mt-1 text-sm text-slate-600">{service.description}</p>
              )}
            </div>
            <div className="ml-4 flex-shrink-0 text-right">
              {service.price != null && (
                <p className="text-sm font-semibold text-teal">${service.price.toFixed(2)}</p>
              )}
              {service.durationMinutes != null && (
                <p className="mt-1 text-xs text-slate-500">{service.durationMinutes} min</p>
              )}
              {!service.active && (
                <span className="mt-1 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  Inactivo
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function SchedulesSection({ schedules }: { schedules: BranchProfilePublic['schedules'] }) {
  if (schedules.length === 0) return null;

  const today = new Date().getDay();
  const dayMap = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  const todayName = dayMap[today];

  return (
    <div className="border-t border-sandy-300 pt-6">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Horarios</h2>
      <ul className="space-y-2">
        {schedules.map((schedule) => {
          const isToday = schedule.dayOfWeek.toLowerCase() === todayName;
          return (
            <li
              key={schedule.id}
              className={`flex items-center justify-between rounded-lg p-3 ${
                isToday ? 'bg-teal/10 ring-1 ring-teal/30' : 'bg-slate-50'
              }`}
            >
              <span className={`text-sm ${isToday ? 'font-semibold text-teal' : 'text-slate-700'}`}>
                {formatDay(schedule.dayOfWeek)}
                {isToday && <span className="ml-2 text-xs">(hoy)</span>}
              </span>
              <div className="flex items-center gap-3">
                {schedule.isHoliday && (
                  <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800">
                    Feriado
                  </span>
                )}
                <span className="text-sm text-slate-600">
                  {formatTime(schedule.openTime)} - {formatTime(schedule.closeTime)}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function RatingSection({ rating }: { rating: BranchProfilePublic['rating'] }) {
  if (rating == null || rating.count === 0) return null;

  return (
    <div className="border-t border-sandy-300 pt-6">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Calificaciones</h2>
      <div className="flex items-center gap-3">
        <span className="text-3xl font-extrabold text-slate-900">{rating.average.toFixed(1)}</span>
        <div>
          <div className="text-teal" aria-label={`${renderStars(rating.average)} de 5 estrellas`}>
            {renderStars(rating.average)}
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Basado en {rating.count} {rating.count === 1 ? 'calificación' : 'calificaciones'}
          </p>
        </div>
      </div>
    </div>
  );
}

export function BranchProfile({ branchId }: BranchProfileProps) {
  const [branch, setBranch] = useState<BranchProfilePublic | null>(null);
  const [state, setState] = useState<UiState>('loading');
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState('loading');
    setError(null);
    try {
      const branchData = await fetchBranchPublic(branchId);
      setBranch(branchData);

      if (!branchData) {
        setState('empty');
      } else {
        setState('success');
      }
    } catch (err) {
      const e = err as { status?: number; detail?: string };
      setError(e.detail || 'No se pudo cargar el perfil de la sucursal.');
      setState('error');
    }
  }, [branchId]);

  useEffect(() => {
    load();
  }, [load]);

  if (state === 'loading') {
    return <LoadingSpinner label="Cargando perfil de sucursal..." />;
  }

  if (state === 'error') {
    return <ErrorBanner message={error ?? 'Error desconocido'} onRetry={load} actionLabel="Reintentar" />;
  }

  if (state === 'empty' || !branch) {
    return (
      <EmptyState
        title="Sucursal no encontrada"
        description="No existe una sucursal con ese identificador."
        actionLabel="Ver todas las clínicas"
        onAction={() => { window.location.href = '/clinicas'; }}
      />
    );
  }

  return (
    <section aria-label={`Perfil de ${branch.name}`} className="py-10">
      <div className="mb-6">
        <Link href="/clinicas" className="text-sm text-teal hover:underline">
          &larr; Volver a clínicas
        </Link>
      </div>

      <Card className="p-8">
        {/* Header */}
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          {branch.logoUrl && (
            <img
              src={branch.logoUrl}
              alt={`Logo de ${branch.name}`}
              className="h-24 w-24 flex-shrink-0 rounded-full object-cover"
              width={96}
              height={96}
            />
          )}
          <div className="flex-1">
            <h1 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">{branch.name}</h1>
            {branch.city && (
              <p className="mt-1 text-sm text-slate-500">📍 {branch.city}</p>
            )}
            {branch.address && (
              <p className="mt-1 text-sm text-slate-600">{branch.address}</p>
            )}
            {branch.phone && (
              <p className="mt-1 text-sm text-slate-600">📞 {branch.phone ?? ''}</p>
            )}
            {branch.rating && (
              <div className="mt-2 flex items-center gap-2" aria-label={`Calificación ${branch.rating.average.toFixed(1)} de 5 estrellas`}>
                <span className="text-lg text-teal">{renderStars(branch.rating.average)}</span>
                <span className="text-sm font-medium text-slate-700">{branch.rating.average.toFixed(1)}</span>
                <span className="text-xs text-slate-500">({branch.rating.count})</span>
              </div>
            )}
            {branch.availability && (
              <div className="mt-2">
                <AvailabilityBadge availability={branch.availability} />
              </div>
            )}
          </div>
        </div>

        {/* Description */}
        {branch.description && (
          <div className="mt-6 border-t border-sandy-300 pt-6">
            <h2 className="mb-3 text-lg font-semibold text-slate-900">Acerca de</h2>
            <p className="text-sm leading-relaxed text-slate-700">{branch.description}</p>
          </div>
        )}

        {/* Services */}
        <ServicesSection services={branch.services} />

        {/* Schedules */}
        <SchedulesSection schedules={branch.schedules} />

        {/* Rating */}
        <RatingSection rating={branch.rating} />

        {/* Reseñas */}
        <div className="mt-6 border-t border-sandy-300 pt-6">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Reseñas</h2>
          <ReviewPublicList branchId={branchId} />
        </div>


        {/* CTA */}
        <div className="mt-6 flex flex-wrap gap-4 border-t border-sandy-300 pt-6">
          <Link href={`/register?branch=${branchId}`}>
            <Button size="lg">Solicitar cita</Button>
          </Link>
          <Link href="/clinicas">
            <Button variant="outline" size="lg">
              Otras clínicas
            </Button>
          </Link>
        </div>
      </Card>
    </section>
  );
}
