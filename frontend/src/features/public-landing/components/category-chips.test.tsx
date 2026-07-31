import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CategoryChips } from "@/features/public-landing/components/category-chips";

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: React.ComponentPropsWithoutRef<"a"> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe("CategoryChips", () => {
  it("renders the public search categories with real routes", () => {
    render(<CategoryChips />);

    expect(screen.getByRole("link", { name: "Veterinaria" })).toHaveAttribute(
      "href",
      "/clinicas?category=Veterinaria",
    );
    expect(screen.getByRole("link", { name: "Urgencias" })).toHaveAttribute(
      "href",
      "/clinicas?category=Urgencias",
    );
  });
});
