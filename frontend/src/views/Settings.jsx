import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, RefreshCw } from 'lucide-react';
import { fetchSettings, updateSettings } from '../lib/api';

export default function Settings({ onRefreshData }) {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSettings()
      .then(res => setSettings(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!settings) return;
    setSaving(true);
    setMessage('');
    try {
      await updateSettings(settings);
      setMessage('Settings updated and rankings recomputed successfully.');
      if (onRefreshData) onRefreshData();
    } catch (e) {
      console.error(e);
      setMessage('Failed to update settings.');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !settings) {
    return <div className="p-8 text-xs text-slate-500">Loading settings...</div>;
  }

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Platform Settings & Scoring Formulas</h1>
          <p className="text-xs text-slate-500 mt-0.5">Configure mathematical weights and recruiter workflow rules.</p>
        </div>
      </div>

      {message && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-md text-xs font-medium">
          {message}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Job Fit Weights */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Job Fit Dimensional Weights</h3>
          <p className="text-xs text-slate-500">Adjust the relative influence of each dimension in the final Job Fit percentage.</p>

          <div className="space-y-3 pt-1">
            {Object.keys(settings.job_fit_weights).map(key => (
              <div key={key} className="flex items-center justify-between gap-4 text-xs">
                <span className="font-semibold text-slate-700 capitalize w-48">
                  {key.replace('_', ' ')}:
                </span>
                <input 
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={settings.job_fit_weights[key]}
                  onChange={e => {
                    const val = parseFloat(e.target.value) || 0;
                    setSettings({
                      ...settings,
                      job_fit_weights: { ...settings.job_fit_weights, [key]: val }
                    });
                  }}
                  className="w-24 text-xs bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-800 focus:outline-none"
                />
              </div>
            ))}
          </div>
        </div>

        {/* NLP Model Weights */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-2xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Academic NLP Ensemble Weights</h3>
          <p className="text-xs text-slate-500">Weights for TF-IDF, MiniLM, and BERT in the academic baseline score.</p>

          <div className="space-y-3 pt-1">
            {Object.keys(settings.nlp_weights).map(key => (
              <div key={key} className="flex items-center justify-between gap-4 text-xs">
                <span className="font-semibold text-slate-700 capitalize w-48">
                  {key.toUpperCase()}:
                </span>
                <input 
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={settings.nlp_weights[key]}
                  onChange={e => {
                    const val = parseFloat(e.target.value) || 0;
                    setSettings({
                      ...settings,
                      nlp_weights: { ...settings.nlp_weights, [key]: val }
                    });
                  }}
                  className="w-24 text-xs bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-800 focus:outline-none"
                />
              </div>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-md shadow-xs transition-colors disabled:opacity-50"
        >
          <Save className="w-3.5 h-3.5" />
          <span>{saving ? 'Saving...' : 'Save & Apply Weights'}</span>
        </button>
      </form>
    </div>
  );
}
