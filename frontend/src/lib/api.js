const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.PROD ? '/api' : 'http://localhost:8000/api');

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview');
  return res.json();
}

export async function fetchJobs() {
  const res = await fetch(`${API_BASE}/jobs`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function createJob(data) {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create job');
  return res.json();
}

export async function activateJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/activate/${jobId}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to activate job');
  return res.json();
}

export async function fetchCandidates() {
  const res = await fetch(`${API_BASE}/candidates`);
  if (!res.ok) throw new Error('Failed to fetch candidates');
  return res.json();
}

export async function fetchCandidateDetail(filename) {
  const res = await fetch(`${API_BASE}/candidate/${encodeURIComponent(filename)}`);
  if (!res.ok) throw new Error('Failed to fetch candidate details');
  return res.json();
}

export async function uploadResumes(files) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  const res = await fetch(`${API_BASE}/screen`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to screen resumes');
  return res.json();
}

export async function loadSampleCandidates() {
  const res = await fetch(`${API_BASE}/load-sample`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to load sample candidates');
  return res.json();
}

export async function updateCandidateStatus(filename, status, notes) {
  const res = await fetch(`${API_BASE}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, status, notes }),
  });
  if (!res.ok) throw new Error('Failed to update status');
  return res.json();
}

export async function runWhatIfSimulation(data) {
  const res = await fetch(`${API_BASE}/what-if`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to run what-if simulation');
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function updateSettings(data) {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}
