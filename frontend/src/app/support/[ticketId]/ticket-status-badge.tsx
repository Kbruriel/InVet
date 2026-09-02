import type { TicketStatus } from '@/shared/api/support';

const STATUS_STYLES: Record<TicketStatus, string> = {
  iniciado: 'bg-blue-100 text-blue-800',
  pendiente: 'bg-amber-100 text-amber-800',
  proceso: 'bg-violet-100 text-violet-800',
  completado: 'bg-emerald-100 text-emerald-800',
  cerrado: 'bg-slate-200 text-slate-700',
};

const STATUS_LABELS: Record<TicketStatus, string> = {
  iniciado: 'Iniciado',
  pendiente: 'Pendiente',
  proceso: 'En proceso',
  completado: 'Completado',
  cerrado: 'Cerrado',
};

export function TicketStatusBadge({ status }: { status: TicketStatus }) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
