/** Tests para HeroSection (FE-003) */

import { render, screen } from '@testing-library/react';
import { HeroSection } from './HeroSection';

// Mock child components
jest.mock('./PublicSearchBar', () => ({ PublicSearchBar: () => <div data-testid="search-bar">Buscador</div> }));
jest.mock('./CategoryChips', () => ({ CategoryChips: () => <div data-testid="category-chips">Categorias</div> }));
jest.mock('./HeroBentoVisual', () => ({ HeroBentoVisual: () => <div data-testid="bento-visual" /> }));

describe('HeroSection', () => {
  it('deberia renderizar el titulo principal', () => {
    render(<HeroSection />);
    expect(screen.getByText(/encuentra la clinica ideal/i)).toBeInTheDocument();
  });

  it('deberia renderizar el buscador', () => {
    render(<HeroSection />);
    expect(screen.getByTestId('search-bar')).toBeInTheDocument();
  });

  it('deberia renderizar accesos a login y registro', () => {
    render(<HeroSection />);

    expect(screen.getByRole('link', { name: /iniciar sesion/i })).toHaveAttribute(
      'href',
      '/login',
    );
    expect(screen.getByRole('link', { name: /registrarse/i })).toHaveAttribute(
      'href',
      '/register',
    );
  });

  it('deberia renderizar los chips de categoria', () => {
    render(<HeroSection />);
    expect(screen.getByTestId('category-chips')).toBeInTheDocument();
  });

  it('deberia tener seccion con aria-label de busqueda', () => {
    const { container } = render(<HeroSection />);
    const section = container.querySelector('section[aria-label="Busqueda de clinicas"]');
    expect(section).toBeInTheDocument();
  });
});
