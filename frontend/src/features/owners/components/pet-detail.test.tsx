import { render, screen, waitFor } from '@testing-library/react';
import { PetDetail } from './pet-detail';
import { usePets } from '../hooks/use-pets';

jest.mock('../hooks/use-pets', () => ({
  usePets: jest.fn(),
}));

describe('PetDetail', () => {
  it('shows empty history when the pet has no prior consultations', async () => {
    const fetchPetById = jest.fn().mockResolvedValue({
      id: 12,
      owner_id: 7,
      nombre: 'Milo',
      especie: 'perro',
      raza: 'Mestizo',
      edad: 4,
      peso: 12,
      fecha_nacimiento: '2022-04-02',
    });
    const fetchPetHistory = jest.fn().mockResolvedValue({ items: [] });

    (usePets as jest.Mock).mockReturnValue({
      editPet: jest.fn(),
      fetchPetById,
      fetchPetHistory,
    });

    render(<PetDetail petId={12} onBack={jest.fn()} />);

    expect(screen.getByLabelText('Cargando detalle de la mascota')).toBeInTheDocument();

    await waitFor(() => expect(fetchPetById).toHaveBeenCalledWith(12));
    expect(fetchPetHistory).toHaveBeenCalledWith(12);
    expect(await screen.findByText('Milo')).toBeInTheDocument();
    expect(screen.getByText('Aún no hay consultas registradas')).toBeInTheDocument();
  });
});