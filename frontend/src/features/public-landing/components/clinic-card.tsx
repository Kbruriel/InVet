import type { ClinicCardModel } from "@/entities/clinic/model";
import { Card } from "@/shared/ui/card";

type ClinicCardProps = {
  clinic: ClinicCardModel;
};

export function ClinicCard({ clinic }: ClinicCardProps) {
  return (
    <Card className="space-y-4 bg-white/90">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-brand-teal">
            {clinic.category}
          </p>
          <h3 className="mt-2 text-xl font-semibold text-ink-strong">
            {clinic.name}
          </h3>
          <p className="mt-1 text-sm text-ink-soft">{clinic.city}</p>
        </div>
        <span className="rounded-full bg-brand-mint/70 px-3 py-1 text-xs font-semibold text-ink-strong">
          {clinic.badge}
        </span>
      </div>

      <ul className="space-y-2 text-sm text-ink-soft">
        {clinic.services.map((service) => (
          <li key={service} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-brand-teal" />
            <span>{service}</span>
          </li>
        ))}
      </ul>

      <p className="text-sm font-medium text-ink-strong">{clinic.responseTime}</p>
    </Card>
  );
}
