'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  fetchVeterinarians,
  createVeterinarian as apiCreateVeterinarian,
  updateVeterinarian as apiUpdateVeterinarian,
  deactivateVeterinarian as apiDeactivateVeterinarian,
  fetchVeterinarian as apiFetchVeterinarian,
  type VeterinarianDTO,
  type VeterinarianCreateDTO,
  type VeterinarianUpdateDTO,
  type ApiError,
} from '@/shared/api/slice-006';

export function useVeterinarians(clinicId?: number) {
  const [items, setItems] = useState<VeterinarianDTO[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size] = useState(20);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const load = useCallback(async (p: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchVeterinarians({ page: p, size, clinic_id: clinicId });
      setItems(data.items);
      setTotal(data.total);
      setPage(p);
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setLoading(false);
    }
  }, [size, clinicId]);

  useEffect(() => { load(1); }, [load]);

  const create = async (payload: VeterinarianCreateDTO): Promise<VeterinarianDTO> => {
    setSubmitting(true); setError(null);
    try {
      const data = await apiCreateVeterinarian(payload);
      await load(page);
      return data;
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const update = async (id: number, payload: VeterinarianUpdateDTO): Promise<VeterinarianDTO> => {
    setSubmitting(true); setError(null);
    try {
      const data = await apiUpdateVeterinarian(id, payload);
      await load(page);
      return data;
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const deactivate = async (id: number): Promise<void> => {
    setSubmitting(true); setError(null);
    try {
      await apiDeactivateVeterinarian(id);
      await load(page);
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const fetchOne = async (id: number): Promise<VeterinarianDTO> => {
    return apiFetchVeterinarian(id);
  };

  return { items, total, page, size, loading, submitting, error, setPage, create, update, deactivate, fetchOne };
}
