'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import { fetchPublicClinics, PublicClinic } from '@/shared/api/public-clinics';
import { Card, Button } from '@/shared/ui/components';
import { CategoryChipsWrapper } from '@/features/public-landing/components/CategoryChipsWrapper';

type UiState = 'loading' | 'success' | 'error' | 'empty';

export default function ClinicsPage() {
  return (
    <Suspense fallback={null}>
      <ClinicsContent />
    </Suspense>
  );
}

function ClinicsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [clinics, setClinics] = useState<PublicClinic[]>([]);
  const [state, setState] = useState<UiState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const page = Number(searchParams.get('page')) || 1;
  const searchQuery = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';

  const loadClinics = useCallback(async (pageNum: number, query?: string, serviceType?: string) => {
    setState('loading');
    setError(null);
    try {
      const params: { page: number; limit: number; search?: string; category?: string } = {
        page: pageNum,
        limit: 12,
      };
      if (query) params.search = query;
      if (serviceType) params.category = serviceType;

      const result = await fetchPublicClinics(params);
      setClinics(result.items);
      setTotalPages(result.totalPages);
      setTotal(result.total);
      setState(result.items.length > 0 ? 'success' : 'empty');
    } catch (err) {
      const e = err as { status?: number; detail?: string };
      setError(e.detail || 'No se pudieron cargar las clinicas. Intenta de nuevo.');
      setState('error');
    }
  }, []);

  useEffect(() => {
    loadClinics(page, searchQuery || undefined, category || undefined);
  }, [page, searchQuery, category, loadClinics]);

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(newPage));
    router.push(`/clinicas?${params.toString()}`);
  };

  return (
    <section aria-label="Listado de clinicas" className="py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">
          Clinicas veterinarias
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          {total > 0 ? `${total} clinica${total !== 1 ? 's' : ''} encontrada${total !== 1 ? 's' : ''}` : 'Busca la clinica ideal para tu mascota'}
        </p>

        <div className="mt-6">
          <CategoryChipsWrapper />
        </div>
      </div>

      {state === 'loading' && (
        <div className="flex items-center justify-center py-20" role="status" aria-label="Cargando clinicas">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-teal/30 border-t-teal" />
          <span className="sr-only">Cargando...</span>
        </div>
      )}

      {state === 'error' && error && (
        <div
          className="rounded-xl bg-red-50 p-6 text-center"
          role="alert"
        >
          <p className="text-sm text-red-700">{error}</p>
          <Button
            variant="outline"
            size="sm"
            className="mt-4 mx-auto"
            onClick={() => loadClinics(page, searchQuery || undefined)}
          >
            Reintentar
          </Button>
        </div>
      )}

      {state === 'empty' && (
        <div className="rounded-xl bg-sandy-100 p-12 text-center" role="status">
          <p className="text-lg font-medium text-slate-700">No se encontraron clinicas</p>
          <p className="mt-2 text-sm text-slate-500">
            Intenta con otros filtros o terminos de busqueda.
          </p>
        </div>
      )}

      {state === 'success' && (
        <>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {clinics.map((clinic) => (
              <Card key={clinic.id} href={`/clinicas/${clinic.id}`}>
                <div className="p-6">
                  {clinic.logoUrl && (
                    <img
                      src={clinic.logoUrl}
                      alt={`Logo de ${clinic.name}`}
                      className="mb-4 h-16 w-16 rounded-full object-cover"
                      loading="lazy"
                      width={64}
                      height={64}
                    />
                  )}
                  <h3 className="text-lg font-semibold text-slate-900">{clinic.name}</h3>
                  {clinic.city && (
                    <p className="mt-1 text-sm text-slate-500">
                      {clinic.city}
                    </p>
                  )}
                  {clinic.description && (
                    <p className="mt-2 line-clamp-2 text-sm text-slate-600">
                      {clinic.description}
                    </p>
                  )}
                  {clinic.rating != null && (
                    <div className="mt-3 flex items-center gap-1" aria-label={`Calificacion ${clinic.rating} de 5 estrellas`}>
                      <span className="text-sm font-medium text-teal">{'★'.repeat(Math.round(clinic.rating))}{'☆'.repeat(5 - Math.round(clinic.rating))}</span>
                      <span className="text-xs text-slate-500">({clinic.rating})</span>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>

          {totalPages > 1 && (
            <nav aria-label="Paginacion de clinicas" className="mt-8 flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => handlePageChange(page - 1)}
                aria-label="Pagina anterior"
              >
                Anterior
              </Button>
              <span className="px-4 text-sm text-slate-600">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => handlePageChange(page + 1)}
                aria-label="Pagina siguiente"
              >
                Siguiente
              </Button>
            </nav>
          )}
        </>
      )}
    </section>
  );
}
