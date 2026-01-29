import React, { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className={`
              pointer-events-auto flex items-start gap-3 p-4 rounded-lg shadow-lg border w-80 toast-enter
              ${toast.type === 'success' ? 'bg-white border-emerald-100 text-slate-800' : ''}
              ${toast.type === 'error' ? 'bg-white border-red-100 text-slate-800' : ''}
              ${toast.type === 'warning' ? 'bg-white border-yellow-100 text-slate-800' : ''}
              ${toast.type === 'info' ? 'bg-white border-blue-100 text-slate-800' : ''}
            `}
          >
            <div className="mt-0.5 shrink-0">
              {toast.type === 'success' && <CheckCircle size={18} className="text-emerald-500" />}
              {toast.type === 'error' && <AlertCircle size={18} className="text-red-500" />}
              {toast.type === 'warning' && <AlertTriangle size={18} className="text-yellow-500" />}
              {toast.type === 'info' && <Info size={18} className="text-blue-500" />}
            </div>
            
            <div className="flex-1 text-sm font-medium">
              {toast.message}
            </div>

            <button 
              onClick={() => removeToast(toast.id)}
              className="text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
