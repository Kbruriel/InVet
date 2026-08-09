import { render, screen } from '@testing-library/react';
import { InternalUserList } from './internal-user-list';
import * as useIUHook from '@/features/slice-006/hooks/use-internal-users';

jest.mock('@/features/slice-006/hooks/use-internal-users');

const mockUseInternalUsers = useIUHook.useInternalUsers as jest.MockedFunction<typeof useIUHook.useInternalUsers>;

describe('InternalUserList', () => {
  it('shows empty state when no internal users', () => {
    mockUseInternalUsers.mockReturnValue({
      items: [],
      total: 0,
      page: 1,
      size: 20,
      loading: false,
      error: null,
      submitting: false,
      setPage: jest.fn(),
      deactivate: jest.fn(),
      create: jest.fn().mockResolvedValue({}),
      update: jest.fn().mockResolvedValue({}),
      fetchOne: jest.fn().mockResolvedValue({}),
    });
    render(<InternalUserList />);
    expect(screen.getByText(/no hay usuarios internos/i)).toBeInTheDocument();
  });

  it('shows internal users in list', () => {
    mockUseInternalUsers.mockReturnValue({
      items: [
        { id: 1, user_id: 5, nombre: 'Maria', rol: 'admin', is_active: true, branch_ids: [1] } as unknown as import('@/shared/api/slice-006').InternalUserDTO,
      ],
      total: 1,
      page: 1,
      size: 20,
      loading: false,
      error: null,
      submitting: false,
      setPage: jest.fn(),
      deactivate: jest.fn(),
      create: jest.fn().mockResolvedValue({}),
      update: jest.fn().mockResolvedValue({}),
      fetchOne: jest.fn().mockResolvedValue({}),
    });
    render(<InternalUserList />);
    const results = screen.getAllByText('Maria');
    expect(results.length).toBeGreaterThan(0);
  });
});
