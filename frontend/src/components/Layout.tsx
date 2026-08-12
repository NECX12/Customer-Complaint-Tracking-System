import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/* ── SVG Icons (inline for zero dependencies) ────────────────── */

const icons = {
  dashboard: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  ),
  complaints: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  users: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  logout: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  ),
  plus: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
    </svg>
  ),
};

/* ── Role badge ──────────────────────────────────────────────── */

const roleBadgeColors: Record<string, string> = {
  CUSTOMER: 'from-emerald-500/20 to-emerald-500/5 text-emerald-400 border-emerald-500/20',
  AGENT: 'from-purple-500/20 to-purple-500/5 text-purple-400 border-purple-500/20',
  ADMIN: 'from-amber-500/20 to-amber-500/5 text-amber-400 border-amber-500/20',
};

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = getNavItems(user.role);

  return (
    <div className="min-h-screen flex">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="w-64 fixed inset-y-0 left-0 z-30 flex flex-col bg-gray-900/80 backdrop-blur-xl border-r border-gray-800/60">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-gray-800/60">
          <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Mikano
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">Complaint Tracker</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User card */}
        <div className="px-3 pb-4">
          <div className="glass-card p-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-600 to-cyan-600 flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-blue-500/20">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-200 truncate">{user.name}</p>
                <span className={`inline-flex items-center px-2 py-0.5 text-[10px] font-semibold rounded-full border bg-gradient-to-r ${roleBadgeColors[user.role]}`}>
                  {user.role}
                </span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-gray-400 bg-gray-800/50 rounded-lg border border-gray-700/40 hover:text-red-400 hover:border-red-500/30 hover:bg-red-500/10 transition-all duration-200"
            >
              {icons.logout}
              Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main Content ────────────────────────────────────── */}
      <main className="flex-1 ml-64">
        <div className="px-8 py-6 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

/* ── Navigation items per role ────────────────────────────────── */

function getNavItems(role: string) {
  const items = [
    { to: '/dashboard', label: 'Dashboard', icon: icons.dashboard },
    { to: '/complaints', label: 'Complaints', icon: icons.complaints },
  ];

  if (role === 'CUSTOMER') {
    items.push({ to: '/complaints/new', label: 'New Complaint', icon: icons.plus });
  }

  if (role === 'ADMIN') {
    items.push({ to: '/users', label: 'Users', icon: icons.users });
  }

  return items;
}
