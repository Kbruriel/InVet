'use client';

import React from 'react';
import Link from 'next/link';

interface AdminLayoutProps {
  children: React.ReactNode;
  title: string;
}

const navItems = [
  { href: '/admin/services', label: 'Servicios' },
  { href: '/admin/veterinarians', label: 'Veterinarios' },
  { href: '/admin/internal-users', label: 'Usuarios internos' },
] as const;

export function AdminLayout({ children, title }: AdminLayoutProps): JSX.Element {
  return (
    <div className="min-h-screen bg-[#fff8f0]">
      {/* Header */}
      <header className="border-b border-sandy-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <h1 className="text-xl font-bold text-[#0a2540]">{title}</h1>
            <nav className="hidden sm:flex gap-4" aria-label="Navegación admin">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full px-4 py-2 text-sm font-medium text-[#0a2540] transition-colors hover:bg-teal/10 focus:outline-none focus:ring-2 focus:ring-teal"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Mobile nav */}
      <nav className="sm:hidden border-b border-sandy-200 bg-white px-4 py-2 flex gap-2 overflow-x-auto" aria-label="Navegación admin móvil">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium text-[#0a2540] transition-colors hover:bg-teal/10"
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
