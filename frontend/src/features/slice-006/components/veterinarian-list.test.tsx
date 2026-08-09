import { render, screen } from '@testing-library/react';
import { VeterinarianList } from './veterinarian-list';
import * as useVetHook from '@/features/slice-006/hooks/use-veterinarians';

jest.mock('@/features/slice-006/hooks/use-veterinarians');

const mockUseVeterinarians = useVetHook.useVeterinarians as jest.MockedFunction<typeof useVetHook.useVeterinarians>;

describe('VeterinarianList', () => {
  it('shows empty state when no veterinarians', () => {
    mockUseVeterinarians.mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      size: 20,
      loading: false,
      error: null,
      submitting: false,
      setPage: jest.fn(),
      deactivate: jest.fn(),
      create: jest.fn().mockResolvedValue({}),
      update: jest.fn().mockResolvedValue({}),
      fetchOne: jest.fn().mockResolvedValue({}),
    });
    render(<VeterinarianList />);
    expect(screen.getByText(/no hay veterinarios/i)).toBeInTheDocument();
  });

  it('shows veterinarians in list', () => {
    mockUseVeterinarians.mockReturnValue({
      items: [
        { id: 1, nombre_completo: 'Dr. Juan', licencia_profesional: '123', especialidad: 'Cirugia', is_active: true } as unknown as import('@/shared/api/slice-006').VeterinarianDTO,
      ],
      total: 1,
      page: 1,
      size: 20,
      loading: false,
      error: null,
      submitting: false,
      setPage: jest.fn(),
      deactivate: jest.fn(),
      create: jest.fn().mockResolvedValue({}),
      update: jest.fn().mockResolvedValue({}),
      fetchOne: jest.fn().mockResolvedValue({}),
    });
    render(<VeterinarianList />);
    const results = screen.getAllByText('Dr. Juan');
    expect(results.length).toBeGreaterThan(0);
  });
});
