/** Tests para CategoryChips (FE-003) */

import { render, screen, fireEvent } from '@testing-library/react';
import { CategoryChips } from './CategoryChips';

// Mock next/navigation - must be at module top level
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => new URLSearchParams(),
}));

describe('CategoryChips', () => {
  beforeEach(() => {
    mockPush.mockClear();
  });

  it('deberia renderizar las tres categorias', () => {
    render(<CategoryChips />);
    expect(screen.getByRole('button', { name: /filtrar por veterinaria/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /filtrar por est[ée]tica/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /filtrar por urgencias/i })).toBeInTheDocument();
  });

  it('deberia agregar query param category al hacer click', () => {
    render(<CategoryChips />);
    const chip = screen.getByRole('button', { name: /filtrar por veterinaria/i });
    fireEvent.click(chip);
    expect(mockPush).toHaveBeenCalledWith('/clinicas?category=veterinaria');
  });

  it('deberia aplicar estilo activo al chip seleccionado', () => {
    // Override the mock to return active category
    jest.spyOn(jest.requireActual('next/navigation'), 'useSearchParams').mockReturnValue(
      new URLSearchParams('category=veterinaria')
    );

    render(<CategoryChips />);
    const activeChip = screen.getByRole('button', { name: /filtrar por veterinaria/i });
    expect(activeChip).toHaveClass('bg-teal');
  });
});
