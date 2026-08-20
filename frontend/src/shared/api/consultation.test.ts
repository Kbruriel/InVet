import { apiClient } from './client';
import {
  createConsultation,
  getConsultation,
  listConsultations,
} from './consultation';

jest.mock('./client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('consultation api client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('lists consultations with page and pet filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      meta: { page: 2, page_size: 10, total: 0, pages: 0 },
    });

    await listConsultations({ pet_id: 44, page: 2, page_size: 10 });

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/api/v1/consultations?page=2&page_size=10&pet_id=44',
    );
  });

  it('gets one consultation by id', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      id: 9,
      appointment_id: 2,
      pet_id: 1,
      clinic_id: 1,
      branch_id: 1,
      veterinarian_id: null,
      history: '',
      diagnosis: 'diagnosis',
      recommendations: '',
      created_by: null,
      updated_at: null,
    });

    await getConsultation(9);

    expect(mockedApiClient.get).toHaveBeenCalledWith('/api/v1/consultations/9');
  });

  it('creates consultations with optional text fields', async () => {
    mockedApiClient.post.mockResolvedValueOnce({
      id: 10,
      appointment_id: 2,
      pet_id: 1,
      clinic_id: 1,
      branch_id: 7,
      veterinarian_id: null,
      history: '',
      diagnosis: 'diagnosis',
      recommendations: '',
      created_by: null,
      updated_at: null,
    });

    await createConsultation({
      appointment_id: 2,
      pet_id: 1,
      diagnosis: 'diagnosis',
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/api/v1/consultations', {
      appointment_id: 2,
      pet_id: 1,
      diagnosis: 'diagnosis',
    });
  });
});
