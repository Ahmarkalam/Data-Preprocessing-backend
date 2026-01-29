import React, { useState } from 'react';
import { KeyRound, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import apiClient from '../api/client';

const Login = ({ onLoginSuccess }) => {
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!apiKey.trim()) return;
    
    // Sanitize key: remove non-printable ASCII chars (keep only space through tilde)
    const cleanKey = apiKey.replace(/[^ -~]/g, "").trim();
    console.log("Sanitized key length:", cleanKey.length); // Debugging

    setLoading(true);
    setError('');

    try {
      if (!cleanKey) throw new Error("Key is empty after sanitation");
      
      // Temporarily store key to test connection
      localStorage.setItem('data_prep_api_key', cleanKey);
      
      // Verify key by fetching client details
      // We assume /clients/me or similar exists, or we try a simple health check with auth
      // Based on typical patterns, we'll try to get client info. 
      // If the backend doesn't have a specific "whoami" endpoint, 
      // we might need to rely on the fact that the request succeeded.
      // Let's assume a protected endpoint check.
      
      await apiClient.get('/clients/me');
      
      onLoginSuccess();
    } catch (err) {
      console.error("Login failed:", err);
      // Log more details if it's an axios error
      if (err.response) {
        console.error("Response data:", err.response.data);
        console.error("Response status:", err.response.status);
      }
      localStorage.removeItem('data_prep_api_key');
      setError(err.message || 'Invalid API Key. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
        <div className="p-8">
          <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-200">
            <KeyRound className="text-white" size={24} />
          </div>
          
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Welcome Back</h1>
          <p className="text-slate-500 mb-8">Enter your API key to access the DataPrep dashboard.</p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="input-field"
                placeholder="dp_live_..."
                autoFocus
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100 animate-in fade-in slide-in-from-top-1">
                <AlertCircle size={16} className="mt-0.5 shrink-0" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !apiKey}
              className="w-full btn-primary py-3 group"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Verifying...
                </>
              ) : (
                <>
                  Access Dashboard
                  <ArrowRight size={18} className="group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>
          </form>
        </div>
        
        <div className="bg-slate-50 p-6 text-center border-t border-slate-100">
          <p className="text-sm text-slate-500">
            Don't have a key?{' '}
            <a href="#" className="text-indigo-600 font-semibold hover:underline">
              Contact Administrator
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
