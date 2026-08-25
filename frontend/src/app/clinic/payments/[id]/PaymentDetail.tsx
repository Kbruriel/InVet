'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { cancelPayment, getPayment } from '@/shared/api/payment';
import type { Payment } from '@/shared/api/payment';
import { Button } from '@/shared/ui/components';
import { ErrorBanner } from '@/shared/ui/components/ErrorBanner';
import { LoadingSpinner } from '@/shared/ui/components/Loading';

const METHOD_LABELS: Record<string, string> = {
  cash: 'Efectivo',
  transfer: 'Transferencia',
  card: 'Tarjeta',
  other: 'Otro',
};

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

type LoadState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; payment: Payment };

export function PaymentDetail() {
  const router = useRouter();
  const params = useParams() as { id: string };
  const paymentId = Number(params.id);
  const [state, setState] = useState<LoadState>({ status: 'loading' });
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);
  const [justCancelled, setJustCancelled] = useState(false);

  const load = useCallback(async () => {
    setState({ status: 'loading' });
    try {
      const payment = await getPayment(paymentId);
      setState({ status: 'ready', payment });
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'status' in err && (err as { status?: number }).status === 404) {
        setState({ status: 'error', message: 'El pago no existe o no pertenece a tu clínica.' });
      } else if (
        err &&
        typeof err === 'object' &&
        'status' in err &&
        (err as { status?: number }).status === 403
      ) {
        setState({ status: 'error', message: 'No tienes permiso para ver este pago.' });
      } else {
        const detail =
          err && typeof err === 'object' && 'detail' in err && typeof (err as { detail?: unknown }).detail === 'string'
            ? (err as { detail: string }).detail
            : 'No fue posible cargar el pago. Intenta de nuevo.';
        setState({ status: 'error', message: detail });
      }
    }
  }, [paymentId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleCancel = () => {
    const confirmed = window.confirm(
      '¿Cancelar este pago? Esta acción no se puede deshacer y el recibo quedará marcado como cancelado.',
    );
    if (!confirmed) return;
    setCancelling(true);
    setCancelError(null);
    cancelPayment(paymentId)
      .then((payment) => {
        setState({ status: 'ready', payment });
        setJustCancelled(true);
      })
      .catch((err: unknown) => {
        const detail =
          err && typeof err === 'object' && 'detail' in err && typeof (err as { detail?: unknown }).detail === 'string'
            ? (err as { detail: string }).detail
            : 'No fue posible cancelar el pago. Intenta de nuevo.';
        setCancelError(detail);
      })
      .finally(() => {
        setCancelling(false);
      });
  };

  if (state.status === 'loading') {
    return <LoadingSpinner label="Cargando pago" />;
  }

  if (state.status === 'error') {
    return (
      <div className="space-y-6">
        <ErrorBanner message={state.message} actionLabel="Reintentar" onRetry={load} />
        <Button type="button" variant="outline" onClick={() => router.push('/clinic/payments/history')}>
          Volver al histórico
        </Button>
      </div>
    );
  }

  const { payment } = state;
  const isPaid = payment.status === 'paid';
  const isCash = payment.method === 'cash';
  const showCashDetail =
    isCash && payment.amount_received !== null && payment.amount_received !== undefined;

  return (
    <div className="space-y-6">
      {justCancelled ? (
        <div role="status" className="rounded-[24px] border border-emerald-200 bg-emerald-50 px-5 py-4">
          <p className="text-sm font-semibold text-emerald-800">
            Pago cancelado correctamente. El recibo permanece visible como histórico.
          </p>
        </div>
      ) : null}

      <section
        aria-label={`Recibo ${payment.id}`}
        className={`rounded-[32px] border p-6 ${
          isPaid ? 'border-sandy-300 bg-white' : 'border-slate-200 bg-slate-50'
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Recibo</p>
            <h1 className="text-3xl font-semibold text-slate-900">#{payment.id}</h1>
          </div>
          <span
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              isPaid ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-600'
            }`}
            aria-live="polite"
          >
            {isPaid ? 'Pagado' : 'Cancelado'}
          </span>
        </div>

        <dl className="mt-6 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <DetailRow label="Cita">#{payment.appointment_id}</DetailRow>
          <DetailRow label="Servicio">#{payment.service_id}</DetailRow>
          <DetailRow label="Método de pago">{METHOD_LABELS[payment.method] ?? payment.method}</DetailRow>
          <DetailRow label="Importe cobrado">{formatMoney(payment.amount)}</DetailRow>
          {showCashDetail ? <DetailRow label="Importe recibido">{formatMoney(payment.amount_received as number)}</DetailRow> : null}
          {showCashDetail && payment.change_amount !== null && payment.change_amount !== undefined ? (
            <DetailRow label="Entregado de cambio">{formatMoney(payment.change_amount)}</DetailRow>
          ) : null}
          <DetailRow label="Fecha del pago">{formatDate(payment.paid_at)}</DetailRow>
          {payment.cancelled_at ? (
            <DetailRow label="Fecha de cancelación">{formatDate(payment.cancelled_at)}</DetailRow>
          ) : null}
        </dl>

        <p className="mt-6 rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-relaxed text-slate-600">
          Este documento es un recibo interno de la clínica. No constituye factura ni
          comprobante fiscal.
        </p>
      </section>

      {isPaid ? (
        <div className="space-y-3">
          {cancelError ? (
            <p role="alert" className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {cancelError}
            </p>
          ) : null}
          <div className="flex flex-wrap gap-3">
            <Button type="button" variant="outline" onClick={() => router.push('/clinic/payments/history')}>
              Volver al histórico
            </Button>
            <button
              type="button"
              onClick={handleCancel}
              disabled={cancelling}
              aria-busy={cancelling || undefined}
              className="inline-flex items-center justify-center rounded-full border-2 border-red-300 px-6 py-3 text-sm font-semibold text-red-700 transition-colors hover:bg-red-50 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-300 focus:ring-offset-2"
            >
              {cancelling ? 'Cancelando...' : 'Cancelar pago'}
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap gap-3">
          <Button type="button" onClick={() => router.push('/clinic/payments')}>
            Registrar nuevo pago
          </Button>
          <Button type="button" variant="outline" onClick={() => router.push('/clinic/payments/history')}>
            Volver al histórico
          </Button>
        </div>
      )}
    </div>
  );
}

function DetailRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-2xl border border-slate-100 bg-white px-4 py-3">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right font-semibold text-slate-900">{children}</dd>
    </div>
  );
}
