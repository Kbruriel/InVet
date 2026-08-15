/**
 * Pruebas unitarias para el hook usePets
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { usePets } from './use-pets';

// Mock dependencias necesarias
const mockGetMyPets = jest.fn();
const mockCreatePet = jest.fn();
const mockUpdatePet = jest.fn();
const mockDeletePet = jest.fn();
const mockGetPet = jest.fn();
const mockGetPetHistory = jest.fn();

jest.mock('../api/owners-api', () => ({
  getMyPets: (...args: unknown[]) => mockGetMyPets(...args),
  createPet: (...args: unknown[]) => mockCreatePet(...args),
  updatePet: (...args: unknown[]) => mockUpdatePet(...args),
  deletePet: (...args: unknown[]) => mockDeletePet(...args),
  getPet: (...args: unknown[]) => mockGetPet(...args),
  getPetHistory: (...args: unknown[]) => mockGetPetHistory(...args),
}));

/* ------------------------------------------------------------------ */
/*  Fixtures                                                           */
/* ------------------------------------------------------------------ */

const petFixture = {
  id: 1,
  owner_id: 9,
  nombre: 'Firulais',
  especie: 'Perro',
  raza: 'Labrador',
  edad: 3,
  peso: 25.0,
  fecha_nacimiento: '2023-01-15',
};

const petListResponseFixture = {
  items: [petFixture],
  meta: { page: 1, page_size: 20, total: 1 },
};

/* ------------------------------------------------------------------ */
/*  Estado inicial                                                     */
/* ------------------------------------------------------------------ */

describe('estado inicial', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia iniciar con pets vacio', () => {
    const { result } = renderHook(() => usePets());
    expect(result.current.pets).toEqual([]);
  });

  it('deberia iniciar loading en false', () => {
    const { result } = renderHook(() => usePets());
    expect(result.current.loading).toBe(false);
  });

  it('deberia iniciar error en null', () => {
    const { result } = renderHook(() => usePets());
    expect(result.current.error).toBeNull();
  });

  it('deberia iniciar pagination en null', () => {
    const { result } = renderHook(() => usePets());
    expect(result.current.pagination).toBeNull();
  });
});

/* ------------------------------------------------------------------ */
/*  fetchPets                                                          */
/* ------------------------------------------------------------------ */

describe('fetchPets', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia setear loading a true durante la carga', async () => {
    mockGetMyPets.mockReturnValueOnce(new Promise(() => {})); // nunca resuelve

    const { result } = renderHook(() => usePets());
    expect(result.current.loading).toBe(false);

    act(() => {
      void result.current.fetchPets();
    });

    expect(result.current.loading).toBe(true);
  });

  it('deberia setear pets cuando la API responde', async () => {
    mockGetMyPets.mockResolvedValueOnce(petListResponseFixture);

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.fetchPets();
    });

    expect(result.current.pets).toHaveLength(1);
    expect(result.current.pets[0].nombre).toBe('Firulais');
  });

  it('deberia setear pagination correctamente', async () => {
    const petListWithMore = {
      items: Array(5)
        .fill(null)
        .map((_, i) => ({ ...petFixture, id: i + 1, nombre: `Pet-${i}` })),
      meta: { page: 2, page_size: 5, total: 20, pages: 4 },
    };
    mockGetMyPets.mockResolvedValueOnce(petListWithMore);

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.fetchPets(2, 5);
    });

    expect(result.current.pagination).toEqual({ page: 2, page_size: 5, total: 20, pages: 4 });
  });

  it('deberia setear error cuando la API falla', async () => {
    mockGetMyPets.mockRejectedValueOnce({ status: 500, detail: 'Server error' });

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.fetchPets();
    });

    expect(result.current.error).toBe('Server error');
    expect(result.current.loading).toBe(false);
  });

  it('deberia llamar getMyPets con los paginacion correctos por defecto', async () => {
    mockGetMyPets.mockResolvedValueOnce(petListResponseFixture);

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.fetchPets();
    });

    expect(mockGetMyPets).toHaveBeenCalledWith(1, 20);
  });

  it('deberia llamar getMyPets con los paginacion correctos customizados', async () => {
    mockGetMyPets.mockResolvedValueOnce(petListResponseFixture);

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.fetchPets(3, 10);
    });

    expect(mockGetMyPets).toHaveBeenCalledWith(3, 10);
  });
});

