'use client';

import React from 'react';

export interface EmptyStateProps {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <section className="py-16" aria-label="Estado vacío">
      <div className="mx-auto max-w-xl text-center">
        <p className="text-lg font-semibold text-slate-700">{title}</p>
        {description && (
          <p className="mt-2 text-sm text-slate-500">{description}</p>
        )}
        {onAction && actionLabel && (
          <button
            type="button"
            onClick={onAction}
            className="mt-6 inline-flex items-center justify-center rounded-full bg-teal px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </section>
  );
}
