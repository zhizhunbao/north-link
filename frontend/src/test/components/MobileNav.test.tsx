/**
 * Unit tests for MobileNav component.
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { MobileNav } from "../../components/layout/MobileNav";

function renderMobileNav() {
  return render(
    <MemoryRouter>
      <MobileNav />
    </MemoryRouter>,
  );
}

describe("MobileNav", () => {
  it("renders all navigation items", () => {
    renderMobileNav();
    expect(screen.getByText("首页")).toBeInTheDocument();
    expect(screen.getByText("比价")).toBeInTheDocument();
    expect(screen.getByText("商户")).toBeInTheDocument();
    expect(screen.getByText("物流")).toBeInTheDocument();
    expect(screen.getByText("设置")).toBeInTheDocument();
  });

  it("renders 5 navigation links", () => {
    renderMobileNav();
    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(5);
  });

  it("links have correct paths", () => {
    renderMobileNav();
    const links = screen.getAllByRole("link");
    const paths = links.map((l) => l.getAttribute("href"));
    expect(paths).toContain("/");
    expect(paths).toContain("/prices");
    expect(paths).toContain("/merchants");
    expect(paths).toContain("/logistics");
    expect(paths).toContain("/settings");
  });

  it("renders nav element with mobile-nav class", () => {
    const { container } = renderMobileNav();
    const nav = container.querySelector("nav.mobile-nav");
    expect(nav).toBeTruthy();
  });
});
