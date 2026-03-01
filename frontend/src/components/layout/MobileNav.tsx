/**
 * Mobile bottom navigation — INFRA-009.
 * Shows on screens ≤768px as bottom tab bar.
 */
import { NavLink } from "react-router-dom";
import {
  DashboardOutlined,
  ShoppingOutlined,
  SettingOutlined,
  RobotOutlined,
  BellOutlined,
} from "@ant-design/icons";

const MOBILE_ITEMS = [
  { path: "/chat", icon: <RobotOutlined />, label: "AI" },
  { path: "/", icon: <DashboardOutlined />, label: "首页" },
  { path: "/prices", icon: <ShoppingOutlined />, label: "比价" },
  { path: "/subscriptions", icon: <BellOutlined />, label: "订阅" },
  { path: "/settings", icon: <SettingOutlined />, label: "设置" },
];

export function MobileNav() {
  return (
    <nav className="mobile-nav">
      <div className="mobile-nav-items">
        {MOBILE_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `mobile-nav-item ${isActive ? "active" : ""}`
            }
          >
            <span className="mobile-nav-item-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
