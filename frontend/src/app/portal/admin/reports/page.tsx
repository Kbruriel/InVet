/**
 * Página principal /portal/admin/reports (FE-015-T05 / BE-015).
 *
 * Composición:
 * - `RequireAuth` garantiza sesión activa (redirect `/login` si no hay).
 * - `FilterBar` expone selector tipo + fechas + botón "Aplicar" con validación.
 * - `useReports` orquesta peticiones + estados (loading/error/total/page/size).
 * - `ReportTable` renderiza el dataset según `reportType` y soporta paginación.
 * - Estados UX: loading → spinner; error → banner con reintentar (ya en
 *   ReportTable cuando `error` no es nulo); empty → mensaje; éxito → tabla + paginación.
 */

'use client';

import { useCallback } from 'react';
import { RequireAuth } from '@/shared/auth/RequireAuth';
import { FilterBar } from '@/features/reports/components/FilterBar';
import { ReportTable } from '@/features/reports/components/ReportTable';
import { getReportColumns } from '@/features/reports/report-columns';
import { useReports } from '@/features/reports/hooks/useReports';
import type { ReportType, ReportFilters } from '@/features/reports/api';

function ReportsPageContent() {
  const {
    reportType,
    page,
    pages,
    total,
    isEmpty,
    loading,
    error,
    data,
    apply,
    goToPage,
    retry,
  } = useReports();

  const columnSet = reportType ? getReportColumns(reportType) : null;
  const rows: Record<string, unknown>[] = columnSet?.getRows(data) ?? [];

  const handleApply = useCallback(
    (type: ReportType, next: ReportFilters) => {
      apply(type, {
        period_start: next.period_start,
        period_end: next.period_end,
      });
    },
    [apply],
  );

  const handlePageChange = useCallback(
    (nextPage: number) => {
      goToPage(Math.max(1, Math.min(pages, nextPage)));
    },
    [goToPage, pages],
  );

  return (
    <div className="py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Reportes operativos</h1>
        <p className="mt-2 text-sm text-slate-500">
          Consulta citas, servicios, consultas, calificaciones y pagos de tu clínica.
        </p>
      </header>

      <div className="mb-6">
        <FilterBar onApply={handleApply} loading={loading} />
      </div>

      {reportType && columnSet ? (
        <ReportTable
          title={columnSet.title}
          columns={columnSet.columns}
          rows={rows}
          rowKey={(row) =>
            row.id != null ? String(row.id) :
            row.clinic_id != null ? String(row.clinic_id) :
            row._synthetic != null ? String(row._synthetic) :
            `${reportType}-${row.veterinarian_id ?? Math.random()}`
          }
          loading={loading}
          error={error}
          onRetry={retry}
          page={page}
          pages={pages}
          total={total}
          onPageChange={handlePageChange}
          isEmpty={isEmpty}
          emptyTitle={columnSet.title}
          emptyDescription="Aún no hay datos para el periodo aplicado."
        />
      ) : (
        <section className="py-10 rounded-[32px] border border-sandy-300 bg-white text-center">
          <p className="text-base font-medium text-slate-700">
            Selecciona un tipo de reporte y aplica los filtros para ver los datos.
          </p>
          <p className="mt-2 text-sm text-slate-500">
            El tipo por defecto es: Citas médicas.
          </p>
        </section>
      )}
    </div>
  );
}

export default function ReportsPage() {
  return (
    <RequireAuth>
      <ReportsPageContent />
    </RequireAuth>
  );
}
