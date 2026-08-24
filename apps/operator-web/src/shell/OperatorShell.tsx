import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import {
  BarChart3,
  CalendarDays,
  ChevronDown,
  LayoutDashboard,
  LogOut,
  MapPinned,
  QrCode,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../state/AuthContext";

const navigation = [
  { to: "/app", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/app/facilities", label: "Facilities", icon: MapPinned },
  { to: "/app/reservations", label: "Reservations", icon: CalendarDays },
  { to: "/app/scanner", label: "Scanner", icon: QrCode },
  { to: "/app/reports", label: "Reports", icon: BarChart3 },
];

export function OperatorShell() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  async function signOut() {
    await logout();
    navigate("/", { replace: true });
  }
  return (
    <div className="app-shell">
      <aside className="side-rail">
        <NavLink to="/app" className="brand" aria-label="ParkingPro overview">
          Parking<span>Pro</span>
        </NavLink>
        <nav aria-label="Operator navigation">
          {navigation.map(({ to, label, icon: Icon, end = false }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                isActive ? "nav-item active" : "nav-item"
              }
            >
              <Icon aria-hidden="true" size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="workspace">
        <header className="top-bar">
          <span className="live-indicator">
            <i /> Last updated just now
          </span>
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <button
                aria-label="Open operator account menu"
                className="user-menu-trigger"
                type="button"
              >
                {user?.full_name} <ChevronDown aria-hidden="true" size={16} />
              </button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
              <DropdownMenu.Content
                align="end"
                className="user-menu-content"
                sideOffset={8}
              >
                <DropdownMenu.Label className="user-menu-label">
                  {user?.email}
                </DropdownMenu.Label>
                <DropdownMenu.Separator className="user-menu-separator" />
                <DropdownMenu.Item
                  className="user-menu-item"
                  onSelect={() => void signOut()}
                >
                  <LogOut aria-hidden="true" size={16} /> Sign out securely
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
