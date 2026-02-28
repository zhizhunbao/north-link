/**
 * Sidebar navigation — INFRA-009.
 * Collapsible sidebar with navigation links and active state.
 */
import { NavLink } from "react-router-dom";
import {
  DashboardOutlined,
  ShoppingOutlined,
  TeamOutlined,
  CarOutlined,
  SettingOutlined,
  FileTextOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from "@ant-design/icons";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const NAV_ITEMS = [
  { path: "/", icon: <DashboardOutlined />, label: "Dashboard" },
  { path: "/prices", icon: <ShoppingOutlined />, label: "比价中心" },
  { path: "/merchants", icon: <TeamOutlined />, label: "商户管理" },
  { path: "/logistics", icon: <CarOutlined />, label: "物流管理" },
  { path: "/orders", icon: <FileTextOutlined />, label: "订单中心" },
  { path: "/settings", icon: <SettingOutlined />, label: "系统设置" },
];

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">N</div>
        <span className="sidebar-logo-text">North Link</span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <span className="nav-item-icon">{item.icon}</span>
            <span className="nav-item-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </button>
      </div>
    </aside>
  );
}
