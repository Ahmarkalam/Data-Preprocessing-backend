import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle, AlertCircle, X, CloudUpload } from 'lucide-react';
import apiClient from '../api/client';

const FileUpload = ({ onUploadSuccess, maxSizeMB = 50 }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('idle'); // idle, success, error
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      if (selectedFile.size > maxSizeMB * 1024 * 1024) {
        setFile(null);
        setErrorMsg(`File size exceeds ${maxSizeMB}MB limit.`);
        return;
      }
      setFile(selectedFile);
      setStatus('idle');
      setErrorMsg('');
      setUploadProgress(0);
    }
  }, [maxSizeMB]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    multiple: false,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    }
  });

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setUploadProgress(0);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post('/upload/tabular', formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      setStatus('success');
      if (onUploadSuccess) onUploadSuccess(response.data);
    } catch (error) {
      console.error("Upload failed:", error);
      setStatus('error');
      setErrorMsg(error.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <div className="p-6">
        <h3 className="text-lg font-bold text-slate-800 mb-1">Upload Data</h3>
        <p className="text-sm text-slate-500 mb-4">Supported formats: CSV, JSON, XLSX</p>
        
        {errorMsg && !file && (
           <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2">
             <AlertCircle size={16} /> {errorMsg}
           </div>
        )}

        {!file ? (
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 group
              ${isDragActive 
                ? 'border-indigo-500 bg-indigo-50' 
                : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50'}`}
          >
            <input {...getInputProps()} />
            <div className={`p-4 rounded-full mb-3 transition-colors ${isDragActive ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-500'}`}>
              <CloudUpload size={32} />
            </div>
            <p className="text-slate-700 font-semibold text-center mb-1">
              {isDragActive ? "Drop the file here" : "Click to upload or drag and drop"}
            </p>
            <p className="text-slate-400 text-xs text-center">
              Maximum file size {maxSizeMB}MB
            </p>
          </div>
        ) : (
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-600 rounded-lg text-white shadow-sm">
                  <File size={20} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">{file.name}</p>
                  <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(2)} KB</p>
                </div>
              </div>
              
              {status === 'idle' && (
                <button 
                  onClick={() => setFile(null)} 
                  className="text-slate-400 hover:text-red-500 transition-colors"
                >
                  <X size={18} />
                </button>
              )}
            </div>
            
            {status === 'idle' && (
              <button 
                onClick={handleUpload}
                disabled={uploading}
                className="w-full btn-primary"
              >
                {uploading ? (
                  <div className="flex flex-col w-full gap-2">
                    <div className="flex justify-between text-xs text-white/90">
                      <span>Uploading...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-indigo-700/50 rounded-full h-1.5">
                      <div 
                        className="bg-white h-1.5 rounded-full transition-all duration-300" 
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                ) : (
                  "Start Upload"
                )}
              </button>
            )}

            {status === 'success' && (
              <div className="flex items-center gap-2 text-green-600 text-sm font-medium bg-green-50 p-3 rounded-lg border border-green-100">
                <CheckCircle size={16} /> Upload Complete
              </div>
            )}

            {status === 'error' && (
              <div className="flex flex-col gap-1 text-red-600 text-sm font-medium bg-red-50 p-3 rounded-lg border border-red-100">
                 <div className="flex items-center gap-2">
                    <AlertCircle size={16} /> Upload Failed
                 </div>
                 {errorMsg && <p className="text-xs text-red-500 pl-6">{errorMsg}</p>}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
