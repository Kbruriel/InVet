'use client';

import { useCallback, useEffect, useState } from 'react';
import { extractApiError, isApiError, listPublicReviews } from '@/shared/api/review';
import type { ReviewListMeta, ReviewRead } from '@/shared/api/review';
import { Button, ErrorBanner, LoadingSpinner } from '@/shared/ui/components';

const PAGE_SIZE = 10;

const RATING_LABELS: { value: number; label: string }[] = [
  { value: 1, label: 'Muy mala' },
  { value: 2, label: 'Mala' },
  { value: 3, label: 'Regular' },
  { value: 4, label: 'Buena' },
  { value: 5, label: 'Excelente' },
];

export function formatDate(value: string | null): string {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function averageRating(items: ReviewRead[]): number | null {
  if (items.length === 0) return null;
  return items.reduce((sum, it) => sum + it.rating, 0) / items.length;
}

export function distribution(items: ReviewRead[]): { star: number; count: number }[] {
  return [1, 2, 3, 4, 5].map((star) => ({
    star,
    count: items.filter((it) => it.rating === star).length,
  }));
}

function Stars({ rating }: { rating: number }) {
  return (
    <span aria-hidden>
      {'★'.repeat(Math.max(0, Math.min(5, rating)))}
      {'☆'.repeat(Math.max(0, 5 - rating))}
    </span>
  );
}

export interface ReviewPublicListProps {
  branchId: number;
}

export function ReviewPublicList({ branchId }: ReviewPublicListProps) {
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<ReviewRead[]>([]);
  const [meta, setMeta] = useState<ReviewListMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (targetPage: number) => {
      setLoading(true);
      setError(null);
      try {
        const response = await listPublicReviews(branchId, {
          page: targetPage,
          page_size: PAGE_SIZE,
        });
        setItems(response.items);
        setMeta(response.meta);
        setPage(response.meta.page);
      } catch (err: unknown) {
        if (isApiError(err)) {
          setError(extractApiError(err));
        } else {
          setError('No fue posible cargar las reseñas. Inténtalo nuevamente.');
        }
        setItems([]);
        setMeta(null);
      } finally {
        setLoading(false);
      }
    },
    [branchId],
  );

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [load]);

  if (loading) {
    return <LoadingSpinner label="Cargando reseñas" />;
  }

  if (error !== null) {
    return <ErrorBanner message={error} actionLabel="Reintentar" onRetry={() => load(1)} />;
  }

  const total = meta?.total ?? 0;
  const avg = averageRating(items);
  const dist = distribution(items);

  return (
    <section aria-label="Reseñas de la sucursal" className="space-y-6">
      <div className="rounded-2xl border border-sandy-200 bg-white p-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1 text-xl font-semibold text-teal-dark">
            <span aria-hidden>{"★".repeat(Math.max(0, Math.min(5, Math.round(avg ?? 0))))}</span>
            <span>{"☆".repeat(Math.max(0, 5 - Math.round(avg ?? 0)))}</span>
          </div>
          <div className="text-sm text-slate-600">
            <span className="font-semibold">{avg !== null ? avg.toFixed(1) : 'N/A'}</span>
            {total > 0 ? (
              <>
                {' '}
                de 5 · {total} reseña{total === 1 ? '' : 's'}
              </>
            ) : null}
          </div>
        </div>

        <ul className="mt-4 space-y-1.5" aria-label="Distribución de calificaciones">
          {dist.map((row) => (
            <li key={row.star} className="flex items-center gap-3">
              <span className="w-8 shrink-0 text-right text-xs text-slate-500">{row.star}★</span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-sandy-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-teal to-mint"
                  style={{
                    width: total > 0 ? `${Math.round((row.count / total) * 100)}%` : '0%',
                  }}
                />
              </div>
              <span className="w-6 shrink-0 text-xs text-slate-500">{row.count}</span>
            </li>
          ))}
        </ul>
      </div>

      {items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-sandy-300 bg-white p-8 text-center" role="status">
          <p className="text-base font-semibold text-slate-700">Aún no hay reseñas</p>
          <p className="mt-1 text-sm text-slate-500">
            Cuando los clientes califiquen su visita, las reseñas aparecerán aquí.
          </p>
        </div>
      ) : (
        <ul className="space-y-4" aria-label="Listado de reseñas">
          {items.map((review) => (
            <li
              key={review.id}
              className="rounded-2xl border border-sandy-200 bg-white p-5"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <Stars rating={review.rating} />
                  <span className="text-sm font-medium text-slate-600">
                    {RATING_LABELS.find((r) => r.value === review.rating)?.label}
                  </span>
                </div>
                {review.created_at ? (
                  <time className="text-xs text-slate-400">
                    {formatDate(review.created_at)}
                  </time>
                ) : null}
              </div>
              {review.comment ? (
                <p className="mt-3 whitespace-pre-line text-[15px] leading-relaxed text-slate-700">
                  {review.comment}
                </p>
              ) : null}

              {review.response ? (
                <div className="mt-4 rounded-xl border-l-4 border-teal bg-sandy-50 p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-teal-dark">
                    Respuesta de la clínica
                  </p>
                  <p className="mt-2 whitespace-pre-line text-[15px] text-slate-700">
                    {review.response.body}
                  </p>
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      {(meta?.pages ?? 0) > 1 ? (
        <nav
          aria-label="Paginación de reseñas"
          className="flex items-center justify-center gap-4"
        >
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => load(page - 1)}
          >
            Anterior
          </Button>
          <span className="text-sm text-slate-600">
            Página {page} de {meta?.pages ?? 1}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= (meta?.pages ?? 1)}
            onClick={() => load(page + 1)}
          >
            Siguiente
          </Button>
        </nav>
      ) : null}
    </section>
  );
}
