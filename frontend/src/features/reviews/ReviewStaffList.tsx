'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  extractApiError,
  isApiError,
  listClinicReviews,
} from '@/shared/api/review';
import type { ReviewListMeta, ReviewRead, ReviewResponseRead } from '@/shared/api/review';
import { Button, ErrorBanner, LoadingSpinner } from '@/shared/ui/components';
import { formatDate } from './ReviewPublicList';
import { ReviewRespondForm } from './ReviewRespondForm';

const PAGE_SIZE = 10;

export interface ReviewStaffListProps {
  branchId?: number;
}

export function ReviewStaffList({ branchId }: ReviewStaffListProps) {
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<ReviewRead[]>([]);
  const [meta, setMeta] = useState<ReviewListMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [localResponses, setLocalResponses] = useState<
    Record<number, ReviewResponseRead>
  >({});

  const load = useCallback(
    async (targetPage: number) => {
      setLoading(true);
      setError(null);
      try {
        const response = await listClinicReviews({
          page: targetPage,
          page_size: PAGE_SIZE,
          branch_id: branchId,
        });
        setItems(response.items);
        setMeta(response.meta);
        setPage(response.meta.page);
      } catch (err: unknown) {
        setError(
          isApiError(err)
            ? extractApiError(err)
            : 'No fue posible cargar las reseñas. Inténtalo nuevamente.',
        );
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

  const handleResponded = (reviewId: number, response: ReviewResponseRead) => {
    setLocalResponses((prev) => ({ ...prev, [reviewId]: response }));
  };

  if (loading) {
    return <LoadingSpinner label="Cargando reseñas de la clínica" />;
  }

  if (error !== null) {
    return (
      <ErrorBanner message={error} actionLabel="Reintentar" onRetry={() => load(1)} />
    );
  }

  const total = meta?.total ?? 0;
  const unanswered = items.filter(
    (review) => !(review.response || localResponses[review.id]),
  ).length;

  return (
    <section aria-label="Reseñas de la clínica" className="space-y-6">
      <div className="rounded-2xl border border-sandy-200 bg-white p-5">
        <p className="text-base font-semibold text-slate-800">
          {total} reseña{total === 1 ? '' : 's'}
        </p>
        <p className="mt-1 text-sm text-slate-500">
          {unanswered > 0
            ? `${unanswered} sin responder en esta página`
            : total > 0
              ? 'Todas las reseñas de esta página tienen respuesta'
              : 'Cuando los clientes califiquen sus visitas, verás sus reseñas aquí.'}
        </p>
      </div>

      {items.length === 0 ? (
        <div
          className="rounded-2xl border border-dashed border-sandy-300 bg-white p-8 text-center"
          role="status"
        >
          <p className="text-base font-semibold text-slate-700">Aún no hay reseñas</p>
          <p className="mt-1 text-sm text-slate-500">
            Cuando los clientes califiquen sus visitas, sus reseñas aparecerán aquí.
          </p>
        </div>
      ) : (
        <ul className="space-y-4" aria-label="Reseñas para responder">
          {items.map((review) => {
            const response = review.response ?? localResponses[review.id] ?? null;
            return (
              <li
                key={review.id}
                className="rounded-2xl border border-sandy-200 bg-white p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span aria-hidden>
                      {'★'.repeat(Math.max(0, Math.min(5, review.rating)))}
                      {'☆'.repeat(Math.max(0, 5 - review.rating))}
                    </span>
                    <span className="text-sm text-slate-600">
                      Calificación {review.rating}/5
                    </span>
                  </div>
                  {review.created_at ? (
                    <time className="text-xs text-slate-400">
                      {formatDate(review.created_at)}
                    </time>
                  ) : null}
                </div>
                {review.comment ? (
                  <p className="mt-2 whitespace-pre-line text-[15px] text-slate-700">
                    {review.comment}
                  </p>
                ) : (
                  <p className="mt-2 text-sm italic text-slate-400">
                    No dejó comentario escrito.
                  </p>
                )}
                <div className="mt-4 border-t border-sandy-100 pt-4">
                  <ReviewRespondForm
                    reviewId={review.id}
                    existingResponse={response}
                    onResponded={(response) => handleResponded(review.id, response)}
                  />
                </div>
              </li>
            );
          })}
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
            Página {page} de {meta?.pages ?? 1} · {total} reseñas
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
