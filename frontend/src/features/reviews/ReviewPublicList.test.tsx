'use client';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ReviewPublicList, averageRating, distribution } from './ReviewPublicList';

jest.mock('@/shared/api/review', () => ({
  listPublicReviews: jest.fn(),
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

function fakeList(items: ReturnType<typeof fakeReview>[], page = 1, pageSize = 10) {
  return {
    items,
    meta: {
      page,
      page_size: pageSize,
      total: items.length,
      pages: Math.max(1, Math.ceil(items.length / pageSize)),
    },
  };
}

describe('ReviewPublicList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state while fetching', async () => {
    jest
      .spyOn(reviewApi, 'listPublicReviews')
      .mockImplementation(() => new Promise(() => {}));

    render(<ReviewPublicList branchId={2} />);

    expect(screen.getByRole('status', { name: 'Cargando reseñas' })).toBeInTheDocument();
    expect(screen.queryByText('Aún no hay reseñas')).not.toBeInTheDocument();
  });

  it('renders average rating and distribution', async () => {
    const list = fakeList([
      fakeReview({ id: 1, rating: 5 }),
      fakeReview({ id: 2, rating: 3 }),
      fakeReview({ id: 3, rating: 4 }),
    ]);
    jest.spyOn(reviewApi, 'listPublicReviews').mockResolvedValue(list);

    render(<ReviewPublicList branchId={2} />);

    await screen.findByRole('list', { name: 'Listado de reseñas' });

    expect(screen.getByText('4.0')).toBeInTheDocument();
    expect(screen.getByText(/3 reseñas/)).toBeInTheDocument();

    const dist = screen.getByRole('list', {
      name: 'Distribución de calificaciones',
    });
    expect(dist).toHaveTextContent('5★');
    expect(dist).toHaveTextContent('1★');
  });

  it('renders each review with comment and clinic response', async () => {
    jest.spyOn(reviewApi, 'listPublicReviews').mockResolvedValue(
      fakeList([
        fakeReview({
          id: 7,
          rating: 4,
          comment: 'Buen servicio',
          response: {
            id: 50,
            review_id: 7,
            branch_id: 2,
            user_id: 9,
            body: 'Gracias por la visita.',
            created_at: '2026-08-25T09:00:00',
            updated_at: null,
          },
        }),
      ]),
    );

    render(<ReviewPublicList branchId={2} />);
    await screen.findByRole('list', { name: 'Listado de reseñas' });

    expect(screen.getByText('Buen servicio')).toBeInTheDocument();
    expect(
      screen.getByRole('list', { name: 'Listado de reseñas' }).textContent,
    ).toContain('Respuesta de la clínica');

    const responseBlock = Array.from(
      screen.getByRole('list', { name: 'Listado de reseñas' }).querySelectorAll('div'),
    ).find((el) => el.textContent?.includes('Respuesta de la clínica'));
    expect(responseBlock?.textContent).toContain('Gracias por la visita.');
  });

  it('renders the empty state when there are no reviews', async () => {
    jest.spyOn(reviewApi, 'listPublicReviews').mockResolvedValue(fakeList([]));

    render(<ReviewPublicList branchId={2} />);

    expect(await screen.findByText('Aún no hay reseñas')).toBeInTheDocument();
    expect(screen.queryByRole('list', { name: 'Listado de reseñas' })).not.toBeInTheDocument();
  });

  it('maps 404 to the error banner and retries on action', async () => {
    jest
      .spyOn(reviewApi, 'listPublicReviews')
      .mockRejectedValueOnce({ status: 404, detail: 'Sucursal no encontrada' })
      .mockResolvedValueOnce(fakeList([fakeReview({ id: 8, rating: 3 })]));

    render(<ReviewPublicList branchId={99} />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.getByText(/Sucursal no encontrada/i)).toBeInTheDocument();

    const callsBefore = (reviewApi.listPublicReviews as jest.Mock).mock.calls.length;

    fireEvent.click(screen.getByRole('button', { name: 'Reintentar' }));

    await screen.findByRole('list', { name: 'Listado de reseñas' });
    const callsAfter = (reviewApi.listPublicReviews as jest.Mock).mock.calls.length;
    expect(callsAfter).toBe(callsBefore + 1);
  });

  it('renders error banner for non-API network errors', async () => {
    jest.spyOn(reviewApi, 'listPublicReviews').mockRejectedValue(new Error('Fallo de red'));

    render(<ReviewPublicList branchId={2} />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.getByText(/no fue posible cargar las reseñas/i)).toBeInTheDocument();
  });

  it('paginates when meta.pages > 1', async () => {
    const page1 = {
      items: Array.from({ length: 10 }, (_, i) => fakeReview({ id: i + 1, rating: 4 })),
      meta: { page: 1, page_size: 10, total: 15, pages: 2 },
    };
    const page2 = {
      items: [fakeReview({ id: 11, rating: 4 })],
      meta: { page: 2, page_size: 10, total: 15, pages: 2 },
    };
    jest
      .spyOn(reviewApi, 'listPublicReviews')
      .mockResolvedValueOnce(page1)
      .mockResolvedValueOnce(page2);

    render(<ReviewPublicList branchId={2} />);
    await screen.findByRole('list', { name: 'Listado de reseñas' });

    await screen.findByText('Página 1 de 2');
    expect(screen.getByRole('button', { name: 'Siguiente' })).not.toBeDisabled();
    expect(screen.getByRole('button', { name: 'Anterior' })).toBeDisabled();

    fireEvent.click(screen.getByRole('button', { name: 'Siguiente' }));
    await screen.findByText('Página 2 de 2');
    expect(screen.getByRole('button', { name: 'Siguiente' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Anterior' })).not.toBeDisabled();
  });

  describe('pure helpers', () => {
    it('averages ratings and handles empty list', () => {
      expect(averageRating([])).toBeNull();
      expect(averageRating([fakeReview({ rating: 5 }), fakeReview({ rating: 3 })])).toBe(4);
    });

    it('computes 5-bucket distribution', () => {
      const dist = distribution([
        fakeReview({ rating: 5 }),
        fakeReview({ rating: 5 }),
        fakeReview({ rating: 3 }),
      ]);
      expect(dist).toEqual([
        { star: 1, count: 0 },
        { star: 2, count: 0 },
        { star: 3, count: 1 },
        { star: 4, count: 0 },
        { star: 5, count: 2 },
      ]);
    });
  });
});
