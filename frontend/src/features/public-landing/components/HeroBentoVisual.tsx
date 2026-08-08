'use client';

export function HeroBentoVisual() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 -z-10 flex items-center justify-end opacity-20 sm:opacity-30"
    >
      <div className="grid grid-cols-3 gap-4 p-8">
        <div className="h-32 w-32 rounded-2xl bg-teal/10" />
        <div className="h-40 w-40 rounded-2xl bg-mint/20" />
        <div className="h-28 w-28 rounded-2xl bg-sandy-200/40" />
        <div className="h-36 w-36 rounded-2xl bg-teal/15" />
        <div className="h-24 w-24 rounded-2xl bg-mint/15" />
        <div className="h-32 w-32 rounded-2xl bg-sandy-100/50" />
      </div>
    </div>
  );
}
