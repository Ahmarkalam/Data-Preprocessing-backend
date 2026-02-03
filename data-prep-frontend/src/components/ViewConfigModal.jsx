import React from 'react';
import { X, Settings, Check, Minus } from 'lucide-react';

const ViewConfigModal = ({ isOpen, onClose, config }) => {
  if (!isOpen || !config) return null;

  const renderValue = (value) => {
    if (typeof value === 'boolean') {
      return value ? <Check size={16} className="text-emerald-500" /> : <Minus size={16} className="text-slate-300" />;
    }
    if (value === null || value === undefined) return <span className="text-slate-400 italic">None</span>;
    if (typeof value === 'object') return JSON.stringify(value);
    return <span className="text-slate-700 font-medium">{String(value)}</span>;
  };

  const formatKey = (key) => {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full border border-slate-200 transform transition-all scale-100 flex flex-col max-h-[80vh]">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50 rounded-t-2xl">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Settings size={20} className="text-indigo-600" /> Pipeline Configuration
            </h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-lg text-slate-500 transition-colors">
            <X size={20}/>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto">
          <div className="space-y-4">
            {Object.entries(config).map(([key, value]) => (
              <div key={key} className="flex justify-between items-center py-2 border-b border-slate-50 last:border-0">
                <span className="text-sm text-slate-600">{formatKey(key)}</span>
                <div className="flex items-center">
                  {renderValue(value)}
                </div>
              </div>
            ))}
            {Object.keys(config).length === 0 && (
              <div className="text-center text-slate-500 py-8">
                No configuration data available.
              </div>
            )}
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl">
           <button 
             onClick={onClose}
             className="w-full py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium rounded-lg transition-colors shadow-sm"
           >
             Close
           </button>
        </div>

      </div>
    </div>
  );
};

export default ViewConfigModal;
