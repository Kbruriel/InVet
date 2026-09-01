'use client';

import { useState, useEffect } from 'react';
import { supportApi, SupportTicket, ListTicketsFilters } from '@/shared/api/support';
import { Button } from '@/shared/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select';

interface TicketListProps {
  onTicketClick: (ticketId: string) => void;
}

export function TicketListFiltered({ onTicketClick }: TicketListProps) {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadTickets();
  }, [page, statusFilter]);

  const loadTickets = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const filters: ListTicketsFilters = {
        page,
        page_size: pageSize,
        ...(statusFilter && { status: statusFilter })
      };

      const response = await supportApi.listTickets(filters);
      setTickets(response.items);
      setTotal(response.total);
    } catch (err) {
      setError('Error al cargar los tickets. Por favor, inténtelo de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= Math.ceil(total / pageSize)) {
      setPage(newPage);
    }
  };

  const handleFilterChange = (value: string) => {
    setStatusFilter(value);
    setPage(1); // Reset to first page when changing filter
  };

  if (loading && tickets.length === 0) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4 mb-4">
        <p className="text-sm text-red-700">{error}</p>
        <Button 
          onClick={loadTickets} 
          variant="outline" 
          className="mt-2"
        >
          Reintentar
        </Button>
      </div>
    );
  }

  if (tickets.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No hay tickets para mostrar</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Controls */}
      <div className="flex flex-wrap gap-4 items-center mb-4">
        <div>
          <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
            Filtrar por estado
          </label>
          <Select value={statusFilter} onValueChange={handleFilterChange}>
            <SelectTrigger id="status-filter" className="w-[180px]">
              <SelectValue placeholder="Seleccionar estado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todos</SelectItem>
              <SelectItem value="initiated">Iniciado</SelectItem>
              <SelectItem value="pending">Pendiente</SelectItem>
              <SelectItem value="process">Proceso</SelectItem>
              <SelectItem value="completed">Completado</SelectItem>
              <SelectItem value="closed">Cerrado</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Título
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
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
                  {ticket.description && (
                    <p className="text-sm text-gray-500 line-clamp-1">{ticket.description}</p>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${ticket.status === 'initiated' ? 'bg-blue-100 text-blue-800' : ''}
                    ${ticket.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : ''}
                    ${ticket.status === 'process' ? 'bg-purple-100 text-purple-800' : ''}
                    ${ticket.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                    ${ticket.status === 'closed' ? 'bg-gray-100 text-gray-800' : ''}`}>
                    {ticket.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(ticket.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex justify-between items-center mt-4">
          <p className="text-sm text-gray-700">
            Mostrando {Math.min(pageSize, total)} de {total} tickets
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
              disabled={page * pageSize >= total}
            >
              Siguiente
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}