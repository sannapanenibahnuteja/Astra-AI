import "./Sidebar.css";

import {
  House,
  MessageSquare,
  Folder,
  Globe,
  Bot,
  Brain,
  Palette,
  Package,
  Settings,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const menu = [
  { icon: House, label: "Home", path: "/" },

  { icon: MessageSquare, label: "Chat", path: "/chat" },

  { icon: Folder, label: "Files", path: "/files" },

  { icon: Globe, label: "Browser", path: "/browser" },

  { icon: Bot, label: "Automation", path: "/automation" },

  { icon: Brain, label: "Memory", path: "/memory" },

  { icon: Palette, label: "Themes", path: "/themes" },

  { icon: Package, label: "Plugins", path: "/plugins" },

  { icon: Settings, label: "Settings", path: "/settings" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h1>⚡ ASTRA</h1>

      <nav>
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "active nav-link" : "nav-link"
              }
            >
              <Icon size={20} />

              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="profile">
        <div className="avatar">B</div>

        <div>
          <strong>Bhanu</strong>

          <p>Developer</p>
        </div>
      </div>
    </aside>
  );
}