import React, { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import apiClient from '../api/client';

const ProtectedRoute = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = loading

  useEffect(() => {
    const checkAuth = async () => {
      const key = localStorage.getItem('data_prep_api_key');
      try {
        if (key) {
          await apiClient.get('/clients/me');
          setIsAuthenticated(true);
          return;
        }
        await apiClient.get('/auth/me');
        setIsAuthenticated(true);
      } catch {
        localStorage.removeItem('data_prep_api_key');
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 size={40} className="text-indigo-600 animate-spin" />
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
