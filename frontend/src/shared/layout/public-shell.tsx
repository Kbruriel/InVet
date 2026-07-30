import type { ReactNode } from "react";
import { PublicFooter } from "@/features/public-landing/components/public-footer";
import { PublicHeader } from "@/features/public-landing/components/public-header";

type PublicShellProps = {
  children: ReactNode;
};

export function PublicShell({ children }: PublicShellProps) {
  return (
    <div className="min-h-screen">
      <PublicHeader />
      <main>{children}</main>
      <PublicFooter />
    </div>
  );
}
