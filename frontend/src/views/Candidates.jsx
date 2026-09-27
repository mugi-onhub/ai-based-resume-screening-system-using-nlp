import React, { useState } from 'react';
import { Search, Filter, Upload, Download, ChevronRight, CheckCircle2, RefreshCw } from 'lucide-react';

export default function Candidates({ candidates, onSelectCandidate, onUpload, loading }) {
  const [search, setSearch] = useState('');
  const [matchFilter, setMatchFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = candidates.filter(c => {
    const matchQuery = search.toLowerCase() === '' || 
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.candidate_skills?.some(s => s.toLowerCase().includes(search.toLowerCase()));

    const matchLevel = matchFilter === 'ALL' || c.match_level === matchFilter;
    const matchStatus = statusFilter === 'ALL' || (c.recruiter_status || 'New') === statusFilter;

    return matchQuery && matchLevel && matchStatus;
  });

  const handleFileUpload = (e) => {
    if (e.target.files?.length > 0) {
      onUpload(e.target.files);
    }
  };

  const exportCSV = () => {
    const rows = [
      ['Rank', 'Candidate Name', 'Job Fit Score', 'Match Level', 'Relevant Exp (Years)', 'Verified Skills', 'Status'],
      ...filtered.map(c => [
        c.rank,
        `"${c.name}"`,
        c.job_fit_score.toFixed(1),
        c.match_level,
        c.experience?.relevant_experience_years?.toFixed(1) || 0,
        `"${c.matched_required?.join(', ')}"`,
        c.recruiter_status || 'New'
      ])
    ];
    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(e => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'CAREERPILOT_Candidates.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Candidate Pipeline</h1>
          <p className="text-xs text-slate-500 mt-0.5">Filter, inspect, and manage candidate evaluations.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-md shadow-xs transition-colors cursor-pointer">
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Resumes</span>
            <input type="file" multiple accept=".pdf,.docx,.txt" onChange={handleFileUpload} className="hidden" />
          </label>
          <button 
            onClick={exportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-md shadow-2xs transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-2xs flex flex-wrap gap-3 items-center justify-between">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search candidate name or skill..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="text-xs bg-transparent w-full focus:outline-none text-slate-800 placeholder:text-slate-400"
          />
        </div>

        <div className="flex items-center gap-2">
          <select 
            value={matchFilter}
            onChange={e => setMatchFilter(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded px-2.5 py-1 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Match Levels</option>
            <option value="Strong Match">Strong Match</option>
            <option value="Good Match">Good Match</option>
            <option value="Review">Review</option>
            <option value="Low Match">Low Match</option>
          </select>

          <select 
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded px-2.5 py-1 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="New">New</option>
            <option value="Under Review">Under Review</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Interview">Interview</option>
            <option value="On Hold">On Hold</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Candidates Data Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-2xs overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-4">Candidate</th>
              <th className="py-3 px-4">Job Fit Score</th>
              <th className="py-3 px-4">Match Level</th>
              <th className="py-3 px-4">Relevant Exp</th>
              <th className="py-3 px-4">Required Skills</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(c => {
              const isStrong = c.match_level === 'Strong Match';
              const isGood = c.match_level === 'Good Match';
              const isReview = c.match_level === 'Review';

              return (
                <tr 
                  key={c.filename} 
                  onClick={() => onSelectCandidate(c.filename)}
                  className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-4 font-semibold text-slate-900 flex items-center gap-2">
                    <span className="text-slate-400 font-normal">#{String(c.rank).padStart(2, '0')}</span>
                    {c.name}
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">{c.job_fit_score?.toFixed(1)}%</td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                      isStrong ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      isGood ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                      isReview ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                      'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}>
                      {c.match_level}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-600">{c.experience?.relevant_experience_years?.toFixed(1)} yrs</td>
                  <td className="py-3 px-4 text-slate-600 font-medium">{c.matched_required?.length} / {c.all_required?.length} verified</td>
                  <td className="py-3 px-4 font-medium text-slate-700">{c.recruiter_status || 'New'}</td>
                  <td className="py-3 px-4 text-right">
                    <span className="text-brand-600 font-semibold hover:underline flex items-center justify-end gap-0.5">
                      Inspect <ChevronRight className="w-3.5 h-3.5" />
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <div className="p-8 text-center text-xs text-slate-500">
            No candidates matching the selected filters.
          </div>
        )}
      </div>
    </div>
  );
}
