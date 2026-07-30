import {
  HeroSection,
  HowItWorksSection,
  ProfessionalCtaSection,
} from "@/features/public-landing";
import { PublicShell } from "@/shared/layout/public-shell";

export default function HomePage() {
  return (
    <PublicShell>
      <HeroSection />
      <HowItWorksSection />
      <ProfessionalCtaSection />
    </PublicShell>
  );
}
