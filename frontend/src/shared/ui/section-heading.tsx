type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function SectionHeading({
  eyebrow,
  title,
  description,
}: SectionHeadingProps) {
  return (
    <header className="space-y-3">
      <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-teal">
        {eyebrow}
      </p>
      <h2 className="text-3xl font-semibold tracking-tight text-ink-strong md:text-4xl">
        {title}
      </h2>
      <p className="max-w-3xl text-base leading-7 text-ink-soft">{description}</p>
    </header>
  );
}
