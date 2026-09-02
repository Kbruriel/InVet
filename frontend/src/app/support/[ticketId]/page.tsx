'use client';

import { useCallback, useEffect, useState } from 'react';

import { supportApi, type SupportTicket } from '@/shared/api/support';
import type { ApiError } from '@/shared/api/client';

import { TicketStatusBadge } from './ticket-status-badge';
import { TicketStatusUpdater } from './ticket-status-updater';

interface SupportTicketPageProps {
  params: { ticketId: string };
}

export default function SupportTicketPage({ params }: SupportTicketPageProps) {
  const [ticket, setTicket] = useState<SupportTicket | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const ticketId = Number(params.ticketId);

  const loadTicket = useCallback(async () => {
    if (!Number.isInteger(ticketId) || ticketId <= 0) {
      setError('El identificador del ticket no es válido.');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      setTicket(await supportApi.getTicket(ticketId));
    } catch (requestError) {
      const apiError = requestError as Partial<ApiError>;
      if (apiError.status === 404) {
        setError('El ticket solicitado no existe.');
      } else {
        setError('No fue posible cargar el ticket.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    void loadTicket();
  }, [loadTicket]);

  if (isLoading) {
    return <p className="p-6">Cargando ticket…</p>;
  }

  if (error || !ticket) {
    return (
      <main className="p-6">
        <p role="alert" className="text-red-600">
          {error ?? 'No fue posible cargar el ticket.'}
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-500">Ticket #{ticket.id}</p>
          <TicketStatusBadge status={ticket.status} />
        </div>
        <h1 className="text-3xl font-bold">{ticket.title}</h1>
      </header>

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <dl className="grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-slate-500">Categoría</dt>
            <dd>{ticket.category?.name ?? 'Sin categoría'}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-slate-500">Creado</dt>
            <dd>{new Date(ticket.created_at).toLocaleString('es-MX')}</dd>
          </div>
        </dl>
        <div className="mt-5">
          <h2 className="text-sm font-medium text-slate-500">Descripción</h2>
          <p className="mt-1 whitespace-pre-wrap">
            {ticket.description ?? 'Sin descripción'}
          </p>
        </div>
      </section>

      <TicketStatusUpdater ticket={ticket} onStatusUpdated={loadTicket} />
    </main>
  );
}
