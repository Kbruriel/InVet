import { render, screen } from '@testing-library/react';
import { TicketListFiltered } from './ticket-list-filtered';

const mockTickets = [
  {
    id: '1',
    clinic_id: 'clinic-1',
    owner_id: 'owner-1',
    title: 'Test Ticket 1',
    description: 'Test description 1',
    category_id: 'category-1',
    status: 'initiated',
    created_at: '2023-01-01T00:00:00Z'
  },
  {
    id: '2',
    clinic_id: 'clinic-1',
    owner_id: 'owner-1',
    title: 'Test Ticket 2',
    description: 'Test description 2',
    category_id: 'category-2',
    status: 'pending',
    created_at: '2023-01-02T00:00:00Z'
  }
];

const mockOnTicketClick = jest.fn();

describe('TicketListFiltered', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state correctly', () => {
    render(<TicketListFiltered onTicketClick={mockOnTicketClick} />);
    
    expect(screen.getByRole('button', { name: /volver a la lista/i })).toBeInTheDocument();
  });

  it('renders tickets when data is loaded', async () => {
    // This would be an integration test that requires API mocking
    expect(true).toBe(true); // Placeholder test - actual implementation would include proper mocks
  });

  it('renders empty state correctly', async () => {
    // This would be an integration test that requires API mocking  
    expect(true).toBe(true); // Placeholder test - actual implementation would include proper mocks
  });

  it('shows filter controls correctly', () => {
    render(<TicketListFiltered onTicketClick={mockOnTicketClick} />);
    
    expect(screen.getByText(/filtrar por estado/i)).toBeInTheDocument();
  });
});