import React, { useState } from 'react';
import { Briefcase, Plus, CheckCircle2, FileText, Sparkles } from 'lucide-react';

export default function Jobs({ jobsData, activeJobId, onSelectJob, onCreateJob, parsedCriteria }) {
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('Engineering & Analytics');
  const [rawText, setRawText] = useState('');

  const activeJob = jobsData.find(j => j.id === activeJobId) || jobsData[0];

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim() || !rawText.trim()) return;
    await onCreateJob({ title, department, raw_text: rawText });
    setTitle('');
    setRawText('');
    setShowCreate(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Job Requisitions</h1>
          <p className="text-xs text-slate-500 mt-0.5">Manage job openings, criteria, and extracted skill intelligence.</p>
        </div>
        <button 
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>{showCreate ? 'Close Form' : 'Create Requisition'}</span>
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-4 animate-in fade-in duration-150">
          <h2 className="text-sm font-bold text-slate-900">New Job Opening</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Role Title</label>
              <input 
                type="text" 
                placeholder="e.g. Lead Machine Learning Engineer" 
                value={title}
                onChange={e => setTitle(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded px-3 py-2 focus:outline-none focus:ring-1 focus:ring-brand-500"
                required
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Department</label>
              <select 
                value={department}
                onChange={e => setDepartment(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded px-3 py-2 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                <option>Engineering & Analytics</option>
                <option>Data Platform & AI</option>
                <option>Product & Design</option>
                <option>Infrastructure & Cloud</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 block mb-1">Job Description Content</label>
            <textarea 
              rows={6}
              placeholder="Paste full job description including Required Qualifications and Preferred Skills sections..."
              value={rawText}
              onChange={e => setRawText(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded p-3 focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono"
              required
            />
          </div>
          <button 
            type="submit"
            className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded shadow-xs transition-colors"
          >
            Save & Activate Job
          </button>
        </form>
      )}

      {/* Active Job Intelligence Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Requisition</span>
                <h2 className="text-lg font-bold text-slate-900 mt-0.5">{activeJob?.title}</h2>
              </div>
              <span className="text-xs font-medium text-slate-500">Created {activeJob?.created}</span>
            </div>

            <div className="text-xs text-slate-600 space-y-2 border-t border-slate-100 pt-3">
              <span className="font-semibold text-slate-800">Job Description Text:</span>
              <pre className="text-xs text-slate-700 bg-slate-50 border border-slate-100 rounded-md p-3 whitespace-pre-wrap font-mono leading-relaxed max-h-72 overflow-y-auto">
                {activeJob?.raw_text}
              </pre>
            </div>
          </div>
        </div>

        {/* Extracted Intelligence Criteria */}
        <div className="space-y-4">
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-2xs space-y-3">
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-brand-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">Extracted Intelligence</h3>
            </div>

            <div className="space-y-2 text-xs">
              <span className="font-bold text-slate-800 block">Mandatory Required Skills:</span>
              <div className="flex flex-wrap gap-1.5">
                {parsedCriteria?.required_skills?.map(s => (
                  <span key={s} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-[11px] font-semibold">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            {parsedCriteria?.preferred_skills?.length > 0 && (
              <div className="space-y-2 text-xs pt-2">
                <span className="font-bold text-slate-800 block">Preferred Skills (Bonus):</span>
                <div className="flex flex-wrap gap-1.5">
                  {parsedCriteria.preferred_skills.map(s => (
                    <span key={s} className="px-2 py-0.5 bg-slate-100 text-slate-700 border border-slate-200 rounded text-[11px] font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2 text-xs text-slate-600">
              <span className="font-bold text-slate-800 block mb-1">Target Experience:</span>
              <span>{parsedCriteria?.min_experience_years || 0} years minimum required</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
