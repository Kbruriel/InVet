'use client';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ReviewRespondForm } from './ReviewRespondForm';

jest.mock('@/shared/api/review', () => ({
  respondReview: jest.fn(),
  extractApiError: (err: unknown) =>
    err && typeof err === 'object' && 'detail' in err
      ? (err as { detail: string }).detail
      : 'Error desconocido',
  getApiStatus: (err: unknown) =>
    err && typeof err === 'object' && 'status' in err
      ? (err as { status: number }).status
      : null,
  isApiError: (err: unknown) =>
    err !== null &&
    typeof err === 'object' &&
    'status' in err &&
    typeof (err as { status?: unknown }).status === 'number',
}));

import * as reviewApi from '@/shared/api/review';

function fakeResponse(overrides: Record<string, unknown> = {}) {
  return {
    id: 50,
    review_id: 11,
    branch_id: 2,
    user_id: 9,
    body: 'Gracias por la visita.',
    created_at: '2026-08-25T09:00:00',
    updated_at: null,
    ...overrides,
  };
}

describe('ReviewRespondForm', () => {
  const onResponded = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('submits the body and calls onResponded with the response', async () => {
    jest.spyOn(reviewApi, 'respondReview').mockResolvedValue(fakeResponse());

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: 'Gracias por la visita.' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    await waitFor(() => expect(onResponded).toHaveBeenCalledTimes(1));
    expect(reviewApi.respondReview).toHaveBeenCalledWith(11, {
      body: 'Gracias por la visita.',
    });
  });

  it('locks the form and shows the existing response when already answered', () => {
    render(
      <ReviewRespondForm
        reviewId={11}
        existingResponse={fakeResponse({ body: 'Gracias por la visita.' })}
        onResponded={onResponded}
      />,
    );

    expect(screen.getByRole('status')).toHaveTextContent('Respuesta enviada');
    expect(screen.getByText('Gracias por la visita.')).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /responder/i }),
    ).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/respuesta de la clínica/i)).not.toBeInTheDocument();
  });

  it('shows a validation error when the body is blank', () => {
    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: '   ' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(/escribe la respuesta/i);
    expect(reviewApi.respondReview).not.toHaveBeenCalled();
  });

  it('trims the body before sending it', async () => {
    jest.spyOn(reviewApi, 'respondReview').mockResolvedValue(fakeResponse());

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: '  Hola, gracias  ' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    await waitFor(() => expect(onResponded).toHaveBeenCalledTimes(1));
    expect(reviewApi.respondReview).toHaveBeenCalledWith(11, { body: 'Hola, gracias' });
  });

  it('limits the response body to 2048 characters (backend max)', () => {
    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    const textarea = screen.getByLabelText(/respuesta de la clínica/i) as HTMLTextAreaElement;
    expect(textarea).toHaveAttribute('maxlength', '2048');

    fireEvent.change(textarea, { target: { value: 'x'.repeat(2048) } });
    expect(screen.getByText(/^2048\/2048$/)).toBeInTheDocument();
  });

  it('sets aria-busy and disables while submitting', async () => {
    jest
      .spyOn(reviewApi, 'respondReview')
      .mockImplementation(() => new Promise(() => {}));

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: 'Hola' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    const button = await waitFor(() => {
      const el = screen.getByRole('button', { name: /enviando|responder/i });
      expect(el).toBeDisabled();
      return el;
    });
    expect(button.getAttribute('aria-busy')).toBe('true');
    expect(button).toHaveTextContent(/enviando/i);
  });

  it('maps 409 to a friendly already-answered error and does not call onResponded', async () => {
    jest.spyOn(reviewApi, 'respondReview').mockRejectedValue({
      status: 409,
      detail: 'Esta reseña ya tiene una respuesta.',
    });

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: 'Hola' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('alert')).toHaveTextContent(/ya tiene una respuesta/i);
    expect(onResponded).not.toHaveBeenCalled();
  });

  it('maps 403 to the server error banner', async () => {
    jest.spyOn(reviewApi, 'respondReview').mockRejectedValue({
      status: 403,
      detail: 'Solo el equipo clínico de la sucursal puede responder reseñas.',
    });

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: 'Hola' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('alert')).toHaveTextContent(
      /solo el equipo clínico de la sucursal/i,
    );
  });

  it('maps 404 to the server error banner', async () => {
    jest.spyOn(reviewApi, 'respondReview').mockRejectedValue({
      status: 404,
      detail: 'Reseña no encontrada',
    });

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: 'Hola' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('alert')).toHaveTextContent(/reseña no encontrada/i);
  });

  it('falls back to a generic error for non-API failures', async () => {
    jest.spyOn(reviewApi, 'respondReview').mockRejectedValue(new Error('Fallo de red'));

    render(
      <ReviewRespondForm reviewId={11} existingResponse={null} onResponded={onResponded} />,
    );

    fireEvent.change(screen.getByLabelText(/respuesta de la clínica/i), {
      target: { value: 'Hola' },
    });
    fireEvent.click(screen.getByRole('button', { name: /responder/i }));

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('alert')).toHaveTextContent(
      /no fue posible enviar la respuesta/i,
    );
  });
});
