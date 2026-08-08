'use client';

import { useState, useEffect } from 'react';

interface PublicSearchBarProps {
  onSearch?: (query: string) => void;
}

export function PublicSearchBar({ onSearch }: PublicSearchBarProps) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    onSearch?.(debouncedQuery);
  }, [debouncedQuery, onSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Debounced query already synced via useEffect
  };

  return (
    <form
      onSubmit={handleSubmit}
      role="search"
      aria-label="Buscar clinicas veterinarias"
      className="flex w-full flex-col gap-3 sm:flex-row"
    >
      <div className="flex-1">
        <label htmlFor="public-search" className="sr-only">
          Buscar clinica
        </label>
        <input
          id="public-search"
          type="search"
          placeholder="Buscar por nombre, ciudad o servicio..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-full border border-sandy-300 bg-white px-6 py-4 text-sm shadow-sm transition-colors focus:border-teal focus:outline-none focus:ring-2 focus:ring-teal"
          aria-label="Buscar clinica por nombre, ciudad o servicio"
        />
      </div>
      <button
        type="submit"
        className="rounded-full bg-teal px-8 py-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
      >
        Buscar
      </button>
    </form>
  );
}
