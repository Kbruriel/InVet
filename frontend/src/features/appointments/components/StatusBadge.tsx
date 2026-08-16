'use client';

/**
 * StatusBadge — Badge de estado con colores semanticos para citas (FE-008).
 */

import React from 'react';

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  pending: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    label: 'Pendiente',
  },
  approved: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    label: 'Aprobada',
  },
  confirmed: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    label: 'Confirmada',
  },
  completed: {
    bg: 'bg-emerald-100',
    text: 'text-emerald-800',
    label: 'Completada',
  },
  no_show: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    label: 'No asistió',
  },
  cancelled: {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    label: 'Cancelada',
  },
  rescheduled: {
    bg: 'bg-purple-100',
    text: 'text-purple-800',
    label: 'Reprogramada',
  },
};

export interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.pending;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text} ${className}`}
      aria-label={`Estado: ${style.label}`}
    >
      {style.label}
    </span>
  );
}