/* ------------------------------------------------------------------ */
/*  addPet                                                             */
/* ------------------------------------------------------------------ */

describe('addPet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia agregar el nuevo pet a la lista', async () => {
    mockCreatePet.mockResolvedValueOnce(petFixture);

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.addPet({ nombre: 'Firulais', especie: 'Perro', raza: 'Labrador', edad: 3 });
    });

    expect(result.current.pets).toHaveLength(1);
    expect(result.current.pets[0].nombre).toBe('Firulais');
  });

  it('deberia lanzar error cuando la API falla', async () => {
    mockCreatePet.mockRejectedValueOnce({ status: 422, detail: 'Nombre requerido' });

    const { result } = renderHook(() => usePets());
    await expect(result.current.addPet({ nombre: 'Firulais', especie: 'Perro', raza: 'Labrador', edad: 3 })).rejects.toThrow('Nombre requerido');
  });

  it('deberia setear error state cuando la API falla', async () => {
    mockCreatePet.mockRejectedValueOnce({ status: 422, detail: 'Nombre requerido' });

    const { result } = renderHook(() => usePets());
    await act(async () => {
      void result.current.addPet({ nombre: 'Firulais', especie: 'Perro', raza: 'Labrador', edad: 3 }).catch(() => {});
    });

    expect(result.current.error).toBe('Nombre requerido');
    expect(result.current.loading).toBe(false);
  });
});

/* ------------------------------------------------------------------ */
/*  editPet                                                            */
/* ------------------------------------------------------------------ */

describe('editPet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUpdatePet.mockReset().mockResolvedValue(petFixture); // Reset to default resolve
  });

  it('deberia actualizar el pet en la lista', async () => {
    const updatedPet = { ...petFixture, nombre: 'Firulais Actualizado' };

    mockGetMyPets.mockResolvedValueOnce(petListResponseFixture);
    mockUpdatePet.mockResolvedValueOnce(updatedPet);

    const { result } = renderHook(() => usePets());

    // Load pets and then edit sequentially, each within an awaited act
    await act(async () => {
      await result.current.fetchPets();
    });

    await waitFor(() => expect(result.current.pets).toHaveLength(1));

    // ensure the mock was called and state updated

    await act(async () => {
      await result.current.editPet(1, { nombre: 'Firulais Actualizado' });
    });

    await waitFor(() => expect(result.current.pets).toHaveLength(1));
    expect(result.current.pets[0].nombre).toBe('Firulais Actualizado');
    expect(result.current.loading).toBe(false);
  });

  it('deberia lanzar error cuando la API falla', async () => {
    // Explicitly mockRejectedValue — beforeEach already cleared previous mocks
    mockUpdatePet.mockRejectedValueOnce({ status: 404, detail: 'Pet not found' });

    const { result } = renderHook(() => usePets());

    // RTL v14 + React 18: .rejects on the raw promise (not wrapped in act)
    await expect(result.current.editPet(1, { nombre: 'Nuevo' })).rejects.toThrow('Pet not found');
  });

  it('deberia setear error state cuando la API falla', async () => {
    mockUpdatePet.mockRejectedValueOnce({ status: 404, detail: 'Pet not found' });

    const { result } = renderHook(() => usePets());
    
    await act(async () => {
      void result.current.editPet(1, { nombre: 'Nuevo' }).catch(() => {});
    });

    expect(result.current.error).toBe('Pet not found');
    expect(result.current.loading).toBe(false);
  });
});

/* ------------------------------------------------------------------ */
/*  removePet                                                          */
/* ------------------------------------------------------------------ */

