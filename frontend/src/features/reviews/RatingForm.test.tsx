'use client';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { RatingForm } from './RatingForm';

jest.mock('@/shared/api/review', () => ({
  createReview: jest.fn(),
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

function fakeReview(overrides: Record<string, unknown> = {}) {
  return {
    id: 11,
    appointment_id: 3,
    branch_id: 2,
    clinic_id: 1,
    user_id: 5,
    rating: 5,
    comment: 'Muy buena atencion.',
    response: null,
    created_at: '2026-08-24T12:00:00',
    updated_at: null,
    ...overrides,
  };
}

describe('RatingForm', () => {
  const onCreated = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    if (typeof window !== 'undefined') {
      window.confirm = jest.fn(() => true);
    }
  });

  it('renders disabled submit until a star is selected', () => {
    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);
    expect(screen.getByRole('button', { name: 'Calificar cita' })).toBeDisabled();

    fireEvent.click(screen.getByRole('radio', { name: /4 estrella/i }));
    expect(screen.getByRole('button', { name: 'Calificar cita' })).not.toBeDisabled();
  });

  it('submits rating and calls onCreated on success', async () => {
    jest.spyOn(reviewApi, 'createReview').mockResolvedValue(fakeReview());

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /5 estrella/i }));
    fireEvent.change(screen.getByLabelText(/comentario/i), { target: { value: 'Muy buena atencion.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    await waitFor(() => expect(onCreated).toHaveBeenCalledTimes(1));
    expect(reviewApi.createReview).toHaveBeenCalledWith({
      appointment_id: 3,
      rating: 5,
      comment: 'Muy buena atencion.',
    });
  });

  it('shows success state and locks the form after creating a review', async () => {
    jest.spyOn(reviewApi, 'createReview').mockResolvedValue(fakeReview());

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /3 estrella/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    expect(await screen.findByText(/ya calificó esta cita/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Calificar cita' })).not.toBeInTheDocument();
  });

  it('disables the submit button (aria-busy) while creating', async () => {
    jest
      .spyOn(reviewApi, 'createReview')
      .mockImplementation(() => new Promise(() => {}));

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /2 estrella/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    const button = await waitFor(() => {
      const el = screen.getByRole('button', { name: 'Calificar cita' });
      expect(el).toBeDisabled();
      return el;
    });
    expect(button.getAttribute('aria-busy')).toBe('true');
  });

  it('maps 409 to the "ya calificó esta cita" state without error banner', async () => {
    jest.spyOn(reviewApi, 'createReview').mockRejectedValue({
      status: 409,
      detail: 'Esta cita ya fue calificada.',
    });

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /1 estrella/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    expect(await screen.findByText(/ya calificó esta cita/i)).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('shows the server error banner on 422', async () => {
    jest.spyOn(reviewApi, 'createReview').mockRejectedValue({
      status: 422,
      detail: 'rating debe estar entre 1 y 5',
    });

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /4 estrella/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.getByText(/rating debe estar entre 1 y 5/i)).toBeInTheDocument();
  });

  it('shows the server error banner on 404', async () => {
    jest.spyOn(reviewApi, 'createReview').mockRejectedValue({
      status: 404,
      detail: 'Cita no encontrada',
    });

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /5 estrella/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.getByText(/cita no encontrada/i)).toBeInTheDocument();
  });

  it('falls back to the generic submit error for non-API failures', async () => {
    jest.spyOn(reviewApi, 'createReview').mockImplementation(() => {
      throw new Error('Network Error');
    });

    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('radio', { name: /2 estrella/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Calificar cita' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.getByText(/no fue posible enviar la calificación/i)).toBeInTheDocument();
  });

  it('renders existing review as already reviewed from the start', () => {
    render(
      <RatingForm
        appointmentId={3}
        existingReview={fakeReview({ rating: 4, comment: 'Buena atención' })}
        onCreated={onCreated}
      />,
    );

    expect(screen.getByText(/ya calificó esta cita/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Calificar cita' })).not.toBeInTheDocument();
    expect(screen.getByText(/Buena atención/i)).toBeInTheDocument();
  });

  it('limits the comment to 2048 characters', () => {
    render(<RatingForm appointmentId={3} existingReview={null} onCreated={onCreated} />);

    const textarea = screen.getByLabelText(/comentario/i) as HTMLTextAreaElement;
    expect(textarea).toHaveAttribute('maxlength', '2048');

    fireEvent.change(textarea, { target: { value: 'x'.repeat(2048) } });
    expect(screen.getByText(/^2048\/2048$/)).toBeInTheDocument();
  });
});
