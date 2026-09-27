import React, { useState } from 'react';
import { 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  FileText, 
  Briefcase, 
  GraduationCap, 
  HelpCircle, 
  ShieldCheck, 
  FolderGit2,
  ChevronRight
} from 'lucide-react';

export default function CandidateModal({ candidate, onClose, onUpdateStatus }) {
  const [activeTab, setActiveTab] = useState('summary');
  const [status, setStatus] = useState(candidate.recruiter_status || 'New');
  const [notes, setNotes] = useState(candidate.recruiter_notes || '');

  if (!candidate) return null;

  const handleSaveStatus = (newStatus) => {
    setStatus(newStatus);
    onUpdateStatus(candidate.filename, newStatus, notes);
  };

  const handleSaveNotes = (e) => {
    e.preventDefault();
    onUpdateStatus(candidate.filename, status, notes);
  };

  const isStrong = candidate.match_level === 'Strong Match';
  const isGood = candidate.match_level === 'Good Match';
  const isReview = candidate.match_level === 'Review';

  const breakdown = [
    { label: 'Required Skill Coverage', score: candidate.breakdown?.required_skill_coverage || 0, weight: '35%' },
    { label: 'Relevant Experience', score: candidate.breakdown?.relevant_experience || 0, weight: '20%' },
    { label: 'Project Relevance', score: candidate.breakdown?.project_relevance || 0, weight: '15%' },
    { label: 'Preferred Skills', score: candidate.breakdown?.preferred_skill_coverage || 0, weight: '10%' },
    { label: 'Education Relevance', score: candidate.breakdown?.education_relevance || 0, weight: '5%' },
    { label: 'Academic NLP Ensemble', score: candidate.breakdown?.nlp_ensemble || 0, weight: '15%' },
  ];

  const statuses = ['New', 'Under Review', 'Shortlisted', 'Interview', 'On Hold', 'Rejected'];

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex justify-end transition-opacity">
      <div className="bg-white w-full max-w-2xl h-full shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-200">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-200 flex items-start justify-between bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-400">#{String(candidate.rank).padStart(2, '0')}</span>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">{candidate.name}</h2>
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${
                isStrong ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                isGood ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                isReview ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                'bg-rose-50 text-rose-700 border border-rose-200'
              }`}>
                {candidate.match_level}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              File: <code className="text-slate-700">{candidate.filename}</code>
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-black text-slate-900">{candidate.job_fit_score?.toFixed(1)}%</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Job Fit Score</div>
            </div>
            <button 
              onClick={onClose}
              className="p-1.5 rounded-md hover:bg-slate-200 text-slate-500 hover:text-slate-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Workflow Action Bar */}
        <div className="px-6 py-3 border-b border-slate-200 bg-white flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-600">Decision Status:</span>
            <select
              value={status}
              onChange={(e) => handleSaveStatus(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded px-2.5 py-1 font-semibold focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {statuses.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <span className="text-[11px] text-slate-400">
            Updated just now
          </span>
        </div>

        {/* Tabs Header */}
        <div className="flex border-b border-slate-200 px-6 bg-slate-50/30 overflow-x-auto text-xs font-medium text-slate-600 gap-6">
          {[
            { id: 'summary', label: 'Match Summary' },
            { id: 'evidence', label: 'Skill Evidence' },
            { id: 'experience', label: 'Experience' },
            { id: 'projects', label: 'Projects' },
            { id: 'signals', label: 'Signals & Questions' },
            { id: 'integrity', label: 'Integrity & Timeline' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 border-b-2 font-semibold transition-colors shrink-0 ${
                activeTab === tab.id 
                  ? 'border-slate-900 text-slate-900' 
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Scrollable Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === 'summary' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">Explainable Job Fit Breakdown</h3>
                <p className="text-xs text-slate-500 mb-4">Transparent multi-dimensional weighting.</p>

                <div className="space-y-3">
                  {breakdown.map(b => (
                    <div key={b.label}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="font-medium text-slate-700">{b.label} <span className="text-slate-400">({b.weight} weight)</span></span>
                        <span className="font-bold text-slate-900">{b.score?.toFixed(1)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-brand-600 rounded-full" style={{ width: `${b.score}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 space-y-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Mathematical Formula</span>
                <pre className="text-[11px] text-slate-700 font-mono whitespace-pre-wrap">{candidate.formula}</pre>
              </div>

              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-2">Preserved Academic NLP Models</h3>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="border border-slate-200 rounded-lg p-2.5 bg-white">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">TF-IDF Lexical</span>
                    <div className="text-base font-bold text-slate-900 mt-0.5">{candidate.nlp_scores?.tfidf?.toFixed(1)}%</div>
                  </div>
                  <div className="border border-slate-200 rounded-lg p-2.5 bg-white">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">MiniLM Semantic</span>
                    <div className="text-base font-bold text-slate-900 mt-0.5">{candidate.nlp_scores?.semantic?.toFixed(1)}%</div>
                  </div>
                  <div className="border border-slate-200 rounded-lg p-2.5 bg-white">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">BERT Contextual</span>
                    <div className="text-base font-bold text-slate-900 mt-0.5">{candidate.nlp_scores?.bert?.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'evidence' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-1">Verbatim Skill Evidence</h3>
                <p className="text-xs text-slate-500 mb-4">Direct quotes extracted from candidate resume with zero hallucination.</p>
              </div>

              <div className="space-y-2.5">
                <span className="text-xs font-bold text-slate-800 block">Mandatory Required Skills:</span>
                {candidate.all_required?.map(skill => {
                  const ev = candidate.evidence?.[skill] || { status: 'Missing', evidence: 'Not found in resume.' };
                  const isMatch = ev.status === 'Strong Match';
                  const isPart = ev.status === 'Partial Match';

                  return (
                    <div 
                      key={skill}
                      className={`border rounded-md p-3 text-xs ${
                        isMatch ? 'border-l-4 border-l-emerald-500 bg-emerald-50/20 border-slate-200' :
                        isPart ? 'border-l-4 border-l-amber-500 bg-amber-50/20 border-slate-200' :
                        'border-l-4 border-l-rose-400 bg-rose-50/20 border-slate-200'
                      }`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-slate-900 capitalize">{skill}</span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          isMatch ? 'bg-emerald-100 text-emerald-800' :
                          isPart ? 'bg-amber-100 text-amber-800' :
                          'bg-rose-100 text-rose-800'
                        }`}>
                          {ev.status}
                        </span>
                      </div>
                      <p className="text-slate-600 italic">"{ev.evidence}"</p>
                    </div>
                  );
                })}
              </div>

              {candidate.all_preferred?.length > 0 && (
                <div className="space-y-2.5 pt-4">
                  <span className="text-xs font-bold text-slate-800 block">Preferred Skills (Bonus):</span>
                  {candidate.all_preferred?.map(skill => {
                    const ev = candidate.evidence?.[skill] || { status: 'Missing', evidence: 'Not found in resume.' };
                    const isMatch = ev.status === 'Strong Match';

                    return (
                      <div key={skill} className="border border-slate-200 border-l-4 border-l-slate-400 rounded-md p-3 text-xs bg-slate-50/30">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold text-slate-900 capitalize">{skill}</span>
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">{ev.status}</span>
                        </div>
                        <p className="text-slate-600 italic">"{ev.evidence}"</p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {activeTab === 'experience' && (
            <div className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div className="border border-slate-200 rounded-lg p-3 bg-white">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Relevant Experience</span>
                  <div className="text-xl font-bold text-slate-900 mt-0.5">{candidate.experience?.relevant_experience_years?.toFixed(1)} yrs</div>
                </div>
                <div className="border border-slate-200 rounded-lg p-3 bg-white">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Total Experience</span>
                  <div className="text-xl font-bold text-slate-900 mt-0.5">{candidate.experience?.total_experience_years?.toFixed(1)} yrs</div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Detected Career Roles</h4>
                <div className="space-y-1">
                  {candidate.experience?.roles?.length > 0 ? (
                    candidate.experience.roles.map(r => (
                      <div key={r} className="text-xs font-semibold text-slate-800 flex items-center gap-1.5">
                        <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                        {r}
                      </div>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">Student / Academic background</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Chronological Employment Timeline</h4>
                <div className="space-y-2">
                  {candidate.experience?.timeline_entries?.map((t, idx) => (
                    <div key={idx} className="border border-slate-200 rounded-md p-2.5 text-xs bg-slate-50/50">
                      <div className="font-bold text-slate-800">{t.start} – {t.end} ({t.duration_years?.toFixed(1)} yrs)</div>
                      <div className="text-slate-600 mt-0.5 italic">{t.context}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">Project Portfolio Relevance</h3>
              {candidate.projects?.length > 0 ? (
                candidate.projects.map((p, idx) => (
                  <div key={idx} className="border border-slate-200 rounded-lg p-4 bg-white shadow-2xs space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-sm text-slate-900">{p.name}</span>
                      <span className="text-xs font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded">
                        {p.relevance_score?.toFixed(1)}% Relevance
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{p.description}</p>
                    <div className="text-xs text-slate-500 pt-1">
                      <strong className="text-slate-700">Technologies:</strong> {Array.from(p.technologies || []).join(', ') || 'General implementation'}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">No standalone project blocks extracted.</p>
              )}
            </div>
          )}

          {activeTab === 'signals' && (
            <div className="space-y-5 text-xs">
              <div>
                <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">Candidate Strengths</h4>
                <ul className="space-y-1.5">
                  {candidate.insights?.why_this_candidate?.map((w, idx) => (
                    <li key={idx} className="text-slate-700 flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">Skill Gaps to Probe</h4>
                {candidate.insights?.gaps_required?.length > 0 ? (
                  <div className="text-rose-700 bg-rose-50/50 border border-rose-200 rounded p-2.5">
                    <strong>Missing Required Skills:</strong> {candidate.insights.gaps_required.join(', ')}
                  </div>
                ) : (
                  <div className="text-emerald-700 bg-emerald-50/50 border border-emerald-200 rounded p-2.5">
                    Full coverage across all mandatory required skills.
                  </div>
                )}
              </div>

              <div>
                <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">Recommended Technical Interview Questions</h4>
                <div className="space-y-2">
                  {candidate.insights?.interview_questions?.map((q, idx) => (
                    <div key={idx} className="bg-slate-50 border border-slate-200 rounded p-3 text-slate-800 italic">
                      ❓ {q}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'integrity' && (
            <div className="space-y-4 text-xs">
              <div className="flex items-center justify-between border border-slate-200 rounded-lg p-3 bg-white">
                <span className="font-bold text-slate-900">Integrity Confidence Score</span>
                <span className="text-base font-bold text-slate-900">{candidate.consistency?.consistency_score?.toFixed(1)}%</span>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 uppercase tracking-wider mb-2">Timeline Review Observations</h4>
                <div className="space-y-2">
                  {candidate.consistency?.flags?.map((f, idx) => (
                    <div key={idx} className="border border-slate-200 rounded p-2.5 bg-slate-50 text-slate-700">
                      {f}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Notes */}
        <div className="p-4 border-t border-slate-200 bg-slate-50/50">
          <form onSubmit={handleSaveNotes} className="flex gap-2">
            <input 
              type="text" 
              placeholder="Add recruiter private note..." 
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="flex-1 text-xs bg-white border border-slate-200 rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <button 
              type="submit"
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded transition-colors"
            >
              Save Note
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
