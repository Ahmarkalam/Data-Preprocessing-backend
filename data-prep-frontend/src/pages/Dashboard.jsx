import React, { useState, useEffect, useCallback } from 'react';
import { FileText, Database, Activity, Clock, Sparkles } from 'lucide-react';
import StatsCard from '../components/StatsCard';
import FileUpload from '../components/FileUpload';
import JobTable from '../components/JobTable';
import CreateJobModal from '../components/CreateJobModal';
import apiClient from '../api/client';
import { useToast } from '../components/useToast';

const Dashboard = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [uploadedPath, setUploadedPath] = useState('');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [clientStats, setClientStats] = useState(null);
  const { addToast } = useToast();

  const fetchClientStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/clients/me');
      setClientStats(response.data);
    } catch (error) {
      console.error('Failed to fetch client stats:', error);
      addToast('Failed to fetch client statistics', 'error');
    }
  }, [addToast]);

  useEffect(() => {
    (async () => {
      await fetchClientStats();
    })();
  }, [refreshTrigger, fetchClientStats]);

  const handleUploadFinished = (response) => {
    if (response && response.file_path) {
      setUploadedPath(response.file_path);
      setIsModalOpen(true);
      addToast('File uploaded successfully! Configure your job.', 'success');
    }
  };

  const handleJobCreated = () => {
    setIsModalOpen(false);
    setRefreshTrigger((prev) => prev + 1);
    addToast('Job created successfully. Processing started.', 'success');
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <section className="rounded-2xl p-5 sm:p-6 bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-900/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <p className="text-indigo-100 text-sm">Welcome back</p>
            <h1 className="text-2xl sm:text-3xl font-bold">Your data hub is ready</h1>
            <p className="text-indigo-100 mt-2 text-sm sm:text-base">Monitor quality metrics, launch new runs, and keep your preprocessing pipeline operating smoothly.</p>
          </div>
          <div className="self-start sm:self-auto rounded-xl bg-white/20 p-3">
            <Sparkles size={24} />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
        <StatsCard
          title="Monthly Quota"
          value={clientStats ? `${clientStats.used_quota_mb.toFixed(1)} / ${clientStats.monthly_quota_mb} MB` : 'Loading...'}
          change={clientStats ? `${((clientStats.used_quota_mb / clientStats.monthly_quota_mb) * 100).toFixed(1)}% Used` : ''}
          icon={Database}
          trend={clientStats && (clientStats.used_quota_mb / clientStats.monthly_quota_mb) > 0.8 ? 'down' : 'up'}
        />
        <StatsCard
          title="Plan Type"
          value={clientStats ? clientStats.plan_type.toUpperCase() : 'Loading...'}
          change="Active"
          icon={Activity}
        />
        <StatsCard title="User" value={clientStats ? clientStats.name : '...'} change="Connected" icon={FileText} />
        <StatsCard title="Avg. Processing" value="~1.2s" change="-0.3s" trend="down" icon={Clock} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 sm:gap-8 items-start">
        <div className="xl:col-span-2 space-y-8">
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-slate-900">Recent Jobs</h2>
            </div>
            <JobTable key={refreshTrigger} />
          </section>
        </div>

        <div className="space-y-6">
          <section>
            <h2 className="text-lg font-bold text-slate-900 mb-4">Quick Action</h2>
            <FileUpload onUploadSuccess={handleUploadFinished} maxSizeMB={clientStats?.plan_type === 'guest' ? 5 : 50} />
          </section>

          <div className="card p-6 bg-gradient-to-br from-slate-900 to-indigo-900 text-white border-none">
            <h3 className="font-bold text-lg mb-2">Team Recommendation</h3>
            <p className="text-indigo-100 text-sm sm:text-base mb-4">
              Use Parquet files for faster uploads and lower memory usage on large datasets.
            </p>
            <button className="text-sm font-semibold bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg transition-colors">
              View Documentation
            </button>
          </div>
        </div>
      </div>

      <CreateJobModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        inputPath={uploadedPath}
        onJobCreated={handleJobCreated}
      />
    </div>
  );
};

export default Dashboard;
