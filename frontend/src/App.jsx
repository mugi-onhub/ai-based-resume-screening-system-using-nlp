import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import Overview from './views/Overview';
import Jobs from './views/Jobs';
import Candidates from './views/Candidates';
import CandidateModal from './views/CandidateModal';
import Shortlists from './views/Shortlists';
import FairnessAudit from './views/FairnessAudit';
import WhatIfSimulator from './views/WhatIfSimulator';
import Analytics from './views/Analytics';
import Settings from './views/Settings';

import { 
  fetchOverview, 
  fetchJobs, 
  fetchCandidates, 
  fetchCandidateDetail,
  uploadResumes, 
  loadSampleCandidates,
  updateCandidateStatus,
  createJob,
  activateJob,
  updateSettings,
  fetchSettings
} from './lib/api';

export default function App() {
  const [currentView, setCurrentView] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [jobsData, setJobsData] = useState([]);
  const [activeJobId, setActiveJobId] = useState('job_001');
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [parsedCriteria, setParsedCriteria] = useState(null);
  const [defaultSkills, setDefaultSkills] = useState([]);
  const [blindMode, setBlindMode] = useState(false);
  const [shortlistThreshold, setShortlistThreshold] = useState(70);
  const [loading, setLoading] = useState(true);

  // Load initial global data
  const loadData = async () => {
    try {
      setLoading(true);
      const [ovData, jbData, cdData, stData] = await Promise.all([
        fetchOverview(),
        fetchJobs(),
        fetchCandidates(),
        fetchSettings(),
      ]);
      setOverview(ovData);
      setJobsData(jbData.jobs || []);
      setActiveJobId(jbData.active_job_id || 'job_001');
      setParsedCriteria(jbData.parsed_active || null);
      setCandidates(cdData.candidates || []);
      setBlindMode(stData.blind_mode || false);
      setShortlistThreshold(stData.shortlist_threshold || 70);
      setDefaultSkills(stData.default_skills || []);
    } catch (e) {
      console.error('Failed to load initial data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectJob = async (jobId) => {
    try {
      setLoading(true);
      await activateJob(jobId);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async (data) => {
    try {
      setLoading(true);
      await createJob(data);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCandidate = async (filename) => {
    try {
      const detail = await fetchCandidateDetail(filename);
      setSelectedCandidate(detail);
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpdateStatus = async (filename, status, notes) => {
    try {
      await updateCandidateStatus(filename, status, notes);
      const [ovData, cdData] = await Promise.all([fetchOverview(), fetchCandidates()]);
      setOverview(ovData);
      setCandidates(cdData.candidates || []);
      if (selectedCandidate && selectedCandidate.filename === filename) {
        setSelectedCandidate(prev => ({ ...prev, recruiter_status: status, recruiter_notes: notes }));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleUploadResumes = async (files) => {
    try {
      setLoading(true);
      await uploadResumes(files);
      await loadData();
    } catch (e) {
      console.error(e);
      alert('Error screening resumes. Please check console.');
    } finally {
      setLoading(false);
    }
  };

  const handleReloadSamples = async () => {
    try {
      setLoading(true);
      await loadSampleCandidates();
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleBlind = async () => {
    const newMode = !blindMode;
    setBlindMode(newMode);
    try {
      const st = await fetchSettings();
      await updateSettings({ ...st, blind_mode: newMode });
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleChangeThreshold = async (val) => {
    setShortlistThreshold(val);
    try {
      const st = await fetchSettings();
      await updateSettings({ ...st, shortlist_threshold: val });
      const ovData = await fetchOverview();
      setOverview(ovData);
    } catch (e) {
      console.error(e);
    }
  };

  const activeJob = jobsData.find(j => j.id === activeJobId) || jobsData[0];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <Sidebar 
        currentView={currentView}
        setCurrentView={setCurrentView}
        jobsData={jobsData}
        activeJobId={activeJobId}
        onSelectJob={handleSelectJob}
        blindMode={blindMode}
        onToggleBlind={handleToggleBlind}
        shortlistThreshold={shortlistThreshold}
        onChangeThreshold={handleChangeThreshold}
      />

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <TopNav 
          activeJob={activeJob}
          onReloadSamples={handleReloadSamples}
          loading={loading}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8 max-w-7xl w-full mx-auto">
          {currentView === 'overview' && (
            <Overview 
              overview={overview}
              candidates={candidates}
              onSelectCandidate={handleSelectCandidate}
              onNavigate={setCurrentView}
            />
          )}

          {currentView === 'jobs' && (
            <Jobs 
              jobsData={jobsData}
              activeJobId={activeJobId}
              onSelectJob={handleSelectJob}
              onCreateJob={handleCreateJob}
              parsedCriteria={parsedCriteria}
            />
          )}

          {currentView === 'candidates' && (
            <Candidates 
              candidates={candidates}
              onSelectCandidate={handleSelectCandidate}
              onUpload={handleUploadResumes}
              loading={loading}
            />
          )}

          {currentView === 'shortlists' && (
            <Shortlists 
              candidates={candidates}
              onSelectCandidate={handleSelectCandidate}
              shortlistThreshold={shortlistThreshold}
            />
          )}

          {currentView === 'fairness' && (
            <FairnessAudit 
              candidates={candidates}
              blindMode={blindMode}
              onToggleBlind={handleToggleBlind}
            />
          )}

          {currentView === 'whatif' && (
            <WhatIfSimulator 
              activeJob={activeJob}
              parsedCriteria={parsedCriteria}
              defaultSkills={defaultSkills}
            />
          )}

          {currentView === 'analytics' && (
            <Analytics />
          )}

          {currentView === 'settings' && (
            <Settings onRefreshData={loadData} />
          )}
        </main>
      </div>

      {/* Candidate Deep Dive Slide-over Drawer */}
      {selectedCandidate && (
        <CandidateModal 
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
          onUpdateStatus={handleUpdateStatus}
        />
      )}
    </div>
  );
}
