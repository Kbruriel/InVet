import { render, screen } from '@testing-library/react';
import { ServiceList } from './service-list';
import * as useServicesHook from '@/features/slice-006/hooks/use-services';

jest.mock('@/features/slice-006/hooks/use-services');

const mockUseServices = useServicesHook.useServices as jest.MockedFunction<typeof useServicesHook.useServices>;

describe('ServiceList', () => {
  it('shows empty state when no services', () => {
    mockUseServices.mockReturnValue({
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
    render(<ServiceList />);
    expect(screen.getByText(/no hay servicios/i)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUseServices.mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      size: 20,
      loading: true,
      error: null,
      submitting: false,
      setPage: jest.fn(),
      deactivate: jest.fn(),
      create: jest.fn().mockResolvedValue({}),
      update: jest.fn().mockResolvedValue({}),
      fetchOne: jest.fn().mockResolvedValue({}),
    });
    render(<ServiceList />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows services in list', () => {
    mockUseServices.mockReturnValue({
      items: [
        { id: 1, name: 'Consulta', price: 500, duration_minutes: 30, is_active: true } as unknown as import('@/shared/api/slice-006').ServiceDTO,
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
    render(<ServiceList />);
    const results = screen.getAllByText('Consulta');
    expect(results.length).toBeGreaterThan(0);
  });
});
