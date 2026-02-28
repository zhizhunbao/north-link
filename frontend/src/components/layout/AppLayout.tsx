/**
 * Main application layout — INFRA-009.
 * Desktop: sidebar + content area.
 * Mobile: content + bottom tab nav.
 */
import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { MobileNav } from "./MobileNav";
import "./AppLayout.css";

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`app-layout ${collapsed ? "collapsed" : ""}`}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <main className="app-content">
        <Outlet />
      </main>
      <MobileNav />
    </div>
  );
}
