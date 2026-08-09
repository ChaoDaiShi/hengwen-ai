import { theme as antdTheme, type ThemeConfig } from "antd";

const light = {
  colorPrimary: "#3e5c76",
  colorInfo: "#3e5c76",
  colorSuccess: "#5b7261",
  colorWarning: "#a9813b",
  colorError: "#a34a3e",
  colorText: "#1c1b19",
  colorTextSecondary: "#5c5953",
  colorTextTertiary: "#8a867e",
  colorTextDisabled: "#b4b0a8",
  colorBgBase: "#fbfaf8",
  colorBgLayout: "#fbfaf8",
  colorBgContainer: "#ffffff",
  colorBorder: "#e6e3dd",
  colorBorderSecondary: "#e6e3dd",
  borderRadius: 4,
  fontSize: 15,
  lineHeight: 1.7,
  controlHeight: 40,
};

const dark = {
  colorPrimary: "#7d9db8",
  colorInfo: "#7d9db8",
  colorSuccess: "#7d9a86",
  colorWarning: "#c2a262",
  colorError: "#c46758",
  colorText: "#edeae4",
  colorTextSecondary: "#b8b3aa",
  colorTextTertiary: "#7d7870",
  colorTextDisabled: "#56524c",
  colorBgBase: "#17161a",
  colorBgLayout: "#17161a",
  colorBgContainer: "#1e1d22",
  colorBorder: "#32302f",
  colorBorderSecondary: "#32302f",
  borderRadius: 4,
  fontSize: 15,
  lineHeight: 1.7,
  controlHeight: 40,
};

export function buildTheme(isDark: boolean): ThemeConfig {
  const palette = isDark ? dark : light;
  return {
    algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    token: {
      ...palette,
      fontFamily:
        "'Inter', 'PingFang SC', 'HarmonyOS Sans SC', 'Microsoft YaHei', system-ui, sans-serif",
      fontFamilyCode: "'JetBrains Mono', ui-monospace, 'SF Mono', monospace",
      boxShadow: "0 1px 2px rgba(28,27,25,.04), 0 4px 12px rgba(28,27,25,.06)",
    },
    components: {
      Button: {
        fontWeight: 500,
        borderRadius: 4,
      },
      Card: {
        borderRadiusLG: 8,
      },
      Input: {
        activeBorderColor: palette.colorPrimary,
        hoverBorderColor: palette.colorPrimary,
        paddingInline: 12,
      },
      Table: {
        headerBg: "transparent",
        headerColor: palette.colorTextSecondary,
        headerSplitColor: "transparent",
        rowHoverBg: isDark ? "#2a2931" : "#f0eee9",
        cellPaddingBlock: 12,
        cellPaddingInline: 16,
      },
      Tabs: {
        inkBarColor: palette.colorPrimary,
        itemSelectedColor: palette.colorPrimary,
        itemColor: palette.colorTextSecondary,
        itemHoverColor: palette.colorPrimary,
      },
      Tag: {
        borderRadiusSM: 4,
      },
      Progress: {
        defaultColor: palette.colorPrimary,
        remainingColor: palette.colorBorder,
        lineBorderRadius: 2,
      },
      Modal: {
        paddingContentHorizontalLG: 32,
        paddingContentVerticalLG: 32,
      },
      Drawer: {
        paddingLG: 32,
      },
      Switch: {
        colorPrimary: palette.colorPrimary,
      },
      Menu: {
        itemSelectedColor: palette.colorPrimary,
      },
    },
  };
}
