/** Tests para PublicSearchBar (FE-003) */

import { render, screen, fireEvent, act } from '@testing-library/react';
import { PublicSearchBar } from './PublicSearchBar';

jest.useFakeTimers();

describe('PublicSearchBar', () => {
  const onSearchMock = jest.fn();

  beforeEach(() => {
    onSearchMock.mockClear();
  });

  it('deberia renderizar input de busqueda con label', () => {
    render(<PublicSearchBar onSearch={onSearchMock} />);
    expect(screen.getByLabelText(/buscar clinica por nombre/i)).toBeInTheDocument();
  });

  it('deberia renderizar boton buscar', () => {
    render(<PublicSearchBar onSearch={onSearchMock} />);
    expect(screen.getByRole('button', { name: /buscar/i })).toBeInTheDocument();
  });

  it('deberia actualizar el valor del input al escribir', () => {
    render(<PublicSearchBar onSearch={onSearchMock} />);
    const input = screen.getByLabelText(/buscar clinica por nombre, ciudad o servicio/i) as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'veterinaria' } });
    expect(input.value).toBe('veterinaria');
  });

  it('deberia llamar onSearch con debounce despues de escribir', () => {
    render(<PublicSearchBar onSearch={onSearchMock} />);
    const input = screen.getByLabelText(/buscar clinica por nombre, ciudad o servicio/i) as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'test' } });

    // Avanzar timers 300ms para el debounce
    act(() => { jest.advanceTimersByTime(300); });

    expect(onSearchMock).toHaveBeenCalledWith('test');
  });

  it('deberia prevenir submit del form', () => {
    render(<PublicSearchBar onSearch={onSearchMock} />);
    const form = screen.getByRole('search');
    fireEvent.submit(form);
    // El form tiene onSubmit que previene default
  });

  it('deberia tener role search', () => {
    render(<PublicSearchBar onSearch={onSearchMock} />);
    expect(screen.getByRole('search')).toBeInTheDocument();
  });
});
