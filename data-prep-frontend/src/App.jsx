import React, { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Layout from './components/Layout';
import apiClient from './api/client';
import { Loader2 } from 'lucide-react';
import { ToastProvider } from './components/Toast';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    // Log error for debugging
    console.error('UI Error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
          <div className="bg-white rounded-xl shadow p-6 border border-slate-200 max-w-md text-center">
            <h2 className="text-lg font-bold text-slate-900 mb-2">Something went wrong</h2>
            <p className="text-slate-500 text-sm mb-4">Please refresh the page. If the issue persists, contact support.</p>
            <button
              className="btn-primary w-full"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppContent() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const key = localStorage.getItem('data_prep_api_key');
    if (!key) {
      setLoading(false);
      return;
    }

    try {
      await apiClient.get('/clients/me');
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Auth check failed:", error);
      localStorage.removeItem('data_prep_api_key');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('data_prep_api_key');
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 size={40} className="text-indigo-600 animate-spin" />
          <p className="text-slate-500 font-medium">Loading DataPrep AI...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <Layout onLogout={handleLogout}>
      <Dashboard />
    </Layout>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
