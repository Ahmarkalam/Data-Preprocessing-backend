import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, LogOut, Settings, BarChart3, Database } from 'lucide-react';

const Layout = ({ children, onLogout }) => {
  const navLinkClass = ({ isActive }) => 
    `flex items-center gap-3 w-full p-3 rounded-lg transition-all ${
      isActive 
        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/20' 
        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
    }`;

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col fixed h-full z-10 transition-all duration-300">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
              <Database className="text-white" size={18} />
            </div>
            <span className="font-bold text-white text-lg tracking-tight">DataPrep AI</span>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Menu</div>
          
          <NavLink to="/dashboard" className={navLinkClass}>
            <LayoutDashboard size={20} /> 
            <span className="font-medium">Dashboard</span>
          </NavLink>
          
          <NavLink to="/analytics" className={navLinkClass}>
            <BarChart3 size={20} /> 
            <span className="font-medium">Analytics</span>
          </NavLink>

          <NavLink to="/settings" className={navLinkClass}>
            <Settings size={20} /> 
            <span className="font-medium">Settings</span>
          </NavLink>
        </nav>
        
        <div className="p-4 border-t border-slate-800">
          <button 
            onClick={onLogout} 
            className="flex items-center gap-3 w-full p-3 hover:bg-red-900/20 text-slate-400 hover:text-red-400 rounded-lg transition-all"
          >
            <LogOut size={20} /> 
            <span className="font-medium">Disconnect</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-20 px-8 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800">Overview</h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-full border border-green-200 text-sm font-medium">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              System Operational
            </div>
            <div className="w-8 h-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm">
              AD
            </div>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
