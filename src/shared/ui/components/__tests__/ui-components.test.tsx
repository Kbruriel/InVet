import { describe, it, expect } from 'vitest';
import { SearchBar } from '@/shared/ui/components/SearchBar';
import { CategoryChips } from '@/shared/ui/components/CategoryChips';
import { ClinicCard } from '@/shared/ui/components/ClinicCard';
import { LoadingSkeleton } from '@/shared/ui/components/LoadingSkeleton';
import { ErrorMessage } from '@/shared/ui/components/ErrorMessage';
import { EmptyState } from '@/shared/ui/components/EmptyState';

// Simple test to check that all components can be imported
describe('UI Components', () => {
  it('should import all UI components successfully', () => {
    expect(SearchBar).toBeDefined();
    expect(CategoryChips).toBeDefined();
    expect(ClinicCard).toBeDefined();
    expect(LoadingSkeleton).toBeDefined();
    expect(ErrorMessage).toBeDefined();
    expect(EmptyState).toBeDefined();
  });
});