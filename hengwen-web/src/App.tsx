import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import { App as AntdApp, ConfigProvider } from "antd";
import AppLayout from "./layout/AppLayout";
import { buildTheme } from "./theme";
import { useDarkMode } from "./hooks/useDarkMode";

const HomePage = lazy(() => import("./pages/HomePage"));
const AnalyzingPage = lazy(() => import("./pages/AnalyzingPage"));
const ReportPage = lazy(() => import("./pages/ReportPage"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));

export default function App() {
  const dark = useDarkMode();

  return (
    <ConfigProvider theme={buildTheme(dark)}>
      <AntdApp>
        <Suspense fallback={null}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/analyzing" element={<AnalyzingPage />} />
              <Route path="/report/:id" element={<ReportPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<HomePage />} />
            </Route>
          </Routes>
        </Suspense>
      </AntdApp>
    </ConfigProvider>
  );
}
