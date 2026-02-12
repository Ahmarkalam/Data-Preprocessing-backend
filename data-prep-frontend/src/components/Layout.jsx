import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  LogOut,
  Settings,
  BarChart3,
  Database,
  Menu,
  X,
  Bell,
} from 'lucide-react';

const navigationItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/settings', label: 'Settings', icon: Settings },
];

const Layout = ({ children, onLogout }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinkClass = ({ isActive }) =>
    `flex items-center gap-3 w-full p-3 rounded-xl transition-all ${
      isActive
        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/30'
        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
    }`;

  const sidebarContent = (
    <>
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-indigo-500 rounded-xl flex items-center justify-center shadow-md shadow-indigo-900/40">
            <Database className="text-white" size={18} />
          </div>
          <div>
            <span className="font-bold text-white text-lg tracking-tight block">DataPrep AI</span>
            <span className="text-xs text-slate-400">Control Center</span>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Menu</div>

        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={navLinkClass}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button
          onClick={onLogout}
          className="flex items-center gap-3 w-full p-3 hover:bg-red-900/25 text-slate-300 hover:text-red-300 rounded-xl transition-all"
        >
          <LogOut size={20} />
          <span className="font-medium">Disconnect</span>
        </button>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-slate-50">
      {isMobileMenuOpen && (
        <button
          aria-label="Close menu overlay"
          onClick={() => setIsMobileMenuOpen(false)}
          className="fixed inset-0 z-30 bg-slate-950/55 backdrop-blur-sm lg:hidden"
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-40 h-full w-72 bg-slate-900 text-slate-200 flex flex-col transition-transform duration-300 ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
      >
        {sidebarContent}
      </aside>

      <main className="min-h-screen lg:ml-72">
        <header className="h-16 bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-20 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsMobileMenuOpen((prev) => !prev)}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div>
              <h2 className="font-semibold text-slate-800 leading-tight">Overview</h2>
              <p className="text-xs text-slate-500 hidden sm:block">Manage preprocessing jobs and monitor quality</p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-200 text-sm font-medium">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              System Operational
            </div>
            <button className="relative p-2 rounded-lg hover:bg-slate-100 text-slate-600" aria-label="Notifications">
              <Bell size={18} />
              <span className="absolute top-1 right-1 h-2 w-2 bg-indigo-500 rounded-full" />
            </button>
            <div className="w-9 h-9 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm">
              AD
            </div>
          </div>
        </header>

        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
};

export default Layout;
