/**
 * Hook para gestionar el perfil del propietario
 */

import { useState, useCallback } from 'react';
import {
  getMyOwner,
  updateMyOwner,
  type ApiError,
  type OwnerResponse,
  type OwnerUpdateData,
} from '../api/owners-api';

interface UseOwnerProfileReturn {
  owner: OwnerResponse | null;
  loading: boolean;
  error: string | null;
  fetchOwner: () => Promise<void>;
  updateProfile: (data: OwnerUpdateData) => Promise<OwnerResponse>;
}

export function useOwnerProfile(): UseOwnerProfileReturn {
  const [owner, setOwner] = useState<OwnerResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOwner = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMyOwner();
      setOwner(data);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (data: OwnerUpdateData): Promise<OwnerResponse> => {
    setLoading(true);
    setError(null);
    try {
      const updated = await updateMyOwner(data);
      setOwner(updated);
      return updated;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Error desconocido');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { owner, loading, error, fetchOwner, updateProfile };
}
