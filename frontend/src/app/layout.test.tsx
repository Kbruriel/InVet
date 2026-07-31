import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import RootLayout, { metadata } from "@/app/layout";

describe("RootLayout", () => {
  it("exposes the base metadata and root html shell", () => {
    const html = renderToStaticMarkup(
      <RootLayout>
        <div>Contenido</div>
      </RootLayout>,
    );

    expect(metadata.title).toBe("InVet");
    expect(html).toContain('lang="es"');
    expect(html).toContain("Contenido");
  });
});
