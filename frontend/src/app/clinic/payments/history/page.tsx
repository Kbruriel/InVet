'use client';

import { PaymentList } from './PaymentList';
import { Button } from '@/shared/ui/components';
import { useRouter } from 'next/navigation';

export default function PaymentsHistoryPage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <section className="space-y-3 rounded-[32px] border border-sandy-300 bg-sandy-100 p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-teal-dark">Histórico</p>
        <h1 className="text-3xl font-semibold text-slate-900">Pagos por periodo</h1>
        <p className="max-w-2xl text-sm leading-relaxed text-slate-600">
          Consulta la cobranza registrada de la clínica. Filtra por rango de fechas y
          abre el detalle de cada recibo.
        </p>
        <Button type="button" variant="outline" onClick={() => router.push('/clinic/payments')}>
          Registrar pago
        </Button>
      </section>

      <PaymentList />
    </div>
  );
}
