import React from 'react';
import { ShieldCheck, AlertTriangle, BarChart3, CheckCircle2 } from 'lucide-react';

const QualityReport = ({ metrics }) => {
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

  return (
    <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
        <BarChart3 size={20} className="text-blue-600" />
        Data Quality Report
      </h3>

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
      {issues && Object.keys(issues).length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
            <p className="text-xs font-bold text-slate-700 uppercase tracking-widest">Detected Issues</p>
          </div>
          <div className="divide-y divide-slate-100">
            {Object.entries(issues).map(([key, value]) => (
              <div key={key} className="px-6 py-4 flex items-start gap-4 hover:bg-slate-50/50 transition-colors">
                <AlertTriangle size={18} className="text-yellow-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-bold text-slate-800 capitalize">{key.replace(/_/g, ' ')}</p>
                  <p className="text-xs text-slate-500 leading-relaxed">{value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default QualityReport;