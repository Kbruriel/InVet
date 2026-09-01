import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TicketForm } from './ticket-form';

const mockCategories = [
  { id: '1', clinic_id: 'clinic-1', name: 'Técnico', active: true },
  { id: '2', clinic_id: 'clinic-1', name: 'Facturación', active: true }
];

describe('TicketForm', () => {
  const onSubmitSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form with all fields', () => {
    render(<TicketForm categories={mockCategories} onSubmitSuccess={onSubmitSuccess} />);
    
    expect(screen.getByLabelText(/título/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/descripción/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/categoría/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /crear ticket/i })).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const createTicketMock = jest.fn().mockResolvedValue({});
    
    // Mock the supportApi module
    jest.mock('@/shared/api/support', () => ({
      ...jest.requireActual('@/shared/api/support'),
      supportApi: {
        createTicket: createTicketMock
      }
    }));

    render(<TicketForm categories={mockCategories} onSubmitSuccess={onSubmitSuccess} />);
    
    fireEvent.change(screen.getByLabelText(/título/i), { target: { value: 'Test ticket' } });
    fireEvent.change(screen.getByLabelText(/descripción/i), { target: { value: 'Test description' } });
    
    fireEvent.click(screen.getByRole('button', { name: /crear ticket/i }));

    await waitFor(() => {
      expect(createTicketMock).toHaveBeenCalledWith({
        title: 'Test ticket',
        description: 'Test description'
      });
    });
  });

  it('shows error message on submission failure', async () => {
    const createTicketMock = jest.fn().mockRejectedValue(new Error('Failed'));
    
    // Mock the supportApi module
    jest.mock('@/shared/api/support', () => ({
      ...jest.requireActual('@/shared/api/support'),
      supportApi: {
        createTicket: createTicketMock
      }
    }));

    render(<TicketForm categories={mockCategories} onSubmitSuccess={onSubmitSuccess} />);
    
    fireEvent.change(screen.getByLabelText(/título/i), { target: { value: 'Test ticket' } });
    
    fireEvent.click(screen.getByRole('button', { name: /crear ticket/i }));

    await waitFor(() => {
      expect(screen.getByText(/error al crear el ticket/i)).toBeInTheDocument();
    });
  });
});