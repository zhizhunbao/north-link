/**
 * Unit tests for AppLayout component.
 */
import { describe, it, expect, vi /* , beforeEach */ } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "../../components/layout/AppLayout";

/* Mock child components to simplify testing */
vi.mock("../../components/layout/MobileNav", () => ({
  MobileNav: () => <nav data-testid="mobile-nav">MobileNav</nav>,
}));

function renderAppLayout() {
  return render(
    <MemoryRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route
            path="/"
            element={<div data-testid="child-content">Child</div>}
          />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("AppLayout", () => {
  it("renders sidebar and main content area", () => {
    renderAppLayout();
    expect(screen.getByText("North Link")).toBeInTheDocument();
    expect(screen.getByTestId("child-content")).toBeInTheDocument();
  });

  it("renders mobile nav", () => {
    renderAppLayout();
    expect(screen.getByTestId("mobile-nav")).toBeInTheDocument();
  });

  it("toggles collapsed class when sidebar toggle is clicked", () => {
    const { container } = renderAppLayout();
    const layout = container.querySelector(".app-layout");
    expect(layout?.className).not.toContain("collapsed");

    const toggleBtn = screen.getByRole("button");
    fireEvent.click(toggleBtn);
    expect(layout?.className).toContain("collapsed");

    fireEvent.click(toggleBtn);
    expect(layout?.className).not.toContain("collapsed");
  });

  it("renders main element with app-content class", () => {
    const { container } = renderAppLayout();
    const main = container.querySelector("main.app-content");
    expect(main).toBeTruthy();
  });
});
