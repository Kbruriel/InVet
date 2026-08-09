/** Pruebas de componente ClinicForm (FE-005) */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ClinicForm } from './ClinicForm';

describe('ClinicForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('muestra campos obligatorios con asterisco', () => {
    render(<ClinicForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);

    expect(screen.getByLabelText(/Nombre/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Direccion/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Ciudad/i)).toBeInTheDocument();
  });

  it('muestra errores de validacion cuando campos estan vacios', async () => {
    render(<ClinicForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);

    fireEvent.click(screen.getByText('Crear Clinica'));

    await waitFor(() => {
      expect(screen.getByText('El nombre es obligatorio.')).toBeInTheDocument();
      expect(screen.getByText('La direccion es obligatoria.')).toBeInTheDocument();
    });
  });

  it('llama onSubmit con datos validos', async () => {
    render(<ClinicForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);

    fireEvent.change(screen.getByLabelText(/Nombre/i), { target: { value: 'Clinica Test' } });
    fireEvent.change(screen.getByLabelText(/Direccion/i), { target: { value: 'Calle 123' } });
    fireEvent.change(screen.getByLabelText(/Ciudad/i), { target: { value: 'Ciudad' } });
    fireEvent.change(screen.getByLabelText(/Estado/i), { target: { value: 'Estado' } });
    fireEvent.change(screen.getByLabelText(/Pais/i), { target: { value: 'Mexico' } });
    fireEvent.change(screen.getByLabelText(/Codigo Postal/i), { target: { value: '12345' } });

    fireEvent.click(screen.getByText('Crear Clinica'));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });
  });

  it('llama onCancel al presionar cancelar', () => {
    render(<ClinicForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);

    fireEvent.click(screen.getByText('Cancelar'));

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('muestra datos iniciales cuando se proporciona initialData', () => {
    const initialData = {
      id: 1,
      name: 'Clinica Existente',
      description: 'Desc existente',
      address: 'Calle Vieja',
      city: 'Ciudad Vieja',
      state: 'Estado Viejo',
      country: 'Mexico Viejo',
      postal_code: '99999',
      phone: '555-9999',
      email: 'old@clinic.com',
      is_active: true,
    };

    render(
      <ClinicForm
        initialData={initialData}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        submitting={false}
      />
    );

    expect(screen.getByLabelText(/Nombre/i)).toHaveValue('Clinica Existente');
    expect(screen.getByLabelText(/Direccion/i)).toHaveValue('Calle Vieja');
    expect(screen.getByText('Editar Clinica')).toBeInTheDocument();
  });

  it('valida formato de email', async () => {
    render(<ClinicForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} submitting={false} />);

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'email-invalido' } });
    fireEvent.change(screen.getByLabelText(/Nombre/i), { target: { value: 'Clinica Test' } });
    fireEvent.change(screen.getByLabelText(/Direccion/i), { target: { value: 'Calle 123' } });
    fireEvent.change(screen.getByLabelText(/Ciudad/i), { target: { value: 'Ciudad' } });
    fireEvent.change(screen.getByLabelText(/Estado/i), { target: { value: 'Estado' } });
    fireEvent.change(screen.getByLabelText(/Pais/i), { target: { value: 'Mexico' } });
    fireEvent.change(screen.getByLabelText(/Codigo Postal/i), { target: { value: '12345' } });

    fireEvent.click(screen.getByText('Crear Clinica'));

    await waitFor(() => {
      expect(screen.getByText('Email invalido.')).toBeInTheDocument();
    });
  });
});
