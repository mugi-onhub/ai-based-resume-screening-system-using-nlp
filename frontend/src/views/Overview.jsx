import React from 'react';
import { 
  Users, 
  CheckCircle2, 
  TrendingUp, 
  Sparkles, 
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';

export default function Overview({ overview, candidates, onSelectCandidate, onNavigate }) {
  const metrics = overview?.metrics || {
    total_candidates: 0,
    shortlisted_count: 0,
    avg_match: 0,
    strong_matches: 0,
    interview_ready: 0,
  };

  const distribution = overview?.distribution || { strong: 0, good: 0, review: 0, low: 0 };
  const total = metrics.total_candidates || 1;

  const distItems = [
    { label: 'Strong match (≥80%)', count: distribution.strong, color: 'bg-emerald-500', barColor: 'bg-emerald-500' },
    { label: 'Good match (65-79%)', count: distribution.good, color: 'bg-brand-600', barColor: 'bg-brand-600' },
    { label: 'Review (50-64%)', count: distribution.review, color: 'bg-amber-500', barColor: 'bg-amber-500' },
    { label: 'Low match (<50%)', count: distribution.low, color: 'bg-rose-500', barColor: 'bg-rose-500' },
  ];

  const topCandidate = candidates[0];

  return (
    <div className="space-y-6">
      {/* Role Hero Card */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">{overview?.job?.title}</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {metrics.total_candidates} candidates analyzed · {metrics.shortlisted_count} shortlisted · Active Requisition
          </p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => onNavigate('shortlists')}
            className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
          >
            Review shortlist
          </button>
          <button 
            onClick={() => onNavigate('jobs')}
            className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-md shadow-2xs transition-colors"
          >
            Manage job
          </button>
        </div>
      </div>

      {/* Restrained Horizontal Metric Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 bg-white border border-slate-200 rounded-lg p-4 shadow-2xs divide-y md:divide-y-0 md:divide-x divide-slate-100">
        <div className="px-3 py-1 md:py-0">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Candidates</span>
          <div className="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">{metrics.total_candidates}</div>
          <span className="text-[11px] text-slate-400 block mt-0.5">Total parsed</span>
        </div>
        <div className="px-3 py-1 md:py-0">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Shortlisted</span>
          <div className="text-2xl font-bold text-emerald-600 tracking-tight mt-0.5">{metrics.shortlisted_count}</div>
          <span className="text-[11px] text-slate-400 block mt-0.5">Fit score ≥ {overview?.shortlist_threshold}%</span>
        </div>
        <div className="px-3 py-1 md:py-0">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Avg. Match</span>
          <div className="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">{metrics.avg_match}%</div>
          <span className="text-[11px] text-slate-400 block mt-0.5">Pool average</span>
        </div>
        <div className="px-3 py-1 md:py-0">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Strong Matches</span>
          <div className="text-2xl font-bold text-slate-900 tracking-tight mt-0.5">{metrics.strong_matches}</div>
          <span className="text-[11px] text-slate-400 block mt-0.5">Score ≥ 80%</span>
        </div>
        <div className="px-3 py-1 md:py-0">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Interview Ready</span>
          <div className="text-2xl font-bold text-brand-600 tracking-tight mt-0.5">{metrics.interview_ready}</div>
          <span className="text-[11px] text-slate-400 block mt-0.5">In pipeline</span>
        </div>
      </div>

      {/* Main Grid: Candidates List + Intelligence Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Candidates List Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Recommended Candidates</h2>
              <p className="text-xs text-slate-500">AI-ranked based on skills, experience, projects, and contextual embeddings.</p>
            </div>
            <button 
              onClick={() => onNavigate('candidates')}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              View all <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2">
            {candidates.slice(0, 7).map((c) => {
              const initials = c.name.replace(/[^a-zA-Z ]/g, '').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase() || 'CA';
              const isStrong = c.match_level === 'Strong Match';
              const isGood = c.match_level === 'Good Match';
              const isReview = c.match_level === 'Review';

              return (
                <div 
                  key={c.filename}
                  onClick={() => onSelectCandidate(c.filename)}
                  className="bg-white border border-slate-200 hover:border-slate-300 hover:shadow-sm rounded-lg p-3.5 flex items-center justify-between cursor-pointer transition-all group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-md bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs shrink-0 group-hover:bg-brand-50 group-hover:text-brand-600 transition-colors">
                      {initials}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-400">#{String(c.rank).padStart(2, '0')}</span>
                        <span className="text-sm font-semibold text-slate-900 truncate group-hover:text-brand-600 transition-colors">
                          {c.name}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 truncate mt-0.5">
                        {c.experience?.relevant_experience_years?.toFixed(1)} yrs relevant exp · {c.matched_required?.length}/{c.all_required?.length} skills verified
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 shrink-0">
                    {/* Score Bar */}
                    <div className="text-right">
                      <div className="text-sm font-bold text-slate-900">{c.job_fit_score?.toFixed(1)}%</div>
                      <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-1">
                        <div 
                          className={`h-full rounded-full ${isStrong ? 'bg-emerald-500' : isGood ? 'bg-brand-600' : isReview ? 'bg-amber-500' : 'bg-rose-500'}`}
                          style={{ width: `${c.job_fit_score}%` }}
                        />
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div className="w-24 text-right">
                      <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold ${
                        isStrong ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                        isGood ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                        isReview ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}>
                        {c.match_level}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Intelligence Sidebar Column */}
        <div className="space-y-6">
          {/* Hiring Intelligence Editorial Callout */}
          <div className="bg-slate-900 text-white rounded-lg p-4.5 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Hiring Intelligence</h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              <strong>{metrics.strong_matches} candidates</strong> meet or exceed all core mandatory requirements.
            </p>
            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="text-slate-400 font-medium">Strongest signal:</div>
              <div className="text-emerald-300 font-semibold">Python + Machine Learning + SQL</div>
            </div>
            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="text-slate-400 font-medium">Recommendation:</div>
              <div>Prioritize <strong className="text-white">{topCandidate?.name || 'top candidate'}</strong> for technical interview round.</div>
            </div>
          </div>

          {/* Candidate Distribution Progress */}
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-2xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Candidate Distribution</h3>
            <p className="text-xs text-slate-500">Breakdown of applicant match levels across active pool.</p>

            <div className="space-y-2.5 pt-1">
              {distItems.map(item => {
                const pct = Math.round((item.count / total) * 100);
                return (
                  <div key={item.label}>
                    <div className="flex justify-between text-xs text-slate-700 mb-1">
                      <span>{item.label}</span>
                      <span className="font-semibold text-slate-900">{item.count} ({pct}%)</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full ${item.barColor} rounded-full`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
