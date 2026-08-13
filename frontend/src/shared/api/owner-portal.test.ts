/** Tests unitarios para owner-portal API client */

import { getAccessToken } from '@/shared/auth/session';
import * as ownerPortal from './owner-portal';

// Mock dependencias
jest.mock('@/shared/auth/session', () => ({
  getAccessToken: jest.fn(),
}));

const mockedFetch = jest.fn();
global.fetch = mockedFetch;

/* ------------------------------------------------------------------ */
/*  getAccessToken helpers                                             */
/* ------------------------------------------------------------------ */

describe('getAccessToken usage in authHeaders', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia incluir Authorization header cuando hay token', async () => {
    (getAccessToken as jest.Mock).mockReturnValue('bearer-test-token');

    mockedFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [], meta: { page: 1, page_size: 20, total: 0 } }),
    });

    await ownerPortal.getMyPets(1, 5);

    const lastCall = mockedFetch.mock.calls[0];
    expect(lastCall[1]?.headers).toHaveProperty('Authorization', 'Bearer bearer-test-token');
  });

  it('deberia funcionar sin token (no-throw)', async () => {
    (getAccessToken as jest.Mock).mockReturnValue(null);

    mockedFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [], meta: { page: 1, page_size: 20, total: 0 } }),
    });

    await expect(ownerPortal.getMyPets()).resolves.not.toThrow();
  });
});

/* ------------------------------------------------------------------ */
/*  getMyOwner                                                         */
/* ------------------------------------------------------------------ */

describe('getMyOwner', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia devolver datos del owner', async () => {
    const mockOwner = {
      id: 1,
      user_id: 9,
      nombre: 'Ana Perez',
      email: 'ana@ejemplo.com',
      telefono: '809-555-0100',
      direccion: 'Calle 1',
      fecha_creacion: '2026-08-10T00:00:00Z',
    };

    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockOwner });

    const result = await ownerPortal.getMyOwner();
    expect(result).toEqual(mockOwner);
    expect(mockedFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/owners/me',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      })
    );
  });

  it('deberia lanzar ApiError cuando response.ok es false', async () => {
    mockedFetch.mockResolvedValue({ ok: false, status: 404, json: async () => ({ detail: 'No encontrado' }) });

    await expect(ownerPortal.getMyOwner()).rejects.toHaveProperty('status', 404);
  });
});

/* ------------------------------------------------------------------ */
/*  updateMyOwner                                                      */
/* ------------------------------------------------------------------ */

describe('updateMyOwner', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia enviar payload correcto y devolver owner actualizado', async () => {
    const updated = { id: 1, user_id: 9, nombre: 'Ana Actualizada', email: 'ana2@ejemplo.com', telefono: null, direccion: null, fecha_creacion: '2026-08-10T00:00:00Z' };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => updated });

    const result = await ownerPortal.updateMyOwner({ nombre: 'Ana Actualizada', email: 'ana2@ejemplo.com' });

    expect(result.nombre).toBe('Ana Actualizada');
    expect(mockedFetch).toHaveBeenCalledWith(
      expect.stringContaining('/owners/me'),
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({ nombre: 'Ana Actualizada', email: 'ana2@ejemplo.com' }),
      })
    );
  });
});

/* ------------------------------------------------------------------ */
/*  getMyPets                                                          */
/* ------------------------------------------------------------------ */

describe('getMyPets', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia construir query params correctos', async () => {
    const mockResponse = { items: [], meta: { page: 2, page_size: 5, total: 10 } };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockResponse });

    await ownerPortal.getMyPets(2, 5);

    const url = mockedFetch.mock.calls[0][0];
    expect(url).toContain('page=2');
    expect(url).toContain('page_size=5');
  });

  it('deberia normalizar meta.page_size cuando viene falta y usa size', async () => {
    const mockResponse = { items: [1, 2], meta: { page: 1, size: 10, total: 2 } };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockResponse });

    const result = await ownerPortal.getMyPets(1, 10);
    expect(result.meta.page_size).toBe(10);
  });

  it('deberia calcular meta.pages correctamente', async () => {
    const mockResponse = { items: [], meta: { page: 1, total: 50 } };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockResponse });

    const result = await ownerPortal.getMyPets(1, 20);
    expect(result.meta.pages).toBe(Math.ceil(50 / 20)); // 3
  });
});

