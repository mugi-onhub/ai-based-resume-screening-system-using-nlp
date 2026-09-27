import React, { useEffect, useState } from 'react';
import { BarChart3, AlertCircle } from 'lucide-react';
import { fetchAnalytics } from '../lib/api';

export default function Analytics() {
  const [data, setData] = useState({ scores: [], missing_skills: [], nlp_comparison: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics()
      .then(res => setData(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Talent Analytics</h1>
          <p className="text-xs text-slate-500 mt-0.5">Aggregated pool distribution, skill gap analysis, and NLP model performance.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Missing Skills Frequency */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-3">
          <h3 className="text-sm font-bold text-slate-900">Most Common Missing Skills</h3>
          <p className="text-xs text-slate-500">Skill shortages identified across the applicant pool.</p>

          <div className="space-y-3 pt-2">
            {data.missing_skills?.map(item => (
              <div key={item.skill}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-800 capitalize">{item.skill}</span>
                  <span className="text-rose-600 font-bold">{item.count} Candidates Missing</span>
                </div>
                <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-rose-500 rounded-full" style={{ width: `${Math.min(100, item.count * 15)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Score Overview */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-3">
          <h3 className="text-sm font-bold text-slate-900">Score Range Spread</h3>
          <p className="text-xs text-slate-500">Distribution of Job Fit ratings.</p>

          <div className="p-4 bg-slate-50 rounded-lg text-xs space-y-2 border border-slate-100">
            <div className="flex justify-between">
              <span className="text-slate-600">Total Analyzed:</span>
              <span className="font-bold text-slate-900">{data.scores?.length || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Highest Match:</span>
              <span className="font-bold text-emerald-600">{Math.max(...(data.scores || [0])).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Lowest Match:</span>
              <span className="font-bold text-rose-600">{Math.min(...(data.scores || [0])).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Comparison Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-2xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">Academic NLP Model Comparison</h3>
        </div>
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Candidate</th>
              <th className="py-2.5 px-3">TF-IDF Lexical</th>
              <th className="py-2.5 px-3">MiniLM Semantic</th>
              <th className="py-2.5 px-3">BERT Contextual</th>
              <th className="py-2.5 px-3">Final Job Fit Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.nlp_comparison?.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50/60">
                <td className="py-2.5 px-3 font-semibold text-slate-900">{row.name}</td>
                <td className="py-2.5 px-3 text-slate-700">{row.tfidf?.toFixed(1)}%</td>
                <td className="py-2.5 px-3 text-slate-700">{row.semantic?.toFixed(1)}%</td>
                <td className="py-2.5 px-3 text-slate-700">{row.bert?.toFixed(1)}%</td>
                <td className="py-2.5 px-3 font-bold text-slate-900">{row.job_fit?.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
