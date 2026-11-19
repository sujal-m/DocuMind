import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Activity, ShieldCheck, Sparkles } from 'lucide-react';
import api from '../../services/api';

export default function Navbar() {
  const location = useLocation();
  const [backendHealthy, setBackendHealthy] = useState(null);

  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/': return 'System Dashboard';
      case '/documents': return 'Document Knowledge Base';
      case '/workspace': return 'AI Research Workspace';
      case '/evaluation': return 'Retrieval & Quality Evaluation';
      case '/settings': return 'System Settings';
      default: return 'DocuMind Intelligence';
    }
  };

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.get('/health', { timeout: 3000 });
        setBackendHealthy(true);
      } catch (e) {
        setBackendHealthy(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-8 z-10 sticky top-0">
      <div>
        <h2 className="text-base font-semibold text-white tracking-tight">
          {getPageTitle(location.pathname)}
        </h2>
        <p className="text-xs text-slate-400">Autonomous Grounded Document Research</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Health status badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              backendHealthy === true
                ? 'bg-emerald-400'
                : backendHealthy === false
                ? 'bg-rose-400'
                : 'bg-amber-400'
            }`}
          />
          <span className="text-slate-300 font-medium">
            {backendHealthy === true ? 'Backend Connected' : backendHealthy === false ? 'Offline' : 'Checking...'}
          </span>
        </div>

        {/* Gemini Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-950/50 border border-indigo-800/60 text-xs text-indigo-300">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Gemini 2.5 Flash</span>
        </div>
      </div>
    </header>
  );
}

