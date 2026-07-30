import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/shared/ui/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "md" | "lg";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function buttonClassName({
  variant = "primary",
  size = "md",
  className,
}: {
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
}) {
  const variantStyles: Record<ButtonVariant, string> = {
    primary:
      "bg-brand-teal text-white shadow-lg shadow-brand-teal/15 hover:bg-[#004d51]",
    secondary:
      "bg-white text-ink-strong ring-1 ring-brand-teal/15 hover:bg-surface-soft",
    ghost: "bg-transparent text-brand-teal hover:bg-brand-teal/10",
  };

  const sizeStyles: Record<ButtonSize, string> = {
    md: "min-h-11 px-5 py-3 text-sm",
    lg: "min-h-12 px-6 py-3.5 text-base",
  };

  return cn(
    "inline-flex items-center justify-center rounded-full font-semibold transition duration-200 disabled:cursor-not-allowed disabled:opacity-60",
    variantStyles[variant],
    sizeStyles[size],
    className,
  );
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClassName({ variant, size, className })}
      {...props}
    />
  );
}
