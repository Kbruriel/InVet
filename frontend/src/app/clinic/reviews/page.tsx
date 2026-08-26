'use client';

import { ReviewStaffList } from '@/features/reviews/ReviewStaffList';

export default function ClinicReviewsPage() {
  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Reseñas de la clínica</h1>
        <p className="mt-1 text-sm text-gray-500">
          Consulta las reseñas de tus clientes y responde las que aún no tienen respuesta.
        </p>
      </div>
      <ReviewStaffList />
    </div>
  );
}
