'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { listPayments } from '@/shared/api/payment';
import type { Payment, PaymentListParams, PaymentPageMeta } from '@/shared/api/payment';
import { Button } from '@/shared/ui/components';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';
import { LoadingSpinner } from '@/shared/ui/components/Loading';

interface PaymentListState {
  items: Payment[];
  meta: PaymentPageMeta | null;
}

function formatMoney(cents: number): string {
  return (cents / 100).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' });
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

const METHOD_LABELS: Record<string, string> = {
  cash: 'Efectivo',
  transfer: 'Transferencia',
  card: 'Tarjeta',
  other: 'Otro',
};

function extractError(err: unknown): string {
  if (err && typeof err === 'object' && 'detail' in err && typeof (err as { detail?: unknown }).detail === 'string') {
    return (err as { detail: string }).detail;
  }
  return 'No fue posible cargar los pagos. Intenta de nuevo.';
}

export function PaymentList() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [data, setData] = useState<PaymentListState>({ items: [], meta: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (targetPage: number) => {
    setLoading(true);
    setError(null);
    try {
      const params: PaymentListParams = {
        page: targetPage,
        page_size: 10,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
      };
      const response = await listPayments(params);
      setData({ items: response.items, meta: response.meta });
      setPage(targetPage);
    } catch (err: unknown) {
      setError(extractError(err));
      setData({ items: [], meta: null });
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate]);

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilter = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    load(1);
  };

  const handleClearFilters = () => {
    setFromDate('');
    setToDate('');
    load(1);
  };

  if (loading) {
    return <LoadingSpinner label="Cargando pagos" />;
  }

  if (error !== null) {
    return (
      <ErrorBanner message={error} actionLabel="Reintentar" onRetry={() => load(page)} />
    );
  }

  const meta = data.meta;

  const hasFilters = Boolean(fromDate || toDate);

  return (
    <section aria-label="Historial de pagos" className="space-y-6">
      <form onSubmit={handleFilter} className="grid gap-4 rounded-[32px] border border-sandy-300 bg-white p-6 sm:grid-cols-2 md:grid-cols-4">
        <div>
          <label htmlFor="from_date" className="mb-1 block text-sm font-medium text-slate-700">
            Desde
          </label>
          <input
            id="from_date"
            name="from_date"
            type="date"
            value={fromDate}
            max={toDate || undefined}
            onChange={(event) => setFromDate(event.target.value)}
            className="w-full rounded-2xl border border-sandy-300 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal"
          />
        </div>
        <div>
          <label htmlFor="to_date" className="mb-1 block text-sm font-medium text-slate-700">
            Hasta
          </label>
          <input
            id="to_date"
            name="to_date"
            type="date"
            value={toDate}
            min={fromDate || undefined}
            onChange={(event) => setToDate(event.target.value)}
            className="w-full rounded-2xl border border-sandy-300 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal"
          />
        </div>
        <div className="flex items-end gap-2 sm:col-span-2">
          <Button type="submit" disabled={loading}>
            Filtrar
          </Button>
          <Button type="button" variant="outline" onClick={handleClearFilters} disabled={loading}>
            Limpiar
          </Button>
        </div>
      </form>

      {data.items.length === 0 ? (
        <div className="rounded-[24px] border border-sandy-200 bg-white p-6 text-center" role="status">
          <p className="text-base font-semibold text-slate-700">No hay pagos en este periodo</p>
          <p className="mt-2 text-sm text-slate-500">
            {hasFilters ? 'Prueba con fechas más amplias o limpia el filtro.' : 'Aun no se han registrado pagos.'}
          </p>
          <div className="mt-4 flex justify-center">
            <Button variant="outline" onClick={() => router.push('/clinic/payments')}>
              Registrar pago
            </Button>
          </div>
        </div>
      ) : (
        <>

      <div className="hidden overflow-x-auto rounded-[32px] border border-sandy-200 bg-white md:block">
        <table className="w-full text-sm">
          <thead className="border-b border-sandy-200 bg-sandy-100">
            <tr>
              <th className="px-5 py-3 text-left font-medium text-slate-600">Fecha</th>
              <th className="px-5 py-3 text-left font-medium text-slate-600">Recibo</th>
              <th className="px-5 py-3 text-left font-medium text-slate-600">Cita</th>
              <th className="px-5 py-3 text-left font-medium text-slate-600">Servicio</th>
              <th className="px-5 py-3 text-right font-medium text-slate-600">Importe</th>
              <th className="px-5 py-3 text-left font-medium text-slate-600">Método</th>
              <th className="px-5 py-3 text-left font-medium text-slate-600">Estado</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((payment) => (
              <tr
                key={payment.id}
                className="cursor-pointer border-b border-sandy-100 last:border-b-0 hover:bg-sandy-100/50"
                onClick={() => router.push(`/clinic/payments/${payment.id}`)}
              >
                <td className="px-5 py-4 text-slate-700">{formatDate(payment.paid_at)}</td>
                <td className="px-5 py-4 font-medium text-slate-900">#{payment.id}</td>
                <td className="px-5 py-4 text-slate-600">#{payment.appointment_id}</td>
                <td className="px-5 py-4 text-slate-600">#{payment.service_id}</td>
                <td className="px-5 py-4 text-right font-semibold text-slate-900">{formatMoney(payment.amount)}</td>
                <td className="px-5 py-4 text-slate-600">{METHOD_LABELS[payment.method] ?? payment.method}</td>
                <td className="px-5 py-4">
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
                      payment.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'
                    }`}
                  >
                    {payment.status === 'paid' ? 'Pagado' : 'Cancelado'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="space-y-4 md:hidden">
        {data.items.map((payment) => (
          <button
            key={payment.id}
            type="button"
            onClick={() => router.push(`/clinic/payments/${payment.id}`)}
            className="w-full space-y-2 rounded-[24px] border border-sandy-200 bg-white p-5 text-left"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-slate-900">Recibo #{payment.id}</p>
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  payment.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'
                }`}
              >
                {payment.status === 'paid' ? 'Pagado' : 'Cancelado'}
              </span>
            </div>
            <p className="text-sm text-slate-600">
              {formatDate(payment.paid_at)} · Cita #{payment.appointment_id} · {METHOD_LABELS[payment.method] ?? payment.method}
            </p>
            <p className="text-base font-semibold text-slate-900">{formatMoney(payment.amount)}</p>
          </button>
        ))}
      </div>

        </>
      )}

      {(meta?.pages ?? 0) > 1 ? (
        <nav aria-label="Paginacion" className="flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => load(page - 1)}
          >
            Anterior
          </Button>
          <span className="text-sm text-slate-600">
            Página {page} de {meta?.pages ?? 1} · {meta?.total ?? 0} pagos
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= (meta?.pages ?? 1)}
            onClick={() => load(page + 1)}
          >
            Siguiente
          </Button>
        </nav>
      ) : (
        <p className="text-center text-xs text-slate-500">
          {data.items.length} pago{data.items.length === 1 ? '' : 's'} en el periodo seleccionado
        </p>
      )}
    </section>
  );
}
