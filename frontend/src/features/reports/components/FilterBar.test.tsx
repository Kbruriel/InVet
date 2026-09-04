import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { FilterBar, REPORT_TYPE_OPTIONS } from './FilterBar';

function setup() {
  const onApply = jest.fn();
  render(<FilterBar onApply={onApply} />);
  return { onApply };
}

function setSelectValue(value: string) {
  const select = screen.getByLabelText('Tipo de reporte') as HTMLSelectElement;
  fireEvent.change(select, { target: { value } });
}

describe('FilterBar (FE-015-T03)', () => {
  it('renders the six report type options', () => {
    setup();
    const select = screen.getByLabelText('Tipo de reporte');
    expect(select).toBeInTheDocument();
    expect(REPORT_TYPE_OPTIONS).toHaveLength(6);
    const optionCount = screen.getAllByRole('option').length;
    expect(optionCount).toBeGreaterThanOrEqual(REPORT_TYPE_OPTIONS.length);
  });

  it('calls onApply with selected type and empty filters when dates are blank', () => {
    const { onApply } = setup();
    const form = document.querySelector('form[role="search"]') as HTMLFormElement;
    setSelectValue('payments');
    act(() => {
      fireEvent.submit(form);
    });

    expect(onApply).toHaveBeenCalledTimes(1);
    expect(onApply).toHaveBeenCalledWith('payments', {
      period_start: undefined,
      period_end: undefined,
    });
  });

  it('forwards period filters when both dates are set and valid', () => {
    const { onApply } = setup();
    const form = document.querySelector('form[role="search"]') as HTMLFormElement;
    fireEvent.change(screen.getByLabelText('Desde'), {
      target: { value: '2026-01-01' },
    });
    fireEvent.change(screen.getByLabelText('Hasta'), {
      target: { value: '2026-01-31' },
    });
    act(() => {
      fireEvent.submit(form);
    });

    expect(onApply).toHaveBeenCalledTimes(1);
    expect(onApply).toHaveBeenCalledWith('appointments', {
      period_start: '2026-01-01',
      period_end: '2026-01-31',
    });
  });

  it('rejects period_start greater than period_end before calling onApply', async () => {
    const { onApply } = setup();
    const form = document.querySelector('form[role="search"]') as HTMLFormElement;
    fireEvent.change(screen.getByLabelText('Desde'), {
      target: { value: '2026-02-15' },
    });
    fireEvent.change(screen.getByLabelText('Hasta'), {
      target: { value: '2026-02-01' },
    });
    act(() => {
      fireEvent.submit(form);
    });

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(onApply).not.toHaveBeenCalled();
  });

  it('accepts identical start/end dates', () => {
    const { onApply } = setup();
    const form = document.querySelector('form[role="search"]') as HTMLFormElement;
    fireEvent.change(screen.getByLabelText('Desde'), {
      target: { value: '2026-03-10' },
    });
    fireEvent.change(screen.getByLabelText('Hasta'), {
      target: { value: '2026-03-10' },
    });
    act(() => {
      fireEvent.submit(form);
    });

    expect(onApply).toHaveBeenCalledTimes(1);
  });

  it('clears dates when restored', () => {
    setup();
    const start = screen.getByLabelText('Desde');
    fireEvent.change(start, { target: { value: '2026-03-10' } });
    fireEvent.click(screen.getByRole('button', { name: /restaurar/i }));

    expect((start as HTMLInputElement).value).toBe('');
  });
});
