import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import apiClient from '../api/client';
import Dashboard from './Dashboard';
import Layout from '../components/Layout';

const TrialPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const setupGuestSession = async () => {
      // 1. Check if we already have a key
      const existingKey = localStorage.getItem('data_prep_api_key');
      
      if (existingKey) {
        // Verify it
        try {
          await apiClient.get('/clients/me');
          // If it's a valid key, we're good.
          // If the user explicitly clicked "Try for Free" but has a pro key, 
          // we just show them the dashboard (maybe with a toast "You are already logged in").
          setLoading(false);
          return;
        } catch {
          // Invalid key, clear it and proceed to generate guest key
          localStorage.removeItem('data_prep_api_key');
        }
      }

      // 2. Generate new guest key
      try {
        const { data } = await apiClient.post('/auth/guest');
        const { api_key } = data;
        
        localStorage.setItem('data_prep_api_key', api_key);
        // Navigate to dashboard for a consistent experience
        navigate('/dashboard');
        return;
      } catch (error) {
        console.error("Failed to create guest session:", error);
        setError("Failed to start free trial. Please try again later.");
        setLoading(false);
      }
    };

    setupGuestSession();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 size={40} className="text-indigo-600 animate-spin" />
          <p className="text-slate-500 font-medium">Setting up your free trial environment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center max-w-md p-6 bg-white rounded-xl shadow-lg border border-red-100">
          <h2 className="text-xl font-bold text-red-600 mb-2">Error</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary w-full">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <Layout onLogout={() => {
      localStorage.removeItem('data_prep_api_key');
      navigate('/');
    }}>
      <div className="mb-6 bg-indigo-50 border border-indigo-100 p-4 rounded-lg flex items-center justify-between">
        <div>
          <h3 className="font-bold text-indigo-900">Guest Trial Mode</h3>
          <p className="text-sm text-indigo-700">Your session will expire in 24 hours. Data limit: 50MB.</p>
        </div>
        <button 
          onClick={() => navigate('/login')}
          className="text-sm bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
        >
          Upgrade to Pro
        </button>
      </div>
      <Dashboard />
    </Layout>
  );
};

export default TrialPage;
