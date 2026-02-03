import React from 'react';
import { ShieldCheck, AlertTriangle, BarChart3, CheckCircle2, Download, Printer } from 'lucide-react';
import apiClient from '../api/client';

const QualityReport = ({ metrics, jobId }) => {
  if (!metrics) return null;

  // Data structure from quality_metrics table 
  const { 
    quality_score, 
    total_records, 
    valid_records, 
    invalid_records, 
    missing_values_percent, 
    issues 
  } = metrics;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const handleDownloadJSON = () => {
    const dataStr = JSON.stringify(metrics, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `quality_report_${jobId || new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = async () => {
    if (!jobId) {
      handlePrint();
      return;
    }
    try {
      const response = await apiClient.get(`/jobs/${jobId}/report`, {
          params: { format: 'pdf' },
          responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${jobId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
        console.error("PDF download failed", e);
        alert("Failed to download PDF. Falling back to print.");
        handlePrint();
    }
  };

  return (
    <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 print:mt-0 print:animate-none">
      <div className="flex justify-between items-center print:hidden">
        <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <BarChart3 size={20} className="text-blue-600" />
          Data Quality Report
        </h3>
        <div className="flex gap-2">
          <button 
            onClick={handleDownloadJSON}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-indigo-600 transition-colors"
          >
            <Download size={16} /> JSON
          </button>
          <button 
            onClick={handleDownloadPDF}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-indigo-600 transition-colors"
          >
            <Printer size={16} /> {jobId ? "Download PDF" : "PDF / Print"}
          </button>
        </div>
      </div>
      
      {/* Print-only header */}
      <div className="hidden print:block mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Data Quality Report</h1>
        <p className="text-sm text-slate-500">Generated on {new Date().toLocaleDateString()}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Quality Score Gauge  */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center">
          <p className="text-sm font-medium text-slate-500 mb-4 uppercase tracking-wider">Overall Quality</p>
          <div className="relative flex items-center justify-center">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle className="text-slate-100" strokeWidth="10" stroke="currentColor" fill="transparent" r="58" cx="64" cy="64"/>
              <circle 
                className={getScoreColor(quality_score)} 
                strokeWidth="10" 
                strokeDasharray={364.4} 
                strokeDashoffset={364.4 - (364.4 * quality_score) / 100} 
                strokeLinecap="round" 
                stroke="currentColor" 
                fill="transparent" r="58" cx="64" cy="64"
              />
            </svg>
            <span className={`absolute text-2xl font-bold ${getScoreColor(quality_score)}`}>
              {quality_score}%
            </span>
          </div>
        </div>

        {/* Record Statistics  */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm col-span-2">
          <p className="text-sm font-medium text-slate-500 mb-6 uppercase tracking-wider">Record Breakdown</p>
          <div className="grid grid-cols-2 gap-8">
            <div className="space-y-1">
              <p className="text-xs font-bold text-slate-400 uppercase">Total Records</p>
              <p className="text-2xl font-bold text-slate-800">{total_records}</p>
            </div>
            <div className="space-y-1 text-right">
              <p className="text-xs font-bold text-slate-400 uppercase">Missing Data</p>
              <p className="text-2xl font-bold text-yellow-600">{missing_values_percent}%</p>
            </div>
            <div className="col-span-2 space-y-2">
              <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden flex">
                <div className="bg-green-500 h-full" style={{ width: `${(valid_records/total_records)*100}%` }}></div>
                <div className="bg-red-500 h-full" style={{ width: `${(invalid_records/total_records)*100}%` }}></div>
              </div>
              <div className="flex justify-between text-[10px] font-bold uppercase tracking-tighter">
                <span className="text-green-600 flex items-center gap-1"><CheckCircle2 size={10}/> Valid: {valid_records}</span>
                <span className="text-red-600 flex items-center gap-1"><AlertTriangle size={10}/> Invalid: {invalid_records}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detected Issues List  */}
      {issues && issues.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
            <p className="text-xs font-bold text-slate-700 uppercase tracking-widest">Processing Summary & Issues</p>
          </div>
          <div className="divide-y divide-slate-100">
            {issues.map((issue, idx) => (
              <div key={idx} className="px-6 py-4 flex items-start gap-4 hover:bg-slate-50/50 transition-colors">
                <CheckCircle2 size={18} className="text-emerald-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-slate-700 leading-relaxed">{issue}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Report - Changes */}
      {metrics.report && metrics.report.changes && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <ShieldCheck size={20} className="text-indigo-600" />
            Processing Changes
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(metrics.report.changes).map(([key, val]) => (
              <div key={key} className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex flex-col">
                <span className="text-xs text-slate-500 uppercase tracking-wider mb-1">{key.replace(/_/g, ' ')}</span>
                <span className="text-xl font-bold text-slate-800">{val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Report - Columns */}
      {metrics.report && metrics.report.columns && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <BarChart3 size={20} className="text-indigo-600" />
              Column Statistics
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 font-semibold">Column</th>
                  <th className="px-6 py-3 font-semibold">Type</th>
                  <th className="px-6 py-3 font-semibold">Missing</th>
                  <th className="px-6 py-3 font-semibold">Unique</th>
                  <th className="px-6 py-3 font-semibold">Mean</th>
                  <th className="px-6 py-3 font-semibold">Min</th>
                  <th className="px-6 py-3 font-semibold">Max</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {Object.entries(metrics.report.columns).map(([col, stats]) => (
                  <tr key={col} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3 font-medium text-slate-900">{col}</td>
                    <td className="px-6 py-3 text-slate-500 font-mono text-xs">{stats.dtype}</td>
                    <td className="px-6 py-3 text-slate-500">
                       <span className={stats.missing > 0 ? "text-amber-600 font-bold" : ""}>{stats.missing}</span>
                    </td>
                    <td className="px-6 py-3 text-slate-500">{stats.unique}</td>
                    <td className="px-6 py-3 text-slate-500">{stats.mean?.toFixed(2) || '-'}</td>
                    <td className="px-6 py-3 text-slate-500">{stats.min !== null && stats.min !== undefined ? (typeof stats.min === 'number' ? stats.min.toFixed(2) : stats.min) : '-'}</td>
                    <td className="px-6 py-3 text-slate-500">{stats.max !== null && stats.max !== undefined ? (typeof stats.max === 'number' ? stats.max.toFixed(2) : stats.max) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default QualityReport;