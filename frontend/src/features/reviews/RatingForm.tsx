'use client';

import { useState } from 'react';
import { createReview, extractApiError, getApiStatus, isApiError } from '@/shared/api/review';
import type { ReviewRead } from '@/shared/api/review';
import { Button } from '@/shared/ui/components';

const RATING_LABELS: { value: number; label: string }[] = [
  { value: 1, label: 'Muy mala' },
  { value: 2, label: 'Mala' },
  { value: 3, label: 'Regular' },
  { value: 4, label: 'Buena' },
  { value: 5, label: 'Excelente' },
];

const COMMENT_MAX = 2048;

export interface RatingFormProps {
  appointmentId: number;
  existingReview: ReviewRead | null;
  onCreated: (review: ReviewRead) => void;
}

export function RatingForm({ appointmentId, existingReview, onCreated }: RatingFormProps) {
  const [rating, setRating] = useState<number>(0);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [alreadyReviewed, setAlreadyReviewed] = useState(false);

  const isLocked = existingReview !== null || alreadyReviewed || success;

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (rating === 0) {
      setError('Selecciona una calificación entre 1 y 5 estrellas.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const review = await createReview({
        appointment_id: appointmentId,
        rating,
        comment: comment.trim() || undefined,
      });
      setSuccess(true);
      onCreated(review);
    } catch (err: unknown) {
      if (isApiError(err)) {
        const status = getApiStatus(err);
        if (status === 409) {
          setAlreadyReviewed(true);
          return;
        }
        setError(extractApiError(err));
      } else {
        setError('No fue posible enviar la calificación. Inténtalo nuevamente.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (isLocked) {
    return (
      <section aria-label="Calificar cita" className="rounded-[32px] border border-sandy-300 bg-white p-6">
        <h3 className="mb-1 text-base font-semibold text-slate-800">Calificar cita</h3>
        <p role="status" className="rounded-2xl bg-sandy-100 px-4 py-3 text-sm text-slate-600">
          Ya calificó esta cita
          {success ? ' correctamente. ¡Gracias por compartir tu opinión!' : '.'}
        </p>
        {existingReview && (
          <div className="mt-3">
            <p className="text-xs font-medium text-slate-500">
              {RATING_LABELS.find((r) => r.value === existingReview.rating)?.label ?? `${existingReview.rating} estrella${existingReview.rating === 1 ? '' : 's'}`}
            </p>
            {existingReview.comment ? (
              <p className="mt-1 text-sm text-slate-600">{existingReview.comment}</p>
            ) : null}
          </div>
        )}
      </section>
    );
  }

  return (
    <section aria-label="Calificar cita" className="rounded-[32px] border border-sandy-300 bg-white p-6">
      <h3 className="mb-4 text-base font-semibold text-slate-800">Calificar cita</h3>
      <form noValidate onSubmit={handleSubmit} className="space-y-6">
        <fieldset disabled={submitting}>
          <legend className="sr-only">Calificación</legend>
          <div role="radiogroup" aria-label="Calificación de la cita" className="flex flex-wrap gap-2">
            {RATING_LABELS.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={rating === value}
                aria-label={`${value} estrella - ${label}`}
                onClick={() => {
                  setRating(value);
                  setError(null);
                }}
                className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                  rating === value
                    ? 'border-teal bg-teal/10 font-semibold text-teal'
                    : 'border-sandy-300 bg-white text-slate-700 hover:border-teal/50'
                }`}
              >
                {value} {label}
              </button>
            ))}
          </div>

          <div>
            <label htmlFor="review-comment" className="mb-1 block text-sm font-medium text-slate-700">
              Comentario (opcional)
            </label>
            <textarea
              id="review-comment"
              value={comment}
              onChange={(event) => setComment(event.target.value.slice(0, COMMENT_MAX))}
              rows={4}
              maxLength={COMMENT_MAX}
              placeholder="Cuenta tu experiencia..."
              aria-invalid={Boolean(error)}
              className="w-full rounded-2xl border border-sandy-300 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal"
            />
            <p className="mt-1 text-right text-xs text-slate-400">
              {comment.length}/{COMMENT_MAX}
            </p>
          </div>
        </fieldset>

        {error ? (
          <p role="alert" className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        <Button type="submit" size="lg" isLoading={submitting} disabled={rating === 0}>
          Calificar cita
        </Button>
      </form>
    </section>
  );
}
