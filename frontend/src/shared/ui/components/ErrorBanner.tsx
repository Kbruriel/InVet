'use client';

import React from 'react';

export interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
  actionLabel?: string;
}

export function ErrorBanner({ message, onRetry, actionLabel = 'Reintentar' }: ErrorBannerProps) {
  return (
    <section className="py-16" role="alert">
      <div className="mx-auto max-w-xl rounded-xl bg-red-50 p-8 text-center">
        <p className="text-lg font-semibold text-red-700">{message}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 inline-flex items-center justify-center rounded-full bg-teal px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </section>
  );
}
