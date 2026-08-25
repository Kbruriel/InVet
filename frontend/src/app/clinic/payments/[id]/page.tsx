'use client';

import { Suspense } from 'react';
import { PaymentDetail } from './PaymentDetail';

export default function PaymentDetailPage() {
  return (
    <Suspense
      fallback={
        <div className="py-16">
          <p className="animate-pulse text-center text-sm text-slate-500">
            Cargando el recibo...
          </p>
        </div>
      }
    >
      <PaymentDetail />
    </Suspense>
  );
}
