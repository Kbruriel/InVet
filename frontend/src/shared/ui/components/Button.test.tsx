/** Tests para Button component (FE-003) */

import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('deberia renderizar texto del boton', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('deberia aplicar variante primary por defecto', () => {
    const { container } = render(<Button>Primary</Button>);
    expect(container.firstChild).toHaveClass('bg-teal');
    expect(container.firstChild).toHaveClass('text-white');
  });

  it('deberia aplicar variante secondary', () => {
    const { container } = render(<Button variant="secondary">Secondary</Button>);
    expect(container.firstChild).toHaveClass('bg-mint');
    expect(container.firstChild).toHaveClass('text-teal-dark');
  });

  it('deberia aplicar variante outline', () => {
    const { container } = render(<Button variant="outline">Outline</Button>);
    expect(container.firstChild).toHaveClass('border-2');
    expect(container.firstChild).toHaveClass('text-teal');
  });

  it('deberia ser disabled cuando se pasa disabled', () => {
    const { container } = render(<Button disabled>Disabled</Button>);
    expect(container.firstChild).toBeDisabled();
  });

  it('deberia aplicar tamano lg', () => {
    const { container } = render(<Button size="lg">Large</Button>);
    expect(container.firstChild).toHaveClass('px-8');
    expect(container.firstChild).toHaveClass('py-4');
  });

  it('deberia tener focus ring visible', () => {
    const { container } = render(<Button>Focusable</Button>);
    expect(container.firstChild).toHaveClass('focus:ring-2');
    expect(container.firstChild).toHaveClass('focus:ring-teal');
  });
});
