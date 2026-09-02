'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  ListTicketsFilters,
  supportApi,
  SupportTicketListItem,
  TICKET_STATUSES,
  TicketStatus,
} from '@/shared/api/support';
import { Button } from '@/shared/ui/components/Button';

interface TicketListProps {
  onTicketClick: (ticketId: number) => void;
}

const PAGE_SIZE = 10;

export function TicketListFiltered({ onTicketClick }: TicketListProps) {
  const [tickets, setTickets] = useState<SupportTicketListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<TicketStatus | ''>('');

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const filters: ListTicketsFilters = {
        page,
        page_size: PAGE_SIZE,
        ...(statusFilter ? { status: statusFilter } : {}),
      };
      const response = await supportApi.listTickets(filters);
      setTickets(response.items);
      setTotal(response.meta.total);
    } catch (err) {
      setError('Error al cargar los tickets. Por favor, inténtelo de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    void loadTickets();
  }, [loadTickets]);

  const handlePageChange = (newPage: number) => {
    const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (newPage >= 1 && newPage <= lastPage) {
      setPage(newPage);
    }
  };

  const handleFilterChange = (value: string) => {
    setStatusFilter(value as TicketStatus | '');
    setPage(1);
  };

  if (loading && tickets.length === 0) {
    return (
      <div className="flex justify-center items-center py-8" role="status" aria-label="Cargando tickets">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4 mb-4" role="alert">
        <p className="text-sm text-red-700">{error}</p>
        <Button onClick={() => void loadTickets()} variant="outline" className="mt-2">
          Reintentar
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="ticket-status-filter" className="block text-sm font-medium text-gray-700 mb-1">
          Filtrar por estado
        </label>
        <select
          id="ticket-status-filter"
          value={statusFilter}
          onChange={(event) => handleFilterChange(event.target.value)}
          className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">Todos los estados</option>
          {TICKET_STATUSES.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </div>

      {tickets.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No hay tickets para mostrar</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Título
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Estado
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Fecha
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tickets.map((ticket) => (
                <tr
                  key={ticket.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onTicketClick(ticket.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{ticket.title}</div>
                    {ticket.category_name && (
                      <p className="text-sm text-gray-500">{ticket.category_name}</p>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                      {ticket.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(ticket.created_at).toLocaleDateString('es-MX')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total > PAGE_SIZE && (
        <div className="flex justify-between items-center mt-4">
          <p className="text-sm text-gray-700">
            Página {page} de {Math.ceil(total / PAGE_SIZE)} · {total} tickets
          </p>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(page + 1)}
              disabled={page * PAGE_SIZE >= total}
            >
              Siguiente
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
