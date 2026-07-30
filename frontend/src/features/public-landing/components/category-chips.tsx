import Link from "next/link";
import { routes } from "@/shared/config/routes";

const categories = [
  { label: "Veterinaria", value: "Veterinaria" },
  { label: "Estetica", value: "Estetica" },
  { label: "Urgencias", value: "Urgencias" },
];

export function CategoryChips() {
  return (
    <div className="flex flex-wrap gap-3">
      {categories.map((category) => (
        <Link
          key={category.value}
          href={`${routes.clinics}?category=${encodeURIComponent(category.value)}`}
          className="rounded-full border border-brand-teal/15 bg-white/75 px-4 py-2 text-sm font-medium text-ink-strong transition hover:border-brand-teal/30 hover:bg-brand-mint/40"
        >
          {category.label}
        </Link>
      ))}
    </div>
  );
}
