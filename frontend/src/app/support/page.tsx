'use client';

import { useCallback, useEffect, useState } from 'react';

import {
  supportApi,
  type SupportCategory,
} from '@/shared/api/support';
import { TicketForm } from '@/features/support/ui/ticket-form';
import { TicketListFiltered } from '@/features/support/ui/ticket-list-filtered';

export default function SupportPage() {
  const [categories, setCategories] = useState<SupportCategory[]>([]);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);
  const [listVersion, setListVersion] = useState(0);

  const loadCategories = useCallback(async () => {
    setCategoriesError(null);
    try {
      setCategories(await supportApi.getCategories());
    } catch {
      setCategoriesError('No fue posible cargar las categorías.');
    }
  }, []);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  return (
    <main className="mx-auto max-w-5xl space-y-8 p-6">
      <header>
        <h1 className="text-3xl font-bold">Soporte</h1>
        <p className="mt-2 text-slate-600">
          Crea una solicitud y consulta el avance de tus tickets.
        </p>
      </header>

      {categoriesError ? (
        <p role="alert" className="text-red-600">
          {categoriesError}
        </p>
      ) : null}

      <section aria-labelledby="new-ticket-heading">
        <h2 id="new-ticket-heading" className="mb-4 text-xl font-semibold">
          Nuevo ticket
        </h2>
        <TicketForm
          categories={categories}
          onSubmitSuccess={() => setListVersion((current) => current + 1)}
        />
      </section>

      <section aria-labelledby="ticket-list-heading">
        <h2 id="ticket-list-heading" className="mb-4 text-xl font-semibold">
          Mis tickets
        </h2>
        <TicketListFiltered
          key={listVersion}
          onTicketClick={(ticketId) => {
            window.location.href = `/support/${ticketId}`;
          }}
        />
      </section>
    </main>
  );
}
