import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Files, 
  BrainCircuit, 
  LineChart, 
  Settings as SettingsIcon,
  PlusCircle,
  Database,
  CheckCircle2
} from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/documents', label: 'Document Library', icon: Files },
    { to: '/workspace', label: 'Research Workspace', icon: BrainCircuit },
    { to: '/evaluation', label: 'Evaluation Suite', icon: LineChart },
    { to: '/settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between h-screen select-none">
      <div>
        {/* Brand */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <BrainCircuit className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight">DocuMind</h1>
            <p className="text-[10px] uppercase font-semibold tracking-wider text-indigo-400">Intelligence Agent</p>
          </div>
        </div>

        {/* Quick Action */}
        <div className="p-4">
          <NavLink
            to="/workspace"
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition shadow-sm hover:shadow-indigo-500/25"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Research Chat</span>
          </NavLink>
        </div>

        {/* Navigation */}
        <nav className="px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                    isActive
                      ? 'bg-slate-800 text-indigo-400 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-slate-200">Local Vector Store</p>
            <p className="text-[11px] text-slate-500 truncate">FAISS IndexFlatIP Active</p>
          </div>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
      </div>
    </aside>
  );
}

