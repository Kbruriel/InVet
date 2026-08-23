import { apiClient } from './client';
import {
  createPrescription,
  getPrescription,
  listPrescriptions,
} from './prescription';

jest.mock('./client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('prescription api client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('lists prescriptions with filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    });

    await listPrescriptions({ pet_id: 7, page: 1, page_size: 10 });

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/prescriptions?page=1&page_size=10&pet_id=7',
    );
  });

  it('gets one prescription by id', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      id: 4,
      consultation_id: 2,
      pet_id: 1,
      clinic_id: 1,
      branch_id: 2,
      veterinarian_id: null,
      diagnosis: 'diagnosis',
      treatment_notes: '',
      created_by: null,
      items: [],
      treatments: [],
      reminders: [],
      created_at: null,
      updated_at: null,
    });

    await getPrescription(4);

    expect(mockedApiClient.get).toHaveBeenCalledWith('/prescriptions/4');
  });

  it('creates prescriptions with optional sections', async () => {
    mockedApiClient.post.mockResolvedValueOnce({
      id: 9,
      consultation_id: 2,
      pet_id: 1,
      clinic_id: 7,
      branch_id: 2,
      veterinarian_id: null,
      diagnosis: 'diagnosis',
      treatment_notes: '',
      created_by: null,
      items: [],
      treatments: [],
      reminders: [],
      created_at: null,
      updated_at: null,
    });

    await createPrescription({
      consultation_id: 2,
      pet_id: 1,
      diagnosis: 'diagnosis',
      items: [{ name: 'Amoxicilina', dosage: '500mg' }],
      treatments: [{ name: 'Aplicar pomada' }],
      reminders: [{ title: 'Control a 7 dias', due_at: '2026-09-01T00:00:00' }],
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/prescriptions', {
      consultation_id: 2,
      pet_id: 1,
      diagnosis: 'diagnosis',
      items: [{ name: 'Amoxicilina', dosage: '500mg' }],
      treatments: [{ name: 'Aplicar pomada' }],
      reminders: [{ title: 'Control a 7 dias', due_at: '2026-09-01T00:00:00' }],
    });
  });
});
