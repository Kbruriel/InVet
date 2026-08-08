/** Tests para API client public (FE-003) */

import { fetchPublicClinics, fetchPublicClinicDetail, fetchPublicBranches, fetchPublicServices } from './public';

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('API Public Client', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe('fetchPublicClinics', () => {
    it('deberia listar clinicas con paginacion', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [{ id: 1, name: 'Clinica A', city: 'CDMX' }],
          total: 1,
          page: 1,
          limit: 12,
          totalPages: 1,
        }),
      });

      const result = await fetchPublicClinics({ page: 1, limit: 12 });

      expect(result.items.length).toBe(1);
      expect(result.total).toBe(1);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/clinicas?page=1&limit=12'),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('deberia incluir search en los query params', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, page: 1, limit: 12, totalPages: 0 }),
      });

      await fetchPublicClinics({ page: 1, limit: 12, search: 'veterinaria' });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('search=veterinaria'),
        expect.anything()
      );
    });

    it('deberia lanzar error en response no ok', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({ detail: 'Parametro invalido' }),
      });

      await expect(fetchPublicClinics({ page: 1 })).rejects.toEqual({
        status: 422,
        detail: 'Parametros de consulta invalidos',
      });
    });
  });

  describe('fetchPublicClinicDetail', () => {
    it('deberia obtener detalle de clinica', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, name: 'Clinica A', city: 'CDMX' }),
      });

      const result = await fetchPublicClinicDetail(1);

      expect(result.name).toBe('Clinica A');
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/clinicas/1'), expect.anything());
    });

    it('deberia lanzar 404 cuando no existe', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'No encontrado' }),
      });

      await expect(fetchPublicClinicDetail(999)).rejects.toEqual({
        status: 404,
        detail: 'Clinica no encontrada',
      });
    });
  });

  describe('fetchPublicBranches', () => {
    it('deberia listar sucursales con filtro clinica_id', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, page: 1, limit: 12, totalPages: 0 }),
      });

      await fetchPublicBranches({ clinicaId: 5 });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('clinica_id=5'),
        expect.anything()
      );
    });
  });

  describe('fetchPublicServices', () => {
    it('deberia listar servicios con filtro sucursal_id', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, page: 1, limit: 12, totalPages: 0 }),
      });

      await fetchPublicServices({ sucursalId: 10 });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('sucursal_id=10'),
        expect.anything()
      );
    });
  });
});
