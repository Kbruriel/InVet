'use client';

import { SupportTicket } from '@/shared/api/support';

interface TicketStatusBadgeProps {
  status: SupportTicket['status'];
}

export function TicketStatusBadge({ status }: TicketStatusBadgeProps) {
  const statusClasses = {
    initiated: 'bg-blue-100 text-blue-800',
    pending: 'bg-yellow-100 text-yellow-800',
    process: 'bg-purple-100 text-purple-800',
    completed: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800'
  };

  return (
    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClasses[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  );
}