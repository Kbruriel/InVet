'use client';

import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  href?: string;
  onClick?: () => void;
}

export function Card({ children, className = '', href, onClick }: CardProps) {
  const baseClasses =
    'bg-white rounded-2xl shadow-sm border border-sandy-300 overflow-hidden transition-shadow hover:shadow-md';

  if (href) {
    return (
      <a
        href={href}
        className={`${baseClasses} ${className}`}
        aria-label={typeof children === 'string' ? children : undefined}
      >
        {children}
      </a>
    );
  }

  if (onClick) {
    return (
      <button
        type="button"
        className={`${baseClasses} ${className} cursor-pointer text-left`}
        onClick={onClick}
      >
        {children}
      </button>
    );
  }

  return <div className={`${baseClasses} ${className}`}>{children}</div>;
}
