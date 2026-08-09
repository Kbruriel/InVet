import { render, screen, fireEvent } from '@testing-library/react';
import { ServiceForm } from './service-form';

const mockOnSubmit = jest.fn();
const mockOnCancel = jest.fn();

describe('ServiceForm', () => {
  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  it('renders form fields', () => {
    render(<ServiceForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    expect(screen.getByLabelText(/nombre del servicio/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/precio/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/duración/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    render(<ServiceForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.click(screen.getByText(/crear servicio/i));
    expect(await screen.findByText(/el nombre es obligatorio/i)).toBeInTheDocument();
    expect(await screen.findByText(/el precio debe ser un valor positivo/i)).toBeInTheDocument();
  });

  it('calls onSubmit with valid data', async () => {
    render(<ServiceForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.change(screen.getByLabelText(/nombre del servicio/i), { target: { value: 'Consulta general' } });
    fireEvent.change(screen.getByLabelText(/precio/i), { target: { value: '500' } });
    fireEvent.change(screen.getByLabelText(/duración/i), { target: { value: '30' } });
    fireEvent.click(screen.getByText(/crear servicio/i));
    expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
      name: 'Consulta general',
      price: 500,
      duration_minutes: 30,
    }));
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(<ServiceForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.click(screen.getByText(/cancelar/i));
    expect(mockOnCancel).toHaveBeenCalled();
  });
});
