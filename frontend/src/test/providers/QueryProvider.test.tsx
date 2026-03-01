/**
 * Unit tests for QueryProvider.
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryProvider } from "../../providers/QueryProvider";

describe("QueryProvider", () => {
  it("renders children correctly", () => {
    render(
      <QueryProvider>
        <div data-testid="child">Hello</div>
      </QueryProvider>,
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("renders multiple children", () => {
    render(
      <QueryProvider>
        <div data-testid="child-1">First</div>
        <div data-testid="child-2">Second</div>
      </QueryProvider>,
    );
    expect(screen.getByTestId("child-1")).toBeInTheDocument();
    expect(screen.getByTestId("child-2")).toBeInTheDocument();
  });
});
