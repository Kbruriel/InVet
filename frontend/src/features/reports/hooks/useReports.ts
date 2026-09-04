/**
 * Hook de estado para reportes operativos (FE-015-T02 / BE-015).
 *
 * Semántica:
 * - No realiza peticiones al montar el componente: la carga ocurre sólo cuando
 *   el usuario aplica filtros (`apply`) o cambia de página / reintenta.
 * - Expone estados: data, total, page, size, pages, loading, error, isEmpty.
 * - Guarda contra condiciones de carrera (races) mediante un contador de request.
 * - Normaliza `total` y `pages` para soportar paginación con cualquier reporte.
 */

'use client';

import { useCallback, useRef, useState } from 'react';
import {
  getPetsCountReport,
  listAppointmentsReport,
  listConsultationsReport,
  listPaymentsReport,
  listRatingsReport,
  listServicesReport,
  type ReportType,
} from '../api';

const PAGE_SIZE = 20;

/** Filtros aplicados a la consulta. */
export interface AppliedFilters {
  period_start?: string | null;
  period_end?: string | null;
}

/** Estado expuesto al componente que consume el hook. */
export interface ReportState {
  /** Tipo de reporte activo (null si aún no se ha aplicado uno). */
  reportType: ReportType | null;
  /** Filtros activos aplicados a la última consulta. */
  filters: AppliedFilters;
  page: number;
  size: number;
  /** Total de registros del reporte. */
  total: number;
  /** Número de páginas (1 en reportes agregados como pets/ratings). */
  pages: number;
  /** true si existe una siguiente página. */
  hasMore: boolean;
  /** true si el reporte no devolvió registros. */
  isEmpty: boolean;
  loading: boolean;
  error: string | null;
  /** Respuesta cruda del endpoint. El tipo exacto depende de `reportType`. */
  data: unknown;
}

function extractError(err: unknown): string {
  if (err && typeof err === 'object') {
    const e = err as { detail?: unknown };
    if (typeof e.detail === 'string' && e.detail.length > 0) {
      return e.detail;
    }
  }
  return 'No fue posible cargar el reporte. Intenta de nuevo.';
}

function normalize(
  type: ReportType,
  response: unknown,
  page: number,
): Pick<ReportState, 'total' | 'pages' | 'hasMore' | 'isEmpty'> {
  const r = response as {
    total?: number;
    size?: number;
    items?: unknown[];
    by_veterinarian?: unknown[];
  };

  let total = 0;
  let pages = 1;
  if (type === 'pets') {
    total = 1;
    pages = 1;
  } else if (type === 'ratings') {
    total = r?.by_veterinarian?.length ?? 0;
    pages = 1;
  } else {
    total = r?.total ?? 0;
    const size = r?.size ?? PAGE_SIZE;
    pages = Math.max(1, Math.ceil(total / size));
  }

  return { total, pages, hasMore: page < pages, isEmpty: total === 0 };
}

const INITIAL: ReportState = {
  reportType: null,
  filters: {},
  page: 1,
  size: PAGE_SIZE,
  total: 0,
  pages: 1,
  hasMore: false,
  isEmpty: false,
  loading: false,
  error: null,
  data: null,
};

export function useReports() {
  const [state, setState] = useState<ReportState>(INITIAL);
  const latestRequest = useRef(0);
  // Persiste el tipo + filtros de la última consulta para navegar/reintentar.
  const activeRef = useRef<{ type: ReportType; filters: AppliedFilters }>({
    type: 'appointments',
    filters: {},
  });

  const runFetch = useCallback(
    async (type: ReportType, filters: AppliedFilters, page: number) => {
      const id = ++latestRequest.current;
      activeRef.current = { type, filters };

      setState((prev) => ({
        ...prev,
        reportType: type,
        filters,
        page,
        loading: true,
        error: null,
      }));

      const query = {
        period_start: filters.period_start,
        period_end: filters.period_end,
        page,
        size: PAGE_SIZE,
      };

      let response: unknown;
      try {
        if (type === 'appointments') response = await listAppointmentsReport(query);
        else if (type === 'services') response = await listServicesReport(query);
        else if (type === 'pets') response = await getPetsCountReport(query);
        else if (type === 'consultations') response = await listConsultationsReport(query);
        else if (type === 'ratings') response = await listRatingsReport(query);
        else response = await listPaymentsReport(query);
      } catch (err) {
        if (id === latestRequest.current) {
          setState((prev) => ({ ...prev, loading: false, error: extractError(err) }));
        }
        return;
      }

      if (id !== latestRequest.current) return;
      const summary = normalize(type, response, page);
      setState((prev) => ({
        ...prev,
        ...summary,
        data: response,
        loading: false,
        error: null,
      }));
    },
    [],
  );

  const apply = useCallback(
    (type: ReportType, filters: AppliedFilters = {}) => {
      runFetch(type, filters, 1);
    },
    [runFetch],
  );

  const goToPage = useCallback(
    (page: number) => {
      const { type, filters } = activeRef.current;
      runFetch(type, filters, page);
    },
    [runFetch],
  );

  const retry = useCallback(() => {
    const { type, filters } = activeRef.current;
    runFetch(type, filters, state.page);
  }, [runFetch, state.page]);

  return { ...state, apply, goToPage, retry };
}
