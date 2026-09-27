import React, { useState, useEffect } from 'react';
import { SlidersHorizontal, ArrowUpDown, Sparkles } from 'lucide-react';
import { runWhatIfSimulation } from '../lib/api';

export default function WhatIfSimulator({ activeJob, parsedCriteria, defaultSkills }) {
  const [reqSkills, setReqSkills] = useState(parsedCriteria?.required_skills || []);
  const [prefSkills, setPrefSkills] = useState(parsedCriteria?.preferred_skills || []);
  const [minExp, setMinExp] = useState(parsedCriteria?.min_experience_years || 2.0);
  const [reqWeight, setReqWeight] = useState(35);
  const [simResults, setSimResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const availableSkills = defaultSkills || ['python', 'sql', 'machine learning', 'scikit-learn', 'docker', 'aws', 'pytorch', 'bert'];

  const handleRunSim = async () => {
    setLoading(true);
    try {
      const data = await runWhatIfSimulation({
        required_skills: reqSkills,
        preferred_skills: prefSkills,
        min_exp_years: minExp,
        required_skills_weight: reqWeight / 100,
      });
      setSimResults(data.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleRunSim();
  }, [reqSkills, prefSkills, minExp, reqWeight]);

  const toggleReq = (skill) => {
    if (reqSkills.includes(skill)) {
      setReqSkills(reqSkills.filter(s => s !== skill));
    } else {
      setReqSkills([...reqSkills, skill]);
      setPrefSkills(prefSkills.filter(s => s !== skill));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">What-If Hiring Simulator</h1>
          <p className="text-xs text-slate-500 mt-0.5">Test hypothetical requirement scenarios and observe live ranking shifts.</p>
        </div>
      </div>

      {/* Simulator Control Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 bg-white border border-slate-200 rounded-lg p-5 shadow-2xs">
        <div className="space-y-4">
          <div>
            <label className="text-xs font-bold text-slate-900 block mb-1">
              Mandatory Required Skills (High Weight)
            </label>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {availableSkills.slice(0, 16).map(skill => {
                const isChecked = reqSkills.includes(skill);
                return (
                  <button
                    key={skill}
                    onClick={() => toggleReq(skill)}
                    className={`px-2.5 py-1 text-xs rounded-md font-semibold border transition-all ${
                      isChecked 
                        ? 'bg-emerald-600 text-white border-emerald-600' 
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {isChecked ? '✔ ' : '+ '}{skill}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-slate-900 mb-1">
              <span>Minimum Experience Target</span>
              <span className="text-brand-600">{minExp} Years</span>
            </div>
            <input 
              type="range"
              min="0"
              max="7"
              step="0.5"
              value={minExp}
              onChange={e => setMinExp(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
            />
          </div>
        </div>

        <div className="space-y-4 border-t lg:border-t-0 lg:border-l lg:border-slate-200 lg:pl-6 pt-4 lg:pt-0">
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-900 mb-1">
              <span>Required Skills Influence Weight</span>
              <span className="text-brand-600">{reqWeight}%</span>
            </div>
            <input 
              type="range"
              min="15"
              max="60"
              step="5"
              value={reqWeight}
              onChange={e => setReqWeight(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
            />
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded p-3 text-xs text-slate-600 space-y-1">
            <span className="font-bold text-slate-800 block">Simulation Note:</span>
            <p>Promoting a skill to mandatory instantly recalculates all candidate Job Fit scores and provides plain-language reasons for rank changes.</p>
          </div>
        </div>
      </div>

      {/* Simulated Ranking Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-2xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">Simulated Ranking Shifts</h3>
          <span className="text-xs text-slate-500">{simResults.length} Candidates Re-ranked</span>
        </div>

        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">New Rank</th>
              <th className="py-2.5 px-3">Original</th>
              <th className="py-2.5 px-3">Rank Shift</th>
              <th className="py-2.5 px-3">Candidate</th>
              <th className="py-2.5 px-3">New Score</th>
              <th className="py-2.5 px-3">Score Delta</th>
              <th className="py-2.5 px-3">Why Ranking Changed</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {simResults.map((r, idx) => {
              const isUp = r.rank_delta > 0;
              const isDown = r.rank_delta < 0;

              return (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="py-2.5 px-3 font-bold text-slate-900">#{String(r.after_rank).padStart(2, '0')}</td>
                  <td className="py-2.5 px-3 text-slate-400 font-medium">#{String(r.before_rank).padStart(2, '0')}</td>
                  <td className="py-2.5 px-3 font-bold">
                    {isUp ? (
                      <span className="text-emerald-600">▲ +{r.rank_delta}</span>
                    ) : isDown ? (
                      <span className="text-rose-600">▼ {r.rank_delta}</span>
                    ) : (
                      <span className="text-slate-400">— 0</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{r.name}</td>
                  <td className="py-2.5 px-3 font-bold text-slate-900">{r.after_score?.toFixed(1)}%</td>
                  <td className="py-2.5 px-3 font-medium text-slate-700">{r.score_delta > 0 ? `+${r.score_delta}` : r.score_delta}%</td>
                  <td className="py-2.5 px-3 text-slate-600 italic">{r.delta_explanation}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
