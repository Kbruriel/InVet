/**
 * Unit tests para StatusBadge (FE-008)
 */

import { render, screen } from '@testing-library/react';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  const testCases = [
    { status: 'pending', expectedText: 'Pendiente' },
    { status: 'approved', expectedText: 'Aprobada' },
    { status: 'confirmed', expectedText: 'Confirmada' },
    { status: 'completed', expectedText: 'Completada' },
    { status: 'no_show', expectedText: 'No se presentó' },
    { status: 'cancelled', expectedText: 'Cancelada' },
    { status: 'rescheduled', expectedText: 'Reprogramada' },
  ];

  test.each(testCases)('renders $status as $expectedText', ({ status, expectedText }) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(expectedText)).toBeInTheDocument();
  });

  test('applies correct aria-label', () => {
    const { container } = render(<StatusBadge status="pending" />);
    const badge = container.querySelector('[aria-label]');
    expect(badge?.getAttribute('aria-label')).toBe('Cita Pendiente');
  });

  test('applies yellow-100 background for pending', () => {
    const { container } = render(<StatusBadge status="pending" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-yellow-100');
  });

  test('applies red-100 background for cancelled', () => {
    const { container } = render(<StatusBadge status="cancelled" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-red-100');
  });

  test('applies green-100 background for completed', () => {
    const { container } = render(<StatusBadge status="completed" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge).toHaveClass('bg-green-100');
  });
});
