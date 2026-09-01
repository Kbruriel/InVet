'use client';

import { useState } from 'react';
import { supportApi, SupportTicket } from '@/shared/api/support';
import { Button } from '@/shared/ui/button';

interface TicketStatusUpdaterProps {
  ticket: SupportTicket;
  onStatusChange?: () => void;
}

export function TicketStatusUpdater({ ticket, onStatusChange }: TicketStatusUpdaterProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Define allowed transitions for each status
  const getAvailableTransitions = () => {
    switch (ticket.status) {
      case 'initiated':
        return ['pending', 'process'];
      case 'pending':
        return ['process', 'completed', 'closed'];
      case 'process':
        return ['completed', 'closed'];
      case 'completed':
        return ['closed'];
      case 'closed':
        return [];
      default:
        return [];
    }
  };

  const availableTransitions = getAvailableTransitions();
  
  const handleStatusChange = async (newStatus: string) => {
    if (!availableTransitions.includes(newStatus)) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await supportApi.updateTicketStatus(ticket.id, { status: newStatus as any });
      onStatusChange?.();
    } catch (err) {
      setError('Error al actualizar el estado del ticket. Por favor, inténtelo de nuevo.');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (availableTransitions.length === 0) {
    return null;
  }

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden mt-6">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-medium text-gray-900">Cambiar estado</h2>
      </div>
      <div className="p-6">
        <p className="text-sm text-gray-600 mb-4">
          Seleccione una transición válida para actualizar el estado del ticket.
        </p>
        
        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {availableTransitions.map((transition) => (
            <Button
              key={transition}
              onClick={() => handleStatusChange(transition)}
              disabled={isSubmitting}
              variant="outline"
              size="sm"
            >
              {transition}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}