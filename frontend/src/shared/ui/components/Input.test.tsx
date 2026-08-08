/** Tests para Input component (FE-003) */

import { render, screen } from '@testing-library/react';
import { Input } from './Input';

describe('Input', () => {
  it('deberia renderizar input con label', () => {
    render(<Input label="Nombre" id="nombre" />);
    expect(screen.getByLabelText(/nombre/i)).toBeInTheDocument();
  });

  it('deberia mostrar error cuando se pasa', () => {
    render(<Input label="Email" id="email" error="Email invalido" />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('Email invalido')).toBeInTheDocument();
  });

  it('deberia tener clase de error en el input', () => {
    const { container } = render(<Input label="Email" id="email" error="Invalido" />);
    expect((container.firstChild as HTMLElement)?.querySelector('input')).toHaveClass('border-red-400');
  });

  it('deberia pasar props al input', () => {
    render(<Input placeholder="Tu nombre" id="name" type="text" />);
    const input = screen.getByPlaceholderText('Tu nombre');
    expect(input).toHaveAttribute('type', 'text');
  });

  it('deberia tener focus ring', () => {
    const { container } = render(<Input label="Test" id="test" />);
    expect((container.firstChild as HTMLElement)?.querySelector('input')).toHaveClass('focus:ring-2');
    expect((container.firstChild as HTMLElement)?.querySelector('input')).toHaveClass('focus:ring-teal');
  });
});
