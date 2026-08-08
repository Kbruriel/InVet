'use client';

import { useSearchParams } from 'next/navigation';

export function ClinicsSearchParams() {
  const searchParams = useSearchParams();
  return (
    <>
      <span className="hidden" data-page={Number(searchParams.get('page')) || 1} />
      <span className="hidden" data-search={searchParams.get('search') || ''} />
      <span className="hidden" data-category={searchParams.get('category') || ''} />
    </>
  );
}