/* ------------------------------------------------------------------ */
/*  createPet                                                          */
/* ------------------------------------------------------------------ */

describe('createPet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia enviar POST con payload de pet', async () => {
    const mockPet = { id: 5, owner_id: 1, nombre: 'Fido', especie: 'Perro', raza: 'Labrador', edad: 3, peso: 25.5, fecha_nacimiento: null };
    mockedFetch.mockResolvedValue({ ok: true, status: 201, json: async () => mockPet });

    const result = await ownerPortal.createPet({ nombre: 'Fido', especie: 'Perro', raza: 'Labrador', edad: 3, peso: 25.5 });

    expect(result.id).toBe(5);
    expect(mockedFetch).toHaveBeenCalledWith(
      expect.stringContaining('/owners/me/pets'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});

/* ------------------------------------------------------------------ */
/*  getPet / updatePet / deletePet                                     */
/* ------------------------------------------------------------------ */

describe('getPet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia hacer GET con el pet_id correcto', async () => {
    const mockPet = { id: 3, owner_id: 1, nombre: 'Michi', especie: 'Gato', raza: 'Siames', edad: 2, peso: 4.0, fecha_nacimiento: null };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockPet });

    const result = await ownerPortal.getPet(3);
    expect(result.nombre).toBe('Michi');
    expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/pets/3', expect.any(Object));
  });
});

describe('updatePet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia enviar PUT con el pet_id y payload', async () => {
    const mockPet = { id: 3, owner_id: 1, nombre: 'Michi Actualizado', especie: 'Gato', raza: 'Siames', edad: 2, peso: 4.0, fecha_nacimiento: null };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockPet });

    const result = await ownerPortal.updatePet(3, { nombre: 'Michi Actualizado' });
    expect(result.nombre).toBe('Michi Actualizado');
    expect(mockedFetch).toHaveBeenCalledWith(
      expect.stringContaining('/pets/3'),
      expect.objectContaining({ method: 'PUT' })
    );
  });
});

describe('deletePet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia enviar DELETE y no lanzar cuando response ok', async () => {
    mockedFetch.mockResolvedValue({ ok: true, status: 204 });

    await expect(ownerPortal.deletePet(3)).resolves.toBeUndefined();
    expect(mockedFetch).toHaveBeenCalledWith(
      expect.stringContaining('/pets/3'),
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  it('deberia lanzar ApiError cuando delete falla', async () => {
    mockedFetch.mockResolvedValue({ 
      ok: false, 
      status: 404,
      json: async () => ({ detail: 'Pet not found' })
    });

    await expect(ownerPortal.deletePet(99)).rejects.toHaveProperty('status', 404);
  });
});

/* ------------------------------------------------------------------ */
/*  getPetHistory                                                      */
/* ------------------------------------------------------------------ */

describe('getPetHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia devolver historial del pet', async () => {
    const mockHistory = { items: [{ id: 1, motivo: 'Vacunacion', diagnostico: 'OK' }], meta: { page: 1, total: 1 } };
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => mockHistory });

    const result = await ownerPortal.getPetHistory(3);
    expect(result.items).toHaveLength(1);
    expect(result.items[0].motivo).toBe('Vacunacion');
  });

  it('deberia devolver items vacíos cuando no hay historial', async () => {
    mockedFetch.mockResolvedValue({ ok: true, status: 200, json: async () => ({ items: [], meta: { page: 1, total: 0 } }) });

    const result = await ownerPortal.getPetHistory(3);
    expect(result.items).toEqual([]);
    expect(result.meta?.total).toBe(0);
  });
});

/* ------------------------------------------------------------------ */
/*  parseResponse (vía errores de endpoint)                          */
/* ------------------------------------------------------------------ */

describe('parseResponse error handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getAccessToken as jest.Mock).mockReturnValue('token');
  });

  it('deberia extraer detail del JSON del error', async () => {
    mockedFetch.mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: 'Campo requerido' }) });

    await expect(ownerPortal.getMyOwner()).rejects.toHaveProperty('detail', 'Campo requerido');
  });

  it('deberia fallback a "Error desconocido" cuando JSON falla', async () => {
    mockedFetch.mockResolvedValue({ ok: false, status: 500, json: async () => { throw new Error('JSON parse fail') } });

    await expect(ownerPortal.getMyOwner()).rejects.toHaveProperty('detail', 'Error desconocido');
  });
});
