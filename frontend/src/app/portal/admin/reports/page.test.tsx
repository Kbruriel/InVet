import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import ReportsPage from './page';
import { useReports } from '@/features/reports/hooks/useReports';
import type { ReportState } from '@/features/reports/hooks/useReports';

// ---------------------------------------------------------------------------
// Isolar la página como composición pura: mockeamos el hook de estado.
// ---------------------------------------------------------------------------
const mockApply = jest.fn();
const mockGoToPage = jest.fn();
const mockRetry = jest.fn();

function state(partial: Partial<ReportState>): ReportState {
  return {
    reportType: null,
    filters: {},
    page: 1,
    size: 20,
    total: 0,
    pages: 1,
    hasMore: false,
    isEmpty: false,
    loading: false,
    error: null,
    data: null,
    ...partial,
  };
}

jest.mock('@/features/reports/hooks/useReports', () => ({
  useReports: jest.fn(() => ({
    ...state({}),
    apply: mockApply,
    goToPage: mockGoToPage,
    retry: mockRetry,
  })),
}));

// ---------------------------------------------------------------------------
// Requerimientos de `RequireAuth` (auth + router).
// ---------------------------------------------------------------------------
jest.mock('@/shared/auth/session', () => ({
  isAuthenticated: jest.fn(() => true),
}));

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
  })),
}));

describe('/portal/admin/reports (FE-015-T05)', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useReports as unknown as jest.Mock).mockReset();
    (useReports as unknown as jest.Mock).mockReturnValue({
      ...state({}),
      apply: mockApply,
      goToPage: mockGoToPage,
      retry: mockRetry,
    });
  });

  it('renders the page header', () => {
    render(<ReportsPage />);
    expect(
      screen.getByRole('heading', { name: /reportes operativos/i }),
    ).toBeInTheDocument();
  });

  it('shows the placeholder CTA when no report type has been applied', () => {
    render(<ReportsPage />);
    expect(
      screen.getByText(/Selecciona un tipo de reporte y aplica los filtros/i),
    ).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('renders the appointments table with rows after applying', async () => {
    (useReports as unknown as jest.Mock).mockReturnValue({
      ...state({
        reportType: 'appointments',
        loading: false,
        total: 1,
        pages: 1,
        isEmpty: false,
        data: {
          items: [
            {
              id: 1,
              clinic_id: 1,
              pet_name: 'Firulais',
              owner_name: 'Ana',
              veterinarian_name: 'Dr. Lasso',
              appointment_type: 'consulta',
              status: 'confirmda',
              scheduled_start: '2026-01-01T10:00:00Z',
              scheduled_end: '2026-01-01T10:30:00Z',
            },
          ],
          total: 1,
          page: 1,
          size: 20,
        },
      }),
      apply: mockApply,
      goToPage: mockGoToPage,
      retry: mockRetry,
    });

    render(<ReportsPage />);

    expect(await screen.findByRole('cell', { name: 'Firulais' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: 'Dr. Lasso' })).toBeInTheDocument();
  });

  it('invokes apply with type + filters when the filter form is submitted', async () => {
    render(<ReportsPage />);

    const form = document.querySelector('form[role="search"]') as HTMLFormElement;
    act(() => {
      fireEvent.submit(form);
    });

    await waitFor(() => {
      expect(mockApply).toHaveBeenCalledTimes(1);
    });
    expect(mockApply).toHaveBeenCalledWith(
      'appointments',
      expect.objectContaining({ period_start: undefined, period_end: undefined }),
    );
  });

  it('renders an error banner with a working retry action', () => {
    (useReports as unknown as jest.Mock).mockReturnValue({
      ...state({
        reportType: 'payments',
        loading: false,
        error: 'Error de red: no se pudo cargar el reporte.',
      }),
      apply: mockApply,
      goToPage: mockGoToPage,
      retry: mockRetry,
    });

    render(<ReportsPage />);

    expect(
      screen.getByRole('alert'),
    ).toHaveTextContent(/Error de red:/i);
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }));
    expect(mockRetry).toHaveBeenCalledTimes(1);
  });

  it('renders the empty message when a report has no data', () => {
    (useReports as unknown as jest.Mock).mockReturnValue({
      ...state({
        reportType: 'consultations',
        loading: false,
        total: 0,
        pages: 1,
        isEmpty: true,
        data: { items: [], total: 0, page: 1, size: 20 },
      }),
      apply: mockApply,
      goToPage: mockGoToPage,
      retry: mockRetry,
    });

    render(<ReportsPage />);

    expect(screen.getByText(/Aún no hay datos para el periodo aplicado/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /aplicar/i })).toBeInTheDocument();
  });

  it('renders pagination controls when pages > 1 and navigates', async () => {
    const rows = Array.from({ length: 5 }, (_, i) => ({
      id: i + 1,
      clinic_id: 1,
      pet_name: `Pet ${i}`,
      owner_name: 'Dueño',
      veterinarian_name: 'Vet',
      appointment_type: 'consulta',
      status: 'ok',
      scheduled_start: '2026-01-01T10:00:00Z',
      scheduled_end: '2026-01-01T10:30:00Z',
    }));
    (useReports as unknown as jest.Mock).mockReturnValue({
      ...state({
        reportType: 'appointments',
        loading: false,
        total: 60,
        pages: 3,
        page: 2,
        isEmpty: false,
        data: { items: rows, total: 60, page: 2, size: 20 },
      }),
      apply: mockApply,
      goToPage: mockGoToPage,
      retry: mockRetry,
    });

    render(<ReportsPage />);

    const next = screen.getByRole('button', { name: /siguiente/i });
    fireEvent.click(next);
    expect(mockGoToPage).toHaveBeenCalledWith(3);

    fireEvent.click(screen.getByRole('button', { name: /anterior/i }));
    expect(mockGoToPage).toHaveBeenLastCalledWith(1);
  });
});
