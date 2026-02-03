import React, { useEffect, useState } from 'react';
import { X, ArrowRight, Activity, Database } from 'lucide-react';
import apiClient from '../api/client';

const BeforeAfterPreview = ({ isOpen, onClose, jobId }) => {
  const [data, setData] = useState({ original: [], cleaned: [], summary: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && jobId) {
      fetchPreview();
    }
  }, [isOpen, jobId]);

  const fetchPreview = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/jobs/${jobId}/preview`);
      setData(res.data);
    } catch (error) {
      console.error("Preview fetch failed", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const renderSummary = () => {
    const orig = data?.summary?.original;
    const clean = data?.summary?.cleaned;
    const diff = data?.summary?.diff;
    const origSug = Object.entries(orig?.suggestions || {}).filter(([, v]) => !!v).map(([k]) => k);
    const cleanSug = Object.entries(clean?.suggestions || {}).filter(([, v]) => !!v).map(([k]) => k);
    const warnings = [...(orig?.warnings || []), ...(clean?.warnings || [])];

    return (
      <div className="p-4 bg-white border-b border-slate-200 grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 mb-1">Rows</div>
          <div className="text-sm text-slate-800">
            <span className="font-bold">{orig?.total_rows ?? '-'}</span>
            <span className="mx-2 text-slate-400">→</span>
            <span className="font-bold text-emerald-700">{clean?.total_rows ?? '-'}</span>
          </div>
          {typeof diff?.rows_delta === 'number' && (
            <div className="text-xs text-slate-500 mt-1">Δ {diff.rows_delta}</div>
          )}
        </div>
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 mb-1">Columns</div>
          <div className="text-sm text-slate-800">
            <span className="font-bold">{orig?.total_columns ?? '-'}</span>
            <span className="mx-2 text-slate-400">→</span>
            <span className="font-bold text-emerald-700">{clean?.total_columns ?? '-'}</span>
          </div>
        </div>
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 mb-2">Suggestions (Original)</div>
          <div className="flex flex-wrap gap-2">
            {origSug.length === 0 ? (
              <span className="text-xs text-slate-400">None</span>
            ) : (
              origSug.map(s => (
                <span key={s} className="text-xs px-2 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  {s}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 mb-2">Warnings</div>
          <div className="flex flex-wrap gap-2">
            {warnings.length === 0 ? (
              <span className="text-xs text-slate-400">None</span>
            ) : (
              warnings.map((w, i) => (
                <span key={i} className="text-xs px-2 py-1 rounded-full bg-red-50 text-red-700 border border-red-200">
                  {w}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="md:col-span-4 p-4 rounded-xl border border-slate-200 bg-slate-50">
          <div className="text-xs font-semibold text-slate-500 mb-2">Applied (Cleaned)</div>
          <div className="flex flex-wrap gap-2">
            {cleanSug.length === 0 ? (
              <span className="text-xs text-slate-400">None</span>
            ) : (
              cleanSug.map(s => (
                <span key={s} className="text-xs px-2 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {s}
                </span>
              ))
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderTable = (rows, title, color) => {
    if (!rows || rows.length === 0) return (
      <div className={`flex-1 flex flex-col border border-${color}-200 rounded-xl overflow-hidden shadow-sm bg-white`}>
         <div className={`p-3 bg-${color}-50 border-b border-${color}-200 font-semibold text-${color}-800 flex items-center gap-2`}>
          <Database size={16} /> {title}
        </div>
        <div className="flex-1 flex items-center justify-center text-slate-400 p-8">
          No data available
        </div>
      </div>
    );

    const columns = Object.keys(rows[0]);
    
    return (
      <div className={`flex-1 flex flex-col border border-${color}-200 rounded-xl overflow-hidden shadow-sm`}>
        <div className={`p-3 bg-${color}-50 border-b border-${color}-200 font-semibold text-${color}-800 flex items-center gap-2 shrink-0`}>
          <Database size={16} /> {title} <span className="text-xs opacity-70">({rows.length} rows preview)</span>
        </div>
        <div className="flex-1 overflow-auto bg-white relative">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="sticky top-0 bg-slate-50 z-10 shadow-sm">
                <tr>
                  {columns.map(col => (
                    <th key={col} className="px-3 py-2 font-semibold text-slate-600 border-b border-r border-slate-200 whitespace-nowrap bg-slate-50">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 transition-colors">
                    {columns.map(col => (
                      <td key={col} className="px-3 py-2 border-b border-r border-slate-100 whitespace-nowrap max-w-[200px] overflow-hidden text-ellipsis" title={String(row[col])}>
                        {String(row[col] === null ? '' : row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-[95vw] h-[90vh] flex flex-col overflow-y-auto animate-in fade-in zoom-in duration-200">
        
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-white shrink-0">
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Activity className="text-indigo-600" /> Data Preview Comparison
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <X size={20} className="text-slate-500" />
          </button>
        </div>

        {!loading && renderSummary()}

        <div className="flex-1 p-4 bg-slate-50 overflow-auto flex flex-col md:flex-row gap-4 min-h-0">
          {loading ? (
             <div className="w-full h-full flex items-center justify-center text-slate-500 gap-2">
                <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                Loading preview...
             </div>
          ) : (
            <>
              {renderTable(data.original, "Original Data", "slate")}
              <div className="hidden md:flex items-center justify-center text-slate-400">
                <ArrowRight size={24} />
              </div>
              {renderTable(data.cleaned, "Cleaned Data", "emerald")}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default BeforeAfterPreview;
