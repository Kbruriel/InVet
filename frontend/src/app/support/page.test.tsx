import { render, screen, waitFor } from '@testing-library/react';
import SupportPage from './page';

// Mock the components and API modules
jest.mock('@/features/support/ui/ticket-form', () => ({
  TicketForm: () => <div data-testid="ticket-form">Mocked Ticket Form</div>
}));

jest.mock('@/features/support/ui/ticket-list', () => ({
  TicketList: () => <div data-testid="ticket-list">Mocked Ticket List</div>
}));

describe('SupportPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', async () => {
    render(<SupportPage />);
    
    expect(screen.getByRole('button', { name: /mostrar formulario/i })).toBeInTheDocument();
  });
});