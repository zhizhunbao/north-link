/**
 * Root application component with routing.
 * Wraps app in providers: Ant Design ConfigProvider + React Query.
 */
import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ConfigProvider, App as AntApp } from "antd";
import zhCN from "antd/locale/zh_CN";
import { theme } from "./theme";
import { QueryProvider } from "./providers/QueryProvider";
import { useAuthStore } from "./stores/useAuthStore";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import { AppLayout } from "./components/layout/AppLayout";
import { LoginPage } from "./pages/Login/Login";
import { DashboardPage } from "./pages/Dashboard/Dashboard";
import { PriceCenterPage } from "./pages/PriceCenter/PriceCenter";
import { MerchantPage } from "./pages/Merchant/Merchant";
import { LogisticsPage } from "./pages/Logistics/Logistics";
import { OrdersPage } from "./pages/Orders/Orders";
import { SettingsPage } from "./pages/Settings/Settings";

function AppRoutes() {
  const restoreAuth = useAuthStore((s) => s.restoreAuth);

  useEffect(() => {
    restoreAuth();
  }, [restoreAuth]);

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/prices" element={<PriceCenterPage />} />
          <Route path="/merchants" element={<MerchantPage />} />
          <Route path="/logistics" element={<LogisticsPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <ConfigProvider theme={theme} locale={zhCN}>
      <AntApp>
        <QueryProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </QueryProvider>
      </AntApp>
    </ConfigProvider>
  );
}
