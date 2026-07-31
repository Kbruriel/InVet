import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatePanel } from "@/shared/ui/state-panel";

describe("StatePanel", () => {
  it("renders the selected tone and content", () => {
    render(
      <StatePanel
        tone="error"
        title="Backend no disponible"
        description="Intentaremos de nuevo mas tarde."
      />,
    );

    const panel = screen.getByText("Backend no disponible").closest("div");

    expect(panel).not.toBeNull();
    expect(panel?.className).toContain("border-rose-200");
    expect(screen.getByText("Intentaremos de nuevo mas tarde.")).toBeInTheDocument();
  });
});