describe('removePet', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia remover el pet de la lista', async () => {
    mockGetMyPets.mockResolvedValueOnce(petListResponseFixture);
    mockDeletePet.mockResolvedValueOnce(undefined as void);

    const { result } = renderHook(() => usePets());
    await act(async () => {
      await result.current.fetchPets();
    });

    expect(result.current.pets).toHaveLength(1);

    await act(async () => {
      await result.current.removePet(1);
    });

    expect(result.current.pets).toHaveLength(0);
  });

  it('deberia lanzar error cuando la API falla', async () => {
    mockDeletePet.mockRejectedValueOnce({ status: 404, detail: 'Pet not found' });

    const { result } = renderHook(() => usePets());
    await expect(result.current.removePet(1)).rejects.toThrow('Pet not found');
  });

  it('deberia setear error state cuando la API falla', async () => {
    mockDeletePet.mockRejectedValueOnce({ status: 404, detail: 'Pet not found' });

    const { result } = renderHook(() => usePets());
    await act(async () => {
      void result.current.removePet(1).catch(() => {});
    });

    expect(result.current.error).toBe('Pet not found');
  });
});

/* ------------------------------------------------------------------ */
/*  fetchPetById                                                       */
/* ------------------------------------------------------------------ */

describe('fetchPetById', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia retornar el pet obtenido de la API', async () => {
    mockGetPet.mockResolvedValueOnce(petFixture);

    const { result } = renderHook(() => usePets());
    const pet = await act(async () => {
      return result.current.fetchPetById(1);
    });

    expect(pet.nombre).toBe('Firulais');
  });

  it('deberia lanzar error cuando la API falla', async () => {
    mockGetPet.mockRejectedValueOnce({ status: 403, detail: 'Forbidden' });

    const { result } = renderHook(() => usePets());
    await expect(result.current.fetchPetById(99)).rejects.toThrow('Forbidden');
  });

  it('deberia setear error state cuando la API falla', async () => {
    mockGetPet.mockRejectedValueOnce({ status: 403, detail: 'Forbidden' });

    const { result } = renderHook(() => usePets());
    await act(async () => {
      void result.current.fetchPetById(99).catch(() => {});
    });

    expect(result.current.error).toBe('Forbidden');
  });
});

/* ------------------------------------------------------------------ */
/*  fetchPetHistory                                                    */
/* ------------------------------------------------------------------ */

describe('fetchPetHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia retornar el historial del pet', async () => {
    const historyResponse = {
      items: [{ id: 1, motivo: 'Vacunacion', diagnostico: 'OK' }],
      meta: { page: 1, total: 1 },
    };
    mockGetPetHistory.mockResolvedValueOnce(historyResponse);

    const { result } = renderHook(() => usePets());
    const history = await act(async () => {
      return result.current.fetchPetHistory(1);
    });

    expect(history.items).toHaveLength(1);
    expect(history.items[0].motivo).toBe('Vacunacion');
  });

  it('deberia lanzar error cuando la API falla', async () => {
    mockGetPetHistory.mockRejectedValueOnce({ status: 500, detail: 'Server error' });

    const { result } = renderHook(() => usePets());
    await expect(result.current.fetchPetHistory(1)).rejects.toThrow('Server error');
  });

  it('deberia setear error state cuando la API falla', async () => {
    mockGetPetHistory.mockRejectedValueOnce({ status: 500, detail: 'Server error' });

    const { result } = renderHook(() => usePets());
    await act(async () => {
      void result.current.fetchPetHistory(1).catch(() => {});
    });

    expect(result.current.error).toBe('Server error');
  });
});

/* ------------------------------------------------------------------ */
/*  Integration: loading state y transiciones                          */
/* ------------------------------------------------------------------ */

describe('integracion', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deberia alternar loading en una operacion completa', async () => {
    mockGetMyPets.mockResolvedValueOnce(petListResponseFixture);

    const { result } = renderHook(() => usePets());

    expect(result.current.loading).toBe(false);

    await act(async () => {
      await result.current.fetchPets();
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('deberia limpiar el loading despues de una operacion con error', async () => {
    mockCreatePet.mockRejectedValueOnce({ status: 500, detail: 'Server error' });

    const { result } = renderHook(() => usePets());
    await expect(result.current.addPet({ nombre: 'Firulais', especie: 'Perro', raza: 'Labrador', edad: 3 })).rejects.toThrow();

    // Despues de un error, loading deberia estar en false
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });
});
