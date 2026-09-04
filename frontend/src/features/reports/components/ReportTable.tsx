/**
 * Tabla de reportes genérica + paginación (FE-015-T04 / BE-015).
 *
 * Componente reusable:
 * - Acepta `columns` (definición de cabeceras + render por celda) y `rows`
 *   (array de datos ya paginados).
 * - Estados: `loading` → spinner; `rows.length === 0` → estado vacío;
 *   `error` → mensaje (la página puede mostrar banner con reintentar).
 * - Paginación: controlado por `page`, `pages`, `onPageChange`. No altera
 *   filtros: la navegación delega el refetch a la página (usa `goToPage`).
 */

'use client';

import { Button, LoadingSpinner, EmptyState } from '@/shared/ui/components';

export interface ReportColumn<RowData> {
  /** Clave única (usado como th scope + key). */
  key: string;
  /** Text de cabecera. */
  header: string;
  /** Alineación de la celda. */
  align?: 'left' | 'right' | 'center';
  /** Función de render para la celda. */
  render: (row: RowData) => React.ReactNode;
}

export interface ReportTableProps<RowData extends Record<string, unknown>> {
  columns: Array<ReportColumn<RowData>>;
  rows: RowData[];
  /** Clave de cada fila (para React key). */
  rowKey: (row: RowData) => string | number;
  loading?: boolean;
  error?: string | null;
  /** Acción opcional al pulsar "Reintentar" en el banner de error. */
  onRetry?: () => void;
  title?: string;
  /* Paginación opcional */
  page?: number;
  pages?: number;
  total?: number;
  onPageChange?: (page: number) => void;
  emptyTitle?: string;
  emptyDescription?: string;
  /** true para forzar estado vacío (p. ej. total === 0) */
  isEmpty?: boolean;
}

const ALIGN_CLASSES: Record<string, string> = {
  left: 'text-left',
  right: 'text-right',
  center: 'text-center',
};

export function ReportTable<RowData extends Record<string, unknown>>({
  columns,
  rows,
  rowKey,
  loading = false,
  error = null,
  onRetry,
  title,
  page = 1,
  pages = 1,
  total,
  onPageChange,
  emptyTitle = 'Sin datos',
  emptyDescription = 'No hay registros para los filtros seleccionados.',
  isEmpty,
}: ReportTableProps<RowData>) {
  if (loading) {
    return <LoadingSpinner label={title ? `Cargando ${title}` : 'Cargando'} />;
  }

  if (error) {
    return (
      <div role="alert" className="rounded-[24px] border border-red-200 bg-red-50 p-6">
        <p className="text-base font-semibold text-red-700">{error}</p>
        {onRetry && (
          <div className="mt-4">
            <Button variant="outline" size="sm" onClick={onRetry}>
              Reintentar
            </Button>
          </div>
        )}
      </div>
    );
  }

  const showEmpty = isEmpty ?? rows.length === 0;

  if (showEmpty) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <section aria-label={title ?? 'Tabla de reporte'} className="space-y-4">
      <div className="overflow-x-auto rounded-[32px] border border-sandy-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-sandy-200 bg-sandy-100">
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={`px-5 py-3 font-medium text-slate-600 ${
                    ALIGN_CLASSES[column.align ?? 'left']
                  }`}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={rowKey(row)}
                className="border-b border-sandy-100 last:border-b-0 hover:bg-sandy-100/50"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-5 py-4 text-slate-700 ${
                      ALIGN_CLASSES[column.align ?? 'left']
                    }`}
                  >
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pages > 1 && onPageChange && (
        <nav
          aria-label="Paginación"
          className="flex items-center justify-center gap-3"
        >
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            Anterior
          </Button>
          <span className="text-sm text-slate-600">
            Página {page} de {pages}
            {typeof total === 'number' ? ` · ${total} registros` : ''}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= pages}
            onClick={() => onPageChange(page + 1)}
          >
            Siguiente
          </Button>
        </nav>
      )}
    </section>
  );
}
