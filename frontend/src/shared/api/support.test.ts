import { supportApi } from './support';
import { apiClient } from './client';

// Mockear apiClient
jest.mock('./client');

describe('supportApi', () => {
  const mockFetch = apiClient as jest.Mocked<typeof apiClient>;
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createTicket', () => {
    it('should create a ticket successfully', async () => {
      const mockTicket = {
        id: 'ticket-1',
        clinic_id: 'clinic-1',
        owner_id: 'owner-1',
        title: 'Test Ticket',
        description: 'Ticket description',
        category_id: 'category-1',
        status: 'initiated',
        created_at: '2023-01-01T00:00:00Z'
      };

      mockFetch.post.mockResolvedValue({
        json: jest.fn().mockResolvedValue(mockTicket),
      } as any);

      const result = await supportApi.createTicket({
        title: 'Test Ticket',
        description: 'Ticket description',
        category_id: 'category-1'
      });

      expect(result).toEqual(mockTicket);
      expect(mockFetch.post).toHaveBeenCalledWith('/tickets', {
        body: JSON.stringify({
          title: 'Test Ticket',
          description: 'Ticket description',
          category_id: 'category-1'
        }),
      });
    });
  });

  describe('listTickets', () => {
    it('should list tickets successfully', async () => {
      const mockResponse = {
        items: [
          {
            id: 'ticket-1',
            clinic_id: 'clinic-1',
            owner_id: 'owner-1',
            title: 'Test Ticket',
            description: 'Ticket description',
            category_id: 'category-1',
            status: 'initiated',
            created_at: '2023-01-01T00:00:00Z'
          }
        ],
        page: 1,
        page_size: 10,
        total: 1
      };

      mockFetch.get.mockResolvedValue({
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await supportApi.listTickets({
        page: 1,
        page_size: 10,
        status: 'initiated'
      });

      expect(result).toEqual(mockResponse);
      expect(mockFetch.get).toHaveBeenCalledWith('/tickets?page=1&page_size=10&status=initiated');
    });
  });

  describe('getTicket', () => {
    it('should get ticket details successfully', async () => {
      const mockTicket = {
        id: 'ticket-1',
        clinic_id: 'clinic-1',
        owner_id: 'owner-1',
        title: 'Test Ticket',
        description: 'Ticket description',
        category_id: 'category-1',
        status: 'initiated',
        created_at: '2023-01-01T00:00:00Z'
      };

      mockFetch.get.mockResolvedValue({
        json: jest.fn().mockResolvedValue(mockTicket),
      } as any);

      const result = await supportApi.getTicket('ticket-1');

      expect(result).toEqual(mockTicket);
      expect(mockFetch.get).toHaveBeenCalledWith('/tickets/ticket-1');
    });
  });

  describe('updateTicketStatus', () => {
    it('should update ticket status successfully', async () => {
      const mockTicket = {
        id: 'ticket-1',
        clinic_id: 'clinic-1',
        owner_id: 'owner-1',
        title: 'Test Ticket',
        description: 'Ticket description',
        category_id: 'category-1',
        status: 'pending',
        created_at: '2023-01-01T00:00:00Z'
      };

      mockFetch.patch.mockResolvedValue({
        json: jest.fn().mockResolvedValue(mockTicket),
      } as any);

      const result = await supportApi.updateTicketStatus('ticket-1', {
        status: 'pending'
      });

      expect(result).toEqual(mockTicket);
      expect(mockFetch.patch).toHaveBeenCalledWith('/tickets/ticket-1/status', {
        body: JSON.stringify({
          status: 'pending'
        }),
      });
    });
  });

  describe('getCategories', () => {
    it('should get active categories successfully', async () => {
      const mockCategories = [
        {
          id: 'category-1',
          clinic_id: 'clinic-1',
          name: 'Technical Support',
          active: true
        },
        {
          id: 'category-2',
          clinic_id: 'clinic-1',
          name: 'Billing',
          active: true
        }
      ];

      mockFetch.get.mockResolvedValue({
        json: jest.fn().mockResolvedValue(mockCategories),
      } as any);

      const result = await supportApi.getCategories();

      expect(result).toEqual(mockCategories);
      expect(mockFetch.get).toHaveBeenCalledWith('/tickets/categories');
    });
  });
});