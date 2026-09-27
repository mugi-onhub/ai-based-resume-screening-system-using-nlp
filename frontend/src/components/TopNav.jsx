import React from 'react';
import { Search, Bell, Sparkles, RefreshCw } from 'lucide-react';

export default function TopNav({ activeJob, onReloadSamples, loading }) {
  return (
    <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
      {/* Breadcrumbs Context */}
      <div className="flex items-center gap-2 text-xs">
        <span className="text-slate-400 font-medium">Requisitions</span>
        <span className="text-slate-300">/</span>
        <span className="text-slate-600 font-medium">{activeJob?.department || 'Engineering'}</span>
        <span className="text-slate-300">/</span>
        <span className="text-slate-900 font-semibold">{activeJob?.title || 'Active Role'}</span>
      </div>

      {/* Actions & Utilities */}
      <div className="flex items-center gap-3">
        <button
          onClick={onReloadSamples}
          disabled={loading}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors disabled:opacity-50"
          title="Reset and reload the 10 sample candidates"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Reload Sample Pool</span>
        </button>

        <div className="h-4 w-px bg-slate-200" />

        <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-semibold shadow-xs">
          HR
        </div>
      </div>
    </header>
  );
}
