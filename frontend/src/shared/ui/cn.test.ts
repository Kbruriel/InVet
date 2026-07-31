import { describe, expect, it } from "vitest";
import { cn } from "@/shared/ui/cn";

describe("cn", () => {
  it("joins only truthy values", () => {
    expect(cn("base", undefined, false, "accent", null, "active")).toBe(
      "base accent active",
    );
  });
});
