/**
 * Hook para gestionar las mascotas del propietario
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  getMyPets,
  createPet,
  updatePet,
  deletePet,
  getPet,
  getPetHistory,
  type ApiError,
  type PetResponse,
  type PetHistoryResponse,
  type PetListResponse,
  type PetCreateData,
  type PetUpdateData,
} from '../api/owners-api';

interface UsePetsReturn {
  pets: PetResponse[];
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    page_size: number;
    total: number;
    pages: number;
  } | null;
  fetchPets: (page?: number, size?: number) => Promise<void>;
  addPet: (data: PetCreateData) => Promise<PetResponse>;
  editPet: (petId: number, data: PetUpdateData) => Promise<PetResponse>;
  removePet: (petId: number) => Promise<void>;
  fetchPetById: (petId: number) => Promise<PetResponse>;
  fetchPetHistory: (petId: number) => Promise<PetHistoryResponse>;
}

export function usePets(): UsePetsReturn {
  const [pets, setPets] = useState<PetResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<UsePetsReturn['pagination']>(null);

  // petsRef mirrors pets state synchronously to avoid stale closure issues
  // in RTL v7 + React 19 where multiple setState calls inside act() can capture
  // outdated snapshots. Using ref ensures callbacks always see the latest value.
  const petsRef = useRef<PetResponse[]>([]);

  useEffect(() => {
    petsRef.current = pets;
  }, [pets]);

  const fetchPets = useCallback(async (page: number = 1, size: number = 20) => {
    setLoading(true);
    setError(null);
    try {
      const data: PetListResponse = await getMyPets(page, size);
      // Direct state set — no functional updater so RTL v7 + React 19 sees the value
      petsRef.current = data.items;
      setPets(data.items);
      setPagination({
        page: data.meta.page,
        page_size: data.meta.page_size ?? data.meta.size ?? size,
        total: data.meta.total,
        pages: data.meta.pages ?? 1,
      });
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  const addPet = useCallback(async (data: PetCreateData): Promise<PetResponse> => {
    setLoading(true);
    setError(null);
    try {
      const pet = await createPet(data);
      // Sync ref before setState so RTL v7 + React 19 captures the value within same act()
      petsRef.current = [...petsRef.current, pet];
      setPets(petsRef.current);
      return pet;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
      throw new Error(apiError.detail || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  const editPet = useCallback(async (petId: number, data: PetUpdateData): Promise<PetResponse> => {
    setLoading(true);
    setError(null);
    try {
      const updated = await updatePet(petId, data);
      // Use petsRef for synchronous read to avoid stale closure in RTL v7 + React 19
      const currentPets = [...petsRef.current];
      const newPets = currentPets.map(pet => (pet.id === petId ? { ...pet, ...updated } : pet));
      setPets(newPets);
      petsRef.current = newPets;
      return updated;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'error desconocido');
      throw new Error(apiError.detail || 'error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  const removePet = useCallback(async (petId: number): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await deletePet(petId);
      // Use direct ref read to avoid stale closure in RTL v7 + React 19
      petsRef.current = petsRef.current.filter(pet => pet.id !== petId);
      setPets(petsRef.current);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
      throw new Error(apiError.detail || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPetById = useCallback(async (petId: number): Promise<PetResponse> => {
    setLoading(true);
    setError(null);
    try {
      return await getPet(petId);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
      throw new Error(apiError.detail || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPetHistory = useCallback(async (petId: number): Promise<PetHistoryResponse> => {
    setLoading(true);
    setError(null);
    try {
      return await getPetHistory(petId);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
      throw new Error(apiError.detail || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    pets,
    loading,
    error,
    pagination,
    fetchPets,
    addPet,
    editPet,
    removePet,
    fetchPetById,
    fetchPetHistory,
  };
}
