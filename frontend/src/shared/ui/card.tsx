import type { HTMLAttributes } from "react";
import { cn } from "@/shared/ui/cn";

type CardProps = HTMLAttributes<HTMLDivElement>;

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_24px_80px_-36px_rgba(18,52,59,0.35)] backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}
