/** Tests para Card component (FE-003) */

import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
  it('deberia renderizar children', () => {
    render(<Card><div>Content</div></Card>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('deberia ser un div por defecto', () => {
    const { container } = render(<Card>Test</Card>);
    expect(container.firstChild).toHaveClass('bg-white');
    expect(container.firstChild).toHaveClass('rounded-2xl');
  });

  it('deberia ser un link cuando se pasa href', () => {
    render(<Card href="/test">Link Card</Card>);
    const link = screen.getByRole('link');
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/test');
  });

  it('deberia ser un button cuando se pasa onClick', () => {
    const handleClick = jest.fn();
    render(<Card onClick={handleClick}>Clickable</Card>);
    const button = screen.getByRole('button', { name: /clickable/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('cursor-pointer');
  });
});
