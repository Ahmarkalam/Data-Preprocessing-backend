import React, { useEffect, useState, useRef } from 'react';
import apiClient from '../api/client';
import { RefreshCw, Download, FileText, CheckCircle2, Play, Clock, AlertCircle, Eye, MessageSquare, Settings } from 'lucide-react';
import BeforeAfterPreview from './BeforeAfterPreview';
import DataChatModal from './DataChatModal';
import ViewConfigModal from './ViewConfigModal';
import ViewReportModal from './ViewReportModal';

const JobTable = () => {
  const [configJob, setConfigJob] = useState(null);
  const [reportJob, setReportJob] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewJobId, setPreviewJobId] = useState(null);
  const [chatJobId, setChatJobId] = useState(null);
  const pollingInterval = useRef(null);

  const fetchJobs = async (showLoading = true) => {
    if (showLoading) setLoading(true);
    try {
      const response = await apiClient.get('/jobs/');
      setJobs(response.data);
      const norm = (s) => String(s || '').toUpperCase();
      const hasActive = response.data.some(j => norm(j.status) === 'PENDING' || norm(j.status) === 'PROCESSING');
      if (hasActive && !pollingInterval.current) startPolling();
      else if (!hasActive && pollingInterval.current) stopPolling();
    } catch (e) { console.error(e); }
    finally { if (showLoading) setLoading(false); }
  };

  const startPolling = () => { pollingInterval.current = setInterval(() => fetchJobs(false), 5000); };
  const stopPolling = () => { if (pollingInterval.current) { clearInterval(pollingInterval.current); pollingInterval.current = null; } };

  const runJobManually = async (jobId) => {
    try { await apiClient.post(`/jobs/${jobId}/execute`); fetchJobs(false); }
    catch { alert("Execution failed"); }
  };

  const downloadJobResult = async (jobId, fileName) => {
    try {
      const response = await apiClient.get(`/jobs/${jobId}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `processed_${fileName}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) { 
      const detail = e?.response?.data;
      try {
        // Try to parse JSON error blob if present
        if (detail instanceof Blob) {
          const text = await detail.text();
          const obj = JSON.parse(text);
          alert(`Download failed: ${obj?.detail || text}`);
          return;
        }
      } catch { /* ignore */ }
      alert("Download failed");
    }
  };

  useEffect(() => { fetchJobs(); return () => stopPolling(); }, []);

  const getStatusBadge = (status) => {
    const styles = {
      COMPLETED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      PROCESSING: 'bg-blue-50 text-blue-700 border-blue-200',
      PENDING: 'bg-slate-100 text-slate-600 border-slate-200',
      FAILED: 'bg-red-50 text-red-700 border-red-200',
    };
    
    const icons = {
      COMPLETED: <CheckCircle2 size={14} />,
      PROCESSING: <RefreshCw size={14} className="animate-spin" />,
      PENDING: <Clock size={14} />,
      FAILED: <AlertCircle size={14} />,
    };

    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1.5 w-fit ${styles[status] || styles.PENDING}`}>
        {icons[status]} {status}
      </span>
    );
  };
  
  const norm = (s) => String(s || '').toUpperCase();
  const getFileName = (job) => {
    const src = job.output_path || '';
    if (typeof src === 'string' && src.length) {
      const name = src.split('\\').pop().split('/').pop();
      return name.replace(/^processed_/, '');
    }
    return `Job ${job.job_id || ''}`;
  };

  return (
    <div className="card">
      <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-white">
        <h3 className="font-semibold text-slate-800">Job History</h3>
        <button 
          onClick={() => fetchJobs(true)} 
          className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">File Name</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {jobs.length === 0 && !loading ? (
              <tr>
                <td colSpan="4" className="px-6 py-12 text-center text-slate-500">
                  <FileText size={48} className="mx-auto text-slate-200 mb-4" />
                  <p>No jobs found. Upload a file to get started.</p>
                </td>
              </tr>
            ) : (
              jobs.map(job => (
                <tr key={job.job_id} className="hover:bg-slate-50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                        <FileText size={18} />
                      </div>
                      <span className="font-medium text-slate-700 text-sm">
                        {getFileName(job)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {getStatusBadge(norm(job.status))}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">
                    {new Date(job.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {norm(job.status) === 'PENDING' && (
                        <button 
                          onClick={() => runJobManually(job.job_id)} 
                          className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg tooltip"
                          title="Run Job"
                        >
                          <Play size={18}/>
                        </button>
                      )}
                      {norm(job.status) === 'COMPLETED' && (
                        <>
                          <button 
                            onClick={() => setChatJobId(job.job_id)} 
                            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
                            title="Chat with Data"
                          >
                            <MessageSquare size={18}/>
                          </button>
                          <button 
                            onClick={() => setPreviewJobId(job.job_id)} 
                            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
                            title="Preview Data"
                          >
                            <Eye size={18}/>
                          </button>
                          <button 
                            onClick={() => setReportJob(job)} 
                            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
                            title="View Quality Report"
                          >
                            <FileText size={18}/>
                          </button>
                          <button 
                            onClick={() => setConfigJob(job)} 
                            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
                            title="View Configuration"
                          >
                            <Settings size={18}/>
                          </button>
                          <button 
                            onClick={() => downloadJobResult(job.job_id, getFileName(job))} 
                            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
                            title="Download Result"
                          >
                            <Download size={18}/>
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <BeforeAfterPreview 
        isOpen={!!previewJobId} 
        onClose={() => setPreviewJobId(null)} 
        jobId={previewJobId} 
      />
      
      <DataChatModal
        isOpen={!!chatJobId}
        onClose={() => setChatJobId(null)}
        jobId={chatJobId}
      />

      <ViewConfigModal 
        isOpen={!!configJob} 
        onClose={() => setConfigJob(null)} 
        config={configJob?.config} 
      />

      <ViewReportModal
        isOpen={!!reportJob}
        onClose={() => setReportJob(null)}
        job={reportJob}
      />
    </div>
  );
};

export default JobTable;
