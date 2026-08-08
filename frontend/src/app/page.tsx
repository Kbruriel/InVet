/**
 * US-003 / FE-003 - Root public landing page
 *
 * This page provides the full public landing with hero search,
 * how-it-works section, and professional CTA.
 */

import { HeroSection } from '@/features/public-landing/components/HeroSection';
import { HowItWorksSection } from '@/features/public-landing/components/HowItWorksSection';
import { ProfessionalCtaSection } from '@/features/public-landing/components/ProfessionalCtaSection';

export const dynamic = 'force-dynamic';

export default function HomePage() {
  return (
    <div className="space-y-16 py-8">
      <HeroSection />
      <HowItWorksSection />
      <ProfessionalCtaSection />
    </div>
  );
}
