'use client';

import { useState, useEffect } from 'react';
import { supportApi, SupportTicket } from '@/shared/api/support';
import { Button } from '@/shared/ui/button';
import { useRouter } from 'next/navigation';
import { TicketStatusBadge } from './ticket-status-badge';
import { TicketStatusUpdater } from './ticket-status-updater';

interface PageProps {
  params: {
    ticketId: string;
  };
}

export default function TicketDetailPage({ params }: PageProps) {
  const [ticket, setTicket] = useState<SupportTicket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchTicket = async () => {
      if (!params.ticketId) {
        setError('ID de ticket inválido');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        const response = await supportApi.getTicket(params.ticketId);
        setTicket(response);
      } catch (err: any) {
        if (err.status === 404) {
          // No se revela información al usuario sobre el ticket
          setError('Ticket no encontrado');
        } else {
          setError('Error al cargar el ticket. Por favor, inténtelo de nuevo.');
          console.error(err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTicket();
  }, [params.ticketId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <div className="rounded-md bg-red-50 p-4 mb-6">
          <p className="text-sm text-red-700">{error}</p>
          <Button 
            onClick={() => router.push('/support')} 
            variant="outline" 
            className="mt-2"
          >
            Volver a la lista de tickets
          </Button>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <div className="rounded-md bg-red-50 p-4 mb-6">
          <p className="text-sm text-red-700">No se pudo cargar el ticket.</p>
          <Button 
            onClick={() => router.push('/support')} 
            variant="outline" 
            className="mt-2"
          >
            Volver a la lista de tickets
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="mb-6">
        <Button 
          onClick={() => router.push('/support')} 
          variant="outline" 
          size="sm"
          className="mb-4"
        >
          ← Volver a la lista
        </Button>
          <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{ticket.title}</h1>
            <div className="flex items-center space-x-2">
              <TicketStatusBadge status={ticket.status} />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-medium text-gray-900">Detalles del ticket</h2>
        </div>
        <div className="p-6">
          <dl className="space-y-4">
            <div className="flex">
              <dt className="text-sm font-medium text-gray-500 w-32">Fecha de creación:</dt>
              <dd className="text-sm text-gray-900">{new Date(ticket.created_at).toLocaleString()}</dd>
            </div>
            {ticket.category_id && (
              <div className="flex">
                <dt className="text-sm font-medium text-gray-500 w-32">Categoría:</dt>
                <dd className="text-sm text-gray-900">{ticket.category_id}</dd>
              </div>
            )}
            {ticket.description && (
              <div className="flex">
                <dt className="text-sm font-medium text-gray-500 w-32">Descripción:</dt>
                <dd className="text-sm text-gray-900">{ticket.description}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Add Status Updater Component */}
      <TicketStatusUpdater ticket={ticket} onStatusChange={() => window.location.reload()} />

      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-medium text-gray-900">Historial de estado</h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-gray-600">Para historial completo del cambio de estado, consulte con soporte.</p>
        </div>
      </div>
    </div>
  );
}