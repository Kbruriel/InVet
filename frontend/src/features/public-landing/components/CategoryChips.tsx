'use client';

import { useRouter, useSearchParams } from 'next/navigation';

const CATEGORIES = [
  { key: 'veterinaria', label: 'Veterinaria' },
  { key: 'estetica', label: 'Estética' },
  { key: 'urgencias', label: 'Urgencias' },
];

export function CategoryChips() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const activeCategory = searchParams.get('category') || '';

  const handleChipClick = (key: string) => {
    const params = new URLSearchParams(searchParams);
    if (key === activeCategory) {
      params.delete('category');
    } else {
      params.set('category', key);
    }
    router.push(`/clinicas?${params.toString()}`);
  };

  return (
    <>
      {CATEGORIES.map((cat) => {
        const isActive = cat.key === activeCategory;
        return (
          <button
            key={cat.key}
            type="button"
            onClick={() => handleChipClick(cat.key)}
            className={`rounded-full px-5 py-2 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2 ${
              isActive
                ? 'bg-teal text-white shadow-md'
                : 'bg-white text-slate-600 shadow-sm hover:bg-sandy-100'
            }`}
            aria-pressed={isActive}
            aria-label={`Filtrar por ${cat.label}`}
          >
            {cat.label}
          </button>
        );
      })}
    </>
  );
}
