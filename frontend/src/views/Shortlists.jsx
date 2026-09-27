import React from 'react';
import { CheckCircle2, ChevronRight, Download } from 'lucide-react';

export default function Shortlists({ candidates, onSelectCandidate, shortlistThreshold }) {
  const shortlisted = candidates.filter(
    c => c.recruiter_status === 'Shortlisted' || c.recruiter_status === 'Interview' || c.job_fit_score >= shortlistThreshold
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Shortlisted Candidates</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {shortlisted.length} candidates qualified for interview pipeline and review.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {shortlisted.map(c => (
          <div 
            key={c.filename}
            onClick={() => onSelectCandidate(c.filename)}
            className="bg-white border border-slate-200 hover:border-slate-300 rounded-lg p-4 flex items-center justify-between cursor-pointer transition-all shadow-2xs group"
          >
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400">#{String(c.rank).padStart(2, '0')}</span>
                <span className="text-sm font-semibold text-slate-900 group-hover:text-brand-600 transition-colors">{c.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {c.recruiter_status || 'Shortlisted'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {c.experience?.relevant_experience_years?.toFixed(1)} yrs domain exp · Skills: {c.matched_required?.join(', ')}
              </p>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <div className="text-base font-bold text-slate-900">{c.job_fit_score?.toFixed(1)}%</div>
                <div className="text-[10px] font-bold text-slate-400 uppercase">Job Fit</div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-brand-600 transition-colors" />
            </div>
          </div>
        ))}

        {shortlisted.length === 0 && (
          <div className="p-8 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-lg">
            No candidates currently meet the shortlist criteria.
          </div>
        )}
      </div>
    </div>
  );
}
