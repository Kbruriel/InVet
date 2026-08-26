'use client';

import { useState } from 'react';
import { extractApiError, getApiStatus, isApiError, respondReview } from '@/shared/api/review';
import type { ReviewResponseRead } from '@/shared/api/review';
import { Button } from '@/shared/ui/components';

const RESPONSE_MAX = 2048;

export interface ReviewRespondFormProps {
  reviewId: number;
  existingResponse: ReviewResponseRead | null;
  onResponded: (response: ReviewResponseRead) => void;
}

export function ReviewRespondForm({
  reviewId,
  existingResponse,
  onResponded,
}: ReviewRespondFormProps) {
  const [body, setBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (existingResponse) {
    return (
      <div
        role="status"
        className="rounded-2xl border border-teal/20 bg-sandy-50 p-4"
      >
        <p className="text-xs font-semibold uppercase tracking-wide text-teal-dark">
          Respuesta enviada
        </p>
        <p className="mt-2 whitespace-pre-line text-[15px] text-slate-700">
          {existingResponse.body}
        </p>
      </div>
    );
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = body.trim();
    if (!trimmed) {
      setError('Escribe la respuesta antes de enviarla.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const response = await respondReview(reviewId, { body: trimmed });
      onResponded(response);
    } catch (err: unknown) {
      if (isApiError(err) && getApiStatus(err) === 409) {
        setError('Esta reseña ya tiene una respuesta registrada.');
      } else if (isApiError(err)) {
        setError(extractApiError(err));
      } else {
        setError('No fue posible enviar la respuesta. Inténtalo nuevamente.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form noValidate onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label
          htmlFor={`respond-review-${reviewId}`}
          className="mb-1 block text-sm font-medium text-slate-700"
        >
          Respuesta de la clínica
        </label>
        <textarea
          id={`respond-review-${reviewId}`}
          value={body}
          onChange={(event) => {
            setBody(event.target.value.slice(0, RESPONSE_MAX));
            setError(null);
          }}
          rows={3}
          maxLength={RESPONSE_MAX}
          placeholder="Escribe una respuesta respetuosa…"
          aria-invalid={error !== null}
          className="w-full rounded-2xl border border-sandy-300 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal"
        />
        <p className="mt-1 text-right text-xs text-slate-400">
          {body.length}/{RESPONSE_MAX}
        </p>
      </div>

      {error ? (
        <p role="alert" className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      <Button type="submit" size="sm" variant="secondary" isLoading={submitting}>
        {submitting ? 'Enviando…' : 'Responder'}
      </Button>
    </form>
  );
}
