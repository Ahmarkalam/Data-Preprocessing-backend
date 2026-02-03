import React, { useState, useEffect } from 'react';
import { User, Mail, Building, Key, Save, Loader2, Copy, CheckCircle } from 'lucide-react';
import apiClient from '../api/client';
import { useToast } from '../components/useToast';

const Settings = () => {
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    company: '',
    api_key: '',
    plan_type: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await apiClient.get('/clients/me');
        setProfile(res.data);
      } catch (error) {
        console.error("Failed to fetch profile:", error);
        addToast("Failed to load profile settings", "error");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [addToast]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      // Assuming we have an update endpoint, or we mock it for now
      // The backend route for update is PATCH /clients/{client_id}
      // But we need to know the ID. 'profile.id' should have it.
      
      await apiClient.patch(`/clients/${profile.id}`, {
        name: profile.name,
        company: profile.company
      });
      
      addToast("Profile updated successfully", "success");
    } catch (error) {
      console.error("Failed to update profile:", error);
      addToast("Failed to update profile", "error");
    } finally {
      setSaving(false);
    }
  };

  const copyApiKey = () => {
    navigator.clipboard.writeText(profile.api_key);
    setCopied(true);
    addToast("API Key copied to clipboard", "success");
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) return <div className="text-slate-500">Loading settings...</div>;

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500">Manage your account settings and API preferences.</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900">Profile Information</h2>
          <p className="text-sm text-slate-500">Update your account details.</p>
        </div>
        
        <form onSubmit={handleSave} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({...profile, name: e.target.value})}
                  className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Company</label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  value={profile.company || ''}
                  onChange={(e) => setProfile({...profile, company: e.target.value})}
                  className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="email"
                  value={profile.email}
                  disabled
                  className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-500 cursor-not-allowed"
                />
              </div>
              <p className="text-xs text-slate-400 mt-1">Email address cannot be changed.</p>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-2 px-6"
            >
              {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
              Save Changes
            </button>
          </div>
        </form>
      </div>

      {/* API Key Section */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900">API Configuration</h2>
          <p className="text-sm text-slate-500">Manage your API keys and access.</p>
        </div>
        
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Your API Key</label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  value={profile.api_key}
                  readOnly
                  className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 bg-slate-50 font-mono text-slate-600"
                />
              </div>
              <button 
                onClick={copyApiKey}
                className="px-4 py-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-600 flex items-center gap-2 transition-colors"
              >
                {copied ? <CheckCircle size={18} className="text-green-600" /> : <Copy size={18} />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Keep this key secret. Do not share it in client-side code.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
