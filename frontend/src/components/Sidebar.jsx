import React from 'react';
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  CheckCircle2, 
  UserCheck, 
  Scale, 
  SlidersHorizontal, 
  BarChart3, 
  Settings as SettingsIcon,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ currentView, setCurrentView, jobsData, activeJobId, onSelectJob, blindMode, onToggleBlind, shortlistThreshold, onChangeThreshold }) {
  const workspaceItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'jobs', label: 'Jobs', icon: Briefcase },
    { id: 'candidates', label: 'Candidates', icon: Users },
    { id: 'shortlists', label: 'Shortlists', icon: CheckCircle2 },
  ];

  const intelligenceItems = [
    { id: 'fairness', label: 'Fairness & Blind Audit', icon: Scale },
    { id: 'whatif', label: 'What-If Simulator', icon: SlidersHorizontal },
  ];

  const managementItems = [
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings & Scoring', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen select-none shrink-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-md bg-slate-900 flex items-center justify-center text-white shadow-sm">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div>
          <span className="font-bold text-slate-900 tracking-tight text-base block leading-none">CAREERPILOT</span>
          <span className="text-[11px] font-medium text-slate-400 mt-0.5 block">AI Recruitment Intelligence</span>
        </div>
      </div>

      {/* Requisition Context Switcher */}
      <div className="p-3.5 border-b border-slate-100 bg-slate-50/50">
        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
          Active Requisition
        </label>
        <select 
          value={activeJobId} 
          onChange={(e) => onSelectJob(e.target.value)}
          className="w-full text-xs font-medium bg-white border border-slate-200 rounded-md py-1.5 px-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 shadow-2xs"
        >
          {jobsData.map(j => (
            <option key={j.id} value={j.id}>{j.title}</option>
          ))}
        </select>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2.5 mb-1.5 block">
            Workspace
          </span>
          <div className="space-y-0.5">
            {workspaceItems.map(item => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive 
                      ? 'bg-slate-100 text-slate-900 font-semibold' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2.5 mb-1.5 block">
            Intelligence
          </span>
          <div className="space-y-0.5">
            {intelligenceItems.map(item => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive 
                      ? 'bg-slate-100 text-slate-900 font-semibold' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2.5 mb-1.5 block">
            Management
          </span>
          <div className="space-y-0.5">
            {managementItems.map(item => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive 
                      ? 'bg-slate-100 text-slate-900 font-semibold' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Global Quick Controls */}
      <div className="p-3.5 border-t border-slate-100 bg-slate-50/50 space-y-3">
        <div>
          <div className="flex justify-between text-[11px] font-medium text-slate-600 mb-1">
            <span>Shortlist Cutoff</span>
            <span className="font-semibold text-slate-900">{shortlistThreshold}%</span>
          </div>
          <input 
            type="range" 
            min="40" 
            max="90" 
            value={shortlistThreshold} 
            onChange={(e) => onChangeThreshold(Number(e.target.value))}
            className="w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
        </div>

        <label className="flex items-center gap-2 cursor-pointer pt-1">
          <input 
            type="checkbox" 
            checked={blindMode} 
            onChange={onToggleBlind} 
            className="rounded text-brand-600 focus:ring-brand-500 h-3.5 w-3.5 border-slate-300"
          />
          <span className="text-xs font-medium text-slate-700 select-none">Blind screening mode</span>
        </label>
      </div>

      {/* Footer Legal & User Info */}
      <div className="p-3 border-t border-slate-100 text-[10px] text-slate-400 flex items-center gap-1.5">
        <ShieldCheck className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span>Decision-support platform</span>
      </div>
    </aside>
  );
}
