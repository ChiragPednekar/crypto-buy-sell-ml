import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, LogOut, LayoutDashboard, Briefcase, BarChart2 } from 'lucide-react';

export default function Navbar({ onLogout }) {
  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
      isActive ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
    }`;

  return (
    <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">
        
        <div className="flex items-center gap-2 text-xl font-bold">
          <Activity className="text-blue-500 w-6 h-6" />
          <span className="bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            AI BTC Trader
          </span>
        </div>

        <div className="flex items-center gap-2 md:gap-6 font-medium text-sm">
          <NavLink to="/" end className={linkClass}>
            <LayoutDashboard className="w-4 h-4" />
            <span className="hidden md:inline">Dashboard</span>
          </NavLink>
          
          <NavLink to="/portfolio" className={linkClass}>
            <Briefcase className="w-4 h-4" />
            <span className="hidden md:inline">Portfolio</span>
          </NavLink>
          
          <NavLink to="/trade" className={linkClass}>
            <BarChart2 className="w-4 h-4" />
            <span className="hidden md:inline">Trade</span>
          </NavLink>
        </div>

        <button 
          onClick={onLogout}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-400 hover:text-rose-400 hover:bg-slate-800/50 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden md:inline">Logout</span>
        </button>

      </div>
    </nav>
  );
}
