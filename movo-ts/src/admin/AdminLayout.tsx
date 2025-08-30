import { NavLink, Outlet } from "react-router-dom";

export default function AdminLayout() {
  const item = (to: string, label: string) => (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `block px-4 py-3 rounded-lg mb-2 ${isActive ? 'bg-violet-600 text-white' : 'hover:bg-zinc-100'}`
      }
    >
      {label}
    </NavLink>
  );

  return (
    <div className="flex h-screen">
      <aside className="w-64 p-4 border-e bg-white">
        <h1 className="font-bold mb-4">Supervisor</h1>
        <a href="/" className="block text-sm text-violet-700 hover:underline mb-3">↩ Back to Main</a>
        {item("/admin/orders", "Orders")}
        {item("/admin/analytics", "AI Analytics")}
        {item("/admin/notifications", "Notifications")}
      </aside>
      <main className="flex-1 overflow-auto bg-zinc-50 p-4">
        <Outlet />
      </main>
    </div>
  );
}


