/** Pruebas de componente ClinicPanel (FE-005) */

import { render, screen, waitFor } from '@testing-library/react';
import { ClinicPanel } from './ClinicPanel';

// Mock del cliente API
const mockFetch = jest.fn();
global.fetch = mockFetch;

const mockClinics = [
  {
    id: 1,
    name: 'Clinica Test 1',
    description: 'Descripcion 1',
    address: 'Calle 1',
    city: 'Ciudad 1',
    state: 'Estado 1',
    country: 'Mexico',
    postal_code: '12345',
    phone: '555-0001',
    email: 'test1@clinic.com',
    is_active: true,
  },
  {
    id: 2,
    name: 'Clinica Test 2',
    description: null,
    address: 'Calle 2',
    city: 'Ciudad 2',
    state: 'Estado 2',
    country: 'Mexico',
    postal_code: '12346',
    phone: null,
    email: null,
    is_active: false,
  },
];

describe('ClinicPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockReset();
  });

  it('muestra estado de loading al iniciar', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // nunca resuelve

    render(<ClinicPanel />);

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('muestra lista de clinicas cuando la API responde', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: mockClinics,
        total: 2,
        page: 1,
        size: 20,
      }),
    });

    render(<ClinicPanel />);

    await waitFor(() => {
      expect(screen.getByText('Clinica Test 1')).toBeTruthy();
      expect(screen.getByText('Clinica Test 2')).toBeTruthy();
    });
  });

  it('muestra empty state cuando no hay clinicas', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: [],
        total: 0,
        page: 1,
        size: 20,
      }),
    });

    render(<ClinicPanel />);

    await waitFor(() => {
      expect(screen.getByText('No hay clinicas registradas')).toBeTruthy();
      expect(screen.getByText('Registrar Clinica')).toBeTruthy();
    });
  });

  it('muestra error cuando la API falla', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Error del servidor' }),
    });

    render(<ClinicPanel />);

    await waitFor(() => {
      expect(screen.getByText('Error del servidor')).toBeTruthy();
    });
  });

  it('muestra estado activo/inactivo con badge', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: mockClinics,
        total: 2,
        page: 1,
        size: 20,
      }),
    });

    render(<ClinicPanel />);

    await waitFor(() => {
      expect(screen.getByText('Activa')).toBeTruthy();
      expect(screen.getByText('Inactiva')).toBeTruthy();
    });
  });

  it('muestra botones de editar e inactivar/reactivar', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: mockClinics,
        total: 2,
        page: 1,
        size: 20,
      }),
    });

    render(<ClinicPanel />);

    await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(3);
      const buttonTexts = buttons.map((b) => b.textContent).filter(Boolean);
      expect(buttonTexts.some((t) => t?.includes('Editar'))).toBe(true);
      expect(buttonTexts.some((t) => t?.includes('Inactivar') || t?.includes('Reactivar'))).toBe(true);
    }, { timeout: 5000 });
  });

  it('muestra boton de nueva clinica', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: mockClinics,
        total: 2,
        page: 1,
        size: 20,
      }),
    });

    render(<ClinicPanel />);

    await waitFor(() => {
      expect(screen.getByText('+ Nueva Clinica')).toBeTruthy();
    });
  });
});
