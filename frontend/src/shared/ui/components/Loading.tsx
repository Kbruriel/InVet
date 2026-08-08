'use client';

import React from 'react';

export interface LoadingSpinnerProps {
  label?: string;
}

export function LoadingSpinner({ label = 'Cargando...' }: LoadingSpinnerProps) {
  return (
    <section className="py-16" role="status" aria-label={label}>
      <div className="flex items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-teal/30 border-t-teal" />
        <span className="sr-only">{label}</span>
      </div>
    </section>
  );
}
