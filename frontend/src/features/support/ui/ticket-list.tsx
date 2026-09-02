'use client';

import { useCallback, useEffect, useState } from 'react';
import { supportApi, SupportTicketListItem } from '@/shared/api/support';
import { Button } from '@/shared/ui/components/Button';

interface TicketListProps {
  onTicketClick: (ticketId: number) => void;
}

const PAGE_SIZE = 10;

export function TicketList({ onTicketClick }: TicketListProps) {
  const [tickets, setTickets] = useState<SupportTicketListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await supportApi.listTickets({ page, page_size: PAGE_SIZE });
      setTickets(response.items);
      setTotal(response.meta.total);
    } catch (err) {
      setError('Error al cargar los tickets. Por favor, inténtelo de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    void loadTickets();
  }, [loadTickets]);

  const handlePageChange = (newPage: number) => {
    const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (newPage >= 1 && newPage <= lastPage) {
      setPage(newPage);
    }
  };

  if (loading && tickets.length === 0) {
    return <div role="status" aria-label="Cargando tickets" className="py-8" />;
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

  if (tickets.length === 0) {
    return <p className="text-center py-8 text-gray-500">No hay tickets para mostrar</p>;
  }

  return (
    <div className="space-y-4">
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
                  {ticket.category_name && <p className="text-sm text-gray-500">{ticket.category_name}</p>}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{ticket.status}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(ticket.created_at).toLocaleDateString('es-MX')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {total > PAGE_SIZE && (
        <div className="flex justify-end space-x-2">
          <Button variant="outline" size="sm" onClick={() => handlePageChange(page - 1)} disabled={page === 1}>
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
      )}
    </div>
  );
}
