/** Tests para ProfessionalCtaSection (FE-003) */

import { render, screen } from '@testing-library/react';
import { ProfessionalCtaSection } from './ProfessionalCtaSection';

describe('ProfessionalCtaSection', () => {
  it('deberia renderizar el titulo del CTA', () => {
    render(<ProfessionalCtaSection />);
    expect(screen.getByText(/tienes una clinica veterinaria/i)).toBeInTheDocument();
  });

  it('deberia tener boton Registrar clinica con link a /register', () => {
    render(<ProfessionalCtaSection />);
    const registerLink = screen.getByRole('link', { name: /registrar clinica/i });
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('deberia tener boton Ver clínicas con link a /clinicas', () => {
    render(<ProfessionalCtaSection />);
    const clinicsLink = screen.getByRole('link', { name: /ver clínicas/i });
    expect(clinicsLink).toHaveAttribute('href', '/clinicas');
  });

  it('deberia tener aria-label de registra tu clinica', () => {
    const { container } = render(<ProfessionalCtaSection />);
    const section = container.querySelector('section[aria-label="Registra tu clinica"]');
    expect(section).toBeInTheDocument();
  });
});
