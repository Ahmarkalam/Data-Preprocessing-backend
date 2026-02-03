import React, { useState, useEffect } from 'react';
import { BarChart3, Database, HardDrive, Zap, Clock, Calendar } from 'lucide-react';
import apiClient from '../api/client';
import StatsCard from '../components/StatsCard';

const Analytics = () => {
  const [usageData, setUsageData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const clientRes = await apiClient.get('/clients/me');
        // We could also fetch specific usage logs if we had an endpoint, 
        // but for now we'll use client details which has some aggregated stats
        setUsageData(clientRes.data);
      } catch (error) {
        console.error("Failed to fetch usage data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsage();
  }, []);

  if (loading) {
    return <div className="text-slate-500">Loading analytics...</div>;
  }

  if (!usageData) {
    return <div className="text-red-500">Failed to load analytics data.</div>;
  }

  const quotaPercent = (usageData.used_quota_mb / usageData.monthly_quota_mb) * 100;
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
        <p className="text-slate-500">Monitor your usage and processing metrics.</p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard 
          title="Total Jobs" 
          value={usageData.total_jobs} 
          change={`${usageData.completed_jobs} Completed`}
          icon={Zap} 
        />
        <StatsCard 
          title="Data Processed" 
          value={`${usageData.used_quota_mb.toFixed(2)} MB`} 
          change="This Month"
          icon={HardDrive} 
        />
        <StatsCard 
          title="Success Rate" 
          value={usageData.total_jobs > 0 ? `${((usageData.completed_jobs / usageData.total_jobs) * 100).toFixed(0)}%` : "0%"} 
          change="Job Completion"
          icon={BarChart3} 
        />
      </div>

      {/* Quota Usage Section */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Database size={20} className="text-indigo-600" />
            Storage & Quota Usage
          </h2>
          <span className="text-sm font-medium text-slate-500">
            Resets on {new Date(new Date().setDate(1)).toLocaleDateString()}
          </span>
        </div>

        <div className="mb-2 flex justify-between text-sm font-medium">
          <span className="text-slate-700">{usageData.used_quota_mb.toFixed(2)} MB Used</span>
          <span className="text-slate-500">{usageData.monthly_quota_mb} MB Limit</span>
        </div>
        
        <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden mb-6">
          <div 
            className={`h-full rounded-full transition-all duration-500 ${
              quotaPercent > 90 ? 'bg-red-500' : quotaPercent > 70 ? 'bg-amber-500' : 'bg-indigo-600'
            }`}
            style={{ width: `${Math.min(quotaPercent, 100)}%` }}
          ></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="text-slate-400" size={18} />
              <span className="text-sm font-semibold text-slate-700">Processing Time</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">~1.2s <span className="text-sm font-normal text-slate-500">avg per file</span></p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
             <div className="flex items-center gap-3 mb-2">
              <Calendar className="text-slate-400" size={18} />
              <span className="text-sm font-semibold text-slate-700">Current Plan</span>
            </div>
            <p className="text-2xl font-bold text-slate-900 capitalize">{usageData.plan_type} <span className="text-sm font-normal text-slate-500">tier</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
