/** Tests para HowItWorksSection (FE-003) */

import { render, screen } from '@testing-library/react';
import { HowItWorksSection } from './HowItWorksSection';

describe('HowItWorksSection', () => {
  it('deberia renderizar el titulo de la seccion', () => {
    render(<HowItWorksSection />);
    expect(screen.getByText(/como funciona invet/i)).toBeInTheDocument();
  });

  it('deberia renderizar los tres pasos', () => {
    render(<HowItWorksSection />);
    expect(screen.getByText('Busca')).toBeInTheDocument();
    expect(screen.getByText('Compara')).toBeInTheDocument();
    expect(screen.getByText('Solicita')).toBeInTheDocument();
  });

  it('deberia tener aria-label de como funciona', () => {
    const { container } = render(<HowItWorksSection />);
    const section = container.querySelector('section[aria-label="Como funciona"]');
    expect(section).toBeInTheDocument();
  });

  it('deberia mostrar descripcion para cada paso', () => {
    render(<HowItWorksSection />);
    expect(screen.getByText(/ingresa el nombre/i)).toBeInTheDocument();
    expect(screen.getByText(/revisa perfiles/i)).toBeInTheDocument();
    expect(screen.getByText(/env.*s tu solicitud/i)).toBeInTheDocument();
  });
});
