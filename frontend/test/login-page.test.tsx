// Mock Next.js App Router hooks before any imports
const mockPush = jest.fn();
jest.mock("next/navigation", () => ({
  ...jest.requireActual("next/navigation"),
  useRouter: () => ({ push: mockPush, refresh: jest.fn() }),
  useSearchParams: () => ({ get: (key: string) => key === "next" ? "/dashboard" : null }),
  useParams: () => ({}),
  usePathname: () => "/login",
}));

import { render, screen } from "@testing-library/react";
import LoginPage from "@/app/login/page";

describe("login page", () => {
  it("renders the login form", () => {
    render(<LoginPage />);

    expect(
      screen.getByRole("heading", { name: /Inicia sesion en InVet/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: /email/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Iniciar sesion/i }),
    ).toBeInTheDocument();
  });
});
