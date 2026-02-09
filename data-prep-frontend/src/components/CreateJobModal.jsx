import React, { useState, useEffect } from 'react';
import { Settings, Play, X, Sliders, Activity, Sparkles } from 'lucide-react';
import apiClient from '../api/client';

const CreateJobModal = ({ isOpen, onClose, inputPath, onJobCreated }) => {
  const [config, setConfig] = useState({
    remove_duplicates: true,
    handle_missing_values: true,
    missing_value_strategy: 'mean',
    normalize_data: false,
    text_cleaning: true,
    remove_html: true,
    remove_emojis: true,
    collapse_punctuation: true,
    normalize_whitespace: true,
    enforce_data_types: true,
    label_normalization: true,
    label_column: '',
    second_duplicate_removal: true,
    drop_outliers: false,
    outlier_threshold: 3.0,
    parse_dates: false,
    encoding_strategy: 'none'
  });
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    if (inputPath && isOpen) {
      runAnalysis();
    }
  }, [inputPath, isOpen]);

  const runAnalysis = async () => {
    setAnalyzing(true);
    setAnalysis(null);
    try {
      const response = await apiClient.post('/jobs/analyze', null, {
        params: { input_path: inputPath }
      });
      setAnalysis(response.data);
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setAnalyzing(false);
    }
  };

  const applySuggestions = () => {
    if (!analysis?.suggestions) return;
    setConfig(prev => ({
      ...prev,
      ...analysis.suggestions
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputPath) return alert("Upload a file first.");

    setLoading(true);
    try {
      const response = await apiClient.post('/jobs/create', null, {
        params: {
          input_path: inputPath,
          data_type: 'tabular', 
          remove_duplicates: config.remove_duplicates,
          handle_missing_values: config.handle_missing_values,
          missing_value_strategy: config.missing_value_strategy,
          normalize_data: config.normalize_data,
              text_cleaning: config.text_cleaning,
              remove_html: config.remove_html,
              remove_emojis: config.remove_emojis,
              collapse_punctuation: config.collapse_punctuation,
              normalize_whitespace: config.normalize_whitespace,
              enforce_data_types: config.enforce_data_types,
              label_normalization: config.label_normalization,
              label_column: config.label_column || undefined,
              second_duplicate_removal: config.second_duplicate_removal,
              drop_outliers: config.drop_outliers,
              outlier_threshold: config.outlier_threshold,
              parse_dates: config.parse_dates,
              encoding_strategy: config.encoding_strategy,
          auto_execute: true  
        }
      });
      onJobCreated(response.data);
    } catch (error) {
      const detail = error.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : JSON.stringify(detail || "Invalid Path");
      alert("Backend Error: " + msg);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-200 transform transition-all scale-100 max-h-[calc(100vh-2rem)] flex flex-col">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50 sticky top-0 z-10">
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Settings size={22} className="text-indigo-600" /> Configure Pipeline
            </h2>
            <p className="text-sm text-slate-500 mt-1">Select preprocessing steps for your data</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-lg text-slate-500 transition-colors">
            <X size={20}/>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6 flex-1 overflow-y-auto min-h-0">
          
          {/* AI Analysis Section */}
          {(analyzing || analysis) && (
            <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100 animate-in fade-in slide-in-from-top-4">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-white rounded-lg border border-indigo-100 shadow-sm text-indigo-600">
                  <Sparkles size={18} />
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h3 className="text-sm font-bold text-indigo-900 mb-1">AI Dataset Analysis</h3>
                    {analysis && (
                        <span className="text-[10px] font-medium px-2 py-0.5 bg-white rounded-full border border-indigo-100 text-indigo-600">
                            {analysis.total_rows} rows • {analysis.total_columns} cols
                        </span>
                    )}
                  </div>
                  
                  {analyzing ? (
                    <div className="flex items-center gap-2 text-xs text-indigo-700 mt-2">
                      <div className="w-3 h-3 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                      Analyzing your data...
                    </div>
                  ) : (
                    <>
                      <div className="space-y-2 mb-3 mt-2">
                        {analysis.warnings.length > 0 ? (
                          analysis.warnings.map((w, i) => (
                            <div key={i} className="flex items-start gap-2 text-xs text-indigo-800">
                              <span className="mt-0.5">•</span> {w}
                            </div>
                          ))
                        ) : (
                          <p className="text-xs text-indigo-800">No critical issues detected. Your data looks good!</p>
                        )}
                      </div>
                      
                      {Object.keys(analysis.suggestions).length > 0 && analysis.warnings.length > 0 && (
                        <button 
                          type="button"
                          onClick={applySuggestions}
                          className="text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-3 py-1.5 rounded-lg transition-colors shadow-sm flex items-center gap-1"
                        >
                          <Sparkles size={12} /> Apply Recommendations
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-200 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-sm">
                  <Sliders size={20} className="text-indigo-600" />
                </div>
                <div>
                  <label className="text-base font-semibold text-slate-800 block">Remove Duplicates</label>
                  <p className="text-base text-slate-500">Identify and remove identical rows</p>
                </div>
              </div>
              <input 
                type="checkbox" 
                checked={config.remove_duplicates} 
                onChange={(e) => setConfig({...config, remove_duplicates: e.target.checked})} 
                className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-200 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-sm">
                  <Sliders size={20} className="text-indigo-600" />
                </div>
                <div>
                  <label className="text-base font-semibold text-slate-800 block">Remove Duplicates After Cleaning</label>
                  <p className="text-base text-slate-500">Run deduplication again post text cleanup</p>
                </div>
              </div>
              <input 
                type="checkbox" 
                checked={config.second_duplicate_removal} 
                onChange={(e) => setConfig({...config, second_duplicate_removal: e.target.checked})} 
                className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-200 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-sm">
                  <Activity size={20} className="text-indigo-600" />
                </div>
                <div>
                  <label className="text-base font-semibold text-slate-800 block">Normalize Data</label>
                  <p className="text-base text-slate-500">Scale numeric values between 0 and 1</p>
                </div>
              </div>
              <input 
                type="checkbox" 
                checked={config.normalize_data} 
                onChange={(e) => setConfig({...config, normalize_data: e.target.checked})} 
                className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
              />
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <label className="text-base font-semibold text-slate-800 block mb-3">Handle Missing Values</label>
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
                <div className="flex items-center gap-3 mb-3 sm:mb-0">
                  <input 
                    type="checkbox" 
                    checked={config.handle_missing_values} 
                    onChange={(e) => setConfig({...config, handle_missing_values: e.target.checked})}
                    className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                  />
                  <span className="text-base text-slate-600">Enable</span>
                </div>
                <select
                  value={config.missing_value_strategy}
                  onChange={(e) => setConfig({...config, missing_value_strategy: e.target.value})}
                  className="text-base border border-slate-300 rounded-lg px-3 py-2 bg-white w-full sm:w-auto"
                >
                  <option value="mean">Mean</option>
                  <option value="median">Median</option>
                  <option value="mode">Mode</option>
                  <option value="drop">Drop Rows</option>
                </select>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
              <label className="text-base font-semibold text-slate-800 block">Text Cleaning</label>
              <div className="flex items-center gap-3">
                <input 
                  type="checkbox" 
                  checked={config.text_cleaning} 
                  onChange={(e) => setConfig({...config, text_cleaning: e.target.checked})}
                  className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                />
                <span className="text-base text-slate-600">Enable</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3">
                <label className="flex items-center gap-3 text-base text-slate-700">
                  <input type="checkbox" className="w-5 h-5" checked={config.remove_html} onChange={(e)=>setConfig({...config, remove_html: e.target.checked})} />
                  Remove HTML
                </label>
                <label className="flex items-center gap-3 text-base text-slate-700">
                  <input type="checkbox" className="w-5 h-5" checked={config.remove_emojis} onChange={(e)=>setConfig({...config, remove_emojis: e.target.checked})} />
                  Remove Emojis
                </label>
                <label className="flex items-center gap-3 text-base text-slate-700">
                  <input type="checkbox" className="w-5 h-5" checked={config.collapse_punctuation} onChange={(e)=>setConfig({...config, collapse_punctuation: e.target.checked})} />
                  Collapse Punctuation
                </label>
                <label className="flex items-center gap-3 text-base text-slate-700">
                  <input type="checkbox" className="w-5 h-5" checked={config.normalize_whitespace} onChange={(e)=>setConfig({...config, normalize_whitespace: e.target.checked})} />
                  Normalize Whitespace
                </label>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
              <label className="text-base font-semibold text-slate-800 block">Labels</label>
              <div className="flex items-center gap-3">
                <input 
                  type="checkbox" 
                  checked={config.label_normalization} 
                  onChange={(e) => setConfig({...config, label_normalization: e.target.checked})}
                  className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                />
                <span className="text-base text-slate-600">Normalize to 0/1</span>
              </div>
              <input
                type="text"
                value={config.label_column}
                onChange={(e)=>setConfig({...config, label_column: e.target.value})}
                placeholder="Label column name (optional)"
                className="w-full text-base border border-slate-300 rounded-lg px-3 py-2 bg-white"
              />
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
              <label className="text-base font-semibold text-slate-800 block">Data Types</label>
              <div className="flex items-center gap-3">
                <input 
                  type="checkbox" 
                  checked={config.enforce_data_types} 
                  onChange={(e) => setConfig({...config, enforce_data_types: e.target.checked})}
                  className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                />
                <span className="text-base text-slate-600">Coerce numeric columns, treat empty as missing</span>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
              <label className="text-base font-semibold text-slate-800 block">Feature Engineering</label>
              
              <div className="flex items-center gap-3">
                <input 
                  type="checkbox" 
                  checked={config.parse_dates} 
                  onChange={(e) => setConfig({...config, parse_dates: e.target.checked})}
                  className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                />
                <span className="text-base text-slate-600">Auto-parse Dates</span>
              </div>

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pt-3 border-t border-slate-200">
                 <span className="text-base text-slate-600 font-medium mb-2 sm:mb-0">Categorical Encoding</span>
                 <select
                  value={config.encoding_strategy}
                  onChange={(e) => setConfig({...config, encoding_strategy: e.target.value})}
                  className="text-base border border-slate-300 rounded-lg px-3 py-2 bg-white w-full sm:w-auto"
                >
                  <option value="none">None</option>
                  <option value="onehot">One-Hot Encoding</option>
                  <option value="label">Label Encoding</option>
                </select>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
              <label className="text-base font-semibold text-slate-800 block">Outliers</label>
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
                <div className="flex items-center gap-3 mb-3 sm:mb-0">
                  <input 
                    type="checkbox" 
                    checked={config.drop_outliers} 
                    onChange={(e) => setConfig({...config, drop_outliers: e.target.checked})}
                    className="w-6 h-6 text-indigo-600 rounded focus:ring-indigo-500 border-gray-300"
                  />
                  <span className="text-base text-slate-600">Drop outliers (z-score)</span>
                </div>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  value={config.outlier_threshold}
                  onChange={(e)=>setConfig({...config, outlier_threshold: parseFloat(e.target.value)})}
                  className="w-full sm:w-28 text-base border border-slate-300 rounded-lg px-3 py-2 bg-white"
                  placeholder="3.0"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100">
            <button 
              type="submit" 
              disabled={loading} 
              className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? "Initializing..." : <><Play size={18} fill="currentColor" /> Run Pipeline</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Helper component for icon
const ActivityIcon = ({ size, className }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
  </svg>
);

export default CreateJobModal;
