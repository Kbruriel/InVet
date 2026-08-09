'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  fetchInternalUsers,
  createInternalUser as apiCreateInternalUser,
  updateInternalUser as apiUpdateInternalUser,
  deactivateInternalUser as apiDeactivateInternalUser,
  fetchInternalUser as apiFetchInternalUser,
  type InternalUserDTO,
  type InternalUserCreateDTO,
  type InternalUserUpdateDTO,
  type ApiError,
} from '@/shared/api/slice-006';

export function useInternalUsers(clinicId?: number) {
  const [items, setItems] = useState<InternalUserDTO[]>([]);
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
      const data = await fetchInternalUsers({ page: p, size, clinic_id: clinicId });
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

  const create = async (payload: InternalUserCreateDTO): Promise<InternalUserDTO> => {
    setSubmitting(true); setError(null);
    try {
      const data = await apiCreateInternalUser(payload);
      await load(page);
      return data;
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const update = async (id: number, payload: InternalUserUpdateDTO): Promise<InternalUserDTO> => {
    setSubmitting(true); setError(null);
    try {
      const data = await apiUpdateInternalUser(id, payload);
      await load(page);
      return data;
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const deactivate = async (id: number): Promise<void> => {
    setSubmitting(true); setError(null);
    try {
      await apiDeactivateInternalUser(id);
      await load(page);
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const fetchOne = async (id: number): Promise<InternalUserDTO> => {
    return apiFetchInternalUser(id);
  };

  return { items, total, page, size, loading, submitting, error, setPage, create, update, deactivate, fetchOne };
}
