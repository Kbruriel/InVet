'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/shared/ui/components/Button';
import { LoadingSpinner as Loading } from '@/shared/ui/components/Loading';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';
import { EmptyState } from '@/shared/ui/components/EmptyState';
import { ClinicForm } from './ClinicForm';
import {
  fetchClinics,
  createClinic,
  updateClinic,
  changeClinicStatus,
  type ClinicRead,
  type ApiError,
  type ClinicCreatePayload,
  type ClinicUpdatePayload,
} from '@/shared/api/clinic-admin-client';

export function ClinicPanel(): JSX.Element {
  const [clinics, setClinics] = useState<ClinicRead[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingClinic, setEditingClinic] = useState<ClinicRead | null>(null);

  const loadClinics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchClinics({ page, size: 20 });
      setClinics(data.items);
      setTotal(data.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    loadClinics();
  }, [loadClinics]);

  const handleSubmitForm = async (payload: ClinicCreatePayload | ClinicUpdatePayload) => {
    setSubmitting(true);
    setError(null);
    try {
      if (editingClinic) {
        await updateClinic(editingClinic.id, payload as ClinicUpdatePayload);
        setShowForm(false);
        setEditingClinic(null);
      } else {
        await createClinic(payload as ClinicCreatePayload);
        setShowForm(false);
      }
      await loadClinics();
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (clinicId: number, active: boolean) => {
    setSubmitting(true);
    setError(null);
    try {
      await changeClinicStatus(clinicId, { active });
      await loadClinics();
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (clinic: ClinicRead) => {
    setEditingClinic(clinic);
    setShowForm(true);
  };

  const totalPages = Math.max(1, Math.ceil(total / 20));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loading label="Cargando clinicas..." />
      </div>
    );
  }

  if (error && !showForm) {
    return (
      <ErrorBanner
        message={error.detail}
        onRetry={() => loadClinics()}
      />
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#0a2540]">Administracion de Clinicas</h1>
          <p className="text-sm text-gray-500 mt-1">
            Gestiona las clinicas registradas en el sistema.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            setEditingClinic(null);
            setShowForm(true);
          }}
          disabled={submitting}
        >
          + Nueva Clinica
        </Button>
      </div>

      {/* Formulario */}
      {showForm && (
        <div className="mb-8">
          <ClinicForm
            initialData={editingClinic ?? undefined}
            onSubmit={handleSubmitForm}
            onCancel={() => {
              setShowForm(false);
              setEditingClinic(null);
            }}
            submitting={submitting}
          />
        </div>
      )}

      {/* Lista */}
      {clinics.length === 0 && !showForm ? (
        <EmptyState
          title="No hay clinicas registradas"
          description="Comienza registrando tu primera clinica."
          actionLabel="Registrar Clinica"
          onAction={() => setShowForm(true)}
        />
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-[#faf3e8]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Nombre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider hidden sm:table-cell">
                    Ciudad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider hidden md:table-cell">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {clinics.map((clinic) => (
                  <tr key={clinic.id} className="hover:bg-[#fff8f0] transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-[#0a2540]">
                      {clinic.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 hidden sm:table-cell">
                      {clinic.city}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 hidden md:table-cell">
                      {clinic.state}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          clinic.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {clinic.is_active ? 'Activa' : 'Inactiva'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right text-sm space-x-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(clinic)}
                        disabled={submitting}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() =>
                          handleStatusChange(clinic.id, !clinic.is_active)
                        }
                        disabled={submitting}
                      >
                        {clinic.is_active ? 'Inactivar' : 'Reactivar'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginacion */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-gray-500">
                Mostrando {((page - 1) * 20) + 1} a{' '}
                {Math.min(page * 20, total)} de {total} clinicas
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1 || submitting}
                >
                  Anterior
                </Button>
                <span className="flex items-center px-3 py-1 text-sm text-gray-600">
                  {page} / {totalPages}
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages || submitting}
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Error global */}
      {error && showForm && (
        <div className="mt-4">
          <ErrorBanner message={error.detail} onRetry={() => setError(null)} />
        </div>
      )}
    </div>
  );
}
