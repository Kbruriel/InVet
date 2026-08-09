import { render, screen, fireEvent } from '@testing-library/react';
import { VeterinarianForm } from './veterinarian-form';

const mockOnSubmit = jest.fn();
const mockOnCancel = jest.fn();

describe('VeterinarianForm', () => {
  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  it('renders form fields', () => {
    render(<VeterinarianForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    expect(screen.getByLabelText(/nombre completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/licencia profesional/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/especialidad/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    render(<VeterinarianForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.click(screen.getByText(/crear veterinario/i));
    expect(await screen.findByText(/el nombre completo es obligatorio/i)).toBeInTheDocument();
    expect(await screen.findByText(/la licencia profesional es obligatoria/i)).toBeInTheDocument();
  });

  it('calls onSubmit with valid data', async () => {
    render(<VeterinarianForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.change(screen.getByLabelText(/nombre completo/i), { target: { value: 'Dr. Juan Perez' } });
    fireEvent.change(screen.getByLabelText(/licencia profesional/i), { target: { value: '12345' } });
    fireEvent.change(screen.getByLabelText(/especialidad/i), { target: { value: 'Cirugia' } });
    fireEvent.click(screen.getByText(/crear veterinario/i));
    expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
      nombre_completo: 'Dr. Juan Perez',
      licencia_profesional: '12345',
      especialidad: 'Cirugia',
    }));
  });
});
