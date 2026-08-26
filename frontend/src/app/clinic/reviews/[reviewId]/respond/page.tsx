'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { getReview } from '@/shared/api/review';
import type { ReviewRead } from '@/shared/api/review';
import { extractApiError, isApiError } from '@/shared/api/review';
import { ReviewRespondForm } from '@/features/reviews/ReviewRespondForm';
import { formatDate } from '@/features/reviews/ReviewPublicList';
import { ErrorBanner, LoadingSpinner } from '@/shared/ui/components';

function Stars({ rating }: { rating: number }) {
  return (
    <span aria-hidden>
      {'★'.repeat(Math.max(0, Math.min(5, rating)))}
      {'☆'.repeat(Math.max(0, 5 - rating))}
    </span>
  );
}

export default function RespondReviewPage() {
  const params = useParams<{ reviewId: string }>();
  const reviewId = Number(params?.reviewId);
  const [review, setReview] = useState<ReviewRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!Number.isInteger(reviewId) || reviewId <= 0) {
      setError('Identificador de reseña inválido.');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getReview(reviewId);
      setReview(data);
    } catch (err: unknown) {
      setError(
        isApiError(err)
          ? extractApiError(err)
          : 'No fue posible cargar la reseña. Inténtalo nuevamente.',
      );
    } finally {
      setLoading(false);
    }
  }, [reviewId]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner label="Cargando reseña" />
      </div>
    );
  }

  if (error !== null || review === null) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <ErrorBanner
          message={error ?? 'No fue posible cargar la reseña.'}
          onRetry={load}
          actionLabel="Reintentar"
        />
        <div className="mt-6">
          <Link href="/clinic/reviews" className="text-sm text-teal hover:underline">
            &larr; Volver a reseñas
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-6">
      <div className="mb-6">
        <Link href="/clinic/reviews" className="text-sm text-teal hover:underline">
          &larr; Volver a reseñas
        </Link>
      </div>

      <section
        aria-label="Reseña a responder"
        className="rounded-2xl border border-sandy-200 bg-white p-6"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <Stars rating={review.rating} />
            <span className="text-sm font-medium text-slate-600">
              Calificación {review.rating}/5
            </span>
          </div>
          {review.created_at ? (
            <time className="text-xs text-slate-400">{formatDate(review.created_at)}</time>
          ) : null}
        </div>
        {review.comment ? (
          <p className="mt-3 whitespace-pre-line text-[15px] leading-relaxed text-slate-700">
            {review.comment}
          </p>
        ) : (
          <p className="mt-3 text-sm italic text-slate-400">No dejó comentario escrito.</p>
        )}
      </section>

      <section aria-label="Respuesta de la clínica" className="mt-6">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Responder reseña</h2>
        <ReviewRespondForm
          reviewId={review.id}
          existingResponse={review.response}
          onResponded={() => undefined}
        />
      </section>
    </div>
  );
}
