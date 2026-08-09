import { lazy, Suspense, useEffect } from "react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { App as AntdApp, ConfigProvider } from "antd";
import AppLayout from "./layout/AppLayout";
import { buildTheme } from "./theme";
import { useDarkMode } from "./hooks/useDarkMode";
import { ANALYSIS_STAGES } from "./lib/analysisStages";
import { useAppStore } from "./store/useAppStore";

const HomePage = lazy(() => import("./pages/HomePage"));
const AnalyzingPage = lazy(() => import("./pages/AnalyzingPage"));
const ReportPage = lazy(() => import("./pages/ReportPage"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));

function RouteFallback() {
  return (
    <div
      className="flex min-h-[40svh] items-center justify-center text-small text-ink-3"
      role="status"
      aria-live="polite"
    >
      正在打开页面…
    </div>
  );
}

export default function App() {
  const dark = useDarkMode();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const timer = window.setInterval(() => {
      const state = useAppStore.getState();
      if (!state.analysis) return;

      if (state.analysis.stageIndex >= ANALYSIS_STAGES.length - 1) {
        const report = state.completeAnalysis();
        if (report && location.pathname === "/analyzing") {
          navigate(`/report/${report.id}`, { replace: true });
        }
        return;
      }

      state.advanceAnalysis();
    }, 900);

    return () => window.clearInterval(timer);
  }, [location.pathname, navigate]);

  return (
    <ConfigProvider theme={buildTheme(dark)}>
      <AntdApp>
        <Suspense fallback={<RouteFallback />}>
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
