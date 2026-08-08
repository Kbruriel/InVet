'use client';

import { Suspense } from 'react';
import { CategoryChips } from './CategoryChips';

export function CategoryChipsWrapper() {
  return (
    <Suspense fallback={null}>
      <CategoryChips />
    </Suspense>
  );
}
