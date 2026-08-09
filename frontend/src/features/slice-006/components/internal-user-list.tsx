'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/shared/ui/components/Button';
import { LoadingSpinner as Loading } from '@/shared/ui/components/Loading';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';
import { EmptyState } from '@/shared/ui/components/EmptyState';
import { useInternalUsers } from '@/features/slice-006/hooks/use-internal-users';
import type { ApiError } from '@/shared/api/slice-006';

export function InternalUserList(): JSX.Element {
  const { items, total, page, size, loading, error, submitting, setPage, deactivate } = useInternalUsers();

  const totalPages = Math.ceil(total / size);

  const handleDeactivate = async (id: number) => {
    if (!confirm('¿Está seguro de desactivar este usuario interno?')) return;
    try {
      await deactivate(id);
    } catch (err) {
      const apiErr = err as ApiError;
      alert(apiErr.detail || 'Error al desactivar el usuario interno');
    }
  };

  if (loading) {
    return <Loading label="Cargando usuarios internos..." />;
  }

  if (error?.status === 401) {
    return <ErrorBanner message="Sesión expirada. Inicia sesión nuevamente." actionLabel="Ir al login" onRetry={() => window.location.href = '/login'} />;
  }

  if (error?.status === 403) {
    return <ErrorBanner message="No tienes permiso para ver esta sección." />;
  }

  if (error) {
    return <ErrorBanner message={error.detail || 'Error al cargar los usuarios internos.'} onRetry={() => window.location.reload()} />;
  }

  if (items.length === 0) {
    return (
      <EmptyState
        title="No hay usuarios internos"
        description="Comienza agregando tu primer usuario interno."
        actionLabel="Crear usuario interno"
        onAction={() => (window.location.href = '/admin/internal-users/create')}
      />
    );
  }

  return (
    <section aria-label="Listado de usuarios internos">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h2 className="text-lg font-semibold text-[#0a2540]">Usuarios internos ({total})</h2>
        <Button variant="primary" onClick={() => (window.location.href = '/admin/internal-users/create')}>
          Nuevo usuario interno
        </Button>
      </div>

      {/* Desktop table */}
      <div className="hidden md:block overflow-x-auto rounded-xl border border-sandy-200 bg-white">
        <table className="w-full text-sm">
          <thead className="border-b border-sandy-200 bg-[#faf3e8]">
            <tr>
              <th className="px-6 py-3 text-left font-medium text-slate-600">Nombre</th>
              <th className="px-6 py-3 text-left font-medium text-slate-600">user_id</th>
              <th className="px-6 py-3 text-left font-medium text-slate-600">Rol</th>
              <th className="px-6 py-3 text-left font-medium text-slate-600 hidden lg:table-cell">Sucursales</th>
              <th className="px-6 py-3 text-left font-medium text-slate-600">Estado</th>
              <th className="px-6 py-3 text-right font-medium text-slate-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((user) => (
              <tr key={user.id} className="border-b border-sandy-100 hover:bg-[#faf3e8]/50">
                <td className="px-6 py-4 font-medium text-[#0a2540]">{user.nombre}</td>
                <td className="px-6 py-4 text-slate-600">{user.user_id}</td>
                <td className="px-6 py-4 text-slate-600">{user.rol}</td>
                <td className="px-6 py-4 text-slate-600 hidden lg:table-cell">
                  {user.branch_ids.length > 0 ? user.branch_ids.join(', ') : '—'}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'
                  }`}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    <Link
                      href={`/admin/internal-users/${user.id}/edit`}
                      className="rounded-full border-2 border-teal px-3 py-1.5 text-xs font-semibold text-teal hover:bg-teal/10"
                    >
                      Editar
                    </Link>
                    {!submitting && (
                      <button
                        type="button"
                        onClick={() => handleDeactivate(user.id)}
                        className="rounded-full border-2 border-red-300 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50"
                      >
                        Desactivar
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="md:hidden space-y-4">
        {items.map((user) => (
          <div key={user.id} className="rounded-xl border border-sandy-200 bg-white p-4 space-y-3">
            <div>
              <p className="font-semibold text-[#0a2540]">{user.nombre}</p>
              <p className="text-sm text-slate-600">user_id: {user.user_id} · Rol: {user.rol}</p>
              {user.branch_ids.length > 0 && (
                <p className="text-xs text-slate-500">Sucursales: {user.branch_ids.join(', ')}</p>
              )}
              <span className={`mt-1 inline-block rounded-full px-3 py-1 text-xs font-semibold ${
                user.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'
              }`}>
                {user.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
            <div className="flex gap-2">
              <Link
                href={`/admin/internal-users/${user.id}/edit`}
                className="rounded-full border-2 border-teal px-4 py-2 text-xs font-semibold text-teal hover:bg-teal/10"
              >
                Editar
              </Link>
              {!submitting && (
                <button
                  type="button"
                  onClick={() => handleDeactivate(user.id)}
                  className="rounded-full border-2 border-red-300 px-4 py-2 text-xs font-semibold text-red-600 hover:bg-red-50"
                >
                  Desactivar
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Anterior</Button>
          <span className="text-sm text-slate-600">Página {page} de {totalPages}</span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Siguiente</Button>
        </div>
      )}
    </section>
  );
}
