import { cn } from "@/shared/ui/cn";

type Tone = "info" | "success" | "error" | "empty";

type StatePanelProps = {
  tone: Tone;
  title: string;
  description: string;
  className?: string;
};

const toneStyles: Record<Tone, string> = {
  info: "border-brand-teal/20 bg-brand-teal/8 text-ink-strong",
  success: "border-emerald-200 bg-emerald-50 text-emerald-950",
  error: "border-rose-200 bg-rose-50 text-rose-950",
  empty: "border-slate-200 bg-slate-50 text-slate-900",
};

export function StatePanel({
  tone,
  title,
  description,
  className,
}: StatePanelProps) {
  return (
    <div
      className={cn(
        "rounded-[24px] border px-5 py-4 shadow-sm",
        toneStyles[tone],
        className,
      )}
    >
      <p className="text-base font-semibold">{title}</p>
      <p className="mt-2 text-sm leading-6 opacity-85">{description}</p>
    </div>
  );
}
