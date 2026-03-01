/**
 * Unit tests for theme configuration.
 */
import { describe, it, expect } from "vitest";
import { theme } from "../theme";

describe("theme", () => {
  it("exports a valid ThemeConfig object", () => {
    expect(theme).toBeDefined();
    expect(theme.token).toBeDefined();
    expect(theme.components).toBeDefined();
  });

  it("defines primary color in HSL format", () => {
    expect(theme.token?.colorPrimary).toMatch(/^hsl\(/);
  });

  it("defines correct border radius values", () => {
    expect(theme.token?.borderRadius).toBe(8);
    expect(theme.token?.borderRadiusLG).toBe(12);
    expect(theme.token?.borderRadiusSM).toBe(6);
  });

  it("defines Inter font family", () => {
    expect(theme.token?.fontFamily).toContain("Inter");
    expect(theme.token?.fontFamily).toContain("PingFang SC");
  });

  it("defines motion durations", () => {
    expect(theme.token?.motionDurationSlow).toBe("0.3s");
    expect(theme.token?.motionDurationMid).toBe("0.2s");
    expect(theme.token?.motionDurationFast).toBe("0.15s");
  });

  it("configures Button component", () => {
    expect(theme.components?.Button).toBeDefined();
    expect(theme.components?.Button?.borderRadius).toBe(8);
    expect(theme.components?.Button?.controlHeight).toBe(40);
  });

  it("configures Card component", () => {
    expect(theme.components?.Card?.borderRadiusLG).toBe(12);
  });

  it("configures Input component", () => {
    expect(theme.components?.Input?.borderRadius).toBe(8);
    expect(theme.components?.Input?.controlHeight).toBe(40);
  });

  it("configures Select component", () => {
    expect(theme.components?.Select?.borderRadius).toBe(8);
  });

  it("configures Table component", () => {
    expect(theme.components?.Table?.borderRadiusLG).toBe(12);
  });

  it("defines semantic colors", () => {
    expect(theme.token?.colorSuccess).toMatch(/^hsl\(/);
    expect(theme.token?.colorWarning).toMatch(/^hsl\(/);
    expect(theme.token?.colorError).toMatch(/^hsl\(/);
  });

  it("sets base font size to 14", () => {
    expect(theme.token?.fontSize).toBe(14);
  });
});
