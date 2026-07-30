import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  PublicSearchBar,
  buildClinicSearchHref,
} from "@/features/public-landing/components/public-search-bar";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

afterEach(() => {
  cleanup();
});

describe("buildClinicSearchHref", () => {
  it("normalizes the clinic search route", () => {
    expect(buildClinicSearchHref("Urgencias 24h")).toBe(
      "/clinicas?query=Urgencias+24h",
    );
  });
});

describe("PublicSearchBar", () => {
  it("shows a validation error when the query is empty", () => {
    render(<PublicSearchBar />);

    fireEvent.click(screen.getByRole("button", { name: "Buscar" }));

    expect(
      screen.getByText("Ingresa una clinica, ciudad o servicio."),
    ).toBeInTheDocument();
  });

  it("calls the search callback when a valid query is submitted", () => {
    const onSearch = vi.fn();
    const { container } = render(<PublicSearchBar onSearch={onSearch} />);

    fireEvent.change(
      screen.getByPlaceholderText("Busca una clinica, ciudad o servicio"),
      {
        target: { value: "Clinica norte" },
      },
    );

    const form = container.querySelector("form");

    if (!form) {
      throw new Error("Expected the search form to be rendered.");
    }

    fireEvent.submit(form);

    expect(onSearch).toHaveBeenCalledWith("/clinicas?query=Clinica+norte");
  });
});
