/**
 * Pruebas unitarias para OwnerProfileForm
 */

'use client';

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { OwnerProfileForm } from '../components/owner-profile-form';
import { useOwnerProfile } from '../hooks/use-owner-profile';

// Mock the hook
jest.mock('../hooks/use-owner-profile', () => ({
  useOwnerProfile: jest.fn(),
}));

describe('OwnerProfileForm', () => {
  const mockFetchOwner = jest.fn();
  const mockUpdateProfile = jest.fn();
  const mockOnSuccess = jest.fn();
  const ownerFixture = {
    id: 1,
    user_id: 9,
    nombre: 'Juan Pérez',
    email: 'juan@ejemplo.com',
    telefono: null,
    direccion: null,
    fecha_creacion: '2026-08-10T00:00:00Z',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    (useOwnerProfile as jest.Mock).mockReturnValue({
      owner: ownerFixture,
      loading: false,
      error: null,
      fetchOwner: mockFetchOwner,
      updateProfile: mockUpdateProfile,
    });
  });

  test('renders form with all fields', () => {
    render(<OwnerProfileForm onSuccess={mockOnSuccess} />);
    
    expect(screen.getByLabelText(/nombre completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/correo electrónico/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/teléfono/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/dirección/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /guardar perfil/i })).toBeInTheDocument();
  });

  test('shows loading state when fetching', () => {
    (useOwnerProfile as jest.Mock).mockReturnValue({
      owner: null,
      loading: true,
      error: null,
      fetchOwner: mockFetchOwner,
      updateProfile: mockUpdateProfile,
    });

    render(<OwnerProfileForm onSuccess={mockOnSuccess} />);
    
    expect(screen.getByText(/cargando perfil/i)).toBeInTheDocument();
  });

  test('submits form successfully', async () => {
    mockUpdateProfile.mockResolvedValue({ id: 1, nombre: 'Juan Pérez' });

    render(<OwnerProfileForm onSuccess={mockOnSuccess} />);
    
    const nombreInput = screen.getByLabelText(/nombre completo/i);
    const emailInput = screen.getByLabelText(/correo electrónico/i);
    const submitButton = screen.getByRole('button', { name: /guardar perfil/i });

    fireEvent.change(nombreInput, { target: { value: 'Juan Pérez' } });
    fireEvent.change(emailInput, { target: { value: 'juan@ejemplo.com' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockUpdateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          nombre: 'Juan Pérez',
          email: 'juan@ejemplo.com',
        })
      );
    });
  });

  test('shows error message on failure', async () => {
    (useOwnerProfile as jest.Mock).mockReturnValue({
      owner: ownerFixture,
      loading: false,
      error: 'Error de conexión',
      fetchOwner: mockFetchOwner,
      updateProfile: mockUpdateProfile,
    });

    render(<OwnerProfileForm onSuccess={mockOnSuccess} />);

    await waitFor(() => {
      expect(screen.getByText('Error de conexión')).toBeInTheDocument();
    });
  });
});
