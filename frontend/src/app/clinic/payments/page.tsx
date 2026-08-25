'use client';

import { Suspense, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PaymentForm } from './PaymentForm';
import type { Payment } from '@/shared/api/payment';
import { Button } from '@/shared/ui/components';

function formatMoney(cents: number): string {
  return (cents / 100).toLocaleString('es-MX', {
    style: 'currency',
    currency: 'MXN',
  });
}

interface PaymentReceiptProps {
  payment: Payment;
}

function PaymentReceipt({ payment }: PaymentReceiptProps) {
  const router = useRouter();
  const isCash = payment.method === 'cash';

  return (
    <div className="space-y-6">
      <section className="space-y-4 rounded-[32px] border border-emerald-200 bg-emerald-50 p-6">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-700">
            Pago registrado
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-emerald-900">
            Recibo #{payment.id}
          </h1>
        </div>

        <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <ReceiptRow label="Método de pago">
            {isCash ? 'Efectivo' : payment.method}
          </ReceiptRow>
          <ReceiptRow label="Importe cobrado">{formatMoney(payment.amount)}</ReceiptRow>
          <ReceiptRow label="Cita asociada">#{payment.appointment_id}</ReceiptRow>
          <ReceiptRow label="Servicio cobrado">#{payment.service_id}</ReceiptRow>
          {payment.amount_received !== null && payment.amount_received !== undefined ? (
            <ReceiptRow label="Importe recibido">
              {formatMoney(payment.amount_received)}
            </ReceiptRow>
          ) : null}
          {isCash && payment.change_amount !== null && payment.change_amount !== undefined ? (
            <ReceiptRow label="Cambio">{formatMoney(payment.change_amount)}</ReceiptRow>
          ) : null}
          <ReceiptRow label="Fecha y hora">
            {new Date(payment.paid_at).toLocaleString('es-MX')}
          </ReceiptRow>
        </dl>

        <p className="rounded-2xl bg-white/80 px-4 py-3 text-xs leading-relaxed text-emerald-800">
          Este comprobante es un recibo interno de la clínica. No constituye factura ni
          comprobante fiscal.
        </p>
      </section>

      <div className="flex flex-wrap gap-3">
        <Button type="button" onClick={() => router.push('/clinic/appointments')}>
          Volver a citas
        </Button>
        <Button type="button" variant="outline" onClick={() => router.push('/portal/owner')}>
          Volver al portal
        </Button>
      </div>
    </div>
  );
}

function ReceiptRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-2xl bg-white/60 px-4 py-3">
      <dt className="text-emerald-900">{label}</dt>
      <dd className="text-right font-semibold text-emerald-950">{children}</dd>
    </div>
  );
}

function PaymentsPage() {
  const [payment, setPayment] = useState<Payment | null>(null);

  if (payment !== null) {
    return <PaymentReceipt payment={payment} />;
  }

  return (
    <div className="space-y-6">
      <section className="space-y-3 rounded-[32px] border border-sandy-300 bg-sandy-100 p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-teal-dark">
          Cobro operacion
        </p>
        <h1 className="text-3xl font-semibold text-slate-900">Registrar pago</h1>
        <p className="max-w-2xl text-sm leading-relaxed text-slate-600">
          Carga el importe, metodo e importe recibido para registrar la cobranza de
          una cita. El pago se asocia a la clinica del usuario autenticado.
        </p>
      </section>

      <PaymentForm onCreated={setPayment} />
    </div>
  );
}

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="py-16">
          <p className="animate-pulse text-center text-sm text-slate-500">
            Cargando el formulario de pagos...
          </p>
        </div>
      }
    >
      <PaymentsPage />
    </Suspense>
  );
}
