'use client';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ReviewStaffList } from './ReviewStaffList';

jest.mock('@/shared/api/review', () => ({
  listClinicReviews: jest.fn(),
  extractApiError: (err: unknown) =>
    err && typeof err === 'object' && 'detail' in err
      ? (err as { detail: string }).detail
      : 'Error desconocido',
  isApiError: (err: unknown) =>
    err !== null &&
    typeof err === 'object' &&
    'status' in err &&
    typeof (err as { status?: unknown }).status === 'number',
}));

jest.mock('./ReviewPublicList', () => ({
  formatDate: (value: string | null) => value ?? '',
}));

jest.mock('./ReviewRespondForm', () => ({
  ReviewRespondForm: jest.fn(function MockRespond(props: {
    reviewId: number;
    existingResponse: unknown;
    onResponded: ((r: unknown) => void) | undefined;
  }) {
    if (props.existingResponse) {
      return (
        <div data-testid={`respond-${props.reviewId}-sent`} data-response={(props.existingResponse as { body: string }).body} />
      );
    }
    return (
      <div data-testid={`respond-${props.reviewId}-form`}>
        <button type="button" onClick={() => props.onResponded?.({ body: 'Gracias por la visita.' })}>
          Simulate respond
        </button>
      </div>
    );
  }),
}));

import * as reviewApi from '@/shared/api/review';

function fakeReview(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    appointment_id: 1,
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

function fakeList(
  items: ReturnType<typeof fakeReview>[],
  page = 1,
  pageSize = 10,
  total?: number,
) {
  const t = total ?? items.length;
  return {
    items,
    meta: {
      page,
      page_size: pageSize,
      total: t,
      pages: Math.max(1, Math.ceil(t / pageSize)),
    },
  };
}

describe('ReviewStaffList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state while fetching', () => {
    jest
      .spyOn(reviewApi, 'listClinicReviews')
      .mockImplementation(() => new Promise(() => {}));

    render(<ReviewStaffList />);

    expect(screen.getByRole('status', { name: 'Cargando reseñas de la clínica' })).toBeInTheDocument();
  });

  it('renders reviews with a respond form and marks answered ones', async () => {
    jest.spyOn(reviewApi, 'listClinicReviews').mockResolvedValue(
      fakeList([
        fakeReview({ id: 1, rating: 5, comment: 'Muy buena atencion.', response: null }),
        fakeReview({
          id: 2,
          rating: 3,
          comment: 'Esperamos bastante',
          response: {
            id: 50,
            review_id: 2,
            branch_id: 2,
            user_id: 9,
            body: 'Gracias por la visita.',
            created_at: '2026-08-25T09:00:00',
            updated_at: null,
          },
        }),
      ]),
    );

    render(<ReviewStaffList />);
    await screen.findByRole('list', { name: 'Reseñas para responder' });

    expect(screen.getByTestId('respond-1-form')).toBeInTheDocument();
    expect(screen.getByTestId('respond-2-sent')).toBeInTheDocument();
    expect(screen.getByText('Esperamos bastante')).toBeInTheDocument();
    expect(screen.getByText(/1 sin responder en esta página/i)).toBeInTheDocument();
  });

  it('marks a review as answered after responding (no reload)', async () => {
    jest.spyOn(reviewApi, 'listClinicReviews').mockResolvedValue(
      fakeList([fakeReview({ id: 1, rating: 5, comment: 'Bien', response: null })]),
    );

    const { rerender } = render(<ReviewStaffList />);
    await screen.findByRole('list', { name: 'Reseñas para responder' });
    expect(screen.getByTestId('respond-1-form')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Simulate respond' }));

    expect(await screen.findByTestId('respond-1-sent')).toBeInTheDocument();
    expect(screen.getByTestId('respond-1-sent').dataset.response).toBe(
      'Gracias por la visita.',
    );
    expect(screen.queryByTestId('respond-1-form')).not.toBeInTheDocument();

    // Re-render with a fresh (still-unanswered) copy: local state must persist.
    rerender(<ReviewStaffList />);
    await screen.findByRole('list', { name: 'Reseñas para responder' });
    expect(screen.getByTestId('respond-1-sent')).toBeInTheDocument();
  });

  it('renders the empty state when there are no reviews', async () => {
    jest.spyOn(reviewApi, 'listClinicReviews').mockResolvedValue(fakeList([]));

    render(<ReviewStaffList />);

    expect(await screen.findByText('Aún no hay reseñas')).toBeInTheDocument();
    expect(screen.queryByRole('list', { name: 'Reseñas para responder' })).not.toBeInTheDocument();
  });

  it('maps 403 to the error banner with a retry action', async () => {
    jest
      .spyOn(reviewApi, 'listClinicReviews')
      .mockRejectedValue({
        status: 403,
        detail: 'Solo personal asignado a la clínica puede listar reseñas.',
      });

    render(<ReviewStaffList />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(
      screen.getByText(/solo personal asignado a la clínica/i),
    ).toBeInTheDocument();

    jest
      .spyOn(reviewApi, 'listClinicReviews')
      .mockResolvedValue(fakeList([fakeReview({ id: 1, rating: 4 })]));
    fireEvent.click(screen.getByRole('button', { name: 'Reintentar' }));

    await screen.findByRole('list', { name: 'Reseñas para responder' });
  });

  it('passes branch_id filter to the API when provided', async () => {
    jest.spyOn(reviewApi, 'listClinicReviews').mockResolvedValue(fakeList([]));

    render(<ReviewStaffList branchId={7} />);
    await screen.findByText('Aún no hay reseñas');

    expect(reviewApi.listClinicReviews).toHaveBeenCalledWith({
      page: 1,
      page_size: 10,
      branch_id: 7,
    });
  });

  it('paginates across pages', async () => {
    const page1 = {
      items: Array.from({ length: 10 }, (_, i) => fakeReview({ id: i + 1, rating: 4 })),
      meta: { page: 1, page_size: 10, total: 12, pages: 2 },
    };
    const page2 = {
      items: [fakeReview({ id: 11, rating: 4 }), fakeReview({ id: 12, rating: 4 })],
      meta: { page: 2, page_size: 10, total: 12, pages: 2 },
    };
    jest
      .spyOn(reviewApi, 'listClinicReviews')
      .mockResolvedValueOnce(page1)
      .mockResolvedValueOnce(page2);

    render(<ReviewStaffList />);
    await screen.findByRole('list', { name: 'Reseñas para responder' });
    await screen.findByText('Página 1 de 2 · 12 reseñas');

    fireEvent.click(screen.getByRole('button', { name: 'Siguiente' }));
    await screen.findByText('Página 2 de 2 · 12 reseñas');
    expect(screen.getByRole('button', { name: 'Siguiente' })).toBeDisabled();
  });
});
