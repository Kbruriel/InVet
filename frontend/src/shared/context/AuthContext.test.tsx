import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthProvider';

// Mock del hook de uso de navegación de Next.js
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Componente de prueba para usar el contexto
const TestComponent = () => {
  const { isAuthenticated, user, loading } = useAuth();
  
  if (loading) return <div data-testid="loading">Cargando...</div>;
  if (!isAuthenticated) return <div data-testid="not-authenticated">No autenticado</div>;
  return (
    <div data-testid="authenticated">
      <span>Usuario: {user?.firstName} {user?.lastName}</span>
    </div>
  );
};

describe('AuthProvider', () => {
  it('should provide auth context values', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });
});