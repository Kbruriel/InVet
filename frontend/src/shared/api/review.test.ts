import { apiClient } from './client';
import {
  createReview,
  extractApiError,
  getApiStatus,
  getReview,
  isApiError,
  listClinicReviews,
  listPublicReviews,
  respondReview,
} from './review';

jest.mock('./client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

function fakeResponse(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    review_id: 11,
    branch_id: 2,
    user_id: 5,
    body: 'Gracias por su paciencia.',
    created_at: '2026-08-24T12:00:00',
    updated_at: null,
    ...overrides,
  };
}

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

describe('review api client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('creates a review', async () => {
    mockedApiClient.post.mockResolvedValueOnce(
      fakeReview({ response: fakeResponse() }),
    );

    await createReview({
      appointment_id: 3,
      rating: 5,
      comment: 'Muy buena atencion.',
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/reviews', {
      appointment_id: 3,
      rating: 5,
      comment: 'Muy buena atencion.',
    });
  });

  it('creates a review without comment', async () => {
    mockedApiClient.post.mockResolvedValueOnce(fakeReview());

    await createReview({ appointment_id: 3, rating: 4 });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/reviews', {
      appointment_id: 3,
      rating: 4,
      comment: undefined,
    });
  });

  it('gets a review by id', async () => {
    mockedApiClient.get.mockResolvedValueOnce(fakeReview());

    await getReview(11);

    expect(mockedApiClient.get).toHaveBeenCalledWith('/reviews/11');
  });

  it('responds to a review', async () => {
    mockedApiClient.post.mockResolvedValueOnce(fakeResponse());

    await respondReview(11, { body: 'Gracias por su paciencia.' });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/reviews/11/respond', {
      body: 'Gracias por su paciencia.',
    });
  });

  it('lists public reviews with default params', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [fakeReview()],
      meta: { page: 1, page_size: 20, total: 1, pages: 1 },
    });

    await listPublicReviews(2);

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/reviews/public/2?page=1&page_size=20',
    );
  });

  it('lists public reviews with custom pagination', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      meta: { page: 2, page_size: 5, total: 3, pages: 1 },
    });

    await listPublicReviews(2, { page: 2, page_size: 5 });

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/reviews/public/2?page=2&page_size=5',
    );
  });

  it('lists clinic reviews with default params', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [fakeReview()],
      meta: { page: 1, page_size: 20, total: 1, pages: 1 },
    });

    await listClinicReviews();

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/reviews?page=1&page_size=20',
    );
  });

  it('lists clinic reviews filtered by branch', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      meta: { page: 3, page_size: 10, total: 25, pages: 3 },
    });

    await listClinicReviews({ page: 3, page_size: 10, branch_id: 4 });

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/reviews?page=3&page_size=10&branch_id=4',
    );
  });

  it('extracts detail message from ApiError-like values', () => {
    expect(extractApiError({ status: 409, detail: 'Esta cita ya fue calificada' })).toBe(
      'Esta cita ya fue calificada',
    );
    expect(extractApiError(new Error('Fallo de red'))).toBe('Fallo de red');
    expect(extractApiError({ status: 500, detail: null })).toBe('Error desconocido');
    expect(extractApiError(null)).toBe('Error desconocido');
  });

  it('reads HTTP status and types errors centrally', () => {
    const apiError = { status: 422, detail: 'rating fuera de rango' };
    expect(getApiStatus(apiError)).toBe(422);
    expect(isApiError(apiError)).toBe(true);
    expect(getApiStatus('boom')).toBeNull();
    expect(isApiError('boom')).toBe(false);
  });
});
