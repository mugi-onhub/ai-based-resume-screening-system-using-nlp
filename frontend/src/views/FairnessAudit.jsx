import React, { useState } from 'react';
import { Scale, ShieldCheck } from 'lucide-react';

export default function FairnessAudit({ candidates, blindMode, onToggleBlind }) {
  const [selectedCandidates, setSelectedCandidates] = useState([]);

  const toggleSelect = (name) => {
    if (selectedCandidates.includes(name)) {
      setSelectedCandidates(selectedCandidates.filter(n => n !== name));
    } else {
      if (selectedCandidates.length < 4) {
        setSelectedCandidates([...selectedCandidates, name]);
      }
    }
  };

  const compCandidates = candidates.filter(c => selectedCandidates.includes(c.name));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Fairness & Blind Screening Audit</h1>
          <p className="text-xs text-slate-500 mt-0.5">Audit candidate ranking parity and test bias-mitigation anonymization.</p>
        </div>
      </div>

      {/* Compliance Guarantee */}
      <div className="bg-slate-900 text-white rounded-lg p-4.5 shadow-sm space-y-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Ethical AI & Compliance Safeguards</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          CAREERPILOT evaluates applicants strictly on job-relevant technical competencies, documented experience, and project evidence. 
          Protected demographic characteristics (age, gender, ethnicity, location, and photos) are entirely excluded from scoring algorithms.
        </p>
      </div>

      {/* Presentation Table */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-3">
        <h3 className="text-sm font-bold text-slate-900">Anonymized vs. Unblinded Presentation</h3>
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Rank</th>
              <th className="py-2.5 px-3">Unblinded Name</th>
              <th className="py-2.5 px-3">Blind Anonymized ID</th>
              <th className="py-2.5 px-3">Job Fit Score</th>
              <th className="py-2.5 px-3">Match Level</th>
              <th className="py-2.5 px-3">Protected Data Used</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {candidates.map(c => (
              <tr key={c.filename} className="hover:bg-slate-50/60">
                <td className="py-2.5 px-3 font-bold text-slate-400">#{String(c.rank).padStart(2, '0')}</td>
                <td className="py-2.5 px-3 font-semibold text-slate-900">{c.raw_name}</td>
                <td className="py-2.5 px-3 font-mono text-slate-700">{c.anon_alias}</td>
                <td className="py-2.5 px-3 font-bold text-slate-900">{c.job_fit_score?.toFixed(1)}%</td>
                <td className="py-2.5 px-3 text-slate-700">{c.match_level}</td>
                <td className="py-2.5 px-3 text-slate-500">None (0%)</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Side-by-Side Comparison */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Side-by-Side Candidate Comparison</h3>
            <p className="text-xs text-slate-500">Select 2 to 4 candidates to contrast dimensional fit.</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {candidates.map(c => {
            const isSelected = selectedCandidates.includes(c.name);
            return (
              <button
                key={c.name}
                onClick={() => toggleSelect(c.name)}
                className={`px-3 py-1 text-xs rounded-md font-medium border transition-colors ${
                  isSelected 
                    ? 'bg-slate-900 text-white border-slate-900' 
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {c.name} ({c.job_fit_score?.toFixed(1)}%)
              </button>
            );
          })}
        </div>

        {compCandidates.length >= 2 ? (
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-700">
                <tr>
                  <th className="p-3 font-bold">Dimension</th>
                  {compCandidates.map(c => (
                    <th key={c.name} className="p-3 font-bold text-slate-900">{c.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="p-3 font-semibold text-slate-600">Job Fit Score</td>
                  {compCandidates.map(c => (
                    <td key={c.name} className="p-3 font-bold text-slate-900">{c.job_fit_score?.toFixed(1)}%</td>
                  ))}
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-600">Relevant Experience</td>
                  {compCandidates.map(c => (
                    <td key={c.name} className="p-3 text-slate-800">{c.experience?.relevant_experience_years?.toFixed(1)} yrs</td>
                  ))}
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-600">Required Skills Verified</td>
                  {compCandidates.map(c => (
                    <td key={c.name} className="p-3 text-slate-800">{c.matched_required?.length} of {c.all_required?.length}</td>
                  ))}
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-600">Academic NLP Ensemble</td>
                  {compCandidates.map(c => (
                    <td key={c.name} className="p-3 text-slate-800">{c.nlp_scores?.fused?.toFixed(1)}%</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg">
            Select at least 2 candidates above to generate side-by-side comparison matrix.
          </div>
        )}
      </div>
    </div>
  );
}
