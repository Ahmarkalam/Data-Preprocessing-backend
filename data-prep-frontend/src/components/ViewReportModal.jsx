import React from 'react';
import { X, FileText } from 'lucide-react';
import QualityReport from './QualityReport';

const ViewReportModal = ({ isOpen, onClose, job }) => {
  if (!isOpen || !job) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full border border-slate-200 transform transition-all scale-100 max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50 sticky top-0 z-10">
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <FileText size={22} className="text-indigo-600" /> Job Report: {job.job_id}
            </h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-lg text-slate-500 transition-colors">
            <X size={20}/>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto">
            {job.quality_metrics ? (
                <QualityReport metrics={job.quality_metrics} jobId={job.job_id} />
            ) : (
                <div className="text-center py-12 text-slate-500">
                    <FileText size={48} className="mx-auto mb-4 text-slate-300" />
                    <p>No report available for this job.</p>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default ViewReportModal;
