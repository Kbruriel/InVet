import { render, screen, fireEvent } from '@testing-library/react';
import { ReportTable, type ReportColumn } from './ReportTable';

type Row = { id: number; name: string; amount: number };

const baseColumns: ReportColumn<Row>[] = [
  { key: 'name', header: 'Nombre', render: (r) => r.name },
  { key: 'amount', header: 'Monto', align: 'right', render: (r) => r.amount.toFixed(2) },
];

const rows: Row[] = [
  { id: 1, name: 'Vaccination', amount: 500 },
  { id: 2, name: 'Surgery', amount: 8500 },
];

describe('ReportTable (FE-015-T04)', () => {
  it('renders headers and rows', () => {
    render(
      <ReportTable
        columns={baseColumns}
        rows={rows}
        rowKey={(r) => r.id}
        title="Servicios"
      />,
    );
    expect(screen.getByRole('columnheader', { name: 'Nombre' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: '8500.00' })).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: '500.00' })).toBeInTheDocument();
  });

  it('shows LoadingSpinner when loading=true', () => {
    render(
      <ReportTable
        columns={baseColumns}
        rows={rows}
        rowKey={(r) => r.id}
        loading
        title="Servicios"
      />,
    );
    expect(screen.getByRole('status', { name: /cargando servicios/i })).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('shows EmptyState when rows is empty (not loading)', () => {
    render(
      <ReportTable
        columns={baseColumns}
        rows={[]}
        rowKey={(r) => r.id}
        emptyTitle="Sin servicios"
        emptyDescription="Ningún servicio en el periodo."
      />,
    );
    expect(screen.getByText('Sin servicios')).toBeInTheDocument();
    expect(screen.getByText(/Ningún servicio/i)).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('shows error message and no table when error is provided', () => {
    render(<ReportTable columns={baseColumns} rows={rows} rowKey={(r) => r.id} error="Sin conexión" />);
    expect(screen.getByRole('alert')).toHaveTextContent(/Sin conexión/);
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('navigates between pages via Anterior/Siguiente (page + total footer)', () => {
    const onPageChange = jest.fn();
    render(
      <ReportTable
        columns={baseColumns}
        rows={rows}
        rowKey={(r) => r.id}
        page={2}
        pages={3}
        total={60}
        onPageChange={onPageChange}
      />,
    );
    expect(screen.queryByRole('button', { name: /anterior/i })).toBeEnabled();
    fireEvent.click(screen.getByRole('button', { name: /anterior/i }));
    expect(onPageChange).toHaveBeenCalledWith(1);

    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));
    expect(onPageChange).toHaveBeenLastCalledWith(3);

    expect(screen.getByText(/Página 2 de 3/)).toBeInTheDocument();
    expect(screen.getByText(/60 registros/)).toBeInTheDocument();
  });

  it('disables Anterior on first page and Siguiente on the last page', () => {
    render(
      <ReportTable
        columns={baseColumns}
        rows={rows}
        rowKey={(r) => r.id}
        page={1}
        pages={3}
        total={60}
        onPageChange={jest.fn()}
      />,
    );
    expect(screen.getByRole('button', { name: /anterior/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /siguiente/i })).toBeEnabled();
  });

  it('hides the pagination bar when pages <= 1', () => {
    render(
      <ReportTable
        columns={baseColumns}
        rows={rows}
        rowKey={(r) => r.id}
        page={1}
        pages={1}
        total={2}
      />,
    );
    expect(screen.queryByRole('navigation', { name: 'Paginación' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /anterior/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /siguiente/i })).not.toBeInTheDocument();
  });
});
