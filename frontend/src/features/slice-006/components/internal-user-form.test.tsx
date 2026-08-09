import { render, screen, fireEvent } from '@testing-library/react';
import { InternalUserForm } from './internal-user-form';

const mockOnSubmit = jest.fn();
const mockOnCancel = jest.fn();

describe('InternalUserForm', () => {
  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  it('renders form fields', () => {
    render(<InternalUserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    expect(screen.getByLabelText(/user_id/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/nombre/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/rol/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    render(<InternalUserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.click(screen.getByText(/crear usuario interno/i));
    expect(await screen.findByText(/el user_id es obligatorio/i)).toBeInTheDocument();
    expect(await screen.findByText(/el nombre es obligatorio/i)).toBeInTheDocument();
  });

  it('calls onSubmit with valid data', async () => {
    render(<InternalUserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);
    fireEvent.change(screen.getByLabelText(/user_id/i), { target: { value: '1' } });
    fireEvent.change(screen.getByLabelText(/nombre/i), { target: { value: 'Maria Garcia' } });
    fireEvent.click(screen.getByText(/crear usuario interno/i));
    expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
      user_id: 1,
      nombre: 'Maria Garcia',
      rol: 'admin',
    }));
  });
});
