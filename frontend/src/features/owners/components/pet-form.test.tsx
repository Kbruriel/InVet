import { fireEvent, render, screen } from '@testing-library/react';
import { PetForm } from './pet-form';

describe('PetForm', () => {
  it('shows validation errors and does not submit invalid data', async () => {
    const handleSubmit = jest.fn().mockResolvedValue(undefined);

    const { container } = render(<PetForm onSubmit={handleSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText('Nombre *'), { target: { value: '   ' } });
    fireEvent.change(screen.getByLabelText('Raza *'), { target: { value: '   ' } });
    fireEvent.change(screen.getByLabelText('Edad (años) *'), { target: { value: '-2' } });
    fireEvent.submit(container.querySelector('form') as HTMLFormElement);

    expect(await screen.findByText('El nombre es requerido')).toBeInTheDocument();
    expect(screen.getByText('La raza es requerida')).toBeInTheDocument();
    expect(screen.getByText('La edad debe estar entre 0 y 50 años')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('submits sanitized form data when valid', async () => {
    const handleSubmit = jest.fn().mockResolvedValue(undefined);

    render(<PetForm onSubmit={handleSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText('Nombre *'), { target: { value: '  Luna ' } });
    fireEvent.change(screen.getByLabelText('Especie *'), { target: { value: 'gato' } });
    fireEvent.change(screen.getByLabelText('Raza *'), { target: { value: '  Siamés ' } });
    fireEvent.change(screen.getByLabelText('Edad (años) *'), { target: { value: '3' } });
    fireEvent.change(screen.getByLabelText('Peso (kg)'), { target: { value: '4.2' } });
    fireEvent.click(screen.getByRole('button', { name: 'Registrar' }));

    expect(handleSubmit).toHaveBeenCalledWith({
      nombre: 'Luna',
      especie: 'gato',
      raza: 'Siamés',
      edad: 3,
      peso: 4.2,
      fecha_nacimiento: undefined,
    });
  });
});