'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  fetchServices,
  createService as apiCreateService,
  updateService as apiUpdateService,
  deactivateService as apiDeactivateService,
  fetchService as apiFetchService,
  type ServiceDTO,
  type ServiceCreateDTO,
  type ServiceUpdateDTO,
  type ApiError,
} from '@/shared/api/slice-006';

export function useServices(clinicId?: number) {
  const [items, setItems] = useState<ServiceDTO[]>([]);
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
      const data = await fetchServices({ page: p, size, clinic_id: clinicId });
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

  const create = async (payload: ServiceCreateDTO): Promise<ServiceDTO> => {
    setSubmitting(true); setError(null);
    try {
      const data = await apiCreateService(payload);
      await load(page);
      return data;
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const update = async (id: number, payload: ServiceUpdateDTO): Promise<ServiceDTO> => {
    setSubmitting(true); setError(null);
    try {
      const data = await apiUpdateService(id, payload);
      await load(page);
      return data;
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const deactivate = async (id: number): Promise<void> => {
    setSubmitting(true); setError(null);
    try {
      await apiDeactivateService(id);
      await load(page);
    } catch (err) { setError(err as ApiError); throw err; }
    finally { setSubmitting(false); }
  };

  const fetchOne = async (id: number): Promise<ServiceDTO> => {
    return apiFetchService(id);
  };

  return { items, total, page, size, loading, submitting, error, setPage, create, update, deactivate, fetchOne };
}
