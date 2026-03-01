/**
 * Unit tests for Sidebar component.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "../../components/layout/Sidebar";

function renderSidebar(collapsed = false, onToggle = vi.fn()) {
  return render(
    <MemoryRouter>
      <Sidebar collapsed={collapsed} onToggle={onToggle} />
    </MemoryRouter>,
  );
}

describe("Sidebar", () => {
  it("renders logo and brand name", () => {
    renderSidebar();
    expect(screen.getByText("N")).toBeInTheDocument();
    expect(screen.getByText("North Link")).toBeInTheDocument();
  });

  it("renders all navigation items", () => {
    renderSidebar();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("比价中心")).toBeInTheDocument();
    expect(screen.getByText("商户管理")).toBeInTheDocument();
    expect(screen.getByText("物流管理")).toBeInTheDocument();
    expect(screen.getByText("订单中心")).toBeInTheDocument();
    expect(screen.getByText("系统设置")).toBeInTheDocument();
  });

  it("renders 6 navigation links", () => {
    renderSidebar();
    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(6);
  });

  it("applies collapsed class when collapsed", () => {
    const { container } = renderSidebar(true);
    const sidebar = container.querySelector("aside");
    expect(sidebar?.className).toContain("collapsed");
  });

  it("does not apply collapsed class when expanded", () => {
    const { container } = renderSidebar(false);
    const sidebar = container.querySelector("aside");
    expect(sidebar?.className).not.toContain("collapsed");
  });

  it("calls onToggle when toggle button is clicked", () => {
    const onToggle = vi.fn();
    renderSidebar(false, onToggle);
    const toggleBtn = screen.getByRole("button");
    fireEvent.click(toggleBtn);
    expect(onToggle).toHaveBeenCalledTimes(1);
  });

  it("links have correct paths", () => {
    renderSidebar();
    const links = screen.getAllByRole("link");
    const paths = links.map((l) => l.getAttribute("href"));
    expect(paths).toContain("/");
    expect(paths).toContain("/prices");
    expect(paths).toContain("/merchants");
    expect(paths).toContain("/logistics");
    expect(paths).toContain("/orders");
    expect(paths).toContain("/settings");
  });
});
