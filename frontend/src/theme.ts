/**
 * Ant Design 5 theme configuration — INFRA-006.
 * Maps CSS design tokens to Ant Design's token system.
 */
import type { ThemeConfig } from "antd";

export const theme: ThemeConfig = {
  token: {
    /* Primary */
    colorPrimary: "hsl(210, 85%, 52%)",
    colorInfo: "hsl(210, 85%, 52%)",
    colorSuccess: "hsl(152, 70%, 42%)",
    colorWarning: "hsl(38, 90%, 50%)",
    colorError: "hsl(0, 75%, 55%)",

    /* Typography */
    fontFamily:
      '"Inter", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif',
    fontSize: 14,

    /* Radius */
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,

    /* Motion */
    motionDurationSlow: "0.3s",
    motionDurationMid: "0.2s",
    motionDurationFast: "0.15s",
  },
  components: {
    Button: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Card: {
      borderRadiusLG: 12,
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Select: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Table: {
      borderRadiusLG: 12,
    },
  },
};
