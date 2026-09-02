'use client';

import { useState } from 'react';

import { Button } from '@/shared/ui/components/Button';
import {
  supportApi,
  type SupportTicket,
  type TicketStatus,
} from '@/shared/api/support';

const STATUS_TRANSITIONS: Record<TicketStatus, readonly TicketStatus[]> = {
  iniciado: ['pendiente', 'proceso'],
  pendiente: ['proceso'],
  proceso: ['completado', 'cerrado'],
  completado: [],
  cerrado: [],
};

const STATUS_LABELS: Record<TicketStatus, string> = {
  iniciado: 'Iniciado',
  pendiente: 'Pendiente',
  proceso: 'En proceso',
  completado: 'Completado',
  cerrado: 'Cerrado',
};

interface TicketStatusUpdaterProps {
  ticket: SupportTicket;
  onStatusUpdated: () => void | Promise<void>;
}

export function TicketStatusUpdater({
  ticket,
  onStatusUpdated,
}: TicketStatusUpdaterProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const availableStatuses = STATUS_TRANSITIONS[ticket.status];

  async function updateStatus(newStatus: TicketStatus) {
    if (!availableStatuses.includes(newStatus)) {
      return;
    }

    setIsUpdating(true);
    setError(null);

    try {
      await supportApi.updateTicketStatus(ticket.id, { new_status: newStatus });
      await onStatusUpdated();
    } catch {
      setError('No fue posible actualizar el estado del ticket.');
    } finally {
      setIsUpdating(false);
    }
  }

  if (availableStatuses.length === 0) {
    return null;
  }

  return (
    <section aria-labelledby="ticket-status-actions">
      <h2 id="ticket-status-actions" className="text-lg font-semibold">
        Cambiar estado
      </h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {availableStatuses.map((status) => (
          <Button
            key={status}
            type="button"
            disabled={isUpdating}
            onClick={() => void updateStatus(status)}
          >
            {STATUS_LABELS[status]}
          </Button>
        ))}
      </div>
      {error ? (
        <p className="mt-3 text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}
